# #!/usr/bin/env python3
"""
Hamming Entity metric.
"""

from typing import Optional, Union

import numpy as np
from numba.typed import List as NumbaList
from pydantic import field_validator
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators.viewer.decorator import viewer
from pypassist.fallback.typing import Dict

from .kernels import hamming_dist_simple, hamming_dist_weighted
from ...base.metric import EntityMetric
from ...base.settings import BaseEntityMetricSettings
from .....loader.base import Loader


@viewer
@dataclass
class HammingEntityMetricSettings(BaseEntityMetricSettings):
    """
    Configuration settings for the Hamming Entity metric.

    Attributes:
        entity_features (Optional[List[str]]):
            Column names for entity features to include in the metric.
            If None, all entity features will be used.
        cost:
            Entity distance mapping. Can be a cost dictionary, a loader instance,
            or a string referencing a Loader in the workenv.
        default_value (float):
            Value used when cost is undefined. Defaults to `0.0`.

    Note: Inherits `entity_features` from BaseEntityMetricSettings.
    """

    cost: Optional[Union[Dict, Loader, str]] = None
    default_value: float = 0.0

    @field_validator("default_value")
    @classmethod
    def validate_default_value_not_nan(cls, v):
        """Validate that default_value is not NaN."""
        if np.isnan(v):
            raise ValueError("default_value cannot be NaN.")
        return v


class HammingEntityMetric(EntityMetric, register_name="hamming"):
    """
    Hamming Entity metric.
    """

    SETTINGS_DATACLASS = HammingEntityMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = HammingEntityMetricSettings()

        super().__init__(settings, workenv=workenv)

    @property
    def cost_dict(self):
        """Return validated cost dictionary from settings."""
        if self._settings.cost is None:
            return None

        cost_dict = self._settings.cost
        if isinstance(cost_dict, Loader):
            cost_dict = self._settings.cost.load()

        if isinstance(cost_dict, str):
            cost_dict = self._try_resolve_loader_from_workenv(cost_dict)

        if not isinstance(cost_dict, dict):
            raise ValueError(
                "Field `cost` must be a dictionary, a Loader instance, "
                "or a string referencing a Loader in the workenv. "
                f"Got: {type(cost_dict)}"
            )

        return cost_dict

    def _compute_single_distance(self, ent_a, ent_b):
        """
        Compute Hamming distance between two entities.

        Args:
            ent_a (Entity): First entity.
            ent_b (Entity): Second entity.

        Returns:
            float: The Hamming distance (0 if equal, cost or 1 if different).
        """
        # Get values using entity_features from metric settings
        val_a = ent_a.get_value(self.entity_features)
        val_b = ent_b.get_value(self.entity_features)

        if self.cost_dict is not None:
            return self.cost_dict.get((val_a, val_b), self._settings.default_value)

        return float(val_a != val_b)

    @property
    def distance_kernel(self):
        """
        Return the Numba-compiled element-wise distance function.
        """
        if self.settings.cost is not None:
            return hamming_dist_weighted
        return hamming_dist_simple

    def validate_feature_types(self, feature_types):
        """
        Validate feature types compatibility with Hamming metric.

        Rules:
            - Textual features are not supported.
            - A single numerical feature is not meaningful.

        For multiple features, each entity tuple becomes a composite category,
        so numerical features are acceptable as part of a composite.

        Args:
            feature_types: List of feature types.

        Raises:
            ValueError: If features are incompatible.
        """
        if "textual" in feature_types:
            raise ValueError(
                "HammingEntityMetric does not support textual features. "
                "Consider using a different metric."
            )

        if feature_types == ["numerical"]:
            raise ValueError(
                "HammingEntityMetric with a single numerical feature is not meaningful. "
                "Consider updating metadata to 'categorical' or using a different metric."
            )

    def prepare_computation_data(self, sequence_array):
        """
        Prepare inputs for Numba execution (encoding, cost matrix).

        Args:
            sequence_array (SequenceArray): The input sequence data.

        Returns:
            tuple: (NumbaList of encoded arrays, context)
        """
        n_seq = len(sequence_array.data)
        if n_seq == 0:
            return NumbaList(), ()

        # Encode sequences to integer indices
        encoded_arrays, vocab_map = self._encode_sequences(sequence_array)

        # Build cost matrix if needed
        context = self._build_context(vocab_map)

        return encoded_arrays, context

    def _encode_sequences(self, sequence_array):
        """
        Encode sequence values to integer indices.

        Returns:
            tuple: (NumbaList of encoded arrays, vocab_map)
        """
        arrays_list = sequence_array.data

        # Convert arrays to lists and collect all values
        seq_as_lists = []
        all_values = []

        for arr in arrays_list:
            if hasattr(arr, "ndim") and arr.ndim > 1:
                values = [tuple(x) for x in arr]
            elif isinstance(arr, np.ndarray):
                values = arr.tolist()
            else:
                values = list(arr)
            seq_as_lists.append(values)
            all_values.extend(values)

        # Build vocabulary mapping
        vocab_map = {v: i for i, v in enumerate(set(all_values))}

        # Encode to NumbaList of 1D arrays
        encoded_arrays = NumbaList()
        for values in seq_as_lists:
            encoded = np.array([vocab_map[v] for v in values], dtype=np.int32)
            encoded_arrays.append(encoded)

        return encoded_arrays, vocab_map

    def _build_context(self, vocab_map):
        """
        Build context tuple for kernel (cost matrix if needed).

        Returns:
            tuple: Empty tuple or (cost_matrix,)
        """
        cost_dict = self.cost_dict
        if cost_dict is None:
            return ()

        n_vocab = len(vocab_map)
        default_val = self.settings.default_value

        cost_matrix = np.full((n_vocab, n_vocab), default_val, dtype=np.float32)
        np.fill_diagonal(cost_matrix, 0.0)

        nan_keys = []
        for (k1, k2), val in cost_dict.items():
            if k1 in vocab_map and k2 in vocab_map:
                if np.isnan(val):
                    nan_keys.append((k1, k2))
                else:
                    i, j = vocab_map[k1], vocab_map[k2]
                    cost_matrix[i, j] = val
                    cost_matrix[j, i] = val

        if nan_keys:
            raise ValueError(
                f"Cost dictionary contains NaN values for keys: {nan_keys[:5]}"
                + (f" (and {len(nan_keys) - 5} more)" if len(nan_keys) > 5 else "")
            )

        return (cost_matrix,)

    def _try_resolve_loader_from_workenv(self, loader):
        """Try to resolve loader from working env."""
        loader = self._workenv.loaders.get(loader, None)
        if loader is None:
            available = list(self._workenv.loaders.keys())
            raise ValueError(
                f"Could not resolve loader '{loader}' from working env. ",
                f"Available: {available}. ",
            )

        return loader
