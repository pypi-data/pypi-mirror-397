# catch_them_all/excepthook.py
"""Integrate a global exception handler.

This module installs the PokedexReport handler as sys.excepthook to render
uncaught exceptions with rich output. It includes a safety fallback to
Python's default handler to ensure reliability.
"""

import sys
from .error_report import PokedexReport
from .utils import _distill_traceback

_original_excepthook = sys.__excepthook__


def install_excepthook() -> None:
    """Replace the default sys.excepthook with PokedexReport's beautiful handler.

    All uncaught exceptions will be rendered using the rich PokedexReport report.
    System exceptions (KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError) remain
    unaffected and propagate normally.
    """

    def handler(exc_type, exc_value, exc_traceback):
        # Let intentional exits pass through
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError)):
            return _original_excepthook(exc_type, exc_value, exc_traceback)

        # All other uncaught exceptions → beautiful report
        try:
            data = _distill_traceback(exc_type, exc_value, exc_traceback)
            report = PokedexReport.from_dict(data)
            report.show()
        except Exception:
            # Nuclear safety: if the handler crashes → fall back to original
            _original_excepthook(exc_type, exc_value, exc_traceback)

    sys.excepthook = handler


def disable_excepthook() -> None:
    """Restore Python's original built-in exception handler.

    Reverses the effect of PokedexReport_enable().
    """
    sys.excepthook = _original_excepthook


__all__ = ["install_excepthook", "disable_excepthook"]
