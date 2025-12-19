#!/usr/bin/env python3
"""
Chi2 distance metric.
"""

import logging
from typing import List, Optional

import numpy as np
from pydantic import field_validator
from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_chi2_single_pair,
    compute_chi2_matrix_chunk,
)
from ...base.metric import SequenceMetric
from ...base.settings import MatrixStorageOptions
from .....sequence.base.array import SequenceArray


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class Chi2SequenceMetricSettings:
    """
    Configuration settings for Chi2 sequence metric computation.

    Attributes:
        entity_features: Column names for entity features to include.
            For multiple features, each entity tuple becomes a composite category.
            If None, all entity features from sequence settings are used.

        distance_matrix: Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming
            from existing matrices.

    Note:
        Chi2 is a distribution-based metric that compares the proportion
        of time spent in each state/category. For EventSequences, each event
        counts as 1 unit. For State/IntervalSequences, durations are used.
    """

    entity_features: Optional[List[str]] = None
    distance_matrix: MatrixStorageOptions = Field(default_factory=MatrixStorageOptions)

    @field_validator("entity_features", mode="before")
    @classmethod
    def normalize_entity_features(cls, v):
        """
        Convert single string to list for user convenience.

        Allows users to pass a simple string when they have only one entity
        feature, instead of requiring a list. Pydantic then handles all native
        validation (type checking, etc.).

        Args:
            v: Entity feature(s) as string or list

        Returns:
            List: The value as a list (Pydantic will validate List[str] after)
        """
        if v is None:
            return v
        if isinstance(v, str):
            return [v]
        return v


class Chi2SequenceMetric(SequenceMetric, register_name="chi2"):
    """
    Chi2 Distance

    This metric uses categorical features to compute the Chi-squared
    distance between state distributions of two sequences.

    For multiple features, each entity tuple (feature1, feature2, ...)
    becomes a composite category.

    Letting p_jx be the proportion of time spent in state j in sequence x,
    the Chi-square distance is:

        chi2(x, y) = sqrt(sum_j (p_jx - p_jy)^2 / (p_jx + p_jy))

    For EventSequences, each event contributes equally (duration = 1).
    For State/IntervalSequences, actual durations are used.

    Uses Numba JIT compilation for performance.

    Note
    ----
    This distribution-based measure is sensitive to time spent in states,
    but insensitive to ordering and exact timing.

    References
    ----------
    Studer, M. and G. Ritschard (2014). A Comparative Review of Sequence
    Dissimilarity Measures. LIVES Working Papers, 33.

    Deville, J. C., & Saporta, G. (1983). Correspondence analysis,
    with an extension towards nominal time series. Journal of econometrics.
    """

    SETTINGS_DATACLASS = Chi2SequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = Chi2SequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def entity_metric(self):
        """Chi2 does not use an entity metric."""
        return None

    @property
    def _entity_features(self):
        """Get the feature(s) to use for Chi2 computation."""
        return self._settings.entity_features

    def _get_entity_features(self, sequence):
        """
        Get the list of entity features to use for Chi2.

        If entity_features is configured in settings, uses those.
        Otherwise, uses all entity features from sequence settings.

        For multiple features, each entity tuple becomes a composite category.

        Args:
            sequence: Sequence or SequencePool.

        Returns:
            List[str]: The feature IDs to use.
        """
        if self._settings.entity_features is not None:
            return self._settings.entity_features
        # Use all entity features from sequence settings
        return sequence.settings.entity_features

    def _validate_feature_types(self, sequence):
        """
        Validate feature types compatibility with Chi2 metric.

        Rules:
            - Textual features are not supported.
            - A single numerical feature is not meaningful.

        For multiple features, each entity tuple becomes a composite category,
        so numerical features are acceptable as part of a composite.

        Args:
            sequence: Sequence or SequencePool with metadata.

        Raises:
            ValueError: If features are incompatible.
        """
        feature_types = self._extract_feature_types(sequence)

        if not feature_types:
            return  # No metadata available, skip validation

        if "textual" in feature_types:
            raise ValueError(
                "Chi2 metric does not support textual features. "
                "Consider using a different metric."
            )

        if feature_types == ["numerical"]:
            raise ValueError(
                "Chi2 metric with a single numerical feature is not meaningful. "
                "Consider updating metadata to 'categorical' or using a different metric."
            )

    def _encode_sequences(self, sequence_array):
        """
        Encode sequence values to integer indices.

        Args:
            sequence_array: SequenceArray with categorical data.

        Returns:
            tuple: (encoded_arrays, n_categories)
                - encoded_arrays: np.ndarray of shape (n_seq, max_len), int32
                - n_categories: int, total number of unique categories
        """
        arrays_list = sequence_array.data
        lengths = sequence_array.lengths
        n_seq = len(arrays_list)
        max_len = int(lengths.max()) if len(lengths) > 0 else 0

        # Convert arrays to lists and collect all values
        # For multi-feature, each entity becomes a tuple (composite category)
        seq_as_lists = []
        all_values = []

        for arr in arrays_list:
            if hasattr(arr, "ndim") and arr.ndim > 1:
                # Multi-features: tuple of features becomes the category
                values = [tuple(x) for x in arr]
            elif isinstance(arr, np.ndarray):
                values = arr.tolist()
            else:
                values = list(arr)
            seq_as_lists.append(values)
            all_values.extend(values)

        # Build vocabulary mapping
        vocab_map = {v: i for i, v in enumerate(set(all_values))}
        n_categories = len(vocab_map)

        # Encode to integer array
        encoded_arrays = np.full((n_seq, max_len), -1, dtype=np.int32)
        for i, values in enumerate(seq_as_lists):
            encoded = [vocab_map[v] for v in values]
            encoded_arrays[i, : len(encoded)] = encoded

        return encoded_arrays, n_categories

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute Chi2 distance between two sequences.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The Chi2 distance for the sequence pair.
        """
        entity_features = self._get_entity_features(seq_a)

        # Extract arrays using SequenceArray with durations
        sa_a = seq_a.get_sequence_array(entity_features, include_durations=True)
        sa_b = seq_b.get_sequence_array(entity_features, include_durations=True)

        # Combine for encoding (to ensure shared vocabulary)
        combined_sa = SequenceArray.concatenate([sa_a, sa_b])

        # Encode values
        encoded_arrays, n_categories = self._encode_sequences(combined_sa)

        # Prepare durations
        durations_list = self._prepare_durations(combined_sa.durations, 2)

        # Compute distance
        return compute_chi2_single_pair(
            encoded_arrays[0],
            encoded_arrays[1],
            int(sa_a.lengths[0]),
            int(sa_b.lengths[0]),
            durations_list[0],
            durations_list[1],
            n_categories,
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise Chi2 distances using Numba-optimized kernels.

        Overrides the default naive loop implementation in SequenceMetric
        with a parallelized, JIT-compiled version for high performance.

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        entity_features = self._get_entity_features(sequence_pool)

        # Extract and prepare data with durations
        sa = sequence_pool.get_sequence_array(entity_features, include_durations=True)
        encoded_arrays, n_categories = self._encode_sequences(sa)

        # Prepare durations
        durations_list = self._prepare_durations(sa.durations, len(encoded_arrays))

        # Compute chunks with resume support
        self._compute_matrix_chunks(
            dm,
            encoded_arrays,
            sa.lengths,
            durations_list,
            n_categories,
            sequence_pool,
        )

    def _compute_matrix_chunks(
        self,
        dm,
        encoded_arrays,
        lengths,
        durations_list,
        n_categories,
        sequence_pool,
    ):
        """
        Compute matrix chunks with resume support.

        Args:
            dm: DistanceMatrix to fill.
            encoded_arrays: Encoded sequence data.
            lengths: Array of sequence lengths.
            durations_list: List of duration arrays.
            n_categories: Total number of categories.
            sequence_pool: Original pool (for progress bar).
        """
        n_sequences = len(encoded_arrays)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        with self._progress_bar(sequence_pool) as pbar:
            for start in range(0, n_sequences, batch_size):
                end = min(start + batch_size, n_sequences)
                pairs_count = self._count_chunk_pairs(start, end, n_sequences)

                # Skip if already computed (resume mode)
                if dm.is_chunk_computed(diagonal, start):
                    pbar.update(pairs_count)
                    continue

                # Compute chunk
                compute_chi2_matrix_chunk(
                    dm.data,
                    start,
                    end,
                    encoded_arrays,
                    lengths,
                    durations_list,
                    n_categories,
                )

                dm.flush()
                dm.mark_chunk_done(diagonal, start, end)
                pbar.update(pairs_count)

    def _prepare_durations(self, durations, n_sequences):
        """
        Prepare durations for Numba kernels.

        For EventSequences (no durations), returns arrays of 1.0.
        For State/IntervalSequences, converts timedeltas to hours.

        Args:
            durations: List of duration arrays from SequenceArray.
            n_sequences: Expected number of sequences.

        Returns:
            List of duration arrays (float64) ready for Numba.
        """
        if durations is None:
            # EventSequence: each event counts as 1
            return [np.ones(1, dtype=np.float64) for _ in range(n_sequences)]

        prepared = []
        for dur in durations:
            if dur is None:
                # No duration info: use 1.0 for each element
                prepared.append(np.ones(1, dtype=np.float64))
            elif np.issubdtype(dur.dtype, np.timedelta64):
                # Convert timedelta64 to hours (float64)
                hours = dur.astype("timedelta64[s]").astype(np.float64) / 3600.0
                prepared.append(hours)
            else:
                # Already numeric: ensure float64
                prepared.append(dur.astype(np.float64))

        return prepared
