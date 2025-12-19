"""
Chi-Squared Distance
====================

Compute the chi-squared distance between two sequences based on state distributions.
"""

# %% [markdown]
# ### Required imports

# %%
from datetime import datetime

# Data simulation
from tanat.dataset.simulation.sequence import (
    generate_state_sequences,
)

# Sequence pools
from tanat.sequence import (
    StateSequencePool,
)

# Sequence Metrics
from tanat.metric.sequence import (
    Chi2SequenceMetric,
    Chi2SequenceMetricSettings,
)

# %% [markdown]
# ## Data Setup
#
# Let's create state sequences to demonstrate the Chi2 metric.
# Chi2 compares the proportion of time spent in each state.

# %%
N_SEQ = 100
SIZE_DISTRIBUTION = [5, 6, 7, 8, 9, 10]
SEED = 42

# Generate state sequences
state_data = generate_state_sequences(
    n_seq=N_SEQ,
    seq_size=SIZE_DISTRIBUTION,
    vocabulary=["healthy", "sick", "recovered"],
    missing_data=0.0,
    entity_feature="status",
    seed=SEED,
)
print(state_data)

state_settings = {
    "id_column": "id",
    "start_column": "start_date",
    "entity_features": ["status"],
    # Avoid warning for last state
    "default_end_value": datetime.now(),
}

state_pool = StateSequencePool(state_data, state_settings)
state_pool

# %% [markdown]
# ### Chi-Squared Distance
#
# Chi2 compares **state distributions** (ignoring temporal order).
# It measures how different the time spent in each state is between sequences.

# %%
# Create Chi2 metric
settings = Chi2SequenceMetricSettings(
    entity_features=["status"],
)
chi2_metric = Chi2SequenceMetric(settings=settings)

# -- Settings overview
chi2_metric

# %%
# Access two sequences
seq_0 = state_pool["seq-0"]
seq_1 = state_pool["seq-1"]

# Compute Chi2 distance
chi2_metric(seq_0, seq_1)

# %% [markdown]
# ### Key difference from other metrics
#
# Chi2 does **not** use an `entity_metric`. It directly computes state distributions.
# - For **StateSequence**: uses actual durations
# - For **EventSequence**: each event counts as 1 unit

# %%
# Compute Chi2 on the full pool
dm = chi2_metric.compute_matrix(state_pool)
dm.to_dataframe().head()
