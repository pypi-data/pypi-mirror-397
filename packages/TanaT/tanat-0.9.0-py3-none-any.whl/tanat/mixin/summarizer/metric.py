#!/usr/bin/env python3
"""
Summarizer mixin for metrics.
"""

from .base import BaseSummarizerMixin


class MetricSummarizerMixin(BaseSummarizerMixin):
    """
    Mixin to add summarization capabilities to Metric classes.
    """

    @property
    def statistics(self):
        """
        Metrics do not provide data statistics.
        """
        raise NotImplementedError("Metrics do not provide data statistics.")

    def _get_title(self):
        """Get the summary title."""
        return f"{self.__class__.__name__}"

    def _format_statistics(self):
        """Format metric settings."""
        lines = []

        # Settings are guaranteed to be a dataclass
        stats = self.settings.__dict__

        for key, value in stats.items():
            # Skip private attributes
            if key.startswith("_"):
                continue

            # Special handling for distance_matrix settings
            if key == "distance_matrix" and hasattr(value, "store_path"):
                if value.store_path:
                    val_str = f"Memmap (resume={value.resume})"
                else:
                    val_str = f"Memory ({value.dtype})"

            # Format value for display
            elif isinstance(value, dict):
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

            lines.append(self._format_stat_line(key, val_str))

        return self._format_section("Settings", "\n".join(lines))

    def _format_data_preview(self):
        """
        No data preview for metrics.
        """
        return ""

    def get_compact_summary(self):
        """
        Generate compact summary (e.g. for use in lists).
        """
        return f"<{self.__class__.__name__}>"
