"""Tests for utils.service_types."""

import pandas as pd

from utils.service_types import requests_per_type


def test_requests_per_type_sorted() -> None:
    """Types are counted and sorted largest first."""
    requests = pd.DataFrame({"type_of_service_request": ["b", "a", "b"]})
    result = requests_per_type(requests)
    assert result["type_of_service_request"].tolist() == ["b", "a"]
    assert result["n_requests"].tolist() == [2, 1]
