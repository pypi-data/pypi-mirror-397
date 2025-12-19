#!/usr/bin/env python3
"""Test TrajectoryMetric."""

import pytest

from tanat.metric.trajectory.type.aggregation import (
    AggregationTrajectoryMetric,
    AggregationTrajectoryMetricSettings,
)
from tanat.metric.sequence.base.metric import SequenceMetric


class TestAggregationTrajectoryMetric:
    """
    Test AggregationTrajectoryMetric on a trajectory pool.
    """

    @pytest.mark.parametrize(
        "sequence_metric", ["linearpairwise", "softdtw", "lcs", "lcp", "edit", "dtw"]
    )
    def test_compute_matrix(self, trajectory_pool, sequence_metric, metric_snapshot):
        """
        Ensure compute_matrix gives the same result whether sequence metric
        is passed as object or string.
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

        # Compute distance matrices
        dm_obj = metric_obj.compute_matrix(trajectory_pool)
        dm_str = metric_str.compute_matrix(trajectory_pool)

        # Convert to DataFrames for comparison
        df_obj = dm_obj.to_dataframe()
        df_str = dm_str.to_dataframe()

        # Verification of equivalence
        assert df_obj.equals(df_str)
        # Verification via snapshot
        metric_snapshot.assert_match(df_obj)
