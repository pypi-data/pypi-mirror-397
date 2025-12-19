"""
Create Custom Metric
============================

Learn how to create a custom entity metric and use it with sequence metrics.
"""

# %% [markdown]
# ### Required imports

# %%
# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
)

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate custom entity metrics.

# %%
N_SEQ = 10
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple sequences for clear metric demonstration
simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D", "E", "F", "G"],
    missing_data=0.0,
    entity_feature="event",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "time_column": "date",
    "entity_features": ["event"],
}

simple_pool = EventSequencePool(simple_data, simple_settings)
simple_pool

# %% [markdown]
# ## Custom Entity Metric
#
# Entity metrics compare individual elements within sequences.
# Let's create a custom metric that computes an "alphabetical distance"
# between two categorical values (e.g., distance between "A" and "C" is 2).

# %%
import numpy as np
from numba import njit
from numba.typed import List as NumbaList
from pydantic.dataclasses import dataclass

from tanat.metric.entity.base.metric import EntityMetric
from tanat.metric.entity.base.settings import BaseEntityMetricSettings


# Define the Numba kernel
@njit
def _alphabetical_kernel(val_a, val_b, context):
    """Compute alphabetical distance between encoded values."""
    dist = abs(val_a - val_b)
    normalize = context[0]  # 1 = normalize, 0 = raw
    if normalize:
        return dist / 25.0
    return float(dist)


@dataclass
class AlphabeticalDistanceSettings(BaseEntityMetricSettings):
    """Settings for the alphabetical distance metric.

    Note: Inherits entity_features from BaseEntityMetricSettings.
    """

    normalize: bool = False  # If True, normalize by max possible distance


class AlphabeticalEntityMetric(EntityMetric, register_name="alphabetical"):
    """
    Metric that computes the alphabetical distance between two entity values.

    For example: distance("A", "C") = 2 (two letters apart)
    """

    SETTINGS_DATACLASS = AlphabeticalDistanceSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = AlphabeticalDistanceSettings()
        super().__init__(settings)

    def _compute_single_distance(self, ent_a, ent_b):
        """
        Compute alphabetical distance between two entities.

        Note:
            Entity types and feature types are already validated by the base class
            before this method is called (via __call__).

        Args:
            ent_a (Entity): First entity.
            ent_b (Entity): Second entity.

        Returns:
            float: The alphabetical distance.
        """
        # Get value using entity_features from metric settings
        val_a = ent_a.get_value(self.entity_features)
        val_b = ent_b.get_value(self.entity_features)

        # Get first character of each value (assuming string values)
        char_a = str(val_a)[0].upper()
        char_b = str(val_b)[0].upper()

        # Compute distance as difference in ASCII values
        dist = abs(ord(char_a) - ord(char_b))

        if self._settings.normalize:
            # Normalize by max distance (25 for A-Z)
            return dist / 25.0

        return float(dist)

    def prepare_computation_data(self, sequence_array):
        """
        Prepare data for Numba computation.
        Needed for SequenceMetric compatibility. Allows efficient use
        of this entity metric within sequence-level metrics.

        Returns a NumbaList of encoded arrays for efficient Numba processing.
        and a context tuple with normalization flag.
        """

        encoded_arrays = NumbaList()
        for arr in sequence_array.data:
            # Encode first character of each value as integer (A=0, B=1, ...)
            encoded = np.array(
                [ord(str(val)[0].upper()) - ord("A") for val in arr], dtype=np.int32
            )
            encoded_arrays.append(encoded)

        # Context: tuple with normalization flag (1 = normalize, 0 = raw)
        context = (int(self._settings.normalize),)

        return encoded_arrays, context

    @property
    def distance_kernel(self):
        """
        Return the Numba-compiled distance function.
        Used for efficient computation at sequence metric level.
        """
        return _alphabetical_kernel

    def validate_feature_types(self, feature_types):
        """
        Entity metric constraint over feature types.
        Here we validate that features are categorical or textual (for alphabetical comparison).
        Use by __call__ or at sequence metric level before computation.
        """
        for ftype in feature_types:
            if ftype not in ("categorical", "textual"):
                raise ValueError(
                    f"AlphabeticalDistanceMetric requires categorical or textual features, "
                    f"got '{ftype}'"
                )


# %% [markdown]
# ### Test the Custom Entity Metric
#
# Let's test our custom metric on individual entities.

# %%
# Access entities from sequences
entity_a = simple_pool["seq-0"][0]
entity_b = simple_pool["seq-1"][0]

print(f"Entity A: {entity_a.value}")
print(f"Entity B: {entity_b.value}")

# %%
# Create and test custom metric
custom_metric = AlphabeticalEntityMetric()
custom_metric

# %%
# Compute distance between two entities
distance = custom_metric(entity_a, entity_b)
print(
    f"Alphabetical distance between '{entity_a.value}' and '{entity_b.value}': {distance}"
)

# %%
# Test with normalization
distance_normalized = custom_metric(entity_a, entity_b, normalize=True)
print(f"Normalized distance: {distance_normalized}")

# %% [markdown]
# ## Use Custom Entity Metric with Sequence Metrics
#
# The real power of custom entity metrics is using them as building blocks
# for sequence-level comparisons. Let's use our metric with `LinearPairwiseSequenceMetric`.

# %%
from tanat.metric.sequence import (
    LinearPairwiseSequenceMetric,
    LinearPairwiseSequenceMetricSettings,
)

# Create LinearPairwise metric using our custom entity metric
linear_settings = LinearPairwiseSequenceMetricSettings(
    entity_metric=custom_metric,
    agg_fun="sum",
)

linear_metric = LinearPairwiseSequenceMetric(settings=linear_settings)
linear_metric

# %%
# Compute distance between two sequences using our custom entity metric
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

print(f"Sequence 0: {[e.value for e in seq_0]}")
print(f"Sequence 1: {[e.value for e in seq_1]}")

distance = linear_metric(seq_0, seq_1)
print(f"LinearPairwise distance with AlphabeticalEntityMetric: {distance:.4f}")

# %%
# Compute full distance matrix using our custom entity metric
dm = linear_metric.compute_matrix(simple_pool)
print("Distance Matrix with AlphabeticalEntityMetric:")
dm.to_dataframe()
