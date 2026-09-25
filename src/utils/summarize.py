"""Summaries of the Chicago 311 service request data."""

from pathlib import Path

import pandas as pd

from utils.settings import DATA_DIR

RAW_DIR = DATA_DIR / "raw"


def load_requests(path: Path = RAW_DIR / "reqs_311.parquet") -> pd.DataFrame:
    """Load the 311 service requests from Box.

    Args:
        path: Location of the requests parquet file.

    Returns:
        One row per service request.
    """
    return pd.read_parquet(path)


def requests_per_area(requests: pd.DataFrame) -> pd.DataFrame:
    """Count service requests in each community area.

    Args:
        requests: 311 requests with a ``community_area`` column.

    Returns:
        Columns ``community_area`` and ``n_requests``, largest count first.

    Example:
        >>> df = pd.DataFrame({"community_area": [1, 1, 2]})
        >>> requests_per_area(df).to_dict("records")
        [{'community_area': 1, 'n_requests': 2}, {'community_area': 2, 'n_requests': 1}]
    """
    counts = requests.groupby("community_area").size().reset_index(name="n_requests")
    return counts.sort_values("n_requests", ascending=False, ignore_index=True)
