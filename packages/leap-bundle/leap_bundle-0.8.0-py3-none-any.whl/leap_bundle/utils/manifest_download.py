"""Utilities for downloading JSON manifests and referenced model files."""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def is_url(input_str: str) -> bool:
    """Check if the input string is a URL."""
    return input_str.startswith("http://") or input_str.startswith("https://")


def is_request_id(input_str: str) -> bool:
    """Check if the input string is a valid request ID."""
    return input_str.isdigit()


def validate_json_url(url: str) -> bool:
    """Validate that a URL points to a JSON file.

    Args:
        url: The URL to validate

    Returns:
        True if the URL appears to point to a JSON file, False otherwise
    """
    # Parse URL and get the path
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Check if path ends with .json (ignoring query parameters)
    return path.endswith(".json")


def convert_huggingface_url(url: str) -> str:
    """Convert HuggingFace blob URLs to raw/resolve URLs.

    HuggingFace URLs with /blob/ in the path return HTML pages.
    This function converts them to /resolve/ URLs which return the raw file.

    The function specifically looks for the pattern:
    https://huggingface.co/{org}/{repo}/blob/{branch}/{path}
    and converts it to:
    https://huggingface.co/{org}/{repo}/resolve/{branch}/{path}

    Args:
        url: The original URL

    Returns:
        The converted URL if it's a HuggingFace blob URL, otherwise the original URL
    """
    if "huggingface.co" not in url:
        return url

    parsed = urlparse(url)
    path_parts = parsed.path.split("/")

    # HuggingFace URL structure: /{org}/{repo}/blob/{branch}/{path...}
    # We need at least: ['', org, repo, 'blob', branch]
    if len(path_parts) >= 5 and path_parts[3] == "blob":
        # Replace the 'blob' at index 3 with 'resolve'
        path_parts[3] = "resolve"
        new_path = "/".join(path_parts)
        return parsed._replace(path=new_path).geturl()

    return url


def verify_json_content(url: str) -> tuple[bool, str]:
    """Verify that a URL returns JSON content.

    Makes a HEAD request to check the Content-Type header, or reads
    the first few bytes to verify it looks like JSON.

    Args:
        url: The URL to verify

    Returns:
        A tuple of (is_valid, error_message). If is_valid is True, error_message is empty.
        If is_valid is False, error_message contains a helpful error description.
    """
    try:
        # Try HEAD request first to check Content-Type
        head_response = requests.head(url, timeout=10, allow_redirects=True)
        content_type = head_response.headers.get("Content-Type", "").lower()

        # Check if Content-Type indicates JSON
        if content_type:
            if "application/json" in content_type:
                return True, ""
            elif "text/html" in content_type:
                if "huggingface.co" in url and "/blob/" in url:
                    return False, (
                        "URL points to a HuggingFace web page (HTML), not a raw JSON file. "
                        "Replace '/blob/' with '/resolve/' in the URL to get the raw file."
                    )
                return (
                    False,
                    "URL returns HTML content, not JSON. Please provide a URL to the raw JSON file.",
                )
            elif (
                "text/plain" not in content_type
                and "application/octet-stream" not in content_type
            ):
                return False, f"URL returns '{content_type}' content, not JSON."

        # If Content-Type is not conclusive, try reading first few bytes
        partial_response = requests.get(url, timeout=10, stream=True)
        first_bytes = (
            partial_response.content[:100].decode("utf-8", errors="ignore").strip()
        )
        partial_response.close()

        # Check if it looks like JSON (starts with { or [)
        if not first_bytes or (
            not first_bytes.startswith("{") and not first_bytes.startswith("[")
        ):
            if first_bytes.lower().startswith(
                "<!doctype html"
            ) or first_bytes.lower().startswith("<html"):
                return (
                    False,
                    "URL returns HTML content, not JSON. Please provide a URL to the raw JSON file.",
                )
            return False, "URL does not appear to return valid JSON content."

        return True, ""

    except requests.exceptions.RequestException as e:
        # If we can't verify, we'll let it proceed and fail later with a better error
        console.print(f"[yellow]⚠[/yellow] Could not verify URL content: {e}")
        return True, ""


def generate_directory_name_from_url(url: str) -> str:
    """Generate a directory name from a URL.

    Split by '/', remove common HuggingFace tokens, concatenate parts with underscore,
    and convert non-alphanumeric characters to underscore.

    Args:
        url: The URL to generate a directory name from

    Returns:
        A sanitized directory name suitable for use as a filesystem path

    Example:
        >>> generate_directory_name_from_url(
        ...     "https://huggingface.co/LiquidAI/LeapBundles/blob/main/LFM2-Audio-1.5B-GGUF/F16.json"
        ... )
        'LiquidAI_LeapBundles_LFM2_Audio_1_5B_GGUF_F16'
    """
    # Parse the URL and get the path
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]

    # Remove common HuggingFace tokens
    common_tokens = {"main", "blob", "resolve", "tree"}
    filtered_parts = [p for p in path_parts if p.lower() not in common_tokens]

    # Remove file extension from last part if it exists
    if filtered_parts and "." in filtered_parts[-1]:
        filtered_parts[-1] = filtered_parts[-1].rsplit(".", 1)[0]

    # Join with underscores and convert non-alphanumeric to underscore
    joined = "_".join(filtered_parts)
    # Replace non-alphanumeric characters with underscore
    cleaned = re.sub(r"[^a-zA-Z0-9]", "_", joined)
    # Remove consecutive underscores
    cleaned = re.sub(r"_+", "_", cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip("_")

    return cleaned if cleaned else "downloaded_bundle"


def download_file(
    url: str, output_path: Path, description: str = "Downloading"
) -> None:
    """Download a file from a URL to the specified path.

    Args:
        url: The URL to download from
        output_path: The local path to save the file to
        description: Description to show in the progress indicator

    Raises:
        requests.exceptions.RequestException: If the download fails
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"{description}...", total=None)

        try:
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            progress.update(task, description=f"{description} completed!")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to download from {url}: {e}")
            raise


def download_manifest(
    manifest_url: str, output_dir: Path, overwrite: bool = False
) -> None:
    """Download a JSON manifest and all referenced files.

    This function downloads a JSON manifest file and all model files referenced
    in the load_time_parameters section. After downloading, it updates the manifest
    to use relative paths instead of URLs.

    Args:
        manifest_url: URL to the JSON manifest file
        output_dir: Directory to save the manifest and referenced files
        overwrite: If True, overwrite existing files. If False, raise an error if file exists.

    Raises:
        FileExistsError: If the manifest file already exists and overwrite is False
        json.JSONDecodeError: If the manifest is not valid JSON
        requests.exceptions.RequestException: If any download fails
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract manifest filename from URL
    parsed_url = urlparse(manifest_url)
    manifest_filename = Path(unquote(parsed_url.path)).name
    if not manifest_filename.endswith(".json"):
        manifest_filename = "manifest.json"

    manifest_path = output_dir / manifest_filename

    # Check if manifest already exists
    if manifest_path.exists():
        if not overwrite:
            console.print(f"[red]✗[/red] Manifest file already exists: {manifest_path}")
            console.print(
                "[yellow]💡[/yellow] Use --overwrite flag to overwrite existing files"
            )
            raise FileExistsError(f"Manifest file already exists: {manifest_path}")
        else:
            console.print(
                f"[yellow]⚠[/yellow] Overwriting existing manifest: {manifest_path}"
            )

    # Download the manifest file
    console.print(f"[blue]ℹ[/blue] Downloading manifest from {manifest_url}...")
    download_file(manifest_url, manifest_path, "Downloading manifest")
    console.print(f"[green]✓[/green] Manifest downloaded to {manifest_path}")

    # Parse the manifest
    try:
        with open(manifest_path) as f:
            content = f.read()
            manifest_data = json.loads(content)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗[/red] Failed to parse JSON manifest: {e}")

        # Try to provide more helpful context
        try:
            with open(manifest_path) as f:
                first_lines = "".join([f.readline() for _ in range(5)])
                if first_lines.strip().lower().startswith(
                    "<!doctype html"
                ) or first_lines.strip().lower().startswith("<html"):
                    console.print(
                        "[red]✗[/red] The downloaded file appears to be HTML, not JSON."
                    )
                    if "huggingface.co" in manifest_url and "/blob/" in manifest_url:
                        console.print(
                            "[yellow]💡[/yellow] Tip: Replace '/blob/' with '/resolve/' in HuggingFace URLs to get the raw file."
                        )
                        suggested_url = manifest_url.replace("/blob/", "/resolve/")
                        console.print(f"[yellow]💡[/yellow] Try: {suggested_url}")
                    else:
                        console.print(
                            "[yellow]💡[/yellow] Make sure you're using a URL to the raw JSON file, not a web page."
                        )
                else:
                    console.print("[red]✗[/red] The file does not contain valid JSON.")
                    console.print(
                        f"[yellow]💡[/yellow] First few characters: {first_lines[:100]}"
                    )
        except Exception:
            pass

        # Re-raise the original error (caller should handle typer.Exit)
        raise

    # Extract load_time_parameters
    load_time_params = manifest_data.get("load_time_parameters", {})
    if not load_time_params:
        console.print("[yellow]⚠[/yellow] No load_time_parameters found in manifest")
        return

    # Download all files referenced in load_time_parameters
    console.print(
        f"[blue]ℹ[/blue] Found {len(load_time_params)} parameters in load_time_parameters"
    )

    updated_params = {}
    for param_name, param_value in load_time_params.items():
        # Skip non-string values (they're not file URLs)
        if not isinstance(param_value, str):
            updated_params[param_name] = param_value
            continue

        # Check if it's a URL
        if is_url(param_value):
            # Extract filename from URL
            file_parsed_url = urlparse(param_value)
            filename = Path(unquote(file_parsed_url.path)).name
            file_path = output_dir / filename

            console.print(f"[blue]ℹ[/blue] Downloading {param_name}: {filename}...")
            download_file(param_value, file_path, f"Downloading {filename}")
            console.print(f"[green]✓[/green] Downloaded {filename}")

            # Update the parameter to use relative path
            updated_params[param_name] = f"./{filename}"
        else:
            # Keep the original value if it's not a URL
            updated_params[param_name] = param_value

    # Update the manifest with relative paths
    manifest_data["load_time_parameters"] = updated_params

    # Write the updated manifest
    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

    console.print(
        f"[green]✓[/green] Manifest updated with relative paths: {manifest_path}"
    )
    console.print(
        f"[green]✓[/green] All files downloaded successfully to: {output_dir}"
    )
