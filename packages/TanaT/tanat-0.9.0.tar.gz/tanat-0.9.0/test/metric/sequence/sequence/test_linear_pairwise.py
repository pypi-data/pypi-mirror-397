#!/usr/bin/env python3
"""Test LinearPairwiseSequenceMetric call method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.linear_pairwise.metric import (
    LinearPairwiseSequenceMetric,
    LinearPairwiseSequenceMetricSettings,
)


class TestLinearPairwiseCall:
    """
    Test LinearPairwiseSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test LinearPairwise with default settings.
        """
        pool = sequence_pools[pool_type]
        metric = LinearPairwiseSequenceMetric()

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_entity_metric_equivalence(self, sequence_pools, pool_type):
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

        seq_a = pool[2]
        seq_b = pool[3]

        assert metric_obj(seq_a, seq_b) == metric_str(seq_a, seq_b)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_padding_penalty(
        self, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test LinearPairwise with padding_penalty.
        """
        pool = sequence_pools[pool_type]
        metric = LinearPairwiseSequenceMetric(
            settings=LinearPairwiseSequenceMetricSettings(padding_penalty=1.0)
        )

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    def test_call_identical_sequences(self, sequence_pools):
        """
        Test that LinearPairwise distance between identical sequences is zero.
        """
        pool = sequence_pools["event"]
        metric = LinearPairwiseSequenceMetric()

        seq_a = pool[1]

        assert metric(seq_a, seq_a) == 0.0
