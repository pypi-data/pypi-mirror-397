#! /usr/venv/bin python3
"""Clustering summarizer."""

import numpy as np

from .base import BaseSummarizerMixin


class ClusteringSummarizerMixin(BaseSummarizerMixin):
    """Implements summarization for cluster data."""

    @property
    def statistics(self):
        """
        Compute clustering statistics.

        Returns:
            dict: Clustering metrics.
        """
        if not self.clusters:
            return {
                "total": 0,
                "avg_size": 0.0,
                "min_size": 0,
                "max_size": 0,
            }

        sizes = [cluster.size for cluster in self.clusters]
        return {
            "total": len(self.clusters),
            "avg_size": float(np.mean(sizes)),
            "min_size": int(np.min(sizes)),
            "max_size": int(np.max(sizes)),
        }

    def _format_statistics(self):
        """Generate cluster statistics section."""
        stats = self.statistics

        lines = [
            self._format_stat_line("Clusters", stats["total"]),
            self._format_stat_line("Avg size", f"{stats['avg_size']:.1f}"),
            self._format_stat_line("Min size", stats["min_size"]),
            self._format_stat_line("Max size", stats["max_size"]),
        ]
        return self._format_section("STATISTICS", "\n".join(lines))

    def _format_data_preview(self):
        """Generate cluster breakdown and settings."""
        sections = []

        # Cluster details
        sections.append(f"{self.INDENT}Cluster Details:")
        if self.clusters is not None:
            sections.append(f"{self.INDENT * 2}{'ID':<15}{'Size':<10}")
            sections.append(f"{self.INDENT * 2}{'-' * 25}")

            for cluster in self.clusters:
                sections.append(f"{self.INDENT * 2}{cluster.id:<15}{cluster.size:<10}")
        else:
            sections.append(f"{self.INDENT * 2}None")

        # Settings section
        sections.extend(
            [
                "",
                f"{self.INDENT}Settings:",
            ]
        )
        sections.append(self._format_settings_lines())

        return self._format_section("CLUSTER DETAILS", "\n".join(sections))

    def _format_settings_lines(self):
        """Format settings with proper value handling."""
        lines = []

        for key, value in self.settings.__dict__.items():
            # Skip private attributes
            if key.startswith("_"):
                continue

            # Format value for display
            if isinstance(value, dict):
                val_str = f"{len(value)} items"
            elif hasattr(value, "__class__") and not isinstance(
                value, (str, int, float, bool, list, tuple, dict, type(None))
            ):
                # Try to get a clean name for objects
                val_str = getattr(value, "__name__", value.__class__.__name__)
            else:
                val_str = str(value)

            # Truncate long values
            if len(val_str) > 30:
                val_str = val_str[:27] + "..."

            lines.append(f"{self.INDENT * 2}{key:<20}{val_str}")

        return "\n".join(lines)

    def get_compact_summary(self):
        """Generate compact summary for embedding in other summaries."""
        stats = self.statistics

        return [
            f"Total clusters: {stats['total']}",
            f"Avg size: {stats['avg_size']:.1f}",
            f"Size range: {stats['min_size']}-{stats['max_size']}",
        ]
