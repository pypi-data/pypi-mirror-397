import zipfile
from pathlib import Path

import requests
from tqdm.auto import tqdm


def download_from_url(
    url: str,
    root: str | Path | None = None,
    filename: str | None = None,
    timeout: float | None = 100.0,
) -> Path:
    """
    Download a file from a URL and save it locally.

    Args:
        url (str): Direct URL of the file to download.
        root (str, Path or None): Optional directory in which to save the file or
        current working directory if None. Defaults to None.
        filename (str or None): Optional name for file.
        If None, the name is inferred from the URL. Defaults to None.
        timeout (float or None): Optional timeout settings. Defaults to 100.0

    Returns:
        Path: The path to the downloaded file.
    """
    url_filename = Path(url).name
    url_suffix = Path(url).suffix

    if filename:
        if url_suffix and not Path(filename).suffix:
            filename = filename + url_suffix.lower()
    else:
        filename = url_filename

    if root is not None:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        path = root / filename
    else:
        path = Path(filename)

    if path.exists():
        return path

    else:
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            total_size = float(response.headers.get("content-length", 0))
            chunk_size = 1 * 1024 * 1024

            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=path.name,
            ) as pbar:

                with open(path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

        except requests.RequestException as req_err:
            print(f"Request Error Occured: {req_err}")
            if path.exists():
                path.unlink()
            raise

        except Exception as err:
            print(f"Unexpected error occurred: {err}")
            if path.exists():
                path.unlink()
            raise

        return path


def extract_zip(
    zip_path: str | Path,
    root: str | Path | None = None,
) -> Path:
    """
    Extract a ZIP file to a target directory.

    Args:
        zip_path (str or Path): Path to the ZIP file.
        root (str, Path or None): Optional extraction directory or directory named
        after ZIP file if None. Defaults to None.

    Returns:
        Path: Directory where the files are extracted.
    """
    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if root is None:
        extract_dir = zip_path.with_suffix("")
    else:
        extract_dir = Path(root)

    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        members = zip_ref.namelist()

        with tqdm(total=len(members, desc=f"Extracting {zip_path.name}")) as pbar:
            for member in members:
                target_path = extract_dir / member

                if target_path.exists():
                    pbar.update(1)
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)

                zip_ref.extract(member, extract_dir)
                pbar.update(1)

    return extract_dir


def download_and_extract_zip(
    url: str,
    download_root: str | Path | None,
    filename: str | None = None,
    remove_zip: bool = False,
):
    """
    Download a ZIP file from URL and extracts its contents.

    Args:
        url (str): URL of the ZIP file to download.
        download_root (str, Path or None): Directory for download and extraction.
        filename (str or None): Optional filename for the downloaded ZIP file.
        remove_zip (bool): Whether to remove zip file after extracting its contents.

    Returns:
        Path: Directory where the files were extracted.
    """
    zip_path = download_from_url(url, root=download_root, filename=filename)
    extract_dir = extract_zip(zip_path, root=download_root)

    if remove_zip:
        zip_path.unlink()

    return extract_dir
