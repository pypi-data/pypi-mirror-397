"""Download command for bundle requests."""

from pathlib import Path
from typing import Optional

import requests
import typer
from rich.console import Console

from leap_bundle.utils.config import is_logged_in
from leap_bundle.utils.exception import handle_cli_exception
from leap_bundle.utils.manifest_download import (
    convert_huggingface_url,
    download_manifest,
    generate_directory_name_from_url,
    is_request_id,
    validate_json_url,
    verify_json_content,
)
from leap_bundle.utils.request_download import download_bundle_request

console = Console()


def download(
    request_id_or_model_name: Optional[str] = typer.Argument(
        None, help="Bundle request ID or LEAP model name to download"
    ),
    quantization: str = typer.Option(
        None,
        "--quantization",
        help="Quantization level to download if downloading an off-the-shelf LEAP model",
    ),
    output_path: str = typer.Option(
        None, "--output-path", help="Directory path to download files to"
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files if they already exist"
    ),
    ctx: typer.Context = typer.Option(None, hidden=True),
) -> None:
    """Download bundle request output or JSON manifest with referenced files.

    This command supports two modes of operation:

    1. Bundle Request Download:
       Provide a bundle request ID to download the generated model bundle file.
       Requires authentication via 'leap-bundle login'.

    2. LEAP Model Download (via Manifest):
       Provide a LEAP model name (and optionally a quantization level). The command will:
       - Resolve the appropriate manifest URL for the model/quantization
       - Download the JSON manifest
       - Download all model files referenced in load_time_parameters
       - Update the local manifest to use relative paths to the downloaded files

    Examples:
        Download a bundle request:
        $ leap-bundle download abc123 --output-path ./output

        Download a LEAP model by name (auto-generates directory name):
        $ leap-bundle download LFM2-1.2B --quantization Q5_K_M

        Download a LEAP model by name with custom output path:
        $ leap-bundle download LFM2-1.2B --quantization Q5_K_M --output-path ./models
    """
    # Show help if no argument provided
    if request_id_or_model_name is None:
        console.print(
            "[yellow]⚠[/yellow] Missing required argument: REQUEST_ID_OR_MODEL_NAME\n"
        )
        console.print(
            "Usage: leap-bundle download [OPTIONS] REQUEST_ID_OR_MODEL_NAME\n"
        )
        console.print(
            "Download bundle request output or JSON manifest with referenced files.\n"
        )
        console.print("[bold]Arguments:[/bold]")
        console.print(
            "  REQUEST_ID_OR_MODEL_NAME  Bundle request ID or LEAP model name to download\n"
        )
        console.print("[bold]Options:[/bold]")
        console.print(
            "  --quantization TEXT  Quantization level for LEAP model downloads (e.g., Q5_K_M)"
        )
        console.print("  --output-path TEXT  Directory path to download files to")
        console.print(
            "  --overwrite         Overwrite existing files if they already exist"
        )
        console.print("  --help              Show this message and exit.\n")
        console.print("[bold]Examples:[/bold]")
        console.print("  # Download a bundle request:")
        console.print("  $ leap-bundle download abc123 --output-path ./output\n")
        console.print("  # Download an off-the-shelf LEAP model by name:")
        console.print("  $ leap-bundle download LFM2-1.2B --quantization Q5_K_M\n")
        raise typer.Exit(0)

    # Check if input is a URL or a request ID
    if is_request_id(request_id_or_model_name):
        # Handle request ID download
        request_id = request_id_or_model_name

        if not is_logged_in():
            console.print(
                "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
            )
            raise typer.Exit(1)

        # Use current directory if output_path not specified
        if output_path is None:
            output_path = "."

        output_dir = Path(output_path)
        if not output_dir.exists():
            console.print(
                f"[red]✗[/red] Output directory does not exist: {output_path}"
            )
            raise typer.Exit(1)

        if not output_dir.is_dir():
            console.print(f"[red]✗[/red] Output path is not a directory: {output_path}")
            raise typer.Exit(1)

        try:
            download_bundle_request(request_id, output_dir, overwrite=overwrite)
        except Exception as e:
            handle_cli_exception(e)
    else:
        model_name = request_id_or_model_name

        # Verify quantization method is provided, or prompt for it
        if quantization is None:
            quantization = typer.prompt(
                "Enter quantization level to download - hit enter to proceed with default",
                default="Q5_K_M",
            )

        # Get manifest URL from endpoint
        params = {"quantization_method": quantization, "model_name": model_name}
        manifest_location_response = requests.get(
            "https://leap.liquid.ai/api/edge-sdk/model-manifest", params=params
        )
        if not manifest_location_response.ok:
            console.print(
                f"[red]✗[/red] Manifest does not exist for model: {model_name} and quantization level: {quantization}."
            )
            raise typer.Exit(1)

        huggingface_manifest_url = manifest_location_response.json()["manifest_url"]

        # Validate that URL points to a JSON file
        if not validate_json_url(huggingface_manifest_url):
            console.print(
                "[red]✗[/red] URL does not appear to point to a JSON file. "
                "Please provide a URL ending with .json"
            )
            raise typer.Exit(1)

        # Convert HuggingFace blob URLs to resolve URLs
        manifest_url = convert_huggingface_url(huggingface_manifest_url)
        if manifest_url != huggingface_manifest_url:
            console.print("[blue]ℹ[/blue] Converted HuggingFace URL to raw file URL")
            console.print(f"[blue]ℹ[/blue] Using: {manifest_url}")

        # Verify the URL returns JSON content
        console.print("[blue]ℹ[/blue] Verifying URL returns JSON content...")
        is_valid, error_msg = verify_json_content(manifest_url)
        if not is_valid:
            console.print(f"[red]✗[/red] {error_msg}")
            raise typer.Exit(1)

        # Determine output directory
        if output_path is None:
            # Generate directory name from URL
            dir_name = generate_directory_name_from_url(manifest_url)
            output_dir = Path.cwd() / dir_name
            console.print(
                f"[blue]ℹ[/blue] No output path specified, using: {output_dir}"
            )
        else:
            output_dir = Path(output_path)

        try:
            download_manifest(manifest_url, output_dir, overwrite=overwrite)
        except Exception as e:
            handle_cli_exception(e)
