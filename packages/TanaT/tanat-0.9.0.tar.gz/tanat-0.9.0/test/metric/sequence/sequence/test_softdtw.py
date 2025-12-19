#!/usr/bin/env python3
"""Test SoftDTWSequenceMetric call method."""

import pytest

from tanat.metric.entity.type.hamming.metric import HammingEntityMetric
from tanat.metric.sequence.type.softdtw.metric import (
    SoftDTWSequenceMetric,
    SoftDTWSequenceMetricSettings,
)


class TestSoftDTWCall:
    """
    Test SoftDTWSequenceMetric call method.

    Note: SoftDTW can return negative values due to the soft-min approximation.
    This is expected behavior for this differentiable variant of DTW.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_default(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test SoftDTW with default settings.
        """
        pool = sequence_pools[pool_type]
        metric = SoftDTWSequenceMetric()

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_entity_metric_equivalence(self, sequence_pools, pool_type):
        """
        Test that entity_metric as object or string gives the same result.
        """
        pool = sequence_pools[pool_type]

        metric_obj = SoftDTWSequenceMetric(
            settings=SoftDTWSequenceMetricSettings(entity_metric=HammingEntityMetric())
        )
        metric_str = SoftDTWSequenceMetric(
            settings=SoftDTWSequenceMetricSettings(entity_metric="hamming")
        )

        seq_a = pool[2]
        seq_b = pool[3]

        assert metric_obj(seq_a, seq_b) == metric_str(seq_a, seq_b)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_gamma(self, sequence_pools, pool_type, metric_snapshot):
        """
        Test SoftDTW with custom gamma value.
        """
        pool = sequence_pools[pool_type]
        metric = SoftDTWSequenceMetric(
            settings=SoftDTWSequenceMetricSettings(gamma=0.1)
        )

        seq_a = pool[2]
        seq_b = pool[3]

        distance = metric(seq_a, seq_b)

        assert isinstance(distance, float)
        metric_snapshot.assert_match(distance)

    def test_call_identical_sequences(self, sequence_pools):
        """
        Test SoftDTW on identical sequences.
        Note: SoftDTW may not return exactly 0 for identical sequences
        due to the soft-min approximation.
        """
        pool = sequence_pools["event"]
        metric = SoftDTWSequenceMetric()

        seq_a = pool[1]
        distance = metric(seq_a, seq_a)

        # SoftDTW on identical sequences should be <= 0
        # (soft-min returns a value <= true min which is 0)
        assert distance <= 0.0
