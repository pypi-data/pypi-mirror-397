#!/usr/bin/env python3
"""
Base class for registable Trajectory metrics.
"""

from abc import abstractmethod
import logging

from pypassist.mixin.cachable import Cachable
from pypassist.runner.workenv.mixin.processor import ProcessorMixin

from .exception import UnregisteredTrajectoryMetricTypeError
from ...base import Metric
from ...matrix import DistanceMatrix
from ....trajectory.pool import TrajectoryPool
from ....trajectory.trajectory import Trajectory

LOGGER = logging.getLogger(__name__)


class TrajectoryMetric(Metric, ProcessorMixin):
    """
    Base class for trajectory metrics that compares pairs of trajectories
    within a trajectory pool.
    """

    _REGISTER = {}

    def __init__(self, settings, *, workenv=None):
        """
        Args:
            settings:
                The metric settings.

            workenv:
                Optional workenv instance.
        """
        Metric.__init__(self, settings, workenv=workenv)
        ProcessorMixin.__init__(self)

    def __call__(self, traj_a, traj_b, **kwargs):
        """
        Calculate the metric for a specific pair of trajectories.

        Validates inputs, then delegates to _compute_single_distance.

        Args:
            traj_a (Trajectory):
                First trajectory.
            traj_b (Trajectory):
                Second trajectory.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the trajectory pair.

        Example:
            >>> distance = metric(traj_a, traj_b)
        """
        self._validate_trajectories(traj_a=traj_a, traj_b=traj_b)

        with self.with_tmp_settings(**kwargs):
            return self._compute_single_distance(traj_a, traj_b)

    @abstractmethod
    def _compute_single_distance(self, traj_a, traj_b):
        """
        Compute distance between two trajectories.

        Subclasses must implement this method with their specific
        computation logic. Settings overrides are already applied
        via with_tmp_settings in __call__.

        Args:
            traj_a (Trajectory): First trajectory.
            traj_b (Trajectory): Second trajectory.

        Returns:
            float: The metric value for the trajectory pair.
        """

    def compute_matrix(self, trajectory_pool, **kwargs):
        """
        Compute the pairwise distance matrix for a pool of trajectories.

        Uses two-level caching:
        - Instance cache (@Cachable): avoids recomputation within same session
        - Disk cache (memmap): persists between sessions if store_path is set

        Args:
            trajectory_pool: Pool of trajectories to compare.
            **kwargs: Optional settings overrides.

        Returns:
            DistanceMatrix containing pairwise distances.

        Example:
            >>> dm = metric.compute_matrix(trajectory_pool)
        """
        self._validate_trajectory_pool(trajectory_pool)
        self._display_header()

        with self.with_tmp_settings(**kwargs):
            dm = self._cached_compute_matrix(trajectory_pool)

        self._display_footer(dm.data.shape)
        return dm

    def _cached_compute_matrix(self, trajectory_pool):
        """
        Wrapper that detects instance cache hits.

        Pattern: We set a flag before calling the cached method.
        If the cached method actually runs, it clears the flag.
        If the flag remains True, we got a cache hit.

        Returns:
            DistanceMatrix: The computed or cached distance matrix.
        """
        # pylint: disable=attribute-defined-outside-init
        self._instance_cache_hit = True
        dm = self._get_or_compute_distance_matrix(
            trajectory_pool, self._get_settings_hash()
        )
        if self._instance_cache_hit:
            self._display_blank_line()
            self._display_message("Using cached matrix (instance cache hit)")
        return dm

    @Cachable.caching_method()
    def _get_or_compute_distance_matrix(self, trajectory_pool, settings_hash=None):
        """
        Load from disk cache or compute the distance matrix.

        Decorated with @Cachable.caching_method() for instance-level caching.

        Args:
            trajectory_pool: Pool of trajectories to compare.
            settings_hash: Optional hash of current settings for cache disk invalidation.

        Returns:
            DistanceMatrix containing pairwise distances.
        """
        # If we reach here, method actually executed (not from instance cache)
        # pylint: disable=attribute-defined-outside-init
        self._instance_cache_hit = False

        n_trajectories = len(trajectory_pool)
        ids = trajectory_pool.unique_ids

        dm = DistanceMatrix.from_storage_options(
            storage_options=self.settings.distance_matrix,
            n=n_trajectories,
            ids=ids,
            settings_hash=settings_hash,
        )

        if dm.is_complete:
            self._display_blank_line()
            self._display_message("Using cached matrix (disk cache hit)")
            return dm

        self._compute_distances(dm, trajectory_pool)
        return dm

    def _compute_distances(self, dm, trajectory_pool):
        """
        Default naive implementation: loop over trajectory pairs in chunks.

        Subclasses can override this method with optimized implementations.

        Args:
            dm: DistanceMatrix to fill.
            trajectory_pool: Pool of trajectories to compare.
        """
        trajectories = list(trajectory_pool)
        n = len(trajectories)
        batch_size = 100
        diagonal = dm.get_diagonal_snapshot()

        with self._progress_bar(trajectory_pool) as pbar:
            for start in range(0, n, batch_size):
                end = min(start + batch_size, n)
                pairs_count = self._count_chunk_pairs(start, end, n)

                # Skip if chunk already computed (resume support)
                if dm.is_chunk_computed(diagonal, start):
                    pbar.update(pairs_count)
                    continue

                # Compute all pairs for this chunk
                for i in range(start, end):
                    for j in range(i, n):
                        dist = self._compute_single_distance(
                            trajectories[i], trajectories[j]
                        )
                        dm.data[i, j] = dist
                        dm.data[j, i] = dist
                        pbar.update(1)

                # Mark chunk as done
                dm.mark_chunk_done(diagonal, start, end)
                dm.flush()

    def _progress_bar(self, trajectory_pool):
        """Create a progress bar for trajectory pool computation.

        Args:
            trajectory_pool (TrajectoryPool): Pool of trajectories to process.

        Returns:
            tqdm: Configured progress bar instance.
        """
        n_trajectories = len(trajectory_pool)
        total_pairs = (n_trajectories * (n_trajectories - 1)) // 2
        return self._create_progress_bar(total_pairs)

    def _validate_trajectory_pool(self, trajectory_pool):
        """
        Validate trajectory pool
        """
        if not isinstance(trajectory_pool, TrajectoryPool):
            raise ValueError(
                f"Invalid trajectory pool. Expected TrajectoryPool, got {type(trajectory_pool)}."
            )

    def _validate_trajectories(self, **trajectories):
        """
        Validate multiple trajectories, ensuring they are of the correct type.

        Args:
            trajectories:
                Dictionary of trajectories to validate.

        Raises:
            ValueError: If any trajectory is invalid.
        """
        for key, trajectory in trajectories.items():
            if not self._is_valid_trajectory(trajectory):
                raise ValueError(
                    f"Invalid trajectory '{key}'. Expected Trajectory, got {type(trajectory)}."
                )

    def _is_valid_trajectory(self, trajectory):
        """
        Check if a given trajectory is valid.

        Args:
            trajectory:
                The trajectory to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(trajectory, Trajectory)

    def _compute_intersection_ids(self, trajectory_pool):
        """
        Compute the intersection of IDs across all sequence pools.

        Args:
            trajectory_pool: TrajectoryPool to analyze.

        Returns:
            set: IDs present in ALL sequence pools.
        """
        # pylint: disable=protected-access
        return TrajectoryPool._derive_id_values(
            trajectory_pool._sequence_pools,
            intersection=True,  # Force intersection mode
        )

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered trajectory metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredTrajectoryMetricTypeError(
            f"Unknown trajectory metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
