"""Scanner integration for Grype and Trivy vulnerability scanners."""

import json
import tempfile
from pathlib import Path
from typing import Any

from rich.console import Console

from ..core.constants import FIELD_ARTIFACTS, FIELD_DESCRIPTOR, FIELD_MATCHES, FIELD_SCANNER, FIELD_SOURCE_FILE
from ..core.exceptions import ReportLoadError
from ..core.json_utils import load_json_report
from ..core.models import ScannerType
from .parallel_scanner import parallel_scan_files
from .scanner_tools import convert_to_cyclonedx, scan_sbom_with_grype, scan_with_trivy

console = Console()


def _get_pipeline_processor():
    """Lazy import of pipeline to avoid circular dependency at module load time."""
    from .pipeline import parallel_pipeline_processing

    return parallel_pipeline_processing


def process_grype_reports(
    reports_dir: Path,
    verbose: bool = False,
    max_workers: int | None = None,
) -> list[dict[str, Any]]:
    """Process reports for Grype scanning with parallel execution.

    Handles two scenarios:
    1. Existing Grype reports - loaded directly without re-scanning
    2. SBOM files - scanned with Grype only (parallel execution)

    Args:
        reports_dir: Directory containing SBOM files and/or Grype reports
        verbose: Enable detailed logging
        max_workers: Maximum concurrent workers for SBOM processing (None = auto-detect)

    Returns:
        List of Grype report dictionaries
    """
    reports: list[dict[str, Any]] = []

    # Find all JSON files (recursively)
    json_files: list[Path] = list(reports_dir.rglob("*.json"))
    if not json_files:
        error_msg = f"No JSON files found in '{reports_dir}'"
        console.print(f"[red]Error:[/red] {error_msg}", style="bold red")
        raise ReportLoadError(str(reports_dir), "No JSON files found in directory")

    # Separate files by type
    sbom_files: list[Path] = []
    grype_report_files: list[Path] = []

    for file_path in json_files:
        # Skip CycloneDX intermediate files
        if ".cdx." in file_path.name:
            continue

        try:
            data = load_json_report(file_path)

            # Check if this is an existing Grype report
            if data.get(FIELD_MATCHES):
                grype_report_files.append(file_path)
            # Check if this is a Syft SBOM (has "artifacts" and "descriptor" fields)
            elif data.get(FIELD_ARTIFACTS) and data.get(FIELD_DESCRIPTOR):
                sbom_files.append(file_path)
            else:
                if verbose:
                    console.print(
                        f"[yellow]⊘[/yellow] Skipped (unknown format): {file_path.name}",
                        style="dim",
                    )
        except Exception as e:
            if verbose:
                console.print(
                    f"[yellow]⊘[/yellow] Skipped {file_path.name}: {e}",
                    style="dim",
                )

    # Load existing Grype reports
    for report_file in grype_report_files:
        try:
            data = load_json_report(report_file)
            data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
            data[FIELD_SCANNER] = "grype"
            reports.append(data)

            if verbose:
                match_count = len(data.get(FIELD_MATCHES, []))
                console.print(
                    f"[green]✓[/green] Loaded: {report_file.name} ([cyan]{match_count}[/cyan] matches)",
                    style="dim",
                )
        except Exception as e:
            console.print(
                f"[red]Error[/red] loading {report_file.name}: {e}",
                style="bold red",
            )

    # Scan SBOM files with Grype only (parallel execution)
    if sbom_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            if verbose:
                console.print(
                    f"[cyan]Scanning {len(sbom_files)} SBOM files with Grype...[/cyan]",
                    style="dim",
                )

            # Scan SBOMs with Grype in parallel - errors are handled gracefully
            try:
                grype_results = parallel_scan_files(
                    files=sbom_files,
                    scan_func=scan_sbom_with_grype,
                    output_dir=output_dir,
                    verbose=verbose,
                    max_workers=max_workers,
                    operation_name="Scanning SBOMs with Grype",
                )

                # Load Grype scan results and filter out empty reports
                for sbom_file, grype_report_path in grype_results:
                    try:
                        grype_data = load_json_report(grype_report_path)
                        # Only include reports with vulnerability matches
                        if grype_data.get(FIELD_MATCHES):
                            grype_data[FIELD_SOURCE_FILE] = str(sbom_file.relative_to(reports_dir))
                            grype_data[FIELD_SCANNER] = "grype"
                            reports.append(grype_data)
                        elif verbose:
                            console.print(
                                f"[yellow]⊘[/yellow] Skipped {sbom_file.name}: No vulnerabilities found",
                                style="dim",
                            )
                    except Exception as e:
                        if verbose:
                            console.print(
                                f"[red]Error[/red] loading Grype report for {sbom_file.name}: {e}",
                                style="bold red",
                            )
            except Exception as e:
                # Handle scanning errors gracefully - log but continue
                if verbose:
                    console.print(
                        f"[red]Error[/red] scanning SBOMs with Grype: {e}",
                        style="bold red",
                    )

    return reports


def process_trivy_reports(
    reports_dir: Path,
    verbose: bool = False,
    max_workers: int | None = None,
) -> list[dict[str, Any]]:
    """Process reports for Trivy scanning with parallel execution.

    Handles three scenarios:
    1. Syft SBOM files: Converts to CycloneDX first, then scans with Trivy
    2. Grype reports: Converts to CycloneDX first, then scans with Trivy
    3. CycloneDX files: Scans directly with Trivy

    Args:
        reports_dir: Directory containing JSON reports or SBOM files.
        verbose: Whether to print detailed processing information.
        max_workers: Maximum number of concurrent workers (None = auto-detect).

    Returns:
        List of Trivy report dictionaries
    """
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path: Path = Path(temp_dir)
        trivy_reports: list[dict[str, Any]] = []

        # Search recursively for JSON files (handles subdirectories from downloaded packages)
        json_files: list[Path] = list(reports_dir.rglob("*.json"))
        if not json_files:
            error_msg = f"No JSON files found in '{reports_dir}'"
            console.print(f"[red]Error:[/red] {error_msg}", style="bold red")
            raise ReportLoadError(str(reports_dir), "No JSON files found in directory")

        # Separate files by type for parallel processing
        sbom_files: list[Path] = []
        grype_files: list[Path] = []

        report_file: Path
        for report_file in json_files:
            # Skip CycloneDX files (intermediate format, not source SBOMs)
            if ".cdx." in report_file.name:
                if verbose:
                    console.print(
                        f"[yellow]⊘[/yellow] Skipped (CycloneDX intermediate file): {report_file.name}",
                        style="dim",
                    )
                continue

            try:
                # Read the file to determine its type
                data: dict[str, Any] = load_json_report(report_file)

                # Check if this is a Syft SBOM (has "artifacts" and "descriptor" fields)
                is_sbom = data.get(FIELD_ARTIFACTS) and data.get(FIELD_DESCRIPTOR)

                if is_sbom:
                    # This is a Syft SBOM, convert to CycloneDX then scan with Trivy
                    if verbose:
                        console.print(
                            f"[cyan]Converting and scanning SBOM[/cyan] {report_file.name} with Trivy...",
                            style="dim",
                        )

                    # Convert to CycloneDX
                    cdx_file = convert_to_cyclonedx(report_file, temp_path, verbose)

                    # Scan with Trivy
                    trivy_report_path = scan_with_trivy(cdx_file, temp_path, verbose)

                    # Load the Trivy report
                    trivy_data: dict[str, Any] = load_json_report(trivy_report_path)
                    # Store relative path for package grouping
                    trivy_data[FIELD_SOURCE_FILE] = str(report_file.relative_to(reports_dir))
                    trivy_data[FIELD_SCANNER] = "trivy"
                    trivy_reports.append(trivy_data)

                    if verbose:
                        console.print(
                            f"  [green]✓[/green] Scanned: {report_file.name}",
                            style="dim",
                        )

                elif data.get(FIELD_MATCHES):
                    grype_files.append(report_file)
                else:
                    # Unknown format, skip
                    if verbose:
                        console.print(
                            f"[yellow]⊘[/yellow] Skipped (unknown format): {report_file.name}",
                            style="dim",
                        )

            except json.JSONDecodeError as e:
                console.print(
                    f"[red]Error[/red] parsing JSON in {report_file.name}: {e}",
                    style="bold red",
                )
                continue
            except Exception as e:
                console.print(
                    f"[red]Error[/red] processing {report_file.name}: {e}",
                    style="bold red",
                )
                continue

        # Process SBOM files - convert to CycloneDX then scan with Trivy
        if sbom_files:
            if verbose:
                console.print(
                    f"[cyan]Converting {len(sbom_files)} SBOMs to CycloneDX in parallel...[/cyan]",
                    style="dim",
                )

            # Step 1: Convert SBOMs to CycloneDX format in parallel
            cdx_results = parallel_scan_files(
                files=sbom_files,
                scan_func=convert_to_cyclonedx,
                output_dir=temp_path,
                verbose=verbose,
                max_workers=max_workers,
                operation_name="Converting SBOMs to CycloneDX",
            )

            # Step 2: Scan CycloneDX files with Trivy in parallel
            cdx_files = [cdx_path for _, cdx_path in cdx_results]
            if cdx_files:
                if verbose:
                    console.print(
                        f"[cyan]Scanning {len(cdx_files)} CycloneDX files with Trivy in parallel...[/cyan]",
                        style="dim",
                    )
                trivy_scan_results = parallel_scan_files(
                    files=cdx_files,
                    scan_func=scan_with_trivy,
                    output_dir=temp_path,
                    verbose=verbose,
                    max_workers=max_workers,
                    operation_name="Scanning CycloneDX with Trivy",
                )

                # Map CycloneDX files back to original SBOM files
                cdx_to_sbom = {cdx_path: sbom_path for sbom_path, cdx_path in cdx_results}

                # Load Trivy reports and add metadata
                for cdx_path, trivy_report_path in trivy_scan_results:
                    original_sbom_file = cdx_to_sbom.get(cdx_path)
                    if original_sbom_file:
                        trivy_data = load_json_report(trivy_report_path)
                        trivy_data[FIELD_SOURCE_FILE] = str(original_sbom_file.relative_to(reports_dir))
                        trivy_data[FIELD_SCANNER] = "trivy"
                        trivy_reports.append(trivy_data)

        # Process Grype reports in parallel (convert to CycloneDX then scan)
        if grype_files:
            if verbose:
                console.print(
                    f"[cyan]Converting {len(grype_files)} Grype reports to CycloneDX in parallel...[/cyan]",
                    style="dim",
                )
            # Step 1: Convert to CycloneDX in parallel
            cdx_results = parallel_scan_files(
                files=grype_files,
                scan_func=convert_to_cyclonedx,
                output_dir=temp_path,
                verbose=verbose,
                max_workers=max_workers,
                operation_name="Converting to CycloneDX",
            )

            # Step 2: Scan CycloneDX files with Trivy in parallel
            cdx_files = [cdx_path for _, cdx_path in cdx_results]
            if cdx_files:
                if verbose:
                    console.print(
                        f"[cyan]Scanning {len(cdx_files)} CycloneDX files with Trivy in parallel...[/cyan]",
                        style="dim",
                    )
                trivy_scan_results = parallel_scan_files(
                    files=cdx_files,
                    scan_func=scan_with_trivy,
                    output_dir=temp_path,
                    verbose=verbose,
                    max_workers=max_workers,
                    operation_name="Scanning CycloneDX with Trivy",
                )

                # Map CycloneDX files back to original Grype files
                cdx_to_grype = {cdx_path: grype_path for grype_path, cdx_path in cdx_results}

                # Load Trivy reports and add metadata
                for cdx_path, trivy_report_path in trivy_scan_results:
                    original_grype_file = cdx_to_grype.get(cdx_path)
                    if original_grype_file:
                        trivy_data = load_json_report(trivy_report_path)
                        trivy_data[FIELD_SOURCE_FILE] = str(original_grype_file.relative_to(reports_dir))
                        trivy_data[FIELD_SCANNER] = "trivy"
                        trivy_reports.append(trivy_data)

        return trivy_reports


def load_reports(
    reports_dir: Path,
    scanner: ScannerType = "grype",
    verbose: bool = False,
    max_workers: int | None = None,
) -> list[dict[str, Any]]:
    """Loads all JSON report files from the specified directory with parallel processing.

    Scanner behavior:
    - Grype: Loads existing Grype reports and scans SBOM files with Grype only
    - Trivy: Converts SBOM/Grype reports to CycloneDX, then scans with Trivy only

    Args:
        reports_dir: Path object pointing to the directory containing JSON
            report files.
        scanner: Type of scanner ("grype" or "trivy").
        verbose: Whether to print detailed loading information.
        max_workers: Maximum number of concurrent workers (None = auto-detect).

    Returns:
        A list of dictionaries, each representing a loaded scan report.
        Only reports with vulnerability matches are included.
    """
    # For Grype scanner, load Grype reports and scan SBOMs with Grype only
    if scanner == "grype":
        return process_grype_reports(reports_dir, verbose, max_workers)

    # For Trivy scanner, convert and scan with Trivy only
    return process_trivy_reports(reports_dir, verbose, max_workers)
