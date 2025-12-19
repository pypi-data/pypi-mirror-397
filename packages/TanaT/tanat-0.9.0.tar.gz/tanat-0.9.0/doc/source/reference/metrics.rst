.. _metrics_reference:

=================
Metrics Reference
=================

Reference documentation for TanaT's distance metrics system for temporal sequence analysis.

Overview
========

TanaT uses a **hierarchical metric composition** approach with three levels:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Level
     - Description
     - Use Case
   * - **EntityMetric**
     - Compares individual entities (single time point observations)
     - Define how to compare two entities
   * - **SequenceMetric**
     - Compares entire sequences (uses EntityMetric for element-wise comparison)
     - Compare patient care pathways
   * - **TrajectoryMetric**
     - Compares multi-sequence trajectories (aggregates sequence distances)
     - Compare complete patient records

Metric Composition
------------------

Most sequence metrics follow this pattern:

.. code-block:: python

   from tanat.metric.sequence import DTWSequenceMetric
   from tanat.metric.entity import HammingEntityMetric
   
   # EntityMetric defines how to compare individual entities
   entity_metric = HammingEntityMetric(
       settings={"entity_features": ["state", "medication"]}
   )
   
   # SequenceMetric uses EntityMetric for element-wise comparison
   dtw = DTWSequenceMetric(
       settings={"entity_metric": entity_metric}
   )
   
   # Compute distance between two sequences
   distance = dtw(sequence_a, sequence_b)

**Simplified syntax** (uses defaults):

.. code-block:: python

   # Uses "hamming" entity metric by default
   dtw = DTWSequenceMetric()
   distance = dtw(sequence_a, sequence_b)

----

==============
Entity Metrics
==============

Entity metrics compare **individual entities** (observations at a single time point).
They are the building blocks used by sequence metrics for element-wise comparisons.

.. tip:: **Need a custom entity metric?**
   See :doc:`/user-guide/auto_examples/03_entity_metric/02_custom` for a step-by-step guide.

.. _hamming-entity-metric:

.. topic:: HammingEntityMetric

   The default entity metric. Compares entities by checking equality.

   → :doc:`Full example </user-guide/auto_examples/03_entity_metric/01_hamming>`

   .. code-block:: python

      from tanat.metric.entity import HammingEntityMetric

   **Settings:**

   - ``entity_features`` *(List[str], default: None)*: Feature names to compare. If None, uses all available entity features.
   - ``cost`` *(Dict / Loader, default: None)*: Custom substitution costs between value pairs. If None, uses 0/1 (equal/different).
   - ``default_value`` *(float, default: 0.0)*: Cost for undefined pairs when using custom cost dict.

   HammingEntityMetric only supports categorical features for single-feature comparisons.
   For multiple features, each entity tuple becomes a composite category (so numerical features are acceptable as part of a composite).

   **Example:**

   .. code-block:: python

      hamming = HammingEntityMetric(
          settings={"entity_features": ["state", "medication"]}
      )
      distance = hamming(entity_a, entity_b)

----

================
Sequence Metrics
================

Sequence metrics compare **entire sequences** by considering the order and timing of entities.
Most sequence metrics use an EntityMetric internally for element-wise comparisons.

.. tip:: **Need a custom sequence metric?**
   See :doc:`/user-guide/auto_examples/04_sequence_metric/07_custom` for a step-by-step guide.

----

.. _dtw-sequence-metric:

.. topic:: DTWSequenceMetric

   Dynamic Time Warping. Finds optimal alignment allowing time stretching/compression.

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/01_dtw>`

   .. code-block:: python

      from tanat.metric.sequence import DTWSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for comparing entities.
   - ``window`` *(int, default: None)*: Sakoe-Chiba band width. None = no constraint.
   - ``max_time_diff`` *(timedelta / int, default: None)*: Maximum time difference between compared events.
   - ``normalize`` *(bool, default: False)*: If True, normalize by warping path length.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      dtw = DTWSequenceMetric(settings={"window": 10, "normalize": True})
      distance = dtw(seq_a, seq_b)

----

.. _softdtw-sequence-metric:

.. topic:: SoftDTWSequenceMetric

   Differentiable version of DTW.

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/06_softdtw>`

   .. code-block:: python

      from tanat.metric.sequence import SoftDTWSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for comparing entities.
   - ``gamma`` *(float, default: 1.0)*: Smoothing parameter. Lower values → closer to standard DTW.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      soft_dtw = SoftDTWSequenceMetric(settings={"gamma": 0.1})
      distance = soft_dtw(seq_a, seq_b)

----

.. _edit-sequence-metric:

.. topic:: EditSequenceMetric

   Edit distance. Counts minimum insertions, deletions, substitutions.

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/02_edit>`

   .. code-block:: python

      from tanat.metric.sequence import EditSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for substitution cost.
   - ``indel_cost`` *(float, default: 1.0)*: Cost for insertion/deletion operations.
   - ``normalize`` *(bool, default: False)*: If True, normalize by maximum sequence length.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      edit = EditSequenceMetric(settings={"indel_cost": 1.0, "normalize": True})
      distance = edit(seq_a, seq_b)

----

.. _lcs-sequence-metric:

.. topic:: LCSSequenceMetric

   Longest Common Subsequence. Similarity based on common elements (order matters).

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/04_lcs>`

   .. code-block:: python

      from tanat.metric.sequence import LCSSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for comparing entities.
   - ``equality_threshold`` *(float, default: 0.0)*: Maximum distance to consider entities as equal.
   - ``as_distance`` *(bool, default: False)*: If True, returns distance instead of LCS length.
   - ``normalize`` *(bool, default: False)*: If True, uses normalized distance formula.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      lcs = LCSSequenceMetric(settings={"as_distance": True, "normalize": True})
      similarity = lcs(seq_a, seq_b)

----

.. _lcp-sequence-metric:

.. topic:: LCPSequenceMetric

   Longest Common Prefix. Similarity based on matching prefix from the start.

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/03_lcp>`

   .. code-block:: python

      from tanat.metric.sequence import LCPSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for comparing entities.
   - ``equality_threshold`` *(float, default: 0.0)*: Maximum distance to consider entities as equal.
   - ``as_distance`` *(bool, default: False)*: If True, returns distance instead of LCP length.
   - ``normalize`` *(bool, default: False)*: If True, uses normalized distance formula.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      lcp = LCPSequenceMetric(settings={"as_distance": True})
      similarity = lcp(seq_a, seq_b)

----

.. _linearpairwise-sequence-metric:

.. topic:: LinearPairwiseSequenceMetric

   Simple pairwise comparison. Compares sequences element by element.

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/05_linear_pairwise>`

   .. code-block:: python

      from tanat.metric.sequence import LinearPairwiseSequenceMetric

   **Settings:**

   - ``entity_metric`` *(str / EntityMetric, default: "hamming")*: Metric for comparing entities.
   - ``agg_fun`` *(str, default: "mean")*: Aggregation function: "mean", "sum".
   - ``padding_penalty`` *(float, default: 0.0)*: Penalty for length difference.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      linear = LinearPairwiseSequenceMetric(settings={"agg_fun": "sum"})
      distance = linear(seq_a, seq_b)

----

.. _chi2-sequence-metric:

.. topic:: Chi2SequenceMetric

   Chi-squared distance. Compares time spent in each state (ignores temporal order).

   → :doc:`Full example </user-guide/auto_examples/04_sequence_metric/08_chi2>`

   .. code-block:: python

      from tanat.metric.sequence import Chi2SequenceMetric

   **Settings:**

   - ``entity_features`` *(List[str], default: None)*: Feature(s) defining categories.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   Chi2 does **not** use an ``entity_metric``. It computes state distributions directly.

   **Duration:** EventSequence counts events; StateSequence uses actual durations.

   **Example:**

   .. code-block:: python

      chi2 = Chi2SequenceMetric(settings={"entity_features": ["state"]})
      distance = chi2(seq_a, seq_b)

----

Computing Distance Matrices
===========================

All metrics support computing pairwise distance matrices for pools:

.. code-block:: python

   from tanat.metric.sequence import DTWSequenceMetric
   
   dtw = DTWSequenceMetric()
   dm = dtw.compute_matrix(sequence_pool)
   
   print(dm.shape)  # (n_sequences, n_sequences)
   print(dm.to_dataframe())

**With disk caching** (for large pools):

.. code-block:: python

   from tanat.metric.matrix import MatrixStorageOptions
   
   dtw = DTWSequenceMetric(settings={
       "distance_matrix": MatrixStorageOptions(
           store_path="./cache/dtw_matrix",
           resume=True
       )
   })
   dm = dtw.compute_matrix(large_pool)

----

===================
Trajectory Metrics
===================

Trajectory metrics compare **multi-sequence trajectories** by aggregating distances
across multiple sequence types.

.. tip:: **Need a custom trajectory metric?**
   See :doc:`/user-guide/auto_examples/05_trajectory_metric/09_custom` for a step-by-step guide.

----

.. _aggregation-trajectory-metric:

.. topic:: AggregationTrajectoryMetric

   Aggregates sequence-level distances across multiple sequence types.

   → :doc:`Full example </user-guide/auto_examples/05_trajectory_metric/01_aggregation>`

   .. code-block:: python

      from tanat.metric.trajectory import AggregationTrajectoryMetric

   **Settings:**

   - ``default_metric`` *(str / SequenceMetric, default: "linearpairwise")*: Default metric for unlisted sequences.
   - ``sequence_metrics`` *(Dict[str, SequenceMetric], default: None)*: Metric per sequence type.
   - ``agg_fun`` *(str, default: "mean")*: How to combine sequence distances.
   - ``weights`` *(Dict[str, float], default: None)*: Weights per sequence type.
   - ``distance_matrix`` *(MatrixStorageOptions)*: Options for disk storage and resume support.

   **Example:**

   .. code-block:: python

      from tanat.metric.trajectory import AggregationTrajectoryMetric
      from tanat.metric.sequence import DTWSequenceMetric
      
      traj_metric = AggregationTrajectoryMetric(settings={
          "sequence_metrics": {"diagnoses": DTWSequenceMetric()},
          "weights": {"diagnoses": 2.0}
      })
      distance = traj_metric(traj_a, traj_b)

----

See Also
========

* :doc:`manipulation` - Data manipulation reference
* :doc:`criterion` - Filtering criteria

API Reference
=============

* :py:mod:`tanat.metric.entity` - Entity metrics
* :py:mod:`tanat.metric.sequence` - Sequence metrics
* :py:mod:`tanat.metric.trajectory` - Trajectory metrics
