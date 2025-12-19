# __init__.py
"""catch_them_all — a comprehensive exception handling package for Python.

This package provides a single decorator that intercepts uncaught exceptions
and converts them into PokedexReport objects. A PokedexReport encapsulates
exception details into structured attributes and exposes methods for rendering,
logging, serialization, and contextual injection.

The package also integrates with sys.excepthook to override the global
exception handler, ensuring consistent behavior across environments. Error
reports are rendered with clear, colorful, and structured output that associates
colors with exception types. The theming system is fully customizable, allowing
users to tailor the appearance of reports while maintaining readability in both
terminals and logs.
"""
from .core import pokeball
from .registry import rescan_imports, _build_registry
from .themes import Style
from .formatter import set_global_style, restore_default_style
from .excepthook import install_excepthook, disable_excepthook

# Build _registry on import
_build_registry()
# auto-install on import
install_excepthook()


__version__ = "1.0.0"
__all__ = ["pokeball",  #core.py
           "rescan_imports",  #registry.py
           "Style",  #themes.py
           "set_global_style",  #formatter.py
           "restore_default_style",  #formatter.py
           "install_excepthook",  #excepthook.py
           "disable_excepthook"] #excepthook.py


















...
