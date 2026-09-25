"""Check that DATA_DIR points at the shared Box folder and that Box is syncing.

Usage:
    uv run python scripts/check_data.py
"""

import argparse
import getpass
import sys
from datetime import datetime

import pandas as pd

from utils.settings import DATA_DIR

HINT = """
DATA_DIR should point at the Box folder dsi-core/clinic/2026-sample. Check .env:
  macOS:     DATA_DIR=~/Library/CloudStorage/Box-Box/dsi-core/clinic/2026-sample
  WSL:       DATA_DIR=/mnt/Box/dsi-core/clinic/2026-sample
If the folder is missing, make sure Box Drive is running and the folder is shared
with you. On WSL, see https://clinic.ds.uchicago.edu/tutorials/box-wsl.html
"""


def main() -> None:
    """Read the sample data from Box and write a sync-test file back."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--name", default=getpass.getuser(), help="name for the sync-test file"
    )
    args = parser.parse_args()

    print(f"DATA_DIR = {DATA_DIR}")
    raw_dir = DATA_DIR / "raw"
    if not raw_dir.is_dir():
        sys.exit(f"Could not find {raw_dir}.\n{HINT}")

    print("raw/:", ", ".join(sorted(p.name for p in raw_dir.iterdir())))
    requests = pd.read_parquet(raw_dir / "reqs_311.parquet")
    print(f"reqs_311.parquet: {len(requests):,} rows")
    print(requests.head())

    sync_file = DATA_DIR / "output" / f"{args.name}-sync-test.txt"
    sync_file.parent.mkdir(exist_ok=True)
    sync_file.write_text(f"Hello from {args.name} at {datetime.now().isoformat()}\n")
    print(f"\nWrote {sync_file}")
    print("Box is connected. Check that the file appears in the Box web app.")


if __name__ == "__main__":
    main()
