#!/usr/bin/env python3
"""
SequenceArray dataclass.
"""

import sys
from dataclasses import dataclass
from typing import Optional, Any, TYPE_CHECKING

import numpy as np
from pypassist.fallback.typing import List

from ...time.anchor import resolve_date_series_from_anchor

# Fallback for slots=True (Python >= 3.10)
dataclass_slots = {}
if sys.version_info >= (3, 10):
    dataclass_slots = {"slots": True}


@dataclass(**dataclass_slots)
class SequenceArray:
    """
    Container for a collection of sequence arrays.
    Can represent a single sequence (size=1) or a pool of sequences (size=N).

    Attributes:
        data: List of numpy arrays containing entity feature values.
        lengths: Array of sequence lengths.
        ids: Optional list of sequence identifiers.
        timestamps: Optional list of timestamp arrays (int64, nanoseconds since epoch).
            Used by time-aware metrics like DTW with time constraints.
        durations: Optional list of duration arrays (float64, seconds).
            Used by metrics like Chi2 that weight by time spent in each state.
    """

    data: List[np.ndarray]
    lengths: np.ndarray
    ids: Optional[List[Any]] = None
    timestamps: Optional[List[np.ndarray]] = None
    durations: Optional[List[np.ndarray]] = None

    def __post_init__(self):
        if len(self.data) != len(self.lengths):
            raise ValueError(
                f"Data and lengths mismatch: {len(self.data)} vs {len(self.lengths)}"
            )
        if self.ids is not None and len(self.ids) != len(self.data):
            raise ValueError(
                f"Data and ids mismatch: {len(self.data)} vs {len(self.ids)}"
            )
        if self.timestamps is not None and len(self.timestamps) != len(self.data):
            raise ValueError(
                f"Data and timestamps mismatch: {len(self.data)} vs {len(self.timestamps)}"
            )
        if self.durations is not None and len(self.durations) != len(self.data):
            raise ValueError(
                f"Data and durations mismatch: {len(self.data)} vs {len(self.durations)}"
            )

    @property
    def size(self):
        """Number of sequences in the collection."""
        return len(self.data)

    @property
    def max_len(self):
        """Maximum length of sequences in the collection."""
        if self.size == 0:
            return 0
        return self.lengths.max()

    @property
    def has_timestamps(self):
        """Check if timestamps are available."""
        return self.timestamps is not None

    @property
    def has_durations(self):
        """Check if durations are available."""
        return self.durations is not None

    @classmethod
    def concatenate(cls, arrays):
        """
        Concatenate multiple SequenceArray objects.

        Args:
            arrays (List[SequenceArray]):
                List of SequenceArray objects to concatenate.

        Returns:
            SequenceArray: The concatenated SequenceArray.
        """
        for arr in arrays:
            if not isinstance(arr, SequenceArray):
                raise ValueError(
                    f"All elements must be SequenceArray, got {type(arr)}."
                )

        data = []
        lengths_list = []
        ids = []
        timestamps = []
        durations = []

        # Check which optional fields are present in all arrays
        has_ids = all(arr.ids is not None for arr in arrays)
        has_timestamps = all(arr.timestamps is not None for arr in arrays)
        has_durations = all(arr.durations is not None for arr in arrays)

        for arr in arrays:
            data.extend(arr.data)
            lengths_list.append(arr.lengths)
            if has_ids:
                ids.extend(arr.ids)
            if has_timestamps:
                timestamps.extend(arr.timestamps)
            if has_durations:
                durations.extend(arr.durations)

        return cls(
            data=data,
            lengths=np.concatenate(lengths_list),
            ids=ids if has_ids else None,
            timestamps=timestamps if has_timestamps else None,
            durations=durations if has_durations else None,
        )

    @classmethod
    def from_sequence(
        cls,
        sequence,
        entity_features=None,
        include_timestamps=False,
        include_durations=False,
    ):
        """
        Create a SequenceArray from a single Sequence.

        Args:
            sequence: The Sequence object to extract data from.
            entity_features (list, optional):
                List of entity features names to include.
                If None, includes all entity_features from sequence settings.
            include_timestamps (bool):
                If True, extract timestamps from temporal columns.
                Timestamps keep their native type (datetime64 or numeric).
                Defaults to False.
            include_durations (bool):
                If True, extract durations from temporal columns.
                For datetime: durations as timedelta.
                For numeric: difference between end and start.
                Defaults to False.

        Returns:
            SequenceArray: The sequence data in array format.
        """
        entity_features = sequence.settings.validate_and_filter_entity_features(
            entity_features
        )

        # Use standardized data to ensure temporal columns are resolved
        # pylint: disable=protected-access
        standardized_data = sequence._get_standardized_data(
            entity_features=entity_features
        )

        # Extract entity feature data
        arr = standardized_data[entity_features].values
        if arr.ndim == 2 and arr.shape[1] == 1:
            arr = arr.ravel()

        # Extract timestamps if requested
        timestamps = None
        if include_timestamps:
            # pylint: disable=protected-access
            anchor = sequence._resolve_anchor()
            temporal_cols = sequence.settings.temporal_columns(standardize=True)
            ts = cls._extract_timestamps(standardized_data, temporal_cols, anchor)
            timestamps = [ts]

        # Extract durations if requested
        durations = None
        if include_durations:
            temporal_cols = sequence.settings.temporal_columns(standardize=True)
            dur = cls._extract_durations(standardized_data, temporal_cols)
            durations = [dur]

        return cls(
            data=[arr],
            lengths=np.array([len(arr)], dtype=np.int16),
            ids=[sequence.id_value],
            timestamps=timestamps,
            durations=durations,
        )

    @classmethod
    def from_sequence_pool(
        cls,
        sequence_pool,
        entity_features=None,
        include_timestamps=False,
        include_durations=False,
    ):
        """
        Create a SequenceArray from a SequencePool.

        Uses a single groupby operation for efficiency.

        Args:
            sequence_pool: The SequencePool object to extract data from.
            entity_features (list, optional):
                List of entity features names to include.
                If None, includes all entity_features from pool settings.
            include_timestamps (bool):
                If True, extract timestamps from temporal columns.
                Timestamps keep their native type (datetime64 or numeric).
                Defaults to False.
            include_durations (bool):
                If True, extract durations from temporal columns.
                For datetime: durations as timedelta.
                For numeric: difference between end and start.
                Defaults to False.

        Returns:
            SequenceArray: The sequence data in array format.
        """
        entity_features = sequence_pool.settings.validate_and_filter_entity_features(
            entity_features
        )

        # Use standardized data to ensure temporal columns are resolved
        # pylint: disable=protected-access
        standardized_data = sequence_pool._get_standardized_data(
            entity_features=entity_features
        )

        # Extract data
        ids = sorted(list(sequence_pool.unique_ids))
        id_col = sequence_pool.settings.id_column

        # Group once for all extractions
        grouped = standardized_data.groupby(level=id_col)

        # Determine temporal columns
        temporal_cols = sequence_pool.settings.temporal_columns(standardize=True)

        # Resolve anchor if timestamps requested
        anchor = None
        if include_timestamps:
            # pylint: disable=protected-access
            anchor = sequence_pool._resolve_anchor()

        # Build arrays with single iteration over groups
        data_list = []
        lengths = []
        timestamps_list = [] if include_timestamps else None
        durations_list = [] if include_durations else None

        for seq_id in ids:
            group_data = grouped.get_group(seq_id)

            # Extract entity features
            arr = group_data[entity_features].values
            if arr.ndim == 2 and arr.shape[1] == 1:
                arr = arr.ravel()
            data_list.append(arr)
            lengths.append(len(arr))

            # Extract timestamps if requested
            if include_timestamps:
                ts = cls._extract_timestamps(group_data, temporal_cols, anchor)
                timestamps_list.append(ts)

            # Extract durations if requested
            if include_durations:
                dur = cls._extract_durations(group_data, temporal_cols)
                durations_list.append(dur)

        return cls(
            data=data_list,
            lengths=np.array(lengths, dtype=np.int16),
            ids=ids,
            timestamps=timestamps_list,
            durations=durations_list,
        )

    @staticmethod
    def _extract_timestamps(data, temporal_cols, anchor):
        """
        Extract timestamps from data using anchor strategy.

        Args:
            data: DataFrame with temporal columns.
            temporal_cols: List of temporal column names.
            anchor: DateAnchor enum specifying the anchoring strategy.

        Returns:
            np.ndarray: Timestamps in their native type (datetime64 or numeric).
        """
        timestamps = resolve_date_series_from_anchor(data, temporal_cols, anchor)
        return timestamps.values

    @staticmethod
    def _extract_durations(data, temporal_cols):
        """
        Extract durations from temporal columns.

        For sequences with only one temporal column (events), returns array of 1.0.
        For sequences with start/end columns, computes the difference.

        Args:
            data: DataFrame with temporal columns.
            temporal_cols: List of temporal column names.

        Returns:
            np.ndarray: Durations as timedelta (datetime) or numeric difference.
        """
        if len(temporal_cols) < 2:
            # Event sequences: no duration, return 1.0 for each entity
            return np.ones(len(data), dtype=np.float32)

        # State/Interval sequences: compute duration
        start_col, end_col = temporal_cols[0], temporal_cols[1]
        start_times = data[start_col]
        end_times = data[end_col]

        durations = end_times - start_times
        return durations.values
