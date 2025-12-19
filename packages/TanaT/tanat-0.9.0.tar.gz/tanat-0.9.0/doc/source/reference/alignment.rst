.. _alignment_reference:

===================
Temporal Alignment
===================

Reference documentation for TanaT's temporal alignment system (T0 management and transformations).

Overview
========

Temporal alignment enables synchronization of sequences by defining a common reference point (T0) for each sequence.
This is essential for:

* Comparative cohort analysis
* Event-aligned studies (e.g., all patients aligned to first hospitalization)
* Longitudinal pattern detection
* Time-to-event analysis

All sequences start with **absolute time** (datetime or timestep). After setting T0, you can transform to **relative time** or **relative rank**.

Setting Reference Dates (T0)
=============================

TanaT provides multiple methods to set reference dates based on different alignment strategies.

.. _zero-from-position:

.. topic:: zero_from_position()

   Set T0 based on entity position within each sequence.

   .. Note::
      This is the default alignment method when no other zeroing is applied (position = 0).

   .. code-block:: python

      pool.zero_from_position(position: int = 0) -> self

   **Attributes:**

   - ``position`` *(int)*: Zero-indexed position (default: 0 = first entity)

   **Example:**

   .. code-block:: python

      # Align to first entity (default behavior)
      pool.zero_from_position(position=0)
      
      # Align to third entity
      pool.zero_from_position(position=2)
      
      # Align to last entity (use negative indexing)
      pool.zero_from_position(position=-1)

   **Use cases:**

   - First entity alignment: All sequences start at T0 = 0
   - Fixed position analysis: Compare sequences from Nth event
   - Last entity alignment: Retrospective analysis from final event

----

.. _direct-t0-assignment:

.. topic:: Direct T0 Assignment

   Manually set reference dates using the ``t_zero`` property.

   .. code-block:: python

      pool.t_zero = {sequence_id: datetime, ...}

   **Example:**

   .. code-block:: python

      from datetime import datetime
      
      # Set custom T0 for specific sequences
      pool.t_zero = {
          "patient_001": datetime(2024, 1, 15),
          "patient_002": datetime(2024, 2, 10),
          "patient_003": datetime(2024, 1, 20)
      }

   **Use cases:**

   - External reference dates (e.g., birth date, diagnosis date from another dataset)
   - Study enrollment dates
   - Custom milestone dates

----

.. _zero-from-query:

.. topic:: zero_from_query()

   Set T0 based on the occurrence of specific entities matching a query.

   .. code-block:: python

      pool.zero_from_query(
          query: str,
          use_first: bool = True,
          anchor: str = "start/middle/end",
      ) -> self

   **Attributes:**

   - ``query`` *(str)*: Pandas-style query string to identify reference entities
   - ``use_first`` *(bool)*: If True, use first matching entity (default: True). If False, use last matching entity.
   - ``anchor`` *(str)*: Reference point within periods for time calculation. Options: "start", "middle", "end".

   **Example:**

   .. code-block:: python

      # Align to first emergency visit
      pool.zero_from_query(
          query="visit_type == 'EMERGENCY'",
          use_first=True
      )
      
      # Align to last treatment event
      pool.zero_from_query(
          query="status == 'TREATMENT'",
          use_last=True
      )
      
      # Complex query with multiple conditions
      pool.zero_from_query(
          query="age > 65 and diagnosis == 'DIABETES'"
      )

   .. note::
      Sequences without matching entities will have ``None`` as T0.

----

Temporal Transformations
========================

After setting T0, transform absolute time to relative representations.

.. _to-relative-time:

.. topic:: to_relative_time()

   Convert timestamps to relative time from T0.

   .. code-block:: python

      pool.to_relative_time(
          granularity: str = "day",
          drop_na: bool = False
      ) -> pd.DataFrame

   **Attributes:**

   - ``granularity`` *(str)*: Time unit for relative time

     - Datetime temporal: ``"year"``, ``"month"``, ``"week"``, ``"day"``, ``"hour"``, ``"minute"``, ``"second"``
     - Timestep temporal: ``"unit"`` (raw timestep difference)

   - ``drop_na`` *(bool)*: If True, remove entities without valid T0

   **Example:**

   .. code-block:: python

      # Convert to days from T0 - returns a DataFrame
      df_relative = pool.to_relative_time(granularity="day")
      print(df_relative)
      #              start  visit_type  diagnosis
      # sequence_id                              
      # patient_001   -4.0     ROUTINE          A
      # patient_001    0.0   EMERGENCY          B
      # patient_001    5.0    FOLLOWUP          A
      
      # Convert to hours, excluding sequences without T0
      df_hours = pool.to_relative_time(granularity="hour", drop_na=True)

   **Resulting time values:**

   - Negative values: Events before T0
   - Zero: Events at T0
   - Positive values: Events after T0

----

.. _to-relative-rank:

.. topic:: to_relative_rank()

   Convert to ordinal positions relative to T0.

   .. code-block:: python

      pool.to_relative_rank(drop_na: bool = False) -> pd.DataFrame

   **Attributes:**

   - ``drop_na`` *(bool)*: If True, remove entities without valid T0

   **Example:**

   .. code-block:: python

      # Convert to relative ranks - returns a DataFrame
      df_ranks = pool.to_relative_rank()
      print(df_ranks)
      #              start  visit_type  diagnosis
      # sequence_id                              
      # patient_001     -1     ROUTINE          A
      # patient_001      0   EMERGENCY          B
      # patient_001      1    FOLLOWUP          A
      
      # With missing T0 handling
      df_ranks = pool.to_relative_rank(drop_na=True)

   **Resulting rank values:**

   - Negative ranks: Entities before T0 (-1 = immediately before)
   - Zero: Entity at T0
   - Positive ranks: Entities after T0 (+1 = immediately after)

   **Use cases:**

   - Sequential pattern analysis regardless of time intervals
   - Comparing sequences with different temporal scales
   - Order-based analysis (1st event after T0, 2nd event after T0, etc.)

----

Workflow Examples
=================

.. topic:: Complete Alignment Workflow

   Typical workflow for temporal alignment and analysis.

   .. code-block:: python

      from tanat.sequence import EventSequencePool
      from tanat.criterion import TimeCriterion
      from tanat.visualization.sequence import SequenceVisualizer
      
      # 1. Set reference dates (T0 = first EMERGENCY visit)
      pool.zero_from_query(
          query="visit_type == 'EMERGENCY'",
          use_first=True
      )
      
      # 2. Transform to relative time (returns DataFrame)
      relative_data = pool.to_relative_time(granularity="day")
      
      # 3. Create new aligned pool from relative data
      aligned_pool = EventSequencePool(
          relative_data,
          settings={
              "id_column": "sequence_id",
              "time_column": "start",
              "entity_features": ["visit_type", "diagnosis"]
          }
      )
      
      # 4. Filter time window around T0 (on aligned pool)
      analysis_window = TimeCriterion(
          start_after=-30,  # 30 days before T0
          end_before=90     # 90 days after T0
      )
      filtered_pool = aligned_pool.filter(analysis_window, level="entity")
      
      # 5. Visualize aligned sequences
      SequenceVisualizer.timeline().draw(filtered_pool).show()

----

Accessing T0 Information
========================

.. topic:: Inspect T0 Values

   **Check T0 values:**

   .. code-block:: python

      # View T0 dictionary
      print(pool.t_zero)
      # Output: {'seq-001': Timestamp(...), 'seq-002': None, ...}

   **Convert to DataFrame:**

   .. code-block:: python

      import pandas as pd
      
      t0_df = pd.DataFrame.from_dict(
          pool.t_zero,
          orient="index",
          columns=["T0"]
      )
      t0_df.describe()

----

Zeroing Configuration
=====================

.. topic:: Available Zeroing Strategies

   Advanced configuration using the ``zeroing`` module (typically for internal use or custom implementations).

   The ``tanat.zeroing`` module provides three main strategies:

   - **QueryZeroingSetter**: Entity query-based (used by ``zero_from_query()``)
   - **PositionZeroingSetter**: Position-based (used by ``zero_from_position()``)
   - **DirectZeroingSetter**: Manual assignment (used by ``t_zero`` property)

   For most use cases, use the pool methods directly rather than instantiating setters manually.

----

API Reference
=============

For complete API documentation, see:

- :py:mod:`tanat.sequence` - Sequence and SequencePool classes
- :py:mod:`tanat.trajectory` - Trajectory and TrajectoryPool classes
- :py:mod:`tanat.zeroing` - Zeroing module (advanced usage)

See Also
========

- :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_sequence` - Hands-on alignment examples
- :doc:`/getting-started/concepts` - Conceptual overview of temporal alignment
- :doc:`criterion` - Filtering aligned sequences
- :doc:`metadata` - Temporal metadata configuration
