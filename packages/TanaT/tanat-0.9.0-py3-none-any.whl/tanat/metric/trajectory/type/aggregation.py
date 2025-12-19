#!/usr/bin/env python3
"""
Aggregation trajectory metric.
"""

import logging
from typing import Union, Optional, Dict

from numba.typed.typedlist import List as NumbaList
from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators.viewer import viewer
from pypassist.mixin.settings import create_settings_snapshot
from pypassist.mixin.cachable import Cachable

from ..base.metric import TrajectoryMetric
from ...sequence.base.metric import SequenceMetric
from ...matrix import MatrixStorageOptions
from ....function.aggregation.base.function import AggregationFunction

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class AggregationTrajectoryMetricSettings:
    """
    Configuration for aggregating metrics from sequence pairs in trajectories.

    Attributes:
        default_metric (Union[str, SequenceMetric]):
            Default metric to use for sequences not in sequence_metrics.
            Can be a string identifier (e.g., "linearpairwise") or a SequenceMetric instance.
            Defaults to "linearpairwise".

        sequence_metrics (Optional[Dict[str, Union[str, SequenceMetric]]]):
            Mapping of sequence names to their corresponding metrics.
            Keys are sequence names, values are string identifiers or SequenceMetric instances.
            Example: {"states": "edit", "events": DTWSequenceMetric()}

        agg_fun (Union[str, AggregationFunction]):
            Aggregation function or string identifier for aggregation.
            Defaults to "mean".

        weights (Optional[Dict[str, float]]):
            Weights for each sequence when aggregating distances.
            Keys are sequence names, values are weights.
            If not specified, all sequences have weight 1.0.
            Example: {"states": 1.0, "actions": 0.5}

        distance_matrix (MatrixStorageOptions):
            Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.
    """

    default_metric: Union[str, SequenceMetric] = "linearpairwise"
    sequence_metrics: Optional[Dict[str, Union[str, SequenceMetric]]] = None
    agg_fun: Union[str, AggregationFunction] = "mean"
    weights: Optional[Dict[str, float]] = None
    distance_matrix: MatrixStorageOptions = Field(default_factory=MatrixStorageOptions)

    def __snapshot_sequence_metrics__(self):
        """
        Custom snapshot for the `sequence_metrics` field.

        Handles non-copyable (cacheable) objects by extracting their settings.

        Used to detect changes and trigger cache invalidation.
        """
        sequence_metrics = self.sequence_metrics
        if sequence_metrics is None:
            return None
        snapshot = {}
        for pool_name, metric in sequence_metrics.items():
            if hasattr(metric, "is_cachable"):  # Handle non-copyable objects
                settings = getattr(metric, "settings", None)
                settings_snapshot = create_settings_snapshot(settings)
                snapshot[pool_name] = settings_snapshot
                continue

            # should be a string identifier to resolve
            snapshot[pool_name] = metric
        return snapshot

    def __snapshot_default_metric__(self):
        """
        Custom snapshot for the `default_metric` field.

        Handles non-copyable (cacheable) objects by extracting their settings.

        Used to detect changes and trigger cache invalidation.
        """
        metric = self.default_metric
        if hasattr(metric, "is_cachable"):  # Handle non-copyable objects
            settings = getattr(metric, "settings", None)
            settings_snapshot = create_settings_snapshot(settings)
            return settings_snapshot

        # should be a string identifier to resolve
        return metric

    def __snapshot_agg_fun__(self):
        """
        Custom snapshot for the `agg_fun` field.

        Handles AggregationFunction objects by extracting their register name.
        Note: AggregationFunction have no settings.

        Used to detect changes and trigger cache invalidation.
        """
        agg_fun = self.agg_fun
        if isinstance(agg_fun, AggregationFunction):
            return agg_fun.get_registration_name()

        # should be a string identifier to resolve
        return agg_fun


class AggregationTrajectoryMetric(TrajectoryMetric, register_name="aggregation"):
    """
    Computes an aggregated metric value between trajectories.
    """

    SETTINGS_DATACLASS = AggregationTrajectoryMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = AggregationTrajectoryMetricSettings()
        super().__init__(settings=settings, workenv=workenv)

    @property
    def _agg_fun(self):
        """
        Retrieves the aggregation function.
        """
        agg_fun = self._settings.agg_fun
        return self._resolve_agg_fun(agg_fun)

    def _compute_single_distance(self, traj_a, traj_b):
        """
        Compute aggregated distance between two trajectories.

        NOTE: Computes on the intersection of sequences present in both trajectories.
        Raises an error if no common sequences exist.

        Args:
            traj_a (Trajectory): First trajectory.
            traj_b (Trajectory): Second trajectory.

        Returns:
            float: The aggregated distance value.

        Raises:
            ValueError: If trajectories have no common sequences.
        """
        seq_names_a = set(traj_a.sequences.keys())
        seq_names_b = set(traj_b.sequences.keys())
        common_seq_names = seq_names_a & seq_names_b

        if not common_seq_names:
            raise ValueError(
                f"Trajectories have no common sequences. "
                f"Got {seq_names_a} vs {seq_names_b}"
            )

        # Warn if sequences differ
        if seq_names_a != seq_names_b:
            missing_in_a = seq_names_b - seq_names_a
            missing_in_b = seq_names_a - seq_names_b
            LOGGER.warning(
                "Trajectories have different sequences. "
                "Computing on intersection: %s. "
                "Missing in traj_a: %s, missing in traj_b: %s",
                common_seq_names,
                missing_in_a or "none",
                missing_in_b or "none",
            )

        values = []
        for seq_name in common_seq_names:
            metric = self._get_metric_for_sequence(seq_name)
            distance = metric(traj_a.sequences[seq_name], traj_b.sequences[seq_name])
            values.append(distance)

        # pylint: disable=not-callable
        return self._agg_fun(values)

    def _get_or_compute_distance_matrix(self, trajectory_pool, settings_hash=None):
        """
        Override to enforce intersection mode before matrix creation.

        Aggregation metric requires all trajectories to have all sequences,
        so we force intersection mode before delegating to the base implementation.
        """
        effective_pool = self._get_effective_pool(trajectory_pool)
        return super()._get_or_compute_distance_matrix(
            effective_pool, settings_hash=settings_hash
        )

    def _compute_distances(self, dm, trajectory_pool):
        """
        Compute aggregated distances for trajectory pairs.

        Overrides the default naive loop implementation to compute
        distance matrices for each sequence pool independently,
        then aggregate them using weighted mean/sum.

        NOTE: trajectory_pool is already in intersection mode (enforced by
        _get_or_compute_distance_matrix).

        Args:
            dm: DistanceMatrix to fill.
            trajectory_pool: TrajectoryPool in intersection mode.
        """
        # Get metrics for all pools
        pool_names = list(trajectory_pool.sequence_pools.keys())
        metrics = self._get_metrics_for_sequences(pool_names)

        # Compute distance matrices for each pool
        pool_matrices = self._compute_pool_matrices(trajectory_pool, metrics)

        # Aggregate into final trajectory matrix
        self._aggregate_into_matrix(dm, pool_matrices, pool_names)

    @Cachable.caching_method()
    def _get_effective_pool(self, trajectory_pool):
        """
        Get the effective trajectory pool, enforcing intersection mode.

        If the pool is not in intersection mode, creates a copy and updates its settings.

        Args:
            trajectory_pool: Original TrajectoryPool.

        Returns:
            TrajectoryPool: Pool with intersection=True.
        """
        if trajectory_pool.settings.intersection:
            return trajectory_pool

        self._display_message(
            "Aggregation metric requires intersection mode. "
            "Enforcing intersection on trajectory pool copy.\n|"
        )

        # Create a copy and update settings to enforce intersection
        pool_copy = trajectory_pool.copy()
        pool_copy.update_settings(intersection=True)

        return pool_copy

    def _compute_pool_matrices(self, trajectory_pool, metrics):
        """
        Compute distance matrix for each sequence pool.

        Args:
            trajectory_pool: TrajectoryPool containing sequences.
            metrics: Dict mapping pool names to their SequenceMetric.

        Returns:
            Dict mapping pool names to their DistanceMatrix.
        """
        pool_matrices = {}
        n_pools = len(metrics)

        self._display_step(1, 2, "Computing sequence metrics")

        for idx, (pool_name, metric) in enumerate(metrics.items(), 1):
            seq_pool = trajectory_pool.sequence_pools.get(pool_name)
            if not seq_pool:
                LOGGER.warning("Missing sequence pool: %s", pool_name)
                continue

            self._display_step(
                idx,
                n_pools,
                f"{pool_name} → {metric.__class__.__name__}",
                is_main=False,
            )

            # Use SequenceMetric's _cached_compute_matrix directly
            # (bypasses header/footer since TrajectoryMetric manages display)
            # pylint: disable=protected-access
            seq_dm = metric._cached_compute_matrix(seq_pool)
            pool_matrices[pool_name] = seq_dm

        return pool_matrices

    def _aggregate_into_matrix(self, dm, pool_matrices, pool_names):
        """
        Aggregate multiple pool distance matrices into the trajectory distance matrix.

        Args:
            dm: DistanceMatrix to fill.
            pool_matrices: Dict of pool name -> DistanceMatrix.
            pool_names: List of pool names (for weight ordering).
        """
        weights = self._get_weights_array(pool_names)

        # Prepare matrices as Numba-compatible list
        matrices_list = self._prepare_matrices_for_numba(pool_matrices, pool_names)

        # Display and aggregate
        agg_fun_name = self._settings.agg_fun
        self._display_step(2, 2, f"Aggregating ({agg_fun_name})")

        n_trajectories = dm.data.shape[0]
        total_pairs = n_trajectories * (n_trajectories - 1) // 2
        with self._create_progress_bar(total_pairs) as pbar:
            dm.aggregate_from(
                matrices=matrices_list,
                weights=weights,
                kernel=self._agg_fun.matrix_kernel,
                pbar=pbar,
            )

    def _get_weights_array(self, pool_names):
        """Get weights list in same order as pool_names."""
        weights_dict = self._settings.weights or {}
        return [weights_dict.get(name, 1.0) for name in pool_names]

    def _prepare_matrices_for_numba(self, pool_matrices, pool_names):
        """Convert pool matrices to Numba-typed list."""
        matrices = NumbaList()
        for name in pool_names:
            if name in pool_matrices:
                matrices.append(pool_matrices[name].data)
        return matrices

    def _get_metrics_for_sequences(self, seq_names):
        """Get metrics for each sequence name."""
        return {name: self._get_metric_for_sequence(name) for name in seq_names}

    def _get_metric_for_sequence(self, seq_name):
        """
        Get the metric for a given sequence.

        Args:
            seq_name: Name of the sequence.

        Returns:
            SequenceMetric: The resolved metric instance.
        """
        sequence_metrics = self._settings.sequence_metrics or {}
        metric = sequence_metrics.get(seq_name, self._settings.default_metric)
        return self._resolve_sequence_metric(metric)

    def _resolve_sequence_metric(self, metric):
        """
        Resolve a metric (string or instance) to a SequenceMetric instance.

        Args:
            metric: String identifier or SequenceMetric instance.

        Returns:
            SequenceMetric: The resolved metric instance.
        """
        if isinstance(metric, SequenceMetric):
            return metric

        if isinstance(metric, str):
            return SequenceMetric.get_metric(metric)

        raise ValueError(
            f"Invalid metric: {metric}. "
            "Expected a SequenceMetric instance or a valid string identifier."
        )
