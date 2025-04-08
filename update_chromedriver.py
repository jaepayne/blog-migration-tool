"""
update_chromedriver.py

Fetches and installs the latest stable version of ChromeDriver
appropriate for the system architecture and OS.
"""

import os
import stat
import zipfile
import shutil
import logging
import requests
import platform

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CHROMEDRIVER_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"


def get_latest_stable_version():
    """
    Returns the latest stable Chrome version string.
    """
    res = requests.get(CHROMEDRIVER_URL)
    res.raise_for_status()
    data = res.json()
    return data["channels"]["Stable"]["version"]


def get_download_url(version):
    """
    Determines the proper ChromeDriver download URL based on OS and architecture.
    """
    os_type = platform.system()
    arch = "linux64"  # default

    if os_type == "Darwin":
        arch = "mac-arm64" if platform.machine() == "arm64" else "mac-x64"
    elif os_type == "Windows":
        arch = "win32"

    res = requests.get(CHROMEDRIVER_URL)
    res.raise_for_status()
    downloads = res.json()["channels"]["Stable"]["downloads"]["chromedriver"]

    for entry in downloads:
        if arch in entry["url"]:
            return entry["url"]

    raise Exception("ChromeDriver download URL for your OS/arch not found.")


def update_chromedriver():
    """
    Downloads and unzips the latest ChromeDriver into the working directory.
    """
    version = get_latest_stable_version()
    url = get_download_url(version)
    zip_name = "chromedriver.zip"

    logging.info(f"⬇️ Downloading ChromeDriver v{version} from {url}")
    with requests.get(url, stream=True) as r:
        with open(zip_name, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall()

    os.remove(zip_name)
    logging.info("✅ ChromeDriver downloaded and extracted.")


def run_update_chromedriver():
    """
    Updates and sets executable permissions on the ChromeDriver binary.
    """
    update_chromedriver()
    driver_path = os.path.join(os.getcwd(), "chromedriver-mac-x64", "chromedriver")

    if os.path.exists(driver_path):
        os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IEXEC)
        logging.info(f"🔧 Set executable permissions: {driver_path}")
        return str(driver_path)
    else:
        logging.warning(f"⚠️ ChromeDriver not found at expected path: {driver_path}")
        return str(driver_path)


if __name__ == "__main__":
    run_update_chromedriver()
