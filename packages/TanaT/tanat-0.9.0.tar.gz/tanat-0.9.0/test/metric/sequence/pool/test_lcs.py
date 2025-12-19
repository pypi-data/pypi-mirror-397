#!/usr/bin/env python3
"""Test LCSSequenceMetric compute_matrix method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.lcs.metric import (
    LCSSequenceMetric,
    LCSSequenceMetricSettings,
)


class TestLCSComputeMatrix:
    """
    Test LCSSequenceMetric compute_matrix method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test compute_matrix with default settings (returns LCS length).
        """
        pool = sequence_pools[pool_type]
        metric = LCSSequenceMetric()

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_entity_metric_equivalence(self, sequence_pools, pool_type):
        """
        Test that entity_metric as object or string gives the same result.
        """
        pool = sequence_pools[pool_type]

        metric_obj = LCSSequenceMetric(
            settings=LCSSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        metric_str = LCSSequenceMetric(
            settings=LCSSequenceMetricSettings(entity_metric="hamming")
        )

        df_obj = metric_obj.compute_matrix(pool).to_dataframe()
        df_str = metric_str.compute_matrix(pool).to_dataframe()

        assert df_obj.equals(df_str)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_as_distance(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test compute_matrix with as_distance=True.
        """
        pool = sequence_pools[pool_type]
        metric = LCSSequenceMetric(settings=LCSSequenceMetricSettings(as_distance=True))

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)
