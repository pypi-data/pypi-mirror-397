.. _criterion_reference:

========================
Data Filtering Criterion
========================

Reference documentation for TanaT's criterion system for filtering and selecting temporal data.

Overview
========

Criterion provide a flexible and composable system for filtering sequences, trajectories, and their entities.
They enable:

* **Cohort selection**: Extract patient subgroups based on clinical criteria
* **Data cleaning**: Remove invalid or incomplete records
* **Pattern detection**: Find specific temporal patterns
* **Window extraction**: Select time-bounded data segments

All criterion support **method chaining** with filtering levels (entity/sequence/trajectory).

Filtering Levels
================

TanaT supports three hierarchical filtering levels:

**Entity-level**
   Filters individual records (events, states, intervals) within sequences.
   Preserves sequence structure but only includes matching entities.

**Sequence-level**
   Filters entire sequences based on whether they contain matching entities.
   Maintains complete sequence context (all entities kept or none).

**Trajectory-level**
   Filters trajectories based on whether they match the specified criteria.
   Available only for TrajectoryPool operations.

.. note::
   - Not all criterion support all filtering levels. See compatibility table below.
   - Entity-level filters are not allowed for StateSequence (will break the continuous nature of states).

Criterion Types
===============

.. _query-criterion:

.. topic:: QueryCriterion

   Pandas-style query filtering on entity attributes.

   → :doc:`Full example </user-guide/auto_examples/02_criterion/01_query>`

   .. code-block:: python

      from tanat.criterion import QueryCriterion

   **Attributes:**

   - ``query`` *(str)*: Pandas query expression (uses ``DataFrame.query()`` syntax).

   **Filtering Levels:** Entity ✓ | Sequence ✓ | Trajectory (via sequence)

   **Examples:**

   .. code-block:: python

      # Simple equality
      criterion = QueryCriterion(query="visit_type == 'EMERGENCY'")
      
      # Numeric comparison
      criterion = QueryCriterion(query="age > 65")
      
      # Multiple conditions
      criterion = QueryCriterion(query="age > 65 and chronic_condition == True")
      
      # Using 'in' operator
      criterion = QueryCriterion(query="visit_type in ['SPECIALIST', 'EMERGENCY']")

----

.. _pattern-criterion:

.. topic:: PatternCriterion

   Sequential pattern matching on entity values.

   → :doc:`Full example </user-guide/auto_examples/02_criterion/04_pattern>`

   .. code-block:: python

      from tanat.criterion import PatternCriterion

   **Attributes:**

   - ``pattern`` *(Dict[str, str | List[str]])*: Feature names to values or sequences.
   - ``contains`` *(bool, default: False)*: If True, pattern can occur anywhere.
   - ``case_sensitive`` *(bool, default: True)*: If False, ignore case in matching.
   - ``operator`` *(str, default: "and")*: Combine multiple patterns ("and" or "or").

   **Filtering Levels:** Entity ✓ | Sequence ✓ | Trajectory (via sequence)

   **Examples:**

   .. code-block:: python

      # Sequential pattern (ordered)
      criterion = PatternCriterion(
          pattern={"health_state": ["SICK", "TREATMENT", "RECOVERY"]},
          contains=True 
      )
      filtered = pool.filter(criterion, level="sequence")
      
      # Regex pattern
      criterion = PatternCriterion(
          pattern={"visit_type": ["regex:^S", "LABORATORY"]},
          contains=True
      )

----

.. _time-criterion:

.. topic:: TimeCriterion

   Time window filtering on temporal boundaries.

   → :doc:`Full example </user-guide/auto_examples/02_criterion/03_time>`

   .. code-block:: python

      from tanat.criterion import TimeCriterion

   **Attributes:**

   - ``start_after`` *(datetime | int, default: None)*: Minimum start time.
   - ``start_before`` *(datetime | int, default: None)*: Maximum start time.
   - ``end_after`` *(datetime | int, default: None)*: Minimum end time.
   - ``end_before`` *(datetime | int, default: None)*: Maximum end time.
   - ``duration_within`` *(bool, default: False)*: Entity must be entirely within bounds.
   - ``sequence_within`` *(bool, default: False)*: Entire sequence must be within bounds.

   **Filtering Levels:** Entity ✓ | Sequence ✓ | Trajectory (via sequence)

   **Examples:**

   .. code-block:: python

      from datetime import datetime, timedelta
      
      # Recent time window (last 3 months)
      recent_start = datetime.now() - timedelta(days=90)
      criterion = TimeCriterion(start_after=recent_start, end_before=datetime.now())
      filtered = pool.filter(criterion, level="entity")
      
      # Entire sequence must be within window
      criterion = TimeCriterion(
          start_after=datetime(2024, 1, 1),
          end_before=datetime(2024, 12, 31),
          sequence_within=True
      )

----

.. _length-criterion:

.. topic:: LengthCriterion

   Sequence length filtering based on entity count.

   → :doc:`Full example </user-guide/auto_examples/02_criterion/05_length>`

   .. code-block:: python

      from tanat.criterion import LengthCriterion

   **Attributes:**

   - ``eq`` *(int, default: None)*: Equal to length.
   - ``ne`` *(int, default: None)*: Not equal to length.
   - ``gt`` *(int, default: None)*: Greater than length.
   - ``ge`` *(int, default: None)*: Greater than or equal to length.
   - ``lt`` *(int, default: None)*: Less than length.
   - ``le`` *(int, default: None)*: Less than or equal to length.

   **Filtering Levels:** Sequence ✓ | Trajectory (via sequence)

   **Examples:**

   .. code-block:: python

      # Sequences with at least 5 entities
      criterion = LengthCriterion(ge=5)
      filtered = pool.filter(criterion)
      
      # Sequences with exactly 10 entities
      criterion = LengthCriterion(eq=10)

----

.. _static-criterion:

.. topic:: StaticCriterion

   Filtering based on static (non-temporal) features.

   → :doc:`Full example </user-guide/auto_examples/02_criterion/02_static>`

   .. code-block:: python

      from tanat.criterion import StaticCriterion

   **Attributes:**

   - ``query`` *(str)*: Pandas query expression on static data (same syntax as QueryCriterion).

   **Filtering Levels:** Sequence ✓ | Trajectory ✓

   **Examples:**

   .. code-block:: python

      # Demographic filtering
      criterion = StaticCriterion(query="age > 65")
      filtered = pool.filter(criterion)
      
      # Multiple static conditions
      criterion = StaticCriterion(query="age > 65 and chronic_condition == True")

----

Applying Criterion
==================

All criterion use the ``filter()`` method on pools.

Basic Filtering
---------------

.. code-block:: python

    # Entity-level filtering
    filtered_pool = pool.filter(criterion, level="entity")
    
    # Sequence-level filtering
    filtered_pool = pool.filter(criterion, level="sequence")
    
    # Default level (typically sequence)
    filtered_pool = pool.filter(criterion)

Identifying Matches
-------------------

Use ``which()`` to get IDs of matching sequences without filtering.

.. code-block:: python

    # Get sequence IDs matching criterion
    matching_ids = pool.which(criterion)
    
    # Type: set of sequence IDs
    print(type(matching_ids))  # <class 'set'>
    
    # Use for set operations
    cohort_a = pool.which(criterion_a)
    cohort_b = pool.which(criterion_b)
    intersection = cohort_a.intersection(cohort_b)

Advanced Filtering
==================

Combining Multiple Criterion
-----------------------------

Use sequential filtering or set operations.

**Sequential approach:**

.. code-block:: python

    # Apply filters in sequence
    pool_filtered = (
        pool
        .filter(StaticCriterion(query="age > 65"))
        .filter(QueryCriterion(query="visit_type == 'EMERGENCY'"), level="sequence")
        .filter(LengthCriterion(gt=5))
    )

**Set-based approach:**

.. code-block:: python

    # Get IDs for each criterion
    elderly = pool.which(StaticCriterion(query="age > 65"))
    with_emergency = pool.which(
        QueryCriterion(query="visit_type == 'EMERGENCY'")
    )
    sufficient_data = pool.which(LengthCriterion(gt=5))
    
    # Combine with set operations
    final_cohort = elderly.intersection(with_emergency).intersection(sufficient_data)
    
    # Create filtered pool
    filtered_pool = pool.subset(final_cohort)

Negation and Exclusion
-----------------------

Exclude sequences matching a criterion.

.. code-block:: python

    # Get all sequence IDs
    all_ids = set(pool.unique_ids)
    
    # Get IDs to exclude
    to_exclude = pool.which(criterion)
    
    # Get complement
    to_keep = all_ids - to_exclude
    
    # Create filtered pool
    filtered_pool = pool.subset(to_keep)

Conditional Filtering
---------------------

Apply different criterion based on conditions.

.. code-block:: python

    # Different criteria for different risk levels
    high_risk_pool = pool.filter(StaticCriterion(query="risk_level == 'HIGH'"))
    low_risk_pool = pool.filter(StaticCriterion(query="risk_level == 'LOW'"))
    
    # Apply risk-specific criteria
    high_risk_filtered = high_risk_pool.filter(LengthCriterion(gt=10))
    low_risk_filtered = low_risk_pool.filter(LengthCriterion(gt=5))

API Reference
=============

For complete API documentation, see:

* :py:class:`tanat.criterion.QueryCriterion` - Query-based filtering
* :py:class:`tanat.criterion.PatternCriterion` - Pattern matching
* :py:class:`tanat.criterion.TimeCriterion` - Time window filtering
* :py:class:`tanat.criterion.LengthCriterion` - Length-based filtering
* :py:class:`tanat.criterion.StaticCriterion` - Static feature filtering

See Also
========

* :doc:`/user-guide/tutorials/02-data_wrangling/data_wrangling_sequence` - Hands-on filtering examples
* :doc:`/getting-started/concepts` - Conceptual overview of filtering
* :doc:`alignment` - Temporal alignment after filtering
* :doc:`metadata` - Understanding feature types for queries
* :doc:`manipulation` -  Data manipulation methods 