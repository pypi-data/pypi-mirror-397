# %% [markdown]
# # MOOC Sequence Analysis with TanaT
#
# ## Overview
#
# This tutorial demonstrates sequence analysis of learner behavior using TanaT with data from a Moodle learning management system. The analysis follows the methodology proposed by Saqr et al. for understanding student engagement patterns in online courses.
#
# **Learning Objectives:**
# - Load and preprocess temporal learning data
# - Create session-based sequences from event logs
# - Visualize learner activity patterns
# - Cluster sequences using Optimal Matching with custom costs
#
# **Dataset Information:**
# The MOOC dataset contains learner interaction logs including:
# - User identifiers and timestamps
# - Action types (view, submit, interact, etc.)
# - Course context and components
# - Event descriptions
#
# **Source:** Saqr, M., López-Pernas, S., Helske, S., Durand, M., Murphy, K., Studer, M., & Ritschard, G. (2024). *Sequence analysis in education: principles, techniques, and tutorial with R*. In *Learning analytics methods and tutorials: A practical guide using R* (pp. 321–354). Springer.
#
# ## Methodology
#
# 1. **Data Preparation**: Load and clean event logs from the LMS
# 2. **Session Detection**: Identify learning sessions using inactivity thresholds
# 3. **Sequence Construction**: Build action sequences per session
# 4. **Exploratory Visualization**: Examine action distributions and timelines
# 5. **Sequence Clustering**: Group similar learning behaviors using edit (Optimal Matching) distance

# %%
import pandas as pd
import numpy as np
import matplotlib as mpl
from tanat.dataset import access

# %% [markdown]
# ### Load the MOOC Events Dataset
#
# TanaT provides direct access to the MOOC dataset through its built-in data access interface.

# %%
# Load MOOC events dataset
df = access("mooc_events")
df.head()

# %% [markdown]
# ### Dataset Description
#
# The dataset contains learner interactions with the following attributes:
#
# | Column | Description |
# |--------|-------------|
# | user | Unique learner identifier |
# | timecreated | Timestamp of the event |
# | Event.context | Course name |
# | Component | Activity type in the course |
# | Event.name | Description of the action performed |
# | Log | Textual log description |
# | Action | Type of action (simplified category) |
#
# For this analysis, we focus on the `Action` feature to characterize learner behavior.

# %% [markdown]
# ### Simplify the Alphabet
#
# Following Saqr et al., we consolidate similar quiz-related events into a single category to reduce vocabulary complexity.

# %%
# Consolidate quiz-related events
quiz_events = {
    "Quiz attempt viewed": "Quiz attempt",
    "Quiz attempt reviewed": "Quiz attempt",
    "Quiz attempt started": "Quiz attempt",
    "Quiz attempt summary viewed": "Quiz attempt",
    "Quiz attempt submitted": "Quiz attempt",
}
df["Event.name"] = df["Event.name"].replace(quiz_events)

# %% [markdown]
# ## 2. Session Detection
#
# ### Define Sessions from Inactivity Threshold
#
# In this dataset, the statistical unit is not a user but a **learning session**. A session is defined as a period of continuous activity, detected by identifying gaps of inactivity.
#
# Following Saqr et al., we use a 2-hour inactivity threshold to split user logs into distinct sessions. This choice yields fewer but longer sequences compared to the original 15-minute threshold.

# %%
# Define inactivity threshold for session detection
INACTIVITY_THRESHOLD = pd.Timedelta("2h")

# Detect sessions: new session when user changes OR time gap exceeds threshold
df = df.sort_values(["user", "timecreated"])
df.timecreated = pd.to_datetime(df.timecreated)
df["session"] = (
    (df["user"] != df["user"].shift())
    | (df["timecreated"].diff() > INACTIVITY_THRESHOLD)
).cumsum()

print(f"Detected {df['session'].nunique()} sessions from {df['user'].nunique()} users")
df.head()

# %%
# Keep session-to-user mapping for later analysis
sessions = df[["user", "session"]].drop_duplicates()
sessions.head()

# %% [markdown]
# ### Create Sequential Index
#
# For sequence analysis focusing on event order (rather than timestamps), we add a position index within each session.


# %%
# Add position index within each session
def add_position_index(group):
    group = group.copy()
    group["index"] = range(len(group))
    return group


df_indexed = (
    df.groupby("session", group_keys=True)
    .apply(add_position_index, include_groups=False)
    .reset_index(drop=False)
)
df_indexed.head()

# %% [markdown]
# ## 3. Sequence Construction with TanaT
#
# ### Define the Sequence Type and Statistical Unit
#
# In sequence analysis, the **actor** (statistical individual) determines what constitutes a sequence. Here, each learning session becomes a sequence, with the student as a static characteristic of that session.
# We use **state sequences** to match the TraMineR data model from the original publication, where each position represents a discrete action state.
# %%
from tanat.sequence import StateSequencePool, StateSequenceSettings

# Configure sequence settings
settings = StateSequenceSettings(
    id_column="session",  # Session as statistical unit
    start_column="index",  # Use position index as time
    entity_features=["Action", "Event.context", "Event.name"],
    static_features=["user"],  # Link sessions to users
)

# Create sequence pool
moocpool = StateSequencePool(
    sequence_data=df_indexed,
    static_data=sessions,
    settings=settings,
)
moocpool

# %% [markdown]
# **Pool Summary:**
# - **5,700 sequences** with lengths ranging from 2 to 153 (mean: 16.8)
# - **Vocabulary size: 246** unique entity combinations
# - Entity features automatically inferred as categorical

# %% [markdown]
# ## 4. Exploratory Data Visualization
#
# ### Pool Statistics

# %%
# Overview statistics
moocpool.statistics

# %%
# Aggregated descriptive statistics
moocpool.describe(dropna=True, by_id=False)

# %%
# Sequence length distribution
lengths = moocpool.describe(dropna=True, by_id=True)["length"]
lengths.plot.box(figsize=(8, 3), vert=False).set_title("Sequence Length Distribution")

# %% [markdown]
# ### Filter Sequences by Length
#
# The length distribution shows that 90% of sequences have fewer than 40 events. We filter out very short sessions (single event) and very long outliers.

# %%
from tanat.criterion import LengthCriterion

# Keep sequences with 2-40 events
moocpool_filtered = moocpool.filter(LengthCriterion(gt=1, le=40), level="sequence")
moocpool_filtered

# %% [markdown]
# ### Visualize Action Distribution
#
# For interpretability, we focus on the `Action` feature, reducing the vocabulary from 246 to 12 action types.
#
# To ensure consistent colors across all visualizations, we define a color palette mapping each action to a specific color.

# %%
# Get action vocabulary and create a consistent color palette
actions = list(moocpool_filtered.get_vocabulary("Action"))
colors = mpl.colormaps["tab20"].colors[: len(actions)]
ACTION_COLORS = dict(zip(actions, [mpl.colors.to_hex(c) for c in colors]))
print(f"Actions ({len(actions)}): {actions}")

# %%
from tanat.visualization.sequence import SequenceVisualizer

# %%
# fmt: off
SequenceVisualizer.histogram(show_as="occurrence", bar_order="descending") \
    .colors(ACTION_COLORS) \
    .title("Action Type Distribution") \
    .draw(moocpool_filtered, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ### Timeline Visualizations
#
# Timelines show the sequence of actions within learning sessions. We use `ACTION_COLORS` to maintain visual consistency across all plots.

# %%
# Timeline for 100 random sessions (flat stacking)
import random

random.seed(42)
sample_ids = random.sample(list(moocpool_filtered.unique_ids), 100)
sample_pool = moocpool_filtered.subset(sample_ids)

# fmt: off
SequenceVisualizer.timeline(stacking_mode="flat") \
    .colors(ACTION_COLORS) \
    .marker(spacing=1) \
    .title("100 Random Sessions") \
    .xlabel("Position in Session") \
    .draw(sample_pool, entity_features=["Action"])
# fmt: on

# %%
# Timeline for a single session (session N°5)
# fmt: off
single_session = moocpool_filtered[5]
SequenceVisualizer.timeline() \
    .colors(ACTION_COLORS) \
    .title("Single Session Timeline") \
    .xlabel("Position in Session") \
    .draw(single_session, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ### State Distribution Over Time
# 
# Distribution plots show how action proportions change across sequence positions.

# %%
# fmt: off
SequenceVisualizer.distribution() \
    .colors(ACTION_COLORS) \
    .title("Action Distribution Over Session Progress") \
    .xlabel("Position in Session") \
    .draw(moocpool_filtered, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ## 5. Alternative: Timestamp-Based Sequences
#
# In the previous analysis, we used sequential order only. Here we demonstrate how to use actual timestamps, creating event sequences with real temporal information.

# %%
from tanat.sequence import EventSequencePool, EventSequenceSettings

# Configure with actual timestamps
settings = EventSequenceSettings(
    id_column="session",
    time_column="timecreated",
    entity_features=["Action", "Event.context", "Event.name"],
    static_features=["user"],
)

# Create event sequence pool
moocpool_timed = EventSequencePool(
    sequence_data=df,
    static_data=sessions,
    settings=settings,
)
moocpool_timed.granularity = "minute"
moocpool_timed

# %% [markdown]
# ### Timeline with Real Timestamps
#
# The same session now shows actual temporal spacing between events.

# %%
# Timeline for 100 random sessions (by category stacking)
import random

random.seed(42)
sample_ids = random.sample(list(moocpool_timed.unique_ids), 100)
sample_pool = moocpool_timed.subset(sample_ids)

# fmt: off
SequenceVisualizer.timeline(stacking_mode="by_category") \
    .colors(ACTION_COLORS) \
    .marker(spacing=1) \
    .title("100 Random Sessions") \
    .xlabel("Absolute time") \
    .draw(sample_pool, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ## 6. Sequence Clustering with Optimal Matching
#
# ### Define Custom Substitution Costs
#
# Following Saqr et al., we use Optimal Matching (OM) with manually defined costs between action types. These costs reflect the semantic similarity between different learner actions.

# %%
# Action vocabulary for reference
moocpool_timed.get_vocabulary("Action")

# %%
# Substitution costs from Saqr et al. (2024)
# Higher values = more dissimilar action types
# fmt: off
cost = {
    ("Applications", "Applications"): 0, ("Applications", "Assignment"): 1.939,
    ("Applications", "Course_view"): 1.868, ("Applications", "Ethics"): 1.966,
    ("Applications", "Feedback"): 1.988, ("Applications", "General"): 1.749,
    ("Applications", "Group_work"): 1.946, ("Applications", "Instructions"): 1.985,
    ("Applications", "La_types"): 1.982, ("Applications", "Practicals"): 1.956,
    ("Applications", "Social"): 2.0, ("Applications", "Theory"): 1.994,
    ("Assignment", "Applications"): 1.939, ("Assignment", "Assignment"): 0,
    ("Assignment", "Course_view"): 1.75, ("Assignment", "Ethics"): 1.996,
    ("Assignment", "Feedback"): 1.970, ("Assignment", "General"): 1.936,
    ("Assignment", "Group_work"): 1.961, ("Assignment", "Instructions"): 1.960,
    ("Assignment", "La_types"): 1.922, ("Assignment", "Practicals"): 1.962,
    ("Assignment", "Social"): 1.993, ("Assignment", "Theory"): 1.982,
    ("Course_view", "Applications"): 1.868, ("Course_view", "Assignment"): 1.750,
    ("Course_view", "Course_view"): 0, ("Course_view", "Ethics"): 1.879,
    ("Course_view", "Feedback"): 1.743, ("Course_view", "General"): 1.801,
    ("Course_view", "Group_work"): 1.524, ("Course_view", "Instructions"): 1.564,
    ("Course_view", "La_types"): 1.749, ("Course_view", "Practicals"): 1.750,
    ("Course_view", "Social"): 1.735, ("Course_view", "Theory"): 1.854,
    ("Ethics", "Applications"): 1.966, ("Ethics", "Assignment"): 1.996,
    ("Ethics", "Course_view"): 1.879, ("Ethics", "Ethics"): 0,
    ("Ethics", "Feedback"): 1.991, ("Ethics", "General"): 1.950,
    ("Ethics", "Group_work"): 1.907, ("Ethics", "Instructions"): 1.991,
    ("Ethics", "La_types"): 1.940, ("Ethics", "Practicals"): 1.945,
    ("Ethics", "Social"): 1.988, ("Ethics", "Theory"): 1.945,
    ("Feedback", "Applications"): 1.988, ("Feedback", "Assignment"): 1.970,
    ("Feedback", "Course_view"): 1.743, ("Feedback", "Ethics"): 1.991,
    ("Feedback", "Feedback"): 0, ("Feedback", "General"): 1.992,
    ("Feedback", "Group_work"): 1.879, ("Feedback", "Instructions"): 1.926,
    ("Feedback", "La_types"): 1.990, ("Feedback", "Practicals"): 1.978,
    ("Feedback", "Social"): 1.999, ("Feedback", "Theory"): 1.945,
    ("General", "Applications"): 1.749, ("General", "Assignment"): 1.936,
    ("General", "Course_view"): 1.801, ("General", "Ethics"): 1.950,
    ("General", "Feedback"): 1.992, ("General", "General"): 0.0,
    ("General", "Group_work"): 1.936, ("General", "Instructions"): 1.909,
    ("General", "La_types"): 1.842, ("General", "Practicals"): 1.961,
    ("General", "Social"): 1.985, ("General", "Theory"): 1.947,
    ("Group_work", "Applications"): 1.946, ("Group_work", "Assignment"): 1.961,
    ("Group_work", "Course_view"): 1.524, ("Group_work", "Ethics"): 1.907,
    ("Group_work", "Feedback"): 1.879, ("Group_work", "General"): 1.936,
    ("Group_work", "Group_work"): 0, ("Group_work", "Instructions"): 1.862,
    ("Group_work", "La_types"): 1.924, ("Group_work", "Practicals"): 1.956,
    ("Group_work", "Social"): 1.873, ("Group_work", "Theory"): 1.938,
    ("Instructions", "Applications"): 1.985, ("Instructions", "Assignment"): 1.960,
    ("Instructions", "Course_view"): 1.564, ("Instructions", "Ethics"): 1.991,
    ("Instructions", "Feedback"): 1.926, ("Instructions", "General"): 1.909,
    ("Instructions", "Group_work"): 1.862, ("Instructions", "Instructions"): 0.0,
    ("Instructions", "La_types"): 1.931, ("Instructions", "Practicals"): 1.954,
    ("Instructions", "Social"): 1.850, ("Instructions", "Theory"): 1.983,
    ("La_types", "Applications"): 1.982, ("La_types", "Assignment"): 1.922,
    ("La_types", "Course_view"): 1.749, ("La_types", "Ethics"): 1.940,
    ("La_types", "Feedback"): 1.990, ("La_types", "General"): 1.842,
    ("La_types", "Group_work"): 1.924, ("La_types", "Instructions"): 1.931,
    ("La_types", "La_types"): 0, ("La_types", "Practicals"): 1.964,
    ("La_types", "Social"): 1.981, ("La_types", "Theory"): 1.907,
    ("Practicals", "Applications"): 1.965, ("Practicals", "Assignment"): 1.962,
    ("Practicals", "Course_view"): 1.750, ("Practicals", "Ethics"): 1.945,
    ("Practicals", "Feedback"): 1.978, ("Practicals", "General"): 1.961,
    ("Practicals", "Group_work"): 1.956, ("Practicals", "Instructions"): 1.954,
    ("Practicals", "La_types"): 1.964, ("Practicals", "Practicals"): 0,
    ("Practicals", "Social"): 1.978, ("Practicals", "Theory"): 1.948,
    ("Social", "Applications"): 2.0, ("Social", "Assignment"): 1.993,
    ("Social", "Course_view"): 1.735, ("Social", "Ethics"): 1.988,
    ("Social", "Feedback"): 1.999, ("Social", "General"): 1.985,
    ("Social", "Group_work"): 1.873, ("Social", "Instructions"): 1.850,
    ("Social", "La_types"): 1.981, ("Social", "Practicals"): 1.978,
    ("Social", "Social"): 0, ("Social", "Theory"): 1.994,
    ("Theory", "Applications"): 1.994, ("Theory", "Assignment"): 1.982,
    ("Theory", "Course_view"): 1.854, ("Theory", "Ethics"): 1.945,
    ("Theory", "Feedback"): 1.996, ("Theory", "General"): 1.947,
    ("Theory", "Group_work"): 1.938, ("Theory", "Instructions"): 1.983,
    ("Theory", "La_types"): 1.907, ("Theory", "Practicals"): 1.948,
    ("Theory", "Social"): 1.994, ("Theory", "Theory"): 0.0,
}
# fmt: on

# %% [markdown]
# ### Configure TanaT Metrics
#
# We combine:
# 1. **Hamming entity metric** with custom costs for comparing individual actions
# 2. **Edit distance** (Optimal Matching) for comparing entire sequences

# %%
from tanat.metric.entity import HammingEntityMetric, HammingEntityMetricSettings
from tanat.metric.sequence import EditSequenceMetric, EditSequenceMetricSettings

# %%
# Entity metric with custom substitution costs
entity_settings = HammingEntityMetricSettings(
    cost=cost,
    entity_features=["Action"],
    default_value=0.0,
)
entity_metric = HammingEntityMetric(settings=entity_settings)

# Sequence metric: Edit distance (Optimal Matching)
sequence_settings = EditSequenceMetricSettings(entity_metric=entity_metric)
sequence_metric = EditSequenceMetric(settings=sequence_settings)

# %%
# Test metric on two sequences
sequence_metric(moocpool_timed[1], moocpool_timed[2])

# %% [markdown]
# ### Apply Hierarchical Clustering
#
# We use hierarchical clustering to group sessions with similar action patterns. The number of clusters (15) follows the original study setup.

# %%
from tanat.clustering import HierarchicalClusterer, HierarchicalClustererSettings

# Configure clustering
cluster_settings = HierarchicalClustererSettings(
    metric=sequence_metric,
    n_clusters=15,
    cluster_column="cluster",
)

# Fit clustering model
clusterer = HierarchicalClusterer(settings=cluster_settings)
clusterer.fit(moocpool_timed)

# %% [markdown]
# ## 7. Cluster Visualization
#
# We now visualize the clusters identified in the previous step. We focus on the 6 largest clusters and reuse `ACTION_COLORS` for consistency.

# %%
# Get the 6 largest clusters
largest_clusters = moocpool_timed.static_data.cluster.value_counts().head(6)
top_6_clusters = largest_clusters.index.tolist()

# %%
from tanat.criterion import StaticCriterion

# Filter to top 6 clusters
moocpool_top6 = moocpool_timed.filter(
    StaticCriterion(query=f"cluster in {top_6_clusters}"),
    level="sequence",
)

# %% [markdown]
# ### Timeline by Cluster
#
# We sample 30 sessions per cluster and align events to the session start using `zero_from_position(0)`.

# %%
N_IDS_PER_CLUSTER = 30

# Sample 30 sequences per cluster
static_df = moocpool_top6.static_data
sampled_ids = []
for cluster_id, group in static_df.groupby("cluster", observed=True):
    n = min(N_IDS_PER_CLUSTER, len(group))
    sampled_ids.extend(group.sample(n=n, random_state=42).index.tolist())

subset_timeline = moocpool_top6.subset(sampled_ids)
subset_timeline.zero_from_position(0)  # Default behavior, explicitly written
print(
    f"Sampled {len(sampled_ids)} sessions across {len(top_6_clusters)} clusters (6x{N_IDS_PER_CLUSTER})"
)

# %%
# fmt: off
SequenceVisualizer.timeline(stacking_mode="flat", relative_time=True) \
    .colors(ACTION_COLORS) \
    .marker(spacing=0.5) \
    .x_axis(autofmt_xdate=False) \
    .facet(by="cluster", cols=3, share_x=False, title_template="Cluster {value}") \
    .title("Session Timelines by Cluster") \
    .xlabel("Relative time (minutes)") \
    .draw(subset_timeline, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ### Distribution by Cluster
#
# Converting to state sequences allows us to visualize aggregated action proportions over time within each cluster.

# %%
# Convert to state sequences for distribution visualization
moocpool_state = moocpool_top6.as_state()
moocpool_state.zero_from_position(0)  # Default behavior, explicitly written

# fmt: off
SequenceVisualizer.distribution(relative_time=True) \
    .colors(ACTION_COLORS) \
    .facet(by="cluster", cols=3, share_x=False, title_template="Cluster {value}") \
    .legend(title="Action") \
    .xlabel("Relative time (minutes)") \
    .title("Session Distribution by Cluster") \
    .draw(moocpool_state, entity_features=["Action"])
# fmt: on

# %% [markdown]
# ## Conclusion
#
# This tutorial demonstrated the correspondence between TanaT and TraMineR by reproducing a learning analytics study originally conducted with TraMineR. TanaT's flexibility allowed us to work with both sequential order and real timestamps, providing richer temporal information than traditional approaches. By implementing edit distance with domain-specific substitution costs, we captured the semantic similarity between different learner actions. The faceted visualization capabilities enabled easy comparison of behavioral patterns across the 15 identified clusters. While our analysis uses actual timestamps rather than just event order, which may explain some differences from the original study, the methodology successfully demonstrates how TanaT can replicate and extend sophisticated sequence analysis workflows from educational research.
