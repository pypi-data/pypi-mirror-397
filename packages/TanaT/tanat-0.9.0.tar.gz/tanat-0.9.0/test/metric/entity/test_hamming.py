#!/usr/bin/env python3
"""Test HammingEntityMetric call method."""

import pytest

from tanat.metric.entity import HammingEntityMetric, HammingEntityMetricSettings


@pytest.fixture
def entity_pairs(sequence_pools):
    """Get a dict of entity pairs (same sequence) for each pool type."""
    pairs = {}
    for pool_type in ["event", "state", "interval"]:
        pool = sequence_pools[pool_type]
        seq = pool[1]
        pairs[pool_type] = (seq[0], seq[1])
    return pairs


class TestHammingEntityMetric:
    """
    Test HammingEntityMetric call method on entities.
    """

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_same_entity(self, entity_pairs, pool_type):
        """
        Test Hamming distance between an entity and itself (should be 0).
        """
        entity_a, _ = entity_pairs[pool_type]
        metric = HammingEntityMetric()

        distance = metric(entity_a, entity_a)

        assert isinstance(distance, float)
        assert distance == 0.0

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_different_entities_same_sequence(
        self, entity_pairs, pool_type, metric_snapshot
    ):
        """
        Test Hamming distance between two different entities from same sequence.
        """
        entity_a, entity_b = entity_pairs[pool_type]
        metric = HammingEntityMetric()

        distance = metric(entity_a, entity_b)
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_symmetry(self, entity_pairs, pool_type):
        """
        Test that Hamming distance is symmetric: d(a,b) == d(b,a).
        """
        entity_a, entity_b = entity_pairs[pool_type]
        metric = HammingEntityMetric()

        distance_ab = metric(entity_a, entity_b)
        distance_ba = metric(entity_b, entity_a)

        assert distance_ab == distance_ba

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_explicit_features(
        self, entity_pairs, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test Hamming with explicit entity_features.
        """
        entity_a, entity_b = entity_pairs[pool_type]
        first_feature = sequence_pools[pool_type].settings.entity_features[0]

        metric = HammingEntityMetric(
            settings=HammingEntityMetricSettings(entity_features=[first_feature])
        )

        distance = metric(entity_a, entity_b)
        metric_snapshot.assert_match(distance)

    # -------------------------------------------------------------------------
    # With cost dictionary
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_cost_dict(
        self, entity_pairs, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test Hamming with a custom cost dictionary.
        """
        entity_a, entity_b = entity_pairs[pool_type]
        first_feature = sequence_pools[pool_type].settings.entity_features[0]

        val_a = entity_a.get_value([first_feature])
        val_b = entity_b.get_value([first_feature])

        # Custom cost: distance is 0.5 between these values
        cost = {(val_a, val_b): 0.5, (val_b, val_a): 0.5}

        metric = HammingEntityMetric(
            settings=HammingEntityMetricSettings(
                entity_features=[first_feature], cost=cost
            )
        )

        distance = metric(entity_a, entity_b)
        metric_snapshot.assert_match(distance)

    @pytest.mark.parametrize("pool_type", ["event", "state", "interval"])
    def test_call_with_default_value(
        self, entity_pairs, sequence_pools, pool_type, metric_snapshot
    ):
        """
        Test Hamming with cost dict and custom default_value for missing pairs.
        """
        entity_a, entity_b = entity_pairs[pool_type]
        first_feature = sequence_pools[pool_type].settings.entity_features[0]

        # Empty cost dict, so default_value will be used
        metric = HammingEntityMetric(
            settings=HammingEntityMetricSettings(
                entity_features=[first_feature], cost={}, default_value=0.75
            )
        )

        distance = metric(entity_a, entity_b)
        metric_snapshot.assert_match(distance)

    def test_call_raises_on_single_numerical_feature(self, entity_pairs):
        """
        Test that Hamming raises ValueError when used with a single numerical feature.

        dosage is a numerical feature in interval pool.
        """
        entity_a, entity_b = entity_pairs["interval"]

        metric = HammingEntityMetric(
            settings=HammingEntityMetricSettings(entity_features=["dosage"])
        )

        with pytest.raises(ValueError):
            metric(entity_a, entity_b)
