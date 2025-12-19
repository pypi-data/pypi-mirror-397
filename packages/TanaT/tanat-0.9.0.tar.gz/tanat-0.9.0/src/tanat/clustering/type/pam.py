#!/usr/bin/env python3
"""
PAM clusterer.
"""

import logging
from typing import Union, Optional

import numpy as np

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass
from pypassist.mixin.cachable import Cachable
from pypassist.dataclass.decorators.viewer import viewer

from ..clusterer import Clusterer
from ..mixin.medoid import MedoidMixin
from ...metric.sequence.base.metric import SequenceMetric
from ...metric.trajectory.base.metric import TrajectoryMetric
from .kernels import pam_build_optimized, pam_swap_optimized

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class PAMClustererSettings:
    """
    Configuration settings for the PAMClusterer.

    Attributes:
        metric (Union[SequenceMetric, TrajectoryMetric, str]):
            The metric used for clustering. If a string identifier is provided,
            (e.g., from a YAML configuration), it will be resolved into an `SequenceMetric`
            or `TrajectoryMetric` object from the global configuration.
        n_clusters (int):
            The number of clusters to form. Must be greater than 0. Defaults to 2.
        max_iter (int):
            Maximum number of iterations for the swap phase. Must be greater than 0.
            Defaults to 50.
        distance_threshold (Optional[float]):
            Optional distance threshold for clustering. If specified, must be non-negative.
            Defaults to None.
        cluster_column (str):
            The column name used to store the clustering results
            as a static feature. Defaults to "__PAM_CLUSTERS__".
    """

    metric: Union[SequenceMetric, TrajectoryMetric, str] = "linearpairwise"
    n_clusters: int = Field(default=2, gt=0)
    max_iter: int = Field(default=50, gt=0)
    distance_threshold: Optional[float] = None
    cluster_column: str = "__PAM_CLUSTERS__"

    @field_validator("distance_threshold")
    @classmethod
    def validate_distance_threshold(cls, v):
        """Validate that distance_threshold is non-negative if specified."""
        if v is None:
            return v

        v = float(v)

        if v < 0:
            raise ValueError("'distance_threshold' must be non-negative if specified.")

        return v


class PAMClusterer(MedoidMixin, Clusterer, register_name="pam"):
    """
    PAM (Partition Around Medoids) clustering implementation is a
    clustering algorithm similar to k-Medoids. In PAM, the medoids
    are *selected objects* (a subset of the complete list of
    objects to cluster).

    The goal of the algorithm is to minimize the inertia of the clustering
    ie. the average dissimilarity of objects to their closest selected object.

    .. important::

        The clustering technique is sound with metrics that hold distance's properties.
        More specifically, the triangular inegality must hold to ensure the convergence
        of the algorithm.
        A short loop detection is implemented in case of use with metrics without this
        property, but it does not protect to possible looping algorithm.

        The user is invited to set up the maximum iteration to avoid an infinite loop.

    .. warning::

        The method requires to precompute the distance matrix. It can be heavy in memory
        for large datasets.
        In such case, we invite the user to choose the CLARA clusterer.

    Example:

        Clustering with PAM, with 5 clusters and a linear pairwise metric.

        >>>    cluster_settings = PAMClustererSettings(metric="linearpairwise", n_clusters=5)
        >>>    clusterer = PAMClusterer(settings=cluster_settings)
        >>>    clusterer.fit(pool)


    .. seealso::

        :py:class:`CLARAClusterer`
            Implementation of the CLARA clusterer which is a sampled version of PAM clusterer.

    """

    SETTINGS_DATACLASS = PAMClustererSettings

    def __init__(self, settings=None, *, workenv=None):
        """
        Initialize the PAM clusterer with the given settings.

        Args:
            settings: Configuration settings for the PAM clusterer.
                If None, default PAMClustererSettings will be used.
            workenv: Optional working env instance.

        Raises:
            ValueError: If the settings type is invalid.
        """
        if settings is None:
            settings = PAMClustererSettings()

        Clusterer.__init__(self, settings, workenv=workenv)
        MedoidMixin.__init__(self)

    @Cachable.caching_method()
    def _compute_fit(self, metric, pool):
        """
        Computes and applies the clustering model to the data.
        The implementation of PAM is derived from this document:
        https://www.cs.umb.edu/cs738/pam1.pdf

        The function computes the clusters and set the `self._cluster`
        attribute with the results. In addition, it set the specific
        `self._medoids` attribute.

        Args:
            metric: The metric to compute distances between data points.
            pool: The data pool (sequence or trajectory data).
            model: The clustering model to use.
        """
        self._n_steps = 4

        # Step 1: Compute distance matrix
        self._display_step(1, self._n_steps, "Computing distance matrix")
        with self._nested_display():
            dist_matrix = metric.compute_matrix(pool)
        pool_idx = dist_matrix.ids

        np_dist_matrix = dist_matrix.to_numpy()
        del dist_matrix  # free memory

        # Step 2: BUILD phase - initial medoid selection
        self._display_step(2, self._n_steps, "BUILD phase (initial medoid selection)")
        selected_list, unselected_list = pam_build_optimized(
            np_dist_matrix, self.settings.n_clusters
        )

        # Step 3: SWAP phase - iterative improvement
        self._display_step(3, self._n_steps, "SWAP phase (iterative improvement)")
        n_iter = 0
        swap = pam_swap_optimized(selected_list, unselected_list, np_dist_matrix)

        while self.settings.max_iter and n_iter < self.settings.max_iter and swap:
            # apply the swap
            selected_list.remove(swap[0])
            selected_list.append(swap[1])
            unselected_list.remove(swap[1])
            unselected_list.append(swap[0])
            # try another swap
            n_iter += 1
            old_swap = swap
            swap = pam_swap_optimized(selected_list, unselected_list, np_dist_matrix)

            # detecting loop
            if swap and old_swap[0] == swap[1] and old_swap[1] == swap[0]:
                logging.warning("PAM stopped due to loop")
                break

        self._display_message(f"Converged in {n_iter} iterations")

        # Finalize clusters (last step displayed by parent fit())
        medoids_idx = selected_list
        self._medoids = [pool_idx[ix] for ix in medoids_idx]
        labels = np.argmin(np_dist_matrix[:, medoids_idx], axis=1)
        self._create_clusters(labels, pool_idx)
