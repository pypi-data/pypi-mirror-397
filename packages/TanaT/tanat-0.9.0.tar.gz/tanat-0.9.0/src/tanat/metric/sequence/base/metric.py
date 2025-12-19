#!/usr/bin/env python3
"""
Base class for sequence metrics.
"""

from abc import abstractmethod
import logging

from pypassist.utils.export import export_to_csv
from pypassist.mixin.cachable import Cachable
from pypassist.runner.workenv.mixin.processor import ProcessorMixin


from .exception import UnregisteredSequenceMetricTypeError
from ...base import Metric
from ...entity.base.metric import EntityMetric
from ...matrix import DistanceMatrix

LOGGER = logging.getLogger(__name__)


class SequenceMetric(Metric, ProcessorMixin):
    """
    Base class for sequence metrics.
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

    @property
    def entity_metric(self):
        """
        Get the entity metric to use.

        Returns:
            EntityMetric: The configured entity-level metric.
        """
        metric = getattr(self.settings, "entity_metric", None)
        if metric is None:
            LOGGER.warning(
                "%s: No entity metric configured in sequence metric settings. "
                "Settings must inherit from BaseSequenceMetricSettings with entity_metric field.",
                self.__class__.__name__,
            )
            return None
        metric = self._resolve_entity_metric(metric)
        return metric

    @property
    def _entity_features(self):
        """
        Get entity features from the configured entity metric.

        Returns:
            Entity features if entity metric is configured, None otherwise.
        """
        entity_metric = self.entity_metric
        return entity_metric.entity_features if entity_metric is not None else None

    def __call__(self, seq_a, seq_b, **kwargs):
        """
        Calculate the metric for a specific pair of sequences.

        Validates inputs, then delegates to _compute_single_distance.

        Args:
            seq_a (Sequence):
                First sequence.
            seq_b (Sequence):
                Second sequence.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the sequence pair.

        Example:
            >>> distance = metric(seq_a, seq_b)
        """
        self._validate_sequences(seq_a=seq_a, seq_b=seq_b)
        self._validate_feature_types(seq_a)

        with self.with_tmp_settings(**kwargs):
            return self._compute_single_distance(seq_a, seq_b)

    @abstractmethod
    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute distance between two sequences.

        Subclasses must implement this method with their specific
        computation logic. Settings overrides are already applied
        via with_tmp_settings in __call__.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The metric value for the sequence pair.
        """

    def compute_matrix(self, sequence_pool, **kwargs):
        """
        Compute the pairwise distance matrix for a pool of sequences.

        Uses two-level caching:
        - Instance cache (@Cachable): avoids recomputation within same session
        - Disk cache (memmap): persists between sessions if store_path is set

        Args:
            sequence_pool: Pool of sequences to compare.
            **kwargs: Optional settings overrides.

        Returns:
            DistanceMatrix containing pairwise distances.

        Example:
            >>> dm = metric.compute_matrix(sequence_pool)
        """
        self._validate_sequence_pool(sequence_pool)
        self._display_header()

        with self.with_tmp_settings(**kwargs):
            dm = self._cached_compute_matrix(sequence_pool)

        self._display_footer(dm.data.shape)
        return dm

    def _compute_distances(self, dm, sequence_pool):
        """
        Default naive implementation: loop over sequence pairs in chunks.

        Subclasses can override this method with optimized implementations
        (e.g., Numba JIT, vectorized operations, parallel processing).

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        sequences = list(sequence_pool)
        n = len(sequences)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        with self._progress_bar(sequence_pool) as pbar:
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
                        dist = self._compute_single_distance(sequences[i], sequences[j])
                        dm.data[i, j] = dist
                        dm.data[j, i] = dist
                        pbar.update(1)

                # Mark chunk as done
                dm.mark_chunk_done(diagonal, start, end)
                dm.flush()

    def _cached_compute_matrix(self, sequence_pool):
        """
        Wrapper that detects instance cache hits.

        Pattern: We set a flag before calling the cached method.
        If the cached method actually runs, it clears the flag.
        If the flag remains True, we got a cache hit.

        Returns:
            DistanceMatrix: The computed or cached distance matrix.
        """
        # Flag to detect instance cache hit
        # pylint: disable=attribute-defined-outside-init
        self._instance_cache_hit = True
        dm = self._get_or_compute_distance_matrix(
            sequence_pool, self._get_settings_hash()
        )
        if self._instance_cache_hit:
            self._display_blank_line()
            self._display_message("Using cached matrix (instance cache hit)")
        return dm

    @Cachable.caching_method()
    def _get_or_compute_distance_matrix(self, sequence_pool, settings_hash=None):
        """
        Load from disk cache or compute the distance matrix.

        Decorated with @Cachable.caching_method() for instance-level caching.

        Args:
            sequence_pool: Pool of sequences to compare.
            settings_hash: Optional hash of current settings for cache disk invalidation.

        Returns:
            DistanceMatrix containing pairwise distances.
        """
        # If we reach here, method actually executed (not from instance cache)
        # pylint: disable=attribute-defined-outside-init
        self._instance_cache_hit = False

        # Ensure feature types are valid and compatible
        self._validate_feature_types(sequence_pool)

        n_sequences = len(sequence_pool)
        ids = sequence_pool.unique_ids

        dm = DistanceMatrix.from_storage_options(
            storage_options=self.settings.distance_matrix,
            n=n_sequences,
            ids=ids,
            settings_hash=settings_hash,
        )

        if dm.is_complete:
            self._display_blank_line()
            self._display_message("Using cached matrix (disk cache hit)")
            return dm

        self._compute_distances(dm, sequence_pool)
        return dm

    @Cachable.caching_method()
    def _resolve_entity_metric(self, metric):
        """
        Resolve the entity metric for this metric.
        First tries to resolve from working env if available,
        then falls back to registered metrics.

        Args:
            metric: The entity metric to resolve.
        Returns:
            Metric: The entity metric instance.
        """
        if not isinstance(metric, str):
            self._validate_entity_metric(metric)
            return metric

        if self._workenv is not None:
            resolved = self._try_resolve_entity_metric_from_workenv(metric)
            if resolved is not None:
                return resolved

        return self._try_resolve_entity_metric_from_registry(metric)

    def _try_resolve_entity_metric_from_workenv(self, metric):
        """Try to resolve entity metric from working env."""
        LOGGER.info(
            "Attempting to resolve entity metric '%s' from working env.", metric
        )
        try:
            entity_metric = self._workenv.metrics.entity[metric]
            LOGGER.info("Entity metric '%s' resolved from working env.", metric)
            return entity_metric
        except KeyError:
            available = list(self._workenv.metrics.entity.keys())
            LOGGER.info(
                "Could not resolve entity metric '%s' from working env. Available: %s. "
                "Resolution skipped. Try from default registered metrics",
                metric,
                ", ".join(available),
            )
            return None

    def _try_resolve_entity_metric_from_registry(self, mtype):
        """Try to resolve entity metric from registry."""
        resolved_metric = EntityMetric.get_metric(mtype)
        LOGGER.info(
            "%s: Using entity metric `%s` with default settings.",
            self.__class__.__name__,
            mtype,
        )
        return resolved_metric

    def _validate_entity_metric(self, metric):
        if not isinstance(metric, EntityMetric):
            raise ValueError(
                f"Invalid entity metric: {metric}. "
                "Expected a EntityMetric instance or a valid string identifier."
            )

    def _validate_feature_types(self, sequence):
        """
        Validate that feature types are compatible with the entity metric.

        Extracts feature types from sequence metadata and delegates
        validation to the entity metric.

        Args:
            sequence: Sequence or SequencePool with metadata.

        Raises:
            ValueError: If feature types are incompatible with entity metric.
        """
        if self.entity_metric is None:
            return

        feature_types = self._extract_feature_types(sequence)
        if feature_types:
            self.entity_metric.validate_feature_types(feature_types)

    def _extract_feature_types(self, sequence):
        """
        Extract feature types from sequence metadata.

        Args:
            sequence: Sequence or SequencePool with metadata.

        Returns:
            List[str]: Feature types for the configured entity features.
                Empty list if metadata is unavailable.
        """
        # Get entity features to use
        entity_features = sequence.settings.validate_and_filter_entity_features(
            self._entity_features
        )

        # Get metadata & entity descriptors
        metadata = sequence.metadata
        entity_descriptors = metadata.entity_descriptors

        # Extract types for configured features
        feature_types = []
        for feature_name in entity_features:
            descriptor = entity_descriptors.get(feature_name)
            if descriptor is not None:
                feature_types.append(descriptor.feature_type)
        return feature_types

    def _progress_bar(self, sequence_pool):
        """Create a progress bar for sequence pool computation.

        Args:
            sequence_pool (SequencePool): Pool of sequences to process.

        Returns:
            tqdm: Configured progress bar instance.
        """
        n_sequences = len(sequence_pool)
        total_pairs = (n_sequences * (n_sequences - 1)) // 2
        return self._create_progress_bar(total_pairs)

    # pylint: disable=arguments-differ
    def process(self, *, sequence_pool, export, output_dir, exist_ok):
        """
        Compute metric in a runner.

        Args:
            sequence_pool: Pool of sequences to analyze
            export: If True, export results
            output_dir: Base output directory
            exist_ok: If True, existing output files will be overwritten

        Returns:
            DataFrame with metric results matrix
        """
        matx_res = self.compute_matrix(sequence_pool)
        if export:
            self.export_settings(
                output_dir=output_dir,
                format_type="yaml",
                exist_ok=exist_ok,
                makedirs=True,
            )
            export_to_csv(matx_res, output_dir / "results.csv")
        return matx_res

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered sequence metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredSequenceMetricTypeError(
            f"Unknown sequence metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
