First Steps
===========

This guide walks you through the core TanaT workflow: loading data, choosing the right sequence type, and exploring your temporal data.

.. note::
   Make sure TanaT is installed: ``pip install tanat`` (see :doc:`installation`).


1. Prepare Your Data
--------------------

TanaT works with pandas DataFrames containing temporal data:

.. code-block:: python

   import pandas as pd
   
   # Sample data: patient visits
   data = pd.DataFrame({
       'patient_id': ['P001', 'P001', 'P001', 'P002', 'P002'],
       'visit_date': pd.to_datetime([
           '2023-01-15', '2023-02-20', '2023-03-10',
           '2023-01-20', '2023-03-15'
       ]),
       'visit_type': ['GP', 'SPECIALIST', 'GP', 'GP', 'EMERGENCY']
   })


2. Choose the Right Sequence Type
---------------------------------

Before creating a pool, identify which sequence type matches your data:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Type
     - Your data has...
     - Example
   * - **EventSequence**
     - Single timestamps (punctual events)
     - Medical visits, purchases, clicks
   * - **IntervalSequence**
     - Start + end dates (can overlap)
     - Treatments, hospital stays, projects
   * - **StateSequence**
     - Contiguous states (no gaps, no overlap)
     - Disease stages, employment status

For our example, visits are **punctual events** so we use ``EventSequencePool``.


3. Create a Sequence Pool
-------------------------

A **pool** groups sequences from multiple individuals:

.. code-block:: python

   from tanat.sequence import EventSequencePool
   
   pool = EventSequencePool(data, settings={
       "id_column": "patient_id",
       "time_column": "visit_date",
       "entity_features": ["visit_type"]
   })


4. Verify Inferred Metadata
---------------------------

When you display the pool, TanaT shows a summary including **automatically inferred metadata**.
It's important to verify this inference is correct before proceeding:

.. code-block:: python

   # Display pool summary with inferred metadata
   print(pool)

.. code-block:: text

   ┌──────────────────────────────────────────────────┐
   │            EventSequencePool summary             │
   └──────────────────────────────────────────────────┘

   STATISTICS
   ─────────────────────────
     Total sequences    2              
     Average length     2.5            
     ...

   Metadata:
     Temporal:
       Type: datetime
       Granularity: DAY
     
     Entity Features (1):
       - visit_type: categorical

You can also get a compact metadata view:

.. code-block:: python

   print(pool.metadata.describe())

If the inference is incorrect, you can update the metadata:

.. code-block:: python

   # Example: correct the timezone
   pool.update_temporal_metadata(timezone="Europe/Paris")
   
   # Example: specify ordered categories
   pool.update_entity_metadata(
       feature_name="visit_type",
       categories=["GP", "SPECIALIST", "EMERGENCY"],
       ordered=True
   )

.. seealso:: :doc:`../reference/metadata` for complete metadata documentation.


5. Access Individual Sequences
------------------------------

.. code-block:: python

   # Get a specific patient's sequence
   patient = pool['P001']
   print(f"Patient P001: {len(patient)} visits")
   
   # View the underlying data
   print(patient.sequence_data)


6. Access Individual Entities
-----------------------------

Within a sequence, you can access individual entities (observations):

.. code-block:: python

   # Get the first entity (visit) in the sequence
   first_visit = patient[0]
   
   # Access entity properties
   print(f"Temporal extent: {first_visit.extent}")  # 2023-01-15 00:00:00
   print(f"Value: {first_visit.value}")             # GP
   
   # Iterate over all entities
   for entity in patient:
       print(f"{entity.extent}: {entity.value}")


Next Steps
----------

:doc:`concepts`
   Deep dive into TanaT core concepts: sequences, trajectories, pools, settings

:doc:`../user-guide/examples/index`
   See complete examples with metrics, visualization, and clustering

:doc:`../reference/metadata`
   Complete metadata reference and update methods

:doc:`../reference/index`
   Full API documentation
