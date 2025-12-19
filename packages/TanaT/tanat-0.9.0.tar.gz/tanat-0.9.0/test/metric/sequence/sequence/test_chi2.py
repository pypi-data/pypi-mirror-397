#!/usr/bin/env python3
"""Test Chi2SequenceMetric call method."""

import pytest

from tanat.metric.sequence.type.chi2.metric import (
    Chi2SequenceMetric,
    Chi2SequenceMetricSettings,
)


class TestChi2Call:
    """
    Test Chi2SequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test Chi2 with default settings (uses all entity_features from sequence).
        """
        pool = sequence_pools[pool_type]
        metric = Chi2SequenceMetric()

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_explicit_features(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test Chi2 with explicit entity_features.
        """
        pool = sequence_pools[pool_type]
        first_feature = pool.settings.entity_features[0]

        metric = Chi2SequenceMetric(
            settings=Chi2SequenceMetricSettings(entity_features=[first_feature])
        )

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_multiple_features(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test Chi2 with multiple entity_features (composite categories).
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

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    def test_call_identical_sequences(self, sequence_pools):
        """
        Test that Chi2 distance between identical sequences is zero.
        """
        pool = sequence_pools["event"]
        metric = Chi2SequenceMetric()

        seq_a = pool[1]

        assert metric(seq_a, seq_a) == 0.0
