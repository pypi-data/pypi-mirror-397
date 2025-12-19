#!/usr/bin/env python3
"""
Display mixin for computation progress..
"""

import time
from contextlib import contextmanager

from tqdm import tqdm


class DisplayIndentManager:
    """
    Global manager for display indentation.

    Allows nested components (like metrics inside clusterers) to
    automatically use the correct indentation level.
    """

    _indent_level = 0
    _indent_prefix = "│   "

    @classmethod
    def get_indent(cls):
        """Get current indentation string."""
        if cls._indent_level == 0:
            return ""
        return cls._indent_prefix * cls._indent_level

    @classmethod
    def increase(cls):
        """Increase indentation level."""
        cls._indent_level += 1

    @classmethod
    def decrease(cls):
        """Decrease indentation level."""
        cls._indent_level = max(0, cls._indent_level - 1)

    @classmethod
    @contextmanager
    def nested(cls):
        """Context manager for nested indentation."""
        cls.increase()
        try:
            yield
        finally:
            cls.decrease()


class DisplayMixin:
    """
    Mixin providing display methods for computation progress.

    This mixin provides a consistent API for displaying progress
    during long-running operations like metric computation or clustering.

    The display uses a box-drawing style:
    ```
    ┌─ ComponentName
    │
    │ Step 1/3: Description
    │   ┌─ NestedComponent
    │   │ ...
    │   └─ Done (...)
    │
    │ Step 2/3: Description
    │
    └─ Done (1.23s)
    ```

    Attributes:
        _start_time: Timer started when _display_header is called.
    """

    def _get_indent(self):
        """Get current indentation string for nested display."""
        return DisplayIndentManager.get_indent()

    def _display_header(self, title=None):
        """
        Display computation header with box styling and start timer.

        Args:
            title: Header title. Defaults to class name.
        """
        # pylint: disable=attribute-defined-outside-init
        self._start_time = time.perf_counter()
        title = title or self.__class__.__name__
        indent = self._get_indent()
        tqdm.write(f"{indent}┌─ {title}")
        # tqdm.write(f"{indent}│")

    def _display_step(self, step, total, description, is_main=True):
        """
        Display a step in the computation.

        Args:
            step: Current step number (1-indexed).
            total: Total number of steps.
            description: Description of the current step.
            is_main: If True, display as main step. If False, as sub-step.
        """
        self._display_blank_line()
        indent = self._get_indent()
        if is_main:
            tqdm.write(f"{indent}│ Step {step}/{total}: {description}")
        else:
            tqdm.write(f"{indent}│   ({step}/{total}) {description}")

    def _display_message(self, message):
        """
        Display an informational message.

        Args:
            message: The message to display.
        """
        indent = self._get_indent()
        tqdm.write(f"{indent}│ {message}")

    def _display_blank_line(self):
        """Display a blank line with proper indentation."""
        indent = self._get_indent()
        tqdm.write(f"{indent}│")

    def _create_progress_bar(self, total, desc="Progress"):
        """
        Create a progress bar with proper indentation.

        Args:
            total: Total number of items.
            desc: Progress bar description.

        Returns:
            tqdm: Configured progress bar instance.
        """
        self._display_blank_line()
        indent = self._get_indent()
        return tqdm(total=total, desc=f"{indent}│ {desc}")

    def _display_footer(self, summary=None):
        """
        Display computation footer with result summary.

        Args:
            summary: Optional summary message (string or tuple for matrix shape).
                     If None, uses elapsed time only.
                     If tuple (rows, cols), formats as matrix dimensions.
        """
        elapsed = time.perf_counter() - getattr(self, "_start_time", 0)

        # Handle different summary types
        if summary is None:
            summary_str = f"{elapsed:.2f}s"
        elif isinstance(summary, tuple) and len(summary) == 2:
            # Matrix shape (rows, cols)
            summary_str = f"{summary[0]}x{summary[1]} matrix, {elapsed:.2f}s"
        else:
            summary_str = str(summary)

        indent = self._get_indent()
        tqdm.write(f"{indent}│")
        tqdm.write(f"{indent}└─ Done ({summary_str})")

    @contextmanager
    def _nested_display(self):
        """
        Context manager for nested display (e.g., metric inside clusterer).

        Increases indentation for any display calls within the context,
        including those from other components using DisplayIndentManager.
        """
        indent = self._get_indent()
        tqdm.write(f"{indent}│")

        with DisplayIndentManager.nested():
            yield
