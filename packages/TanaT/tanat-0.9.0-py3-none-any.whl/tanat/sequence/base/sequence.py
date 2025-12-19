#!/usr/bin/env python3
"""
Sequence base class.
"""

from abc import abstractmethod

from pypassist.mixin.cachable import Cachable
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError

from ...criterion.base.enum import CriterionLevel
from ...criterion.utils import resolve_and_init_criterion
from ...mixin.manipulation.sequence import SequenceManipulationMixin
from ...mixin.summarizer.sequence import SequenceSummarizerMixin
from .exception import UnregisteredSequenceTypeError
from .array import SequenceArray


class Sequence(
    # ABC inherited via SequenceManipulationMixin → MetadataMixin
    SequenceManipulationMixin,
    SequenceSummarizerMixin,
    Cachable,
    SettingsMixin,
    Registrable,
):
    """
    Base class for sequence objects.
    """

    _REGISTER = {}
    _IS_POOL = False  ## A flag to differentiate between SequencePool and Sequence

    def __init__(
        self,
        id_value,
        sequence_data,
        settings,
        static_data=None,
        metadata=None,
    ):
        """
        Args:
            sequence_data:
                The input sequence data.

            settings:
                The sequence settings.

            static_data:
                Optional static data associated with this sequence.

            metadata (SequenceMetadata | dict | None):
                Sequence metadata. If None or incomplete, inferred from data.
                Includes temporal descriptor, granularity, and feature descriptors.
        """
        self.id_value = id_value
        SettingsMixin.__init__(self, settings)
        Cachable.__init__(self)
        SequenceManipulationMixin.__init__(
            self,
            sequence_data=sequence_data,
            static_data=static_data,
            metadata=metadata,
        )

    @classmethod
    def init(
        cls, stype, id_value, sequence_data, settings, metadata=None, static_data=None
    ):
        """
        Initialize the sequence for a specific type.

        Args:
            stype:
                The sequence type.

            id_value:
                The ID of the sequence.

            sequence_data:
                The input sequence data.

            settings:
                The sequence settings.

            metadata:
                The metadata for the input data.

            static_data:
                The static feature data.

        Returns:
            An instance of the sequence.
        """
        try:
            sequence_cls = cls.get_registered(stype)
            sequence = sequence_cls(
                id_value=id_value,
                sequence_data=sequence_data,
                settings=settings,
                metadata=metadata,
                static_data=static_data,
            )
        except UnregisteredTypeError as err:
            registered_sequence_types = cls.list_registered()
            raise UnregisteredSequenceTypeError(
                f"Unknown sequence type: '{stype}'. "
                f"Available sequence types: {registered_sequence_types}"
            ) from err

        return sequence

    @property
    def dim(self):
        """
        Returns the dimension of entity in the sequence,
        corresponding to the number of columns in `sequence_data`.
        """
        return self.sequence_data.shape[1]

    @property
    def dim_names(self):
        """
        Returns the dimension names of entity in the sequence,
        corresponding to the column names in `sequence_data`.
        """
        return list(self.sequence_data.columns)

    @Cachable.caching_method()
    def get_sequence_array(
        self,
        entity_features=None,
        include_timestamps=False,
        include_durations=False,
    ):
        """
        Get the sequence data as a SequenceArray object (containing a single sequence).

        Args:
            entity_features (list, optional):
                List of entity features names to include.
                If None, includes all entity_features.
            include_timestamps (bool):
                If True, extract timestamps from temporal columns.
                Timestamps keep their native type (datetime64 or numeric).
                For sequences with start/end columns, uses the resolved anchor
                (START for events/states, settings.anchor for intervals).
                Defaults to False.
            include_durations (bool):
                If True, extract durations from temporal columns (for State/Interval).
                For datetime: durations as timedelta.
                For numeric: difference between end and start.
                Only applicable for sequences with start/end columns.
                Defaults to False.

        Returns:
            SequenceArray: The sequence data in array format.
        """
        return SequenceArray.from_sequence(
            self,
            entity_features=entity_features,
            include_timestamps=include_timestamps,
            include_durations=include_durations,
        )

    def entities(self):
        """
        Yields entities generator.
        """
        for _, row in self.sequence_data.iterrows():
            yield self._get_entity(row)

    def match(self, criterion, criterion_type=None, **kwargs):
        """
        Determine if the sequence matches the criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. The criterion must be applicable at the 'sequence' level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            bool: True if the sequence matches the criterion, False otherwise

        Examples:
            Test if sequence contains emergency events:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> has_emergency = sequence.match(criterion)
            >>> print(f"Has emergency: {has_emergency}")

            Test sequence length:

            >>> from tanat.criterion.sequence.type.length.settings import LengthCriterion
            >>> criterion = LengthCriterion(gt=5)
            >>> is_long = sequence.match(criterion)
        """
        criterion, _ = resolve_and_init_criterion(
            criterion, "sequence", criterion_type, CriterionLevel.SEQUENCE
        )
        return bool(criterion.match(self, **kwargs))

    def filter(self, criterion, criterion_type=None, inplace=False, **kwargs):
        """
        Filter entities that match the criterion.

        Args:
            criterion (Union[Criterion, dict]):
                Defines the criterion, either as a dictionary or a Criterion
                object. The criterion must be applicable at the 'entity' level.
            criterion_type (str, optional):
                Indicates the type of criterion to apply, such as "query" or
                "pattern". Required if criterion is provided as a dictionary.
                Defaults to None.
            inplace (bool, optional):
                If True, modifies the current sequence in place. Defaults to
                False.
            kwargs:
                Additional keyword arguments to override criterion attributes.

        Returns:
            Sequence: A filtered sequence or None if inplace.

        Examples:
            Filter entities without missing values:

            >>> from tanat.criterion.mixin.query.settings import QueryCriterion
            >>> criterion = QueryCriterion(query="event_type.notna()")
            >>> clean_seq = sequence.filter(criterion)
            >>> print(f"Original: {len(sequence)}, Filtered: {len(clean_seq)}")

            Filter entities using pattern matching:

            >>> from tanat.criterion.mixin.pattern.settings import PatternCriterion
            >>> criterion = PatternCriterion(pattern={"event_type": "EMERGENCY"})
            >>> emergency_entities = sequence.filter(criterion)
        """
        # -- validate, resolve, and initialize criterion
        criterion, _ = resolve_and_init_criterion(
            criterion, "entity", criterion_type, CriterionLevel.ENTITY
        )
        return criterion.filter(self, inplace, **kwargs)

    def __getitem__(self, index):
        """
        Return entity/entities at given position(s).

        Args:
            index (int | slice):
                - int: Single entity at position (supports negative indexing)
                - slice: New Sequence with entities in range (supports step)

        Returns:
            Entity or Sequence: Single entity for int index, new Sequence for slice

        Examples:
            Access single entities:

            >>> first_entity = sequence[0]
            >>> last_entity = sequence[-1]
            >>> second_entity = sequence[1]

            Slice sequences:

            >>> first_five = sequence[:5]
            >>> from_third = sequence[3:]
            >>> middle = sequence[2:7]
            >>> all_but_last = sequence[:-1]
            >>> all_but_first_and_last = sequence[1:-1]

            Step sampling:

            >>> every_second = sequence[::2]
            >>> every_tenth = sequence[::10]

        Note:
            For relative (T0-based) slicing, use the slice() method:

            >>> sequence.slice(-2, 1, relative=True)  # From T0-2 to T0
            >>> sequence.slice(0, 100, step=5, relative=True)  # T0 to T0+100, every 5
        """
        if isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step

            # Delegate to slice() method which handles RankCriterion
            return self.slice(start=start, end=stop, step=step, inplace=False)

        # Int indexing (supports negative via iloc)
        return self._get_entity(self._get_standardized_data().iloc[index])

    @abstractmethod
    def _get_entity(self, data):
        """
        Get an entity instance.
        """

    def __len__(self):
        """
        Returns the number of entity, corresponding to the number of rows in `sequence_data`.
        """
        return len(self.sequence_data)
