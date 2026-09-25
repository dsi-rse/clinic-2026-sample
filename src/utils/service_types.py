"""Summaries of 311 requests by service type."""

import pandas as pd


def requests_per_type(requests: pd.DataFrame) -> pd.DataFrame:
    """Count service requests of each type, largest first.

    Args:
        requests: 311 requests with a ``type_of_service_request`` column.

    Returns:
        Columns ``type_of_service_request`` and ``n_requests``.
    """
    counts = (
        requests.groupby("type_of_service_request")
        .size()
        .reset_index(name="n_requests")
    )
    return counts.sort_values("n_requests", ascending=False, ignore_index=True)
