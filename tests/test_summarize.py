"""Tests for utils.summarize."""

import pandas as pd

from utils.summarize import requests_per_area


def test_requests_per_area_counts_and_sorts() -> None:
    """Areas are counted and sorted largest first."""
    requests = pd.DataFrame({"community_area": [3, 1, 3, 3, 1, 2]})
    result = requests_per_area(requests)
    assert result["community_area"].tolist() == [3, 1, 2]
    assert result["n_requests"].tolist() == [3, 2, 1]
