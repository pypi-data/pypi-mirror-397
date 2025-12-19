#!/usr/bin/env python3
"""
Download the latest axe-core library for bundling.

This script downloads axe-core from CDN and saves it to the assets directory
for local injection into pages during accessibility testing.
"""

import urllib.request
from pathlib import Path


# axe-core CDN URL (latest stable version)
AXE_VERSION = "4.10.2"
AXE_CDN_URL = f"https://cdnjs.cloudflare.com/ajax/libs/axe-core/{AXE_VERSION}/axe.min.js"

# Output path relative to this script
SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = SCRIPT_DIR.parent / "src" / "a11y_mcp" / "assets" / "axe.min.js"


def download_axe() -> None:
    """Download axe-core from CDN."""
    print(f"Downloading axe-core v{AXE_VERSION} from {AXE_CDN_URL}...")

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Download the file
    urllib.request.urlretrieve(AXE_CDN_URL, OUTPUT_PATH)

    # Verify download
    file_size = OUTPUT_PATH.stat().st_size
    print(f"Saved to {OUTPUT_PATH}")
    print(f"File size: {file_size / 1024:.1f} KB")

    if file_size < 100_000:  # axe.min.js should be > 100KB
        print("WARNING: File seems too small, download may have failed")
    else:
        print("Download complete!")


if __name__ == "__main__":
    download_axe()
