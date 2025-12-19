.. _metadata_reference:

========
Metadata
========

Reference documentation for TanaT's metadata system.

Overview
========

Metadata describes the structure, types, and constraints of temporal data in TanaT.
It is automatically inferred but can be inspected and updated as needed.

See :doc:`/getting-started/concepts` for conceptual introduction and :doc:`/user-guide/tutorials/04-metadata/metadata_management` for practical examples.

Metadata Components
===================

.. _temporal-metadata:

.. topic:: Temporal Metadata

   Describes time representation. Two types are supported.

   **Datetime** (calendar time with timezone):

   .. code-block:: python

      {
          "temporal_type": "datetime",
          "granularity": "second",
          "settings": {"timezone": "UTC", "date_format": "%Y-%m-%d %H:%M:%S"}
      }

   **Timestep** (abstract numerical time):

   .. code-block:: python

      {
          "temporal_type": "timestep",
          "granularity": "unit",
          "settings": {"min_value": 0, "max_value": 100}
      }

----

.. _entity-metadata:

.. topic:: Entity Metadata

   Describes features within sequences. Supported types:

   - **categorical**: Discrete categories (ordered or unordered)
   - **numerical**: Continuous or discrete numbers
   - **duration**: Time durations with specific granularity

----

.. _static-metadata:

.. topic:: Static Metadata

   Describes additional features not tied to temporal extent.
   Available in both :py:class:`SequencePool` and :py:class:`TrajectoryPool`.

   Static features use the same structure as entity metadata (categorical, numerical, or duration types).

----

Update Methods
==============

.. _update-temporal-metadata:

.. topic:: update_temporal_metadata()

   Update temporal metadata settings.

   .. code-block:: python

      pool.update_temporal_metadata(temporal_type=None, granularity=None, **kwargs)

   **Attributes:**

   - ``temporal_type`` *(str)*: ``"datetime"`` or ``"timestep"``.
   - ``granularity`` *(str)*: Time unit (e.g., ``"day"``, ``"hour"``). Use ``"unit"`` for timestep.
   - ``settings`` *(Dict)*: Type-specific settings as dictionary.
   - ``**kwargs``: Override settings (timezone, min_value, max_value, etc.).

   **Type-Specific Attributes:**

   *Datetime* (see :py:class:`DateTimeSettings`):
     - min_value: Minimum datetime value in the data
     - max_value: Maximum datetime value in the data 
     - timezone: Timezone string (e.g., 'UTC', 'Europe/Paris')
     - format: Optional datetime format string for parsing

   *Timestep* (see :py:class:`TimestepSettings`):
     - ``min_value``: Minimum timestep value (numeric)
     - ``max_value``: Maximum timestep value (numeric)
     - ``dtype``: Target pandas dtype (e.g., 'int64', 'float32')

   **Example:**

   .. code-block:: python

      # Update timezone
      pool.update_temporal_metadata(timezone="Europe/Paris")
      
      # Switch to timestep
      pool.update_temporal_metadata(temporal_type="timestep")

----

.. _update-entity-metadata:

.. topic:: update_entity_metadata()

   Update metadata for an entity feature.

   .. code-block:: python

      pool.update_entity_metadata(feature_name: str, 
                                  feature_type: str = None, 
                                  settings: Dict|FeatureSettings = None, 
                                  **kwargs) -> self

   **Attributes:**

   - ``feature_name`` *(str)*: Name of the feature.
   - ``feature_type`` *(str)*: Type of feature - ``"categorical"``, ``"numerical"``, or ``"duration"``.
   - ``settings`` *(Dict|FeatureSettings)*: Feature-specific settings as a dictionary or :py:class:`FeatureSettingsBase` object.
   - ``**kwargs``: Feature-specific attributes that override ``settings`` if both are provided.
     
   **Feature-Specific Attributes:**

   *Categorical features* (see :py:class:`CategoricalFeatureSettings`):
     - ``categories``: List of valid category values
     - ``ordered``: Whether categories have an ordering

   *Numerical features* (see :py:class:`NumericalFeatureSettings`):
     - ``dtype``: Target pandas dtype (e.g., ``'float32'``, ``'int64'``)
     - ``min_value``: Minimum value in the data
     - ``max_value``: Maximum value in the data

   *Duration features* (see :py:class:`DurationFeatureSettings`):
     - ``granularity``: Time unit - ``HOUR``, ``DAY``, ``WEEK``, ``MONTH``, or ``YEAR`` (default: ``DAY``)
     - ``min_value``: Minimum duration (numeric or timedelta)
     - ``max_value``: Maximum duration (numeric or timedelta)

   **Example:**

   .. code-block:: python

      # Categorical feature
      pool.update_entity_metadata(
          feature_name="status",
          feature_type="categorical",
          categories=["A", "B", "C"],
          ordered=True
      )
      
      # Duration feature
      pool.update_entity_metadata(
          feature_name="duration_hours",
          feature_type="duration",
          granularity="hour"
      )

----

.. _update-static-metadata:

.. topic:: update_static_metadata()

   Update metadata for a static feature.

   .. code-block:: python

      pool.update_static_metadata(feature_name: str, 
                                  feature_type: str = None, 
                                  settings: Dict|FeatureSettings = None, 
                                  **kwargs) -> self

   **Available in:** Both :py:class:`SequencePool` and :py:class:`TrajectoryPool`

   Same attributes as ``update_entity_metadata()``.

   **Example:**

   .. code-block:: python

      # In a SequencePool
      pool.update_static_metadata(
          feature_name="gender",
          feature_type="categorical",
          categories=["M", "F", "Other"]
      )
      
      # In a TrajectoryPool
      trajectory.update_static_metadata(
          feature_name="birth_year",
          feature_type="numerical",
          dtype="int"
      )

----

Inspection Methods
==================

.. _metadata-describe:

.. topic:: metadata.describe()

   Human-readable metadata description.

   .. code-block:: python

      pool.metadata.describe(verbose: bool = False) -> str

   **Attributes:**

   - ``verbose`` *(bool)*: If True, include detailed descriptions

   **Example:**

   .. code-block:: python

      print(pool.metadata.describe(verbose=True))

----

.. _metadata-view:

.. topic:: metadata.view()

   Display metadata as YAML with inline documentation.

   .. code-block:: python

      pool.metadata.view() -> None

   **Example:**

   .. code-block:: python

      pool.metadata.view()

----

Metadata Propagation
====================

**In SequencePool**

Updates affect all sequences in the pool:

.. code-block:: python

   pool.update_temporal_metadata(timezone="UTC")
   # All sequences now use UTC

**In TrajectoryPool**

Temporal updates propagate to all contained sequence pools:

.. code-block:: python

   trajectory.update_temporal_metadata(timezone="UTC")
   # All sequence pools in trajectory now use UTC

.. warning::
   Static metadata updates at trajectory level do not propagate to individual sequence pools.
   Each sequence pool maintains its own static metadata independently.

----

Best Practices
==============

1. **Let TanaT infer first**: Automatic inference handles most cases
2. **Inspect before updating**: Use ``.metadata.describe(verbose=True)``
3. **Update using dedicated methods**: Use ``update_*_metadata()`` methods

.. code-block:: python

    pool.update_temporal_metadata(timezone="UTC") \
        .update_entity_metadata("status", feature_type="categorical") \
        .update_static_metadata("gender", feature_type="categorical")

API Reference
=============

For complete API documentation, see:

- :py:class:`tanat.metadata.descriptor.temporal`
- :py:class:`tanat.metadata.descriptor.feature`

See Also
--------

* :doc:`/getting-started/concepts` - Conceptual overview
* :doc:`/user-guide/tutorials/04-metadata/metadata_management` - Hands-on tutorial
* :doc:`/user-guide/tutorials/05-type_conversions/sequence_conversions` - Sequence type conversions
