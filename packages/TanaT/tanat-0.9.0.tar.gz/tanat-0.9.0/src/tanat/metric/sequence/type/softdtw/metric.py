#!/usr/bin/env python3
"""
SoftDTW (Soft Dynamic Time Warping) metric.
"""

import logging
from typing import Union

from pydantic.dataclasses import dataclass, Field
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_softdtw_single_pair,
    compute_softdtw_matrix_chunk,
)
from ...base.metric import SequenceMetric
from ...base.settings import BaseSequenceMetricSettings
from ....entity.base.metric import EntityMetric
from .....sequence.base.array import SequenceArray


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class SoftDTWSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for SoftDTW (Soft Dynamic Time Warping) sequence metric computation.

    Attributes:
        entity_metric:
            Specifies the metric used for calculating distances at the entity level.
            It can be either a string identifier corresponding to an EntityMetric
            in the registry (or within a working environment), such as "hamming",
            or an instance of the EntityMetric class. The default value is "hamming".

        gamma: Regularization parameter for soft-min function.
            Controls smoothness of the approximation. Lower values make it
            closer to true DTW. Must be positive. Defaults to 1.0.

        distance_matrix: Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.

    Note: Inherits entity_metric and distance_matrix from BaseSequenceMetricSettings.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    gamma: float = Field(default=1.0, gt=0.0)


class SoftDTWSequenceMetric(SequenceMetric, register_name="softdtw"):
    """
    Soft Dynamic Time Warping (SoftDTW)

    A differentiable version of DTW that replaces the min operator with a
    soft-minimum, allowing for gradient computation. This implementation uses
    a regularization parameter gamma to control the smoothness of the approximation.

    See Also
    --------
    DTWSequenceMetric : Standard DTW (Dynamic Time Warping) metric.

    References
    ----------
    .. [1] Marco Cuturi & Mathieu Blondel. Soft-DTW: a Differentiable Loss Function for
        Time-Series, ICML 2017.
    .. [2] Mathieu Blondel, Arthur Mensch & Jean-Philippe Vert.
        Differentiable divergences between time series,
        International Conference on Artificial Intelligence and Statistics, 2021.
    """

    SETTINGS_DATACLASS = SoftDTWSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = SoftDTWSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def _gamma(self):
        """Get the gamma regularization parameter."""
        return self._settings.gamma

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute SoftDTW distance between two sequences.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The SoftDTW distance for the sequence pair.
        """
        entity_features = self._entity_features

        # Extract arrays using SequenceArray
        sa_a = seq_a.get_sequence_array(entity_features)
        sa_b = seq_b.get_sequence_array(entity_features)

        # Combine for encoding (to ensure shared vocabulary)
        combined_sa = SequenceArray.concatenate([sa_a, sa_b])

        # Prepare execution context
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(
            combined_sa
        )

        # Compute distance
        return compute_softdtw_single_pair(
            encoded_arrays[0],
            encoded_arrays[1],
            sa_a.lengths[0],
            sa_b.lengths[0],
            dist_kernel,
            context,
            self._gamma,
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise SoftDTW distances using Numba-optimized kernels.

        Overrides the default naive loop implementation in SequenceMetric
        with a parallelized, JIT-compiled version for high performance.

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        # Extract and prepare data
        sa = sequence_pool.get_sequence_array(self._entity_features)
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(sa)

        # Compute chunks with resume support
        self._compute_matrix_chunks(
            dm,
            encoded_arrays,
            sa.lengths,
            dist_kernel,
            context,
            sequence_pool,
        )

    def _compute_matrix_chunks(
        self,
        dm,
        encoded_arrays,
        lengths,
        dist_kernel,
        context,
        sequence_pool,
    ):
        """
        Compute matrix chunks with resume support.

        Args:
            dm: DistanceMatrix to fill.
            encoded_arrays: Encoded sequence data.
            lengths: Array of sequence lengths.
            dist_kernel: Numba distance kernel function.
            context: Context for the distance kernel.
            sequence_pool: Original pool (for progress bar).
        """
        n_sequences = len(encoded_arrays)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        gamma = self._gamma

        with self._progress_bar(sequence_pool) as pbar:
            for start in range(0, n_sequences, batch_size):
                end = min(start + batch_size, n_sequences)
                pairs_count = self._count_chunk_pairs(start, end, n_sequences)

                # Skip if already computed (resume mode)
                if dm.is_chunk_computed(diagonal, start):
                    pbar.update(pairs_count)
                    continue

                # Compute chunk
                compute_softdtw_matrix_chunk(
                    dm.data,
                    start,
                    end,
                    encoded_arrays,
                    lengths,
                    dist_kernel,
                    context,
                    gamma,
                )

                dm.flush()
                dm.mark_chunk_done(diagonal, start, end)
                pbar.update(pairs_count)

    def _prepare_execution_context(self, sequence_array):
        """
        Prepare data and kernels for Numba execution.

        Args:
            sequence_array: SequenceArray containing the sequences.

        Returns:
            Tuple of (encoded_arrays, context, dist_kernel).
        """
        encoded_arrays, context = self.entity_metric.prepare_computation_data(
            sequence_array
        )
        dist_kernel = self.entity_metric.distance_kernel
        return encoded_arrays, context, dist_kernel
