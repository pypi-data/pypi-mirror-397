#!/usr/bin/env python3
"""
Facet mixin for creating grid visualizations based on static features.
"""

import math
import logging
from typing import Optional, Tuple

from pydantic.dataclasses import dataclass
import matplotlib.pyplot as plt

LOGGER = logging.getLogger(__name__)


@dataclass
class FacetConfig:
    """Configuration for faceted visualizations.

    Attributes:
        by (str): Column name from static_data to facet by.
        cols (int): Number of columns in the grid.
        rows (Optional[int]): Number of rows (auto-calculated if None).
        share_x (bool): Whether to share x-axis across facets.
        share_y (bool): Whether to share y-axis across facets.
        figsize_per_facet (Tuple[float, float]): Figure size (width, height) per facet.
        title_template (str): Template for facet titles.
        legend_shared (bool): True for single shared legend, False for individual legends.
    """

    by: str
    cols: int = 3
    rows: Optional[int] = None
    share_x: bool = True
    share_y: bool = True
    figsize_per_facet: Tuple[float, float] = (5, 4)
    title_template: str = "{by} = {value}"
    # Legend configuration
    legend_shared: bool = True  # True: single shared legend, False: individual legends


class FacetMixin:
    """
    Mixin for creating faceted (grid) visualizations.

    Enables splitting a visualization into multiple subplots based on
    a static feature column, similar to ggplot2's facet_grid/facet_wrap.

    The mixin adds a `facet()` method to configure faceting and modifies
    the draw behavior to create a grid of subplots when enabled.
    """

    _facet_config = None

    @property
    def facet_enabled(self):
        """Check if faceting is enabled."""
        return self._facet_config is not None and bool(self._facet_config.by)

    def facet(
        self,
        by,
        cols=3,
        rows=None,
        share_x=True,
        share_y=True,
        figsize_per_facet=(5, 4),
        title_template="{by} = {value}",
        legend_shared=True,
    ):
        """
        Configure faceted visualization by a static feature.

        Creates a grid of subplots, one for each unique value of the
        specified static feature column.

        Args:
            by: Column name from static_data to facet by (static feature).
            cols: Number of columns in the grid.
            rows: Number of rows (auto-calculated if None).
            share_x: Whether to share x-axis across facets.
            share_y: Whether to share y-axis across facets.
            figsize_per_facet: Figure size (width, height) per facet.
            title_template: Template for facet titles.
                Available placeholders: {by}, {value}, {index}.
            legend_shared: If True, displays a single shared legend for all
                facets. If False, each facet has its own legend.
                Use `.legend()` to customize title, location, etc.

        Returns:
            self: For method chaining.
        """
        self._facet_config = FacetConfig(
            by=by,
            cols=cols,
            rows=rows,
            share_x=share_x,
            share_y=share_y,
            figsize_per_facet=figsize_per_facet,
            title_template=title_template,
            legend_shared=legend_shared,
        )
        return self

    def reset_facet(self):
        """
        Disable faceting and reset to single plot mode.

        Returns:
            self: For method chaining.
        """
        self._facet_config = None
        return self

    def _get_facet_values(self, sequence_or_pool):
        """
        Get unique values for the facet column from static data.

        Args:
            sequence_or_pool: Sequence or SequencePool with static_data

        Returns:
            list: Sorted unique values of the facet column

        Raises:
            ValueError: If facet column not found in static_data
        """
        if sequence_or_pool.static_data is None:
            raise ValueError(
                f"Cannot facet: pool has no static_data. "
                f"Facet column '{self._facet_config.by}' requires static data."
            )

        if self._facet_config.by not in sequence_or_pool.settings.static_features:
            available = list(sequence_or_pool.settings.static_features)
            raise ValueError(
                f"Facet column '{self._facet_config.by}' not found in static_data. "
                f"Available columns: {available}"
            )

        values = sequence_or_pool.static_data[self._facet_config.by].unique()
        # Sort for consistent ordering
        try:
            return sorted(values)
        except TypeError:
            # If values are not sortable, return as-is
            return list(values)

    def _calculate_grid_dimensions(self, n_facets):
        """
        Calculate grid dimensions (rows, cols) for the given number of facets.

        Args:
            n_facets: Number of facets to display

        Returns:
            Tuple of (rows, cols)
        """
        cols = min(self._facet_config.cols, n_facets)
        rows = self._facet_config.rows or math.ceil(n_facets / cols)
        return rows, cols

    def _create_faceted_figure(self, n_facets):
        """
        Create figure and axes for faceted visualization.

        Args:
            n_facets: Number of facets

        Returns:
            Tuple of (figure, list of axes)
        """
        rows, cols = self._calculate_grid_dimensions(n_facets)
        config = self._facet_config

        # Calculate total figure size
        width = config.figsize_per_facet[0] * cols
        height = config.figsize_per_facet[1] * rows

        fig, axes = plt.subplots(
            rows,
            cols,
            figsize=(width, height),
            sharex=config.share_x,
            sharey=config.share_y,
            squeeze=False,  # Always return 2D array
        )

        return fig, axes.flatten().tolist()

    def _format_facet_title(self, value, index):
        """
        Format the title for a single facet.

        Args:
            value: The facet value
            index: The facet index (0-based)

        Returns:
            Formatted title string
        """
        return self._facet_config.title_template.format(
            by=self._facet_config.by,
            value=value,
            index=index,
        )

    def _filter_pool_for_facet(self, sequence_or_pool, facet_value):
        """
        Filter sequence_or_pool to include only sequences matching the facet value.

        Args:
            sequence_or_pool: Sequence or SequencePool to filter
            facet_value: Value to filter by

        Returns:
            Filtered SequencePool
        """
        column = self._facet_config.by

        # Handle different value types for query string
        if isinstance(facet_value, str):
            query = f'{column} == "{facet_value}"'
        else:
            query = f"{column} == {facet_value}"

        static_criterion = {"query": query}
        return sequence_or_pool.filter(
            static_criterion,
            criterion_type="static",
            level="sequence",
        )

    def _draw_faceted(
        self,
        sequence_or_pool,
        drop_na=True,
        entity_features=None,
        **kwargs,
    ):
        """
        Draw faceted visualization.

        Creates a grid of subplots, one for each unique value of the
        facet column.

        Args:
            sequence_or_pool: Sequence or SequencePool to visualize
            drop_na: Whether to drop NA values
            entity_features: Entity features to include
            **kwargs: Additional drawing arguments

        Returns:
            Tuple of (figure, list of axes)
        """
        # Get facet values and create figure
        facet_values = self._get_facet_values(sequence_or_pool)
        n_facets = len(facet_values)

        if n_facets == 0:
            raise ValueError(
                f"No values found for facet column '{self._facet_config.by}'"
            )

        fig, axes = self._create_faceted_figure(n_facets)
        legend_handles = None
        legend_labels = None

        # Draw each facet
        for i, value in enumerate(facet_values):
            ax = axes[i]

            # Single facet uses full data, otherwise filter for this value
            subset = (
                sequence_or_pool
                if n_facets == 1
                else self._filter_pool_for_facet(sequence_or_pool, value)
            )

            if len(subset) == 0:
                LOGGER.warning(
                    "No sequences found for facet value '%s', skipping", value
                )
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(self._format_facet_title(value, i))
                continue

            # Prepare data and render for this subset
            data = self.prepare_data(
                subset,
                drop_na=drop_na,
                entity_features=entity_features,
                **kwargs,
            )
            self._render(ax, data)

            # Set facet title
            ax.set_title(self._format_facet_title(value, i))

            # Capture legend handles from first valid facet
            if legend_handles is None:
                handles, labels = ax.get_legend_handles_labels()
                if handles:
                    legend_handles = handles
                    legend_labels = labels

            # Remove individual legends if shared mode or legend disabled
            legend_settings = self.settings.legend
            show_legend = (
                legend_settings.show if hasattr(legend_settings, "show") else True
            )

            if self._facet_config.legend_shared or not show_legend:
                # Remove individual legend
                legend = ax.get_legend()
                if legend is not None:
                    legend.remove()

        # Hide unused axes
        for i in range(n_facets, len(axes)):
            axes[i].axis("off")

        # Add shared legend if configured and legend is enabled
        legend_settings = self.settings.legend
        show_legend = legend_settings.show if hasattr(legend_settings, "show") else True

        if self._facet_config.legend_shared and show_legend and legend_handles:
            self._add_shared_legend(fig, legend_handles, legend_labels, legend_settings)

        plt.tight_layout()

        # Adjust layout for shared legend
        if self._facet_config.legend_shared and show_legend and legend_handles:
            self._adjust_layout_for_legend(fig, legend_settings)

        return fig, axes[:n_facets]

    def _add_shared_legend(self, fig, handles, labels, legend_settings):
        """
        Add a shared legend to the figure.

        Args:
            fig: Matplotlib figure
            handles: Legend handles
            labels: Legend labels
            legend_settings: LegendSettings from self.settings.legend
        """
        # Get settings from legend_settings, with defaults
        title = getattr(legend_settings, "title", None)
        loc = getattr(legend_settings, "loc", "right")
        bbox_to_anchor = getattr(legend_settings, "bbox_to_anchor", None)

        # Build legend kwargs
        legend_kwargs = {
            "frameon": True,
        }
        if title:
            legend_kwargs["title"] = title

        # Handle location - map simple names to figure legend positions
        if bbox_to_anchor:
            # User provided custom bbox_to_anchor
            legend_kwargs["loc"] = loc
            legend_kwargs["bbox_to_anchor"] = bbox_to_anchor
        elif loc in ("right", "center left"):
            legend_kwargs["loc"] = "center left"
            legend_kwargs["bbox_to_anchor"] = (1.0, 0.5)
        elif loc in ("bottom", "upper center"):
            legend_kwargs["loc"] = "upper center"
            legend_kwargs["bbox_to_anchor"] = (0.5, 0.0)
            legend_kwargs["ncol"] = min(len(labels), 6)
        elif loc in ("top", "lower center"):
            legend_kwargs["loc"] = "lower center"
            legend_kwargs["bbox_to_anchor"] = (0.5, 1.0)
            legend_kwargs["ncol"] = min(len(labels), 6)
        else:
            # Default to right side
            legend_kwargs["loc"] = "center left"
            legend_kwargs["bbox_to_anchor"] = (1.0, 0.5)

        fig.legend(handles, labels, **legend_kwargs)

    def _adjust_layout_for_legend(self, fig, legend_settings):
        """
        Adjust figure layout to make room for the shared legend.

        Args:
            fig: Matplotlib figure
            legend_settings: LegendSettings from self.settings.legend
        """
        loc = getattr(legend_settings, "loc", "right")
        bbox_to_anchor = getattr(legend_settings, "bbox_to_anchor", None)

        # If custom bbox_to_anchor, don't auto-adjust
        if bbox_to_anchor:
            return

        if loc in ("right", "center left"):
            fig.subplots_adjust(right=0.85)
        elif loc in ("bottom", "upper center"):
            fig.subplots_adjust(bottom=0.15)
        elif loc in ("top", "lower center"):
            fig.subplots_adjust(top=0.85)
