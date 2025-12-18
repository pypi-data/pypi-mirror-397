"""Utilities for downloading bundle request outputs."""

from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from leap_bundle.utils.api_client import APIClient

console = Console()

doc_link_utm_params = {
    "utm_source": "leapbundle",
    "utm_medium": "cli",
}
doc_link = f"https://docs.liquid.ai/leap?{'&'.join(f'{k}={v}' for k, v in sorted(doc_link_utm_params.items()))}"


def download_bundle_request(
    request_id: str, output_dir: Path, overwrite: bool = False
) -> None:
    """Download a completed bundle request output.

    This function retrieves a signed download URL for the specified bundle request
    and downloads the bundle file to the output directory.

    Args:
        request_id: The ID of the bundle request to download
        output_dir: Directory to save the bundle file to
        overwrite: If True, overwrite existing files. If False, raise an error if file exists.

    Raises:
        FileExistsError: If the output file already exists and overwrite is False
        requests.exceptions.RequestException: If the download fails
        Exception: If the API request fails or other errors occur
    """
    client = APIClient()
    console.print(
        f"[blue]ℹ[/blue] Requesting download for bundle request {request_id}..."
    )

    result = client.download_bundle_request(request_id)
    signed_url = result["signed_url"]
    parsed_url = urlparse(signed_url)
    filename: str = Path(unquote(parsed_url.path)).name
    if not filename or filename == "/":
        filename = f"bundle-{request_id}.bundle"
    output_file = output_dir / filename

    console.print(f"[green]✓[/green] Download URL obtained for request {request_id}")

    # Check if output file already exists
    if output_file.exists():
        if not overwrite:
            console.print(f"[red]✗[/red] Output file already exists: {output_file}")
            console.print(
                "[yellow]💡[/yellow] Use --overwrite flag to overwrite existing files"
            )
            raise FileExistsError(f"Output file already exists: {output_file}")
        else:
            console.print(
                f"[yellow]⚠[/yellow] Overwriting existing file: {output_file}"
            )

    console.print(f"[blue]ℹ[/blue] Download URL: {signed_url}")
    console.print(
        "[blue]ℹ[/blue] If the download fails, you can manually retry using the above URL within 10 hours."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading bundle output...", total=None)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            response = requests.get(signed_url, timeout=300)
            response.raise_for_status()
            with open(output_file, "wb") as f:
                f.write(response.content)

            progress.update(task, description="Download completed!")

            console.print(
                f"[green]✓[/green] Download completed successfully! File saved to: {output_file}"
            )
            console.print(
                f"[blue]ℹ[/blue] Your model bundle is ready for deployment with the LEAP Edge SDK: {doc_link}"
            )

        except Exception as download_error:
            console.print(f"[red]✗[/red] Download failed: {download_error}")
            raise
