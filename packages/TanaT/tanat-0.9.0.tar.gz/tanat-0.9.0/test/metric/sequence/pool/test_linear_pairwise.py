#!/usr/bin/env python3
"""Test LinearPairwiseSequenceMetric compute_matrix method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.linear_pairwise.metric import (
    LinearPairwiseSequenceMetric,
    LinearPairwiseSequenceMetricSettings,
)


class TestLinearPairwiseComputeMatrix:
    """
    Test LinearPairwiseSequenceMetric compute_matrix method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test compute_matrix with default settings.
        """
        pool = sequence_pools[pool_type]
        metric = LinearPairwiseSequenceMetric()

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_entity_metric_equivalence(self, sequence_pools, pool_type):
        """
        Test that entity_metric as object or string gives the same result.
        """
        pool = sequence_pools[pool_type]

        metric_obj = LinearPairwiseSequenceMetric(
            settings=LinearPairwiseSequenceMetricSettings(
                entity_metric=HammingEntityMetric()
            )
        )
        metric_str = LinearPairwiseSequenceMetric(
            settings=LinearPairwiseSequenceMetricSettings(entity_metric="hamming")
        )

        df_obj = metric_obj.compute_matrix(pool).to_dataframe()
        df_str = metric_str.compute_matrix(pool).to_dataframe()

        assert df_obj.equals(df_str)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_with_padding_penalty(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test compute_matrix with padding_penalty.
        """
        pool = sequence_pools[pool_type]
        metric = LinearPairwiseSequenceMetric(
            settings=LinearPairwiseSequenceMetricSettings(padding_penalty=1.0)
        )

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)
