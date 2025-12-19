"""Testing `extract()`."""

import os
import subprocess
import glob
import zipfile
import requests
from ninja_zip_streamer import extract


URL = "https://nextcloud.inrae.fr/s/LSmCRfWDNz7fXTB/download"
# URL = "https://nextcloud.inrae.fr/s/ryNw4Gi8TGaassa/download"  # smaller file
BL_ZIP = "/tmp/archive.zip"
BL_UNZIPPED = "/tmp/bl_unzipped"


def download_and_extract_baseline():
    """Download and extract the baseline."""
    if os.path.isdir(BL_UNZIPPED):
        return
    with open(BL_ZIP, "wb") as file:
        file.write(requests.get(URL, timeout=10).content)
    with zipfile.ZipFile(BL_ZIP, "r") as zip_ref:
        zip_ref.extractall(BL_UNZIPPED)


def diff(out: str):
    """Compare the baseline with the extracted directory."""
    cmd = ["diff", out, BL_UNZIPPED]
    print(f"Command: {cmd}")
    proc = subprocess.run(cmd, check=True)
    assert proc.returncode == 0, "Wrong return code of diff command"


def test_remote_archive():
    """Test to grab/decompress a remote archive."""
    out = "/tmp/remote"
    extract(URL, out)
    download_and_extract_baseline()
    diff(out)


def test_local_archive():
    """Test to grab/decompress a local archive."""
    out = "/tmp/local"
    download_and_extract_baseline()
    extract(BL_ZIP, out)
    diff(out)


def test_extract_only_suffixes():
    """ "Test the extraction of subset of suffixes."""
    out = "/tmp/local_suffixes"
    extract(BL_ZIP, out, only_suffixes=".xml")
    for file in glob.glob(os.path.join(out, "**/*")):
        if os.path.isfile(file):
            assert file.endswith(".xml")
