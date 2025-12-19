#!/usr/bin/env python3
"""
Fixtures specific to metric tests.
"""

import pytest

import pandas as pd


# Default precision for metric snapshot comparisons
METRIC_PRECISION = 4


class MetricSnapshot:
    """Wrapper around syrupy snapshot that rounds values before comparison."""

    def __init__(self, snapshot, precision=METRIC_PRECISION):
        self._snapshot = snapshot
        self._precision = precision

    def assert_match(self, value):
        """Assert that the rounded value matches the snapshot."""
        if isinstance(value, pd.DataFrame):
            # It's a DataFrame, round it and convert to CSV
            self._snapshot.assert_match(value.round(self._precision).to_csv())
        elif isinstance(value, float):
            # It's a float, round it
            self._snapshot.assert_match(round(value, self._precision))
        else:
            # Fallback for other types
            self._snapshot.assert_match(value)


@pytest.fixture
def metric_snapshot(snapshot):
    """
    Fixture for metric tests that automatically rounds values to 4 decimals.

    Usage:
        def test_my_metric(self, metric_snapshot):
            # For DataFrame results
            df = metric.compute_matrix(pool).to_dataframe()
            metric_snapshot.assert_match(df)

            # For scalar results
            distance = metric(seq_a, seq_b)
            metric_snapshot.assert_match(distance)
    """
    return MetricSnapshot(snapshot)
