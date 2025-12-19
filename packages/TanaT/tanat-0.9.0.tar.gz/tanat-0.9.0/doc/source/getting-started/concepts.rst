.. _concepts_ref:

Core Concepts
=============

This page introduces the fundamental concepts of TanaT's data model.
Understanding these concepts is essential for using the library effectively.

----

Entities, Sequences, and Trajectories
-------------------------------------

TanaT distinguishes three levels of temporal data structures:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Level
     - Description
     - Example
   * - **Entity**
     - A single observation with temporal extent
     - A medical visit, a hospitalization
   * - **Sequence**
     - Collection of entities for one individual
     - All visits of patient P001
   * - **Trajectory**
     - Multiple sequences for one individual
     - Visits + hospitalizations + lab results for P001

Entity
~~~~~~

An **entity** is the atomic unit of temporal data. It has:

- **Features**: One or more descriptive attributes (categorical or numerical)
- **Temporal extent**: Either a single timestamp or a time interval

Sequence
~~~~~~~~

A **sequence** is a collection of entities for a single individual.
All entities in a sequence share the same type (events, intervals, or states)
and the same feature structure.

The diagram below shows a sequence with 4 event entities.
Note that two events can share the same timestamp (Event A and Event B on Nov 8).

.. mermaid::

   gantt
      dateFormat  YYYY-MM-DD
      axisFormat %d
      title Event Sequence Example

      Event A (1st) : milestone, A1, 2023-11-01, 0d
      Event A (2nd) : milestone, A2, 2023-11-08, 0d
      Event B       : milestone, B1, 2023-11-08, 0d
      Event C       : milestone, C1, 2023-11-23, 0d

Trajectory
~~~~~~~~~~

A **trajectory** combines multiple sequences of different types for the same individual.
It can also include **static features** (attributes not tied to time, like birth date or gender).

The diagram below shows a trajectory with three sequence types:

.. mermaid::

   gantt
      dateFormat  YYYY-MM-DD
      axisFormat %d
      title Trajectory Example

      section Visits
      Event A : milestone, A1, 2023-11-01, 0d
      Event A : milestone, A2, 2023-11-08, 0d
      Event B : milestone, B1, 2023-11-20, 0d

      section Hospitalizations
      Stay : I1, 2023-11-15, 2023-11-18

      section Lab Tests
      Test U : milestone, U1, 2023-11-09, 0d
      Test V : milestone, V1, 2023-11-13, 0d

----

Sequence Types
--------------

TanaT supports three types of temporal extent:

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Type
     - Temporal Extent
     - Constraints
   * - **Event**
     - Single timestamp (punctual)
     - None
   * - **Interval**
     - Start and end dates
     - Can overlap, gaps allowed
   * - **State**
     - Start and end dates
     - Contiguous, no overlap, no gaps

.. mermaid::

   gantt
      dateFormat  YYYY-MM-DD
      axisFormat %d
      title       Comparison of Sequence Types

      section Event
      Event A : milestone, A1, 2023-11-01, 0d
      Event A : milestone, A2, 2023-11-08, 0d
      Event B : milestone, B1, 2023-11-20, 0d

      section Interval
      Interval K : K1, 2023-11-04, 2023-11-09
      Interval J : J1, 2023-11-12, 2023-11-17
      Interval I : I1, 2023-11-15, 2023-11-19

      section State
      State U : U1, 2023-11-01, 2023-11-08
      State V : V1, 2023-11-08, 2023-11-12
      State W : W1, 2023-11-12, 2023-11-18
      State X : X1, 2023-11-18, 2023-11-22

**When to use each type:**

- **Event**: Point-in-time occurrences (visits, purchases, clicks)
- **Interval**: Duration-based events that can overlap (treatments, projects)
- **State**: Continuous states without gaps (disease stages, employment status)

----

Pools
-----

A **pool** is a collection of sequences or trajectories from multiple individuals.
All items in a pool share the same structure (same features, same temporal type).

.. code-block:: python

   from tanat.sequence import EventSequencePool
   
   # Create a pool from a DataFrame
   pool = EventSequencePool(data, settings={
       "id_column": "patient_id",
       "time_column": "visit_date",
       "entity_features": ["visit_type"]
   })
   
   # Access individual sequences
   patient_001 = pool["P001"]
   
   # Iterate over all sequences
   for sequence in pool:
       print(sequence.id, len(sequence))

Pools are the primary data structure for analysis operations like
computing distance matrices or clustering.

----

Settings
--------

TanaT uses **settings objects** to configure pools, metrics, and other components.
This pattern provides:

- Clear separation of configuration from data
- Type validation and defaults
- Reproducibility (settings can be exported/imported)

.. code-block:: python

   from tanat.sequence import EventSequencePool, EventSequenceSettings
   
   # Explicit settings object
   settings = EventSequenceSettings(
       id_column="patient_id",
       time_column="visit_date",
       entity_features=["visit_type"]
   )
   
   pool = EventSequencePool(data, settings)

Most TanaT classes have a corresponding settings class
(e.g., ``DTWSequenceMetric`` → ``DTWSequenceMetricSettings``).

----

See Also
--------

* :doc:`first-steps` – Minimal working example
* :doc:`../user-guide/tutorials/04-metadata/metadata_management` – Working with metadata
* :doc:`../user-guide/tutorials/05-type_conversions/sequence_conversions` – Converting between sequence types
* :doc:`../reference/index` – Complete API documentation
