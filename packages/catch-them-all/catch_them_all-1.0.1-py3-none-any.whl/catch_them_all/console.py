# catch_them_all/console.py supp= python 3.8+

"""Provide a global Rich console instance for consistent terminal output.

This module defines a single, preconfigured Console used throughout the
library to render rich reports. Its configuration ensures reliable color
and width behavior across terminals, IDEs (including PyCharm), and
recorded exports.
"""

from rich.console import Console

# The one and only console — created once, used everywhere
console = Console(
    force_terminal=True,
    record=True,

    color_system="auto",       # Enables color detection with FORCE_COLOR support
    legacy_windows=False,            # ← this = so PyCharm finally obeys and shows color
    highlight=True,
)
# Enforce a minimum width for consistent report layout
console.width = max(console.size.width, 120)

__all__ = ["console"]
