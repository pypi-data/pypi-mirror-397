#!/usr/bin/env python3
"""Test LCPSequenceMetric call method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.lcp.metric import (
    LCPSequenceMetric,
    LCPSequenceMetricSettings,
)


class TestLCPCall:
    """
    Test LCPSequenceMetric call method.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test LCP with default settings (returns LCP length).
        """
        pool = sequence_pools[pool_type]
        metric = LCPSequenceMetric()

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

        metric_obj = LCPSequenceMetric(
            settings=LCPSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        metric_str = LCPSequenceMetric(
            settings=LCPSequenceMetricSettings(entity_metric="hamming")
        )

        seq_a = pool[2]
        seq_b = pool[3]

        assert metric_obj(seq_a, seq_b) == metric_str(seq_a, seq_b)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_as_distance(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test LCP with as_distance=True (returns distance instead of length).
        """
        pool = sequence_pools[pool_type]
        metric = LCPSequenceMetric(settings=LCPSequenceMetricSettings(as_distance=True))

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        assert distance >= 0
        metric_snapshot.assert_match(distance)

    def test_call_identical_sequences(self, sequence_pools):
        """
        Test LCP on identical sequences: LCP length equals sequence length.
        """
        pool = sequence_pools["event"]
        metric = LCPSequenceMetric()

        seq_a = pool[1]
        lcp_value = metric(seq_a, seq_a)

        # LCP of identical sequences = sequence length
        assert lcp_value == len(seq_a)
