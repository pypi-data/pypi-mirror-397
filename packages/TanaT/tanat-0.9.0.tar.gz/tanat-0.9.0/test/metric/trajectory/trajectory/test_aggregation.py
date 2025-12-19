#!/usr/bin/env python3
"""Test TrajectoryMetric."""

import pytest

from tanat.metric.trajectory.type.aggregation import (
    AggregationTrajectoryMetric,
    AggregationTrajectoryMetricSettings,
)
from tanat.metric.sequence.base.metric import SequenceMetric


class TestAggregationTrajectoryCall:
    """
    Test AggregationTrajectoryMetric call.
    """

    @pytest.mark.parametrize(
        "sequence_metric", ["linearpairwise", "softdtw", "lcs", "lcp", "edit", "dtw"]
    )
    def test_call(self, trajectory_pool, sequence_metric, metric_snapshot):
        """
        Ensure call gives the same result whether sequence metric is passed as object or string.
        """

        # Initialisation with SequenceMetric object
        seqmetric_obj = SequenceMetric.get_metric(mtype=sequence_metric)
        metric_obj = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                sequence_metrics={
                    "event": seqmetric_obj,
                    "state": seqmetric_obj,
                    "interval": seqmetric_obj,
                }
            )
        )
        # Initialisation with string
        metric_str = AggregationTrajectoryMetric(
            settings=AggregationTrajectoryMetricSettings(
                sequence_metrics={
                    "event": sequence_metric,
                    "state": sequence_metric,
                    "interval": sequence_metric,
                }
            )
        )

        ## -- trajectories to compare
        traj_a = trajectory_pool[2]
        traj_b = trajectory_pool[3]

        # Call with SequenceMetric object
        value_obj = metric_obj(traj_a, traj_b)
        # Call with string
        value_str = metric_str(traj_a, traj_b)
        # Check consistency
        assert value_obj == value_str
        metric_snapshot.assert_match(value_obj)
