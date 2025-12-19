#!/usr/bin/env python3
"""Test Chi2SequenceMetric compute_matrix method."""

import pytest

from tanat.metric.sequence.type.chi2.metric import (
    Chi2SequenceMetric,
    Chi2SequenceMetricSettings,
)


class TestChi2ComputeMatrix:
    """
    Test Chi2SequenceMetric compute_matrix method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test compute_matrix with default settings (uses all entity_features).
        """
        pool = sequence_pools[pool_type]
        metric = Chi2SequenceMetric()

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_with_explicit_features(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test compute_matrix with explicit entity_features.
        """
        pool = sequence_pools[pool_type]
        first_feature = pool.settings.entity_features[0]

        metric = Chi2SequenceMetric(
            settings=Chi2SequenceMetricSettings(entity_features=[first_feature])
        )

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_compute_matrix_with_multiple_features(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test compute_matrix with multiple entity_features (composite categories).
        """
        pool = sequence_pools[pool_type]
        entity_features = pool.settings.entity_features

        if len(entity_features) >= 2:
            metric = Chi2SequenceMetric(
                settings=Chi2SequenceMetricSettings(entity_features=entity_features[:2])
            )
        else:
            metric = Chi2SequenceMetric(
                settings=Chi2SequenceMetricSettings(entity_features=entity_features)
            )

        dm = metric.compute_matrix(pool)
        df = dm.to_dataframe()

        metric_snapshot.assert_match(df)
