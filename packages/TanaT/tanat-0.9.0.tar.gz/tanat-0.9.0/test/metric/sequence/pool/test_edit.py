#!/usr/bin/env python3
"""Test EditSequenceMetric compute_matrix method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.edit.metric import (
    EditSequenceMetric,
    EditSequenceMetricSettings,
)


class TestEditComputeMatrix:
    """
    Test EditSequenceMetric compute_matrix method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test compute_matrix with default settings.
        """
        pool = sequence_pools[pool_type]
        metric = EditSequenceMetric()

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_entity_metric_equivalence(self, sequence_pools, pool_type):
        """
        Test that entity_metric as object or string gives the same result.
        """
        pool = sequence_pools[pool_type]

        metric_obj = EditSequenceMetric(
            settings=EditSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        metric_str = EditSequenceMetric(
            settings=EditSequenceMetricSettings(entity_metric="hamming")
        )

        df_obj = metric_obj.compute_matrix(pool).to_dataframe()
        df_str = metric_str.compute_matrix(pool).to_dataframe()

        assert df_obj.equals(df_str)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_with_normalize(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test compute_matrix with normalize=True.
        """
        pool = sequence_pools[pool_type]
        metric = EditSequenceMetric(settings=EditSequenceMetricSettings(normalize=True))

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)
