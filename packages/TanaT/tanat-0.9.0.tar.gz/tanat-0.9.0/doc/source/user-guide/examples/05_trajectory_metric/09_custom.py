"""
Create Custom Metric
==================

Create a custom trajectory metric.
"""

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime

# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_event_sequences,
    generate_state_sequences,
)

# Sequence pools
from tanat.sequence import (
    EventSequencePool,
    StateSequencePool,
)

from tanat.trajectory import TrajectoryPool

# %% [markdown]
# ## Data Setup
#
# Let's create a simple sequence data to demonstrate the aggregation metric.

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

# %%
# Generate another set of simple sequences (states)
simple_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["Z", "Y", "X", "W"],
    missing_data=0.0,
    entity_feature="states",
    seed=SEED,
)

simple_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "default_end_value": datetime.now(),  # Avoid warning
    "entity_features": ["states"],
}
simple_pool_2 = StateSequencePool(simple_data, simple_settings)
simple_pool_2

# %%
# Build trajectory pool
trajectory_pool = TrajectoryPool.init_empty()
trajectory_pool.add_sequence_pool(simple_pool, "events")
trajectory_pool.add_sequence_pool(simple_pool_2, "states")

# Configure settings
trajectory_pool.update_settings(intersection=False)


# %% [markdown]
# ### Custom Trajectory Metric
#
# Define a dummy trajectory metric that consistently returns a fixed distance value between two trajectories.
#
# **Minimal implementation**: Override `_compute_single_distance(traj_a, traj_b)` to define your metric logic.
#
# **Performance optimization**: For large pools, you can also override `_compute_distances(dm, trajectory_pool)`
# to use vectorized operations or parallel processing (see AggregationTrajectoryMetric for an example).


# %%
# Create a custom trajectory metric
from pydantic.dataclasses import dataclass, Field

from tanat.metric.trajectory.base.metric import TrajectoryMetric
from tanat.metric.matrix import MatrixStorageOptions


@dataclass
class DummySettings:
    """Settings for the dummy metric.

    Note: distance_matrix is required for compute_matrix() support.
    """

    value: int = 42  # Distance value to return
    # Required for compute_matrix() support
    distance_matrix: MatrixStorageOptions = Field(default_factory=MatrixStorageOptions)


class DummyTrajectoryMetric(TrajectoryMetric, register_name="dummy"):
    """Metric that computes a dummy distance between two trajectories."""

    SETTINGS_DATACLASS = DummySettings

    def __init__(self, settings=None):
        if settings is None:
            settings = DummySettings()
        super().__init__(settings)

    def _compute_single_distance(self, traj_a, traj_b):
        """
        Compute dummy distance between two trajectories.
        """
        # always return the fixed value from settings
        return self.settings.value


# %%
# Access two simple trajectories
traj_1 = trajectory_pool["seq-0"]
traj_2 = trajectory_pool["seq-1"]

# Test custom metric
custom_metric = DummyTrajectoryMetric()
custom_metric(traj_1, traj_2)

# %%
dm = custom_metric.compute_matrix(trajectory_pool)
dm.to_dataframe().head()
