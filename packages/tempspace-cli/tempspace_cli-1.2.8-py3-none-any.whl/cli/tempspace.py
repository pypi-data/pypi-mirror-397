import argparse
import requests
import os
import sys
import hashlib
import multiprocessing

import math
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import qrcode
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn

from rich.live import Live
import shutil
import tempfile
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Default configuration
DEFAULT_SERVER_URL = "https://tempspace.needrp.net"
CHUNK_SIZE = 1024 * 1024  # 1MB

def parse_time(time_str: str) -> int:
    """Parses a user-provided time string into a total number of hours.

    Supports strings ending in 'd' for days, 'h' for hours, or a plain
    number for hours.

    Args:
        time_str: The time string to parse (e.g., '7d', '24h', '360').

    Returns:
        The total number of hours as an integer, or None if parsing fails.
    """
    time_str = time_str.lower().strip()
    if time_str.endswith('d'):
        try:
            days = int(time_str[:-1])
            return days * 24
        except ValueError:
            return None
    elif time_str.endswith('h'):
        try:
            return int(time_str[:-1])
        except ValueError:
            return None
    else:
        try:
            return int(time_str)
        except ValueError:
            return None

def format_size(size_bytes: int) -> str:
    """Converts a file size in bytes into a human-readable string.

    Args:
        size_bytes: The size of the file in bytes.

    Returns:
        A formatted string representing the size (e.g., "1.23 MB").
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def calculate_file_hash(filepath: str) -> str:
    """Calculates the SHA256 hash of a file.

    Args:
        filepath: The path to the file.

    Returns:
        The hex digest of the SHA256 hash.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()




def get_retry_session(retries=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504]):
    """Creates a requests Session with automatic retries."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def zip_directory(path: str) -> str:
    """Zips a directory and returns the path to the temporary zip file."""
    # Create a temporary directory to store the zip
    temp_dir = tempfile.mkdtemp()
    # Use the original folder name for the zip file
    base_name = os.path.basename(os.path.normpath(path))
    archive_base = os.path.join(temp_dir, base_name)
    
    shutil.make_archive(archive_base, 'zip', path)
    return archive_base + ".zip"


def download_file(console, url, password=None):
    """Downloads a file from Tempspace."""
    session = get_retry_session()
    
    try:
        # Check if it's a valid Tempspace URL and extract ID logic if needed, 
        # but for now we'll assume the URL is the full download link or similar.
        # Actually, the user provides the "Download Link" which usually leads to a landing page.
        # The CLI needs to handle the actual file download.
        # If the URL is http://site/DOWLOAD_ID, the direct download might be different.
        # Let's assume the user passes the direct download link or we try to download from it.
        # However, Tempspace likely has a landing page.
        # If the user gives the landing page URL, we might need to scrape or use an API.
        # Given I don't see the server code, I'll assume the user might provide a direct file URL 
        # or the tool should try to GET the URL.
        # If the server has an API like /api/download/<id>?password=..., that would be best.
        # Looking at upload_file response: `download_link = data.get('url')`.
        # Code audit earlier showed `DEFAULT_SERVER_URL`.
        # Use regex to extract ID from URL if possible, or just try GET.
        
        # Simple approach: GET the URL. If it initiates a download (headers), good.
        
        session.head(url, allow_redirects=True)
        # Check headers for content-disposition or just proceed
        
        if password:
             # If password is needed, headers or query param might be required.
             # Since I don't know the exact server auth mechanism for downloads,
             # I will try passing it as a query param 'password' or header 'X-Password'.
             # Better: ask the user to enter it if the server responds 401/403.
             pass

        # For a streaming download
        response = session.get(url, stream=True, params={'password': password} if password else None)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        disposition = response.headers.get('content-disposition')
        # Try to get filename from Content-Disposition
        filename = None
        if disposition:
            import re
            # specific regex for filename="example.txt" or filename=example.txt
            fname = re.findall(r'filename=["\']?([^"\';]+)["\']?', disposition)
            if fname:
                filename = fname[0]
        
        # Fallback to URL if no filename found from headers
        if not filename:
             from urllib.parse import unquote
             parsed_path = unquote(url.split("?")[0])
             filename = parsed_path.split("/")[-1]
             
        if not filename:
            filename = "downloaded_file"

        progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%", "•",
            TransferSpeedColumn(), "•",
            TimeRemainingColumn(),
        )
        
        with Live(Panel(progress, title="[cyan]Downloading[/cyan]", border_style="cyan", title_align="left")):
            task_id = progress.add_task(filename, total=total_size)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(CHUNK_SIZE):
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))
                    
        console.print(Panel(f"[bold green]Download successful![/] Saved to '{filename}'", border_style="green"))

    except Exception as e:
        console.print(Panel(f"[bold red]Download failed:[/] {e}", border_style="red"))


def upload_file(console, filepath, hours, password, one_time, qr, url):
    """Handles the upload of a single file.

    Args:
        console: The Rich console object for output.
        filepath (str): The path to the file to upload.
        hours (int): The number of hours until the file expires.
        password (str): The password for the file.
        one_time (bool): Whether the file should be a one-time download.
        qr (bool): Whether to display a QR code for the download link.
        url (str): The base URL of the Tempspace server.
    """
    # --- Validate Inputs ---
    if not os.path.isfile(filepath):
        console.print(Panel(f"[bold red]Error:[/] File not found at '{filepath}'", title="[bold red]Error[/bold red]", border_style="red"))
        return  # Return instead of exiting to allow other files to be processed

    # --- Display File Details ---
    table = Table(title="File Details", show_header=False, box=box.ROUNDED, border_style="cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("File Name", os.path.basename(filepath))
    table.add_row("File Size", format_size(os.path.getsize(filepath)))
    table.add_row("Expiration", f"{hours} hours")
    table.add_row("Password", "[green]Yes[/green]" if password else "[red]No[/red]")
    table.add_row("One-Time Download", "[green]Yes[/green]" if one_time else "[red]No[/red]")

    # --- Prepare Upload ---
    upload_url = f"{url.rstrip('/')}"
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    # --- Calculate Hash ---
    client_hash = calculate_file_hash(filepath)
    table.add_row("File Hash", f"[cyan]{client_hash}[/cyan]")
    console.print(table)


    # --- Chunked Upload ---
    response = None
    session = get_retry_session()
    try:
        # 1. Initiate Upload
        initiate_response = session.post(f"{upload_url}/upload/initiate")
        initiate_response.raise_for_status()
        upload_id = initiate_response.json()['upload_id']

        # 2. Upload Chunks
        progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%", "•",
            TransferSpeedColumn(), "•",
            TimeRemainingColumn(),
        )

        with Live(Panel(progress, title="[cyan]Uploading[/cyan]", border_style="cyan", title_align="left")):
            task_id = progress.add_task(filename, total=file_size)
            with open(filepath, 'rb') as f:
                chunk_number = 0
                while chunk := f.read(CHUNK_SIZE):
                    chunk_number += 1
                    chunk_data = {
                        'upload_id': upload_id,
                        'chunk_number': str(chunk_number)
                    }
                    files = {'file': (f'chunk_{chunk_number}', chunk, 'application/octet-stream')}

                    chunk_response = session.post(
                        f"{upload_url}/upload/chunk",
                        data=chunk_data,
                        files=files
                    )
                    chunk_response.raise_for_status()
                    progress.update(task_id, advance=len(chunk))

        # 3. Finalize Upload
        console.print(Panel("[bold green]Finalizing upload...[/bold green]", border_style="green"))
        finalize_data = {
            'upload_id': upload_id,
            'filename': filename,
            'hours': str(hours),
            'one_time': str(one_time).lower(),
            'client_hash': client_hash,  # Send the client-side hash for verification
        }
        if password:
            finalize_data['password'] = password

        response = session.post(f"{upload_url}/upload/finalize", data=finalize_data)
        response.raise_for_status()

    except FileNotFoundError:
        console.print(Panel(f"[bold red]Error:[/] The file '{filepath}' was not found.", title="[bold red]Error[/bold red]", border_style="red"))
        return
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if e.response:
            try:
                error_message = e.response.json().get('detail', e.response.text)
            except Exception:
                error_message = e.response.text
        console.print(Panel(f"[bold red]An error occurred:[/] {error_message}", title="[bold red]Error[/bold red]", border_style="red"))
        return
    except Exception as e:
        console.print(Panel(f"[bold red]An unexpected error occurred:[/] {e}", title="[bold red]Error[/bold red]", border_style="red"))
        return

    # --- Handle Response ---
    if response is not None:
        if response.status_code == 200:
            try:
                data = response.json()
                download_link = data.get('url')
                file_hash = data.get('hash')
                hash_verified = data.get('hash_verified', False)

                success_message = f"[bold green]Upload successful![/bold green]\n\nDownload Link: {download_link}"
                if file_hash:
                    verified_status = "[bold green]Yes[/bold green]" if hash_verified else "[bold red]No[/bold red]"
                    success_message += f"\nFile Hash (SHA256): {file_hash}"
                    success_message += f"\nHash Verified: {verified_status}"

                success_panel = Panel(success_message, title="[bold cyan]Success[/bold cyan]", border_style="green")
                console.print(success_panel)

                if qr:
                    qr_code = qrcode.QRCode()
                    qr_code.add_data(download_link)
                    qr_code.make(fit=True)
                    qr_code.print_ascii()

            except requests.exceptions.JSONDecodeError:
                # Fallback for older servers or unexpected plain text responses
                download_link = response.text.strip()
                success_panel = Panel(f"[bold green]Upload successful![/bold green]\n\nDownload Link: {download_link}",
                                      title="[bold cyan]Success[/bold cyan]", border_style="green")
                console.print(success_panel)

                if qr:
                    qr_code = qrcode.QRCode()
                    qr_code.add_data(download_link)
                    qr_code.make(fit=True)
                    qr_code.print_ascii()
        else:
            try:
                error_details = response.json()
                error_message = error_details.get('detail', 'No details provided.')
            except requests.exceptions.JSONDecodeError:
                error_message = response.text
            console.print(Panel(f"[bold red]Error:[/] Upload failed with status code {response.status_code}\n[red]Server message:[/] {error_message}", title="[bold red]Error[/bold red]", border_style="red"))


def main():
    """The main entry point for the Tempspace CLI tool.

    Handles argument parsing, interactive mode, file validation,
    and orchestrates the chunked file upload process for one or more files.
    """
    console = Console()

    # --- Handle Download Command ---
    if len(sys.argv) > 1 and sys.argv[1] == 'download':
        parser = argparse.ArgumentParser(description="Download a file from Tempspace.")
        parser.add_argument("url", help="The URL of the file to download.")
        parser.add_argument("-p", "--password", help="The password for the file.")
        
        # We process only the download arguments
        if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
             parser.print_help()
             sys.exit(0)
             
        args = parser.parse_args(sys.argv[2:])
        download_file(console, args.url, args.password)
        return

    # --- Header ---
    console.print(Panel("[bold cyan]Tempspace File Uploader[/bold cyan]", expand=False, border_style="blue"))

    parser = argparse.ArgumentParser(
        description="Upload one or more files to Tempspace.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("filepaths", nargs='*', default=[], help="The path(s) to the file(s) you want to upload.")
    parser.add_argument("-t", "--time", type=str, default='24', help="Set the file's expiration time for all files. Examples: '24h', '7d', '360' (hours).\nDefault: '24' (24 hours).")
    parser.add_argument("-p", "--password", type=str, help="Protect all files with a password.")
    parser.add_argument("--one-time", action="store_true", help="All files will be deleted after the first download.")
    parser.add_argument("--url", type=str, default=os.environ.get("TEMPSPACE_URL", DEFAULT_SERVER_URL), help=f"The URL of the Tempspace server.\nCan also be set with the TEMPSPACE_URL environment variable.\nDefault: {DEFAULT_SERVER_URL}")
    parser.add_argument("--qr", action="store_true", help="Display a QR code of the download link for each file.")
    parser.add_argument("--it", action="store_true", help="Enable interactive mode for a single file upload.")

    args = parser.parse_args()

    filepaths = args.filepaths

    # --- Interactive Mode ---
    if args.it:
        # Interactive mode only supports a single file, so we overwrite the filepaths list
        filepath = Prompt.ask("Enter the path to the file you want to upload")
        filepaths = [filepath]
        args.time = Prompt.ask("Set the file's expiration time (e.g., '24h', '7d')", default='24')
        args.password = Prompt.ask("Protect the file with a password?", default=None, password=True)
        args.one_time = Confirm.ask("Delete the file after the first download?", default=False)
        args.qr = Confirm.ask("Display a QR code of the download link?", default=False)

    # --- Validate Inputs ---
    if not filepaths:
        console.print(Panel("[bold red]Error:[/] No file path(s) provided.", title="[bold red]Error[/bold red]", border_style="red"))
        parser.print_help()
        sys.exit(1)

    hours = parse_time(args.time)
    if hours is None:
        console.print(Panel(f"[bold red]Error:[/] Invalid time format '{args.time}'. Use formats like '24h', '7d', or '360'.", title="[bold red]Error[/bold red]", border_style="red"))
        sys.exit(1)

    # --- Process each file ---
    # --- Process each file ---
    for i, filepath in enumerate(filepaths):
        actual_path = filepath
        is_temp = False
        
        if os.path.isdir(filepath):
            console.print(f"[bold yellow]Zipping directory '{os.path.basename(filepath)}'...[/]")
            actual_path = zip_directory(filepath)
            is_temp = True

        if len(filepaths) > 1:
            console.print(f"\n[bold yellow]Uploading file {i+1} of {len(filepaths)}: {os.path.basename(actual_path)}[/bold yellow]\n")
        
        upload_file(console, actual_path, hours, args.password, args.one_time, args.qr, args.url)
        
        if is_temp:
            os.remove(actual_path)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
