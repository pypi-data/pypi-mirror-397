#!/usr/bin/env python3
"""
Distance Matrix class.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from pydantic.dataclasses import dataclass
from pypassist.utils.convert import ensure_list
from pypassist.utils.export import create_directory

LOGGER = logging.getLogger(__name__)


@dataclass
class MatrixStorageOptions:
    """
    Configuration for matrix storage and computation.

    Attributes:
        store_path: Path to store the matrix on disk (memmap).
            If None, the matrix is kept in memory only. Defaults to None.
        dtype: Data type for matrix values ('float32', 'float64'). Defaults to 'float32'.
        resume: If True, resume from existing compatible matrix (memmap).
            If False, always recompute from scratch. Defaults to True.
    """

    store_path: Optional[str] = None
    dtype: str = "float32"
    resume: bool = True


class DistanceMatrix:
    """
    A wrapper around a distance matrix (numpy array or memmap) with associated IDs.
    Handles both in-memory and on-disk storage transparently.
    """

    _METADATA_FILENAME = "metadata.json"
    _DATA_FILENAME = "data.bin"

    def __init__(
        self,
        data,
        ids=None,
        store_path=None,
        settings_hash=None,
        *,
        _presorted=False,
    ):
        """
        Initialize a DistanceMatrix.

        Args:
            data: The underlying matrix data.
            ids: List of identifiers corresponding to rows/columns.
                Will be sorted for reproducibility.
            store_path: Path to the file if data is a memmap.
            settings_hash: Hash of settings for cache validation.
                If None, cache is always considered invalid.
            _presorted: Internal flag to skip sorting (ids already sorted).
        """
        self._data = data
        if ids is None:
            self._ids = None
        elif _presorted:
            self._ids = ids
        else:
            self._ids = sorted(ensure_list(ids))
        self._store_path = store_path
        self._settings_hash = settings_hash

    @property
    def data(self):
        """Access the underlying data array."""
        return self._data

    @property
    def ids(self):
        """Access the list of IDs."""
        return self._ids

    @property
    def shape(self):
        """Return the shape of the matrix."""
        return self._data.shape

    @property
    def is_memmap(self):
        """Check if the matrix is stored on disk (memmap)."""
        return isinstance(self._data, np.memmap)

    @property
    def is_complete(self):
        """
        Check if matrix computation is complete.

        Uses diagonal values as markers: NaN means not computed yet.
        """
        diagonal = np.diagonal(self._data)
        return not np.any(np.isnan(diagonal))

    def to_dataframe(self):
        """
        Convert the matrix to a pandas DataFrame.

        Warning: This will load the entire matrix into memory if it's a memmap.
        """
        return pd.DataFrame(self._data, index=self._ids, columns=self._ids)

    def to_numpy(self):
        """
        Return the matrix as a numpy array.

        Warning: This might load data into memory.
        """
        return np.array(self._data)

    def flush(self):
        """Flush changes to disk if using memmap."""
        if self.is_memmap and hasattr(self._data, "flush"):
            self._data.flush()

    # =========================================================================
    # RESUME HELPERS
    # =========================================================================

    def get_diagonal_snapshot(self):
        """
        Get a copy of the diagonal for fast resume checking.

        Reading from memmap once is faster than repeated access.

        Returns:
            np.ndarray: Copy of the diagonal values.
        """
        return np.diagonal(self._data).copy()

    def is_chunk_computed(self, diagonal, start):
        """
        Check if a chunk starting at `start` is already computed.

        Args:
            diagonal: Pre-extracted diagonal snapshot.
            start: Starting index of the chunk.

        Returns:
            bool: True if chunk is computed (diagonal[start] is not NaN).
        """
        return not np.isnan(diagonal[start])

    def mark_chunk_done(self, diagonal, start, end):
        """
        Mark a chunk as completed by updating the diagonal snapshot.

        Args:
            diagonal: Pre-extracted diagonal snapshot (will be updated).
            start: Starting index of the chunk.
            end: Ending index of the chunk (exclusive).
        """
        for i in range(start, end):
            diagonal[i] = self._data[i, i]

    def save_metadata(self):
        """Save metadata to a JSON file in the storage directory."""
        if not self._store_path:
            return

        create_directory(self._store_path)

        store_path = Path(self._store_path)
        meta_path = store_path / self._METADATA_FILENAME
        meta = {
            "ids": self._ids,
            "shape": self.shape,
            "dtype": str(self._data.dtype),
            "settings_hash": self._settings_hash,
        }
        with meta_path.open("w", encoding="utf-8") as file:
            json.dump(meta, file)

    @classmethod
    def load(cls, path, mode="r+"):
        """
        Load a DistanceMatrix from a storage directory.

        Args:
            path: Path to the storage directory.
            mode: File mode for memmap ('r', 'r+', 'w+', 'c').

        Returns:
            DistanceMatrix instance.

        Raises:
            FileNotFoundError: If metadata or data file is missing.
        """
        path = Path(path)
        meta_path = path / cls._METADATA_FILENAME
        data_path = path / cls._DATA_FILENAME

        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with meta_path.open("r", encoding="utf-8") as file:
            meta = json.load(file)

        ids = meta.get("ids")
        shape = tuple(meta.get("shape"))
        dtype = np.dtype(meta.get("dtype"))
        settings_hash = meta.get("settings_hash")

        data = np.memmap(data_path, dtype=dtype, mode=mode, shape=shape)
        return cls(
            data,
            ids=ids,
            store_path=str(path),
            settings_hash=settings_hash,
            _presorted=True,
        )

    @classmethod
    def exists(cls, path):
        """
        Check if a valid DistanceMatrix storage exists at path.

        Args:
            path: Path to check.

        Returns:
            bool: True if both metadata.json and data.bin exist.
        """
        path = Path(path)
        if not path.is_dir():
            return False
        meta_exists = (path / cls._METADATA_FILENAME).exists()
        data_exists = (path / cls._DATA_FILENAME).exists()
        return meta_exists and data_exists

    @classmethod
    def _check_compatibility(cls, existing_dm, shape, ids, dtype, settings_hash):
        """
        Check if existing matrix matches the requested specs.

        Args:
            existing_dm: Loaded DistanceMatrix to check.
            shape: Expected shape.
            ids: Expected list of IDs (must be pre-sorted).
            dtype: Expected data type.
            settings_hash: Expected settings hash. If None, cache is invalid
                (resume not possible without hash verification).

        Returns:
            bool: True if matrix is compatible and can be resumed.
        """
        # No hash => cannot validate cache, force recompute
        if settings_hash is None:
            LOGGER.debug("No settings hash provided, cannot validate cache.")
            return False

        basic_match = (
            existing_dm.shape == shape
            and existing_dm.ids == ids
            and existing_dm.data.dtype == dtype
        )
        if not basic_match:
            return False

        stored_hash = existing_dm._settings_hash  # pylint: disable=protected-access
        return stored_hash == settings_hash

    @classmethod
    def _create_new(cls, path, shape, dtype, ids, mode, settings_hash):
        """
        Create a new DistanceMatrix at the given path.

        Initializes diagonal with NaN to track computation progress.

        Args:
            path: Storage directory path.
            shape: Matrix shape (n, n).
            dtype: Data type for the matrix.
            ids: List of IDs for rows/columns.
            mode: File mode for memmap.
            settings_hash: Hash of metric settings.

        Returns:
            DistanceMatrix instance.
        """
        create_directory(path)
        path = Path(path)
        data_path = path / cls._DATA_FILENAME
        data = np.memmap(data_path, dtype=dtype, mode=mode, shape=shape)
        np.fill_diagonal(data, np.nan)

        matrix = cls(
            data,
            ids=ids,
            store_path=str(path),
            settings_hash=settings_hash,
            _presorted=True,
        )
        matrix.save_metadata()
        return matrix

    @classmethod
    def open_or_create(cls, path, shape, dtype, ids, mode="w+", settings_hash=None):
        """
        Open existing matrix if it matches specs, else create new.

        Args:
            path: Path to the storage directory.
            shape: Expected shape of the matrix.
            dtype: Expected dtype of the matrix.
            ids: List of IDs for rows/columns.
            mode: File mode for memmap.
            settings_hash: Hash of settings for verification.

        Returns:
            DistanceMatrix instance.
        """
        # Sort ids once for all operations
        sorted_ids = sorted(ensure_list(ids)) if ids is not None else None

        if cls.exists(path):
            try:
                existing_dm = cls.load(path, mode="r+")
                if cls._check_compatibility(
                    existing_dm, shape, sorted_ids, dtype, settings_hash
                ):
                    LOGGER.debug("Resuming from existing matrix at '%s'.", path)
                    return existing_dm

                LOGGER.info("Overwriting existing matrix at '%s'.", path)
            except (OSError, ValueError, KeyError, FileNotFoundError) as e:
                LOGGER.warning(
                    "Failed to load existing matrix at '%s': %s. Creating new.",
                    path,
                    e,
                )

        LOGGER.debug("Creating new matrix at '%s'.", path)
        return cls._create_new(path, shape, dtype, sorted_ids, mode, settings_hash)

    @classmethod
    def from_storage_options(cls, storage_options, n, ids, settings_hash=None):
        """
        Create a DistanceMatrix from MatrixStorageOptions.

        Factory method that handles both in-memory and on-disk cases.

        Args:
            dm_settings: DistanceMatrixSettings instance (or None for in-memory).
            n: Number of sequences (matrix will be n x n).
            ids: List of IDs for rows/columns.
            settings_hash: Hash of metric settings for cache validation.
                Only used if dm_settings.resume is True.

        Returns:
            DistanceMatrix instance (in-memory or memmap).
        """
        shape = (n, n)

        # No store_path => in-memory
        if storage_options.store_path is None:
            dtype = np.dtype(storage_options.dtype)
            data = np.zeros(shape, dtype=dtype)
            np.fill_diagonal(data, np.nan)  # Mark as not computed
            return cls(data, ids=ids)

        # On-disk with optional resume
        dtype = np.dtype(storage_options.dtype)
        hash_for_resume = settings_hash if storage_options.resume else None

        return cls.open_or_create(
            path=storage_options.store_path,
            shape=shape,
            dtype=dtype,
            ids=ids,
            settings_hash=hash_for_resume,
        )

    def aggregate_from(self, matrices, weights, kernel, batch_size=500, pbar=None):
        """
        Aggregate multiple distance matrices into this matrix using chunked computation.

        Args:
            matrices: Numba-typed list of matrix data arrays.
            weights: Weights for each matrix (list/array).
            kernel: Numba chunk kernel (e.g., matrix_chunk_mean_kernel).
            batch_size: Number of rows per chunk.
            pbar: Optional progress bar to update.
        """
        weights = np.asarray(weights, dtype=np.float32)
        n = self.shape[0]
        diagonal = self.get_diagonal_snapshot()

        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)

            # Skip if already computed (resume mode)
            if self.is_chunk_computed(diagonal, start):
                if pbar:
                    pbar.update(self._count_chunk_pairs(start, end, n))
                continue

            # Compute chunk
            kernel(self._data, matrices, weights, start, end, n)

            self.flush()
            self.mark_chunk_done(diagonal, start, end)

            if pbar:
                pbar.update(self._count_chunk_pairs(start, end, n))

    @staticmethod
    def _count_chunk_pairs(start, end, n):
        """Count the number of unique pairs in a chunk."""
        count = 0
        for i in range(start, end):
            count += n - i - 1
        return count

    def __getitem__(self, key):
        """Delegate indexing to the underlying data."""
        return self._data[key]

    def __repr__(self):
        """Custom representation showing storage mode and shape."""
        storage_type = "Memmap" if self.is_memmap else "Memory"
        path_info = f" at '{self._store_path}'" if self._store_path else ""
        ids_info = f" with {len(self._ids)} IDs" if self._ids else " without IDs"

        return (
            f"<DistanceMatrix: {self.shape} ({storage_type}{path_info})"
            f"{ids_info}>\n{self._data.__repr__()}"
        )
