"""
Create Custom Metric
==================

Create a custom sequence metric.
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
# Let's create a simple sequence data to demonstrate the soft DTW metric.

# %%
N_SEQ = 100
SIZE_DISTRIBUTION = [4, 5, 6, 7, 8, 9, 10, 11, 12]
SEED = 42

# Generate simple sequences for clear metric demonstration
simple_data = generate_event_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["A", "B", "C", "D"],
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
# ### Custom Sequence Metric
#
# Define a custom sequence metric that simply calculates the length difference between two sequences.
#
# **Minimal implementation**: Override `_compute_single_distance(seq_a, seq_b)` to define your metric logic.
#
# **Performance optimization**: For large pools, you can also override `_compute_distances(dm, sequence_pool)`
# to use vectorized operations or Numba JIT compilation (see DTW, LCS implementations for examples).


# %%
# Create a custom sequence metric
from pydantic.dataclasses import dataclass, Field
from tanat.metric.sequence.base.metric import SequenceMetric
from tanat.metric.matrix import MatrixStorageOptions


@dataclass
class SimpleLengthSettings:
    """Settings for the length metric.

    Note: We don't inherit from BaseSequenceMetricSettings since this metric
    doesn't use an entity_metric. We only declare distance_matrix which is
    required for compute_matrix() support.
    """

    absolute: bool = True  # If True, returns absolute value of the difference
    # Required for compute_matrix() support
    distance_matrix: MatrixStorageOptions = Field(default_factory=MatrixStorageOptions)


class SimpleLengthMetric(SequenceMetric, register_name="length"):
    """Metric that simply calculates the length difference between two sequences."""

    SETTINGS_DATACLASS = SimpleLengthSettings

    def __init__(self, settings=None):
        if settings is None:
            settings = SimpleLengthSettings()
        super().__init__(settings)

    def _compute_single_distance(self, seq_a, seq_b):
        """Calculate the length difference between two sequences."""
        len_a = len(seq_a.sequence_data)
        len_b = len(seq_b.sequence_data)

        difference = len_a - len_b

        if self._settings.absolute:
            return abs(difference)

        return difference


# %%
# Access two simple sequences
seq_0 = simple_pool["seq-0"]
seq_1 = simple_pool["seq-1"]

# Test custom metric
custom_metric = SimpleLengthMetric()
custom_metric(seq_0, seq_1)

# %%
dm = custom_metric.compute_matrix(simple_pool)
dm.to_dataframe().head()
