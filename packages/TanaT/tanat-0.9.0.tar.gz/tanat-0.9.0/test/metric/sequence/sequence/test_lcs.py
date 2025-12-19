#!/usr/bin/env python3
"""Test LCSSequenceMetric call method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.lcs.metric import (
    LCSSequenceMetric,
    LCSSequenceMetricSettings,
)


class TestLCSCall:
    """
    Test LCSSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test LCS with default settings (returns LCS length).
        """
        pool = sequence_pools[pool_type]
        metric = LCSSequenceMetric()

        seq_a = pool[2]
        seq_b = pool[3]

        value = metric(seq_a, seq_b)

        assert isinstance(value, float)
        assert value >= 0
        metric_snapshot.assert_match(value)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_entity_metric_equivalence(self, sequence_pools, pool_type):
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

        seq_a = pool[2]
        seq_b = pool[3]

        assert metric_obj(seq_a, seq_b) == metric_str(seq_a, seq_b)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_as_distance(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test LCS with as_distance=True (returns distance instead of length).
        """
        pool = sequence_pools[pool_type]
        metric = LCSSequenceMetric(settings=LCSSequenceMetricSettings(as_distance=True))

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    def test_call_identical_sequences(self, sequence_pools):
        """
        Test LCS on identical sequences: LCS length equals sequence length.
        """
        pool = sequence_pools["event"]
        metric = LCSSequenceMetric()

        seq_a = pool[1]
        lcs_value = metric(seq_a, seq_a)

        # LCS of identical sequences = sequence length
        assert lcs_value == len(seq_a)
