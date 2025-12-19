# catch_them_all/utils.py supp= python 3.8+
"""Provide introspection utilities for traceback distillation and registry construction.

This module offers side‑effect‑free tools for extracting frames, scanning
modules, and building an exception summary registry. Importing it does not
mutate state.
"""

from __future__ import annotations

import inspect
import sys
import traceback
from datetime import datetime
from pathlib import Path
from threading import Lock
from types import ModuleType, TracebackType
from typing import Any, Dict, Optional, Type
_scanned_lock = Lock()   # <-- module level, one time


# Internal set — tracks which modules have already been scanned for incremental rescan performance
_scanned_modules: set[str] = set()


# ------------------------------------------------------------------
# 1. Find candidate modules that can be safely introspected
# ------------------------------------------------------------------
def _scan_for_candidate_modules() -> Dict[str, ModuleType]:
    """Return a dict of module_name → module_object for modules that:
        - Have a real source file on disk
        - Are not frozen, C extensions, or namespace packages
        - Have not been scanned before (incremental rescan support)

        This function is deliberately private and used only by the public rescan() in core.py.

        Returns
        -------
        Dict[str, ModuleType]
            Mapping of module names to module objects ready for exception extraction.
        """

    with _scanned_lock:
        modules_dict: Dict[str, ModuleType] = {}

        for name, module in sys.modules.items():
            if not module:
                continue


            if not hasattr(module, "__file__"):
                continue

            file_path = module.__file__
            if not isinstance(file_path, str):
                continue
            if file_path.startswith("<") and file_path.endswith(">"):   # frozen, REPL, etc.
                continue
            if file_path.endswith((".so", ".pyd", ".dll")):              # C extensions
                continue
            if name in _scanned_modules:
                continue

            modules_dict[name] = module

        # Mark these modules as processed for future incremental rescans
        _scanned_modules.update(modules_dict.keys())

        return modules_dict

# ------------------------------------------------------------------
# 2. Extract exception classes from modules
# ------------------------------------------------------------------
def _extract_exceptions_from_modules(
    modules: Dict[str, ModuleType],
) -> Dict[str, Type[BaseException]]:
    """Extract all concrete exception classes from the given imported modules.

        Returns a deduplicated registry keyed by the exception's **original defining module**
        (`exception.__module__ + "." + exception.__name__`), ignoring any module that merely
        re-exports it.

        This gives one clean entry per exception class and matches the naming used in tracebacks,
        IDEs, and documentation tools.

        Parameters
        ----------
        modules : Dict[str, ModuleType]
            Dict of module_name → module object from _scan_for_candidate_modules().

        Returns
        -------
        Dict[str, Type[BaseException]]
            Mapping "defining_module.ExceptionName" → exception class.
        """
    exceptions: Dict[str, Type[BaseException]] = {}

    # Control-flow exceptions are part of the language runtime -> always exclude
    excluded = {KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError}

    for mod_name, module in modules.items():
        # Some third-party modules raise during attribute access (lazy loaders,
        # __getattr__ traps, permission errors, etc.). must not let one bad module
        # kill the entire scan.
        try:
            # Walk module.__dict__ directly to avoid triggering __getattr__ side effects
            for _attr_name, obj in module.__dict__.items():
                if not inspect.isclass(obj):
                    continue
                if not issubclass(obj, BaseException):
                    continue
                if obj in excluded:
                    continue
                if inspect.isabstract(obj):
                    # Abstract base exceptions (ABC or @abstractmethod) are not instantiable
                    # and are never meant to be caught directly.
                    continue

                # ------------------------------------------------------------------
                # Canonical name resolution – the heart of the function
                # ------------------------------------------------------------------
                defining_module = getattr(obj, "__module__", None)
                if not defining_module:
                    # Extremely rare corner case (e.g. class created with types.new_class)
                    # without setting __module__). Skip it – nothing sane to do.
                    continue

                # Only register exceptions that were originally defined inside one of
                # the packages that are being scanned. This prevents stdlib exceptions or
                # unrelated third-party exceptions from leaking in just because they
                # are re-exported somewhere.
                if defining_module not in modules:
                    continue

                module_exception_key = f"{defining_module}.{obj.__name__}"
                exceptions[module_exception_key] = obj   # deduplication happens automatically

        except Exception:  # noqa: BLE001
            # So to not let a single problematic module abort the whole registry build.
            # This is battle-tested behaviour in tools like pytest, coverage, etc.
            continue

    return exceptions



# ------------------------------------------------------------------
# 3. Extract human-readable summaries from docstrings
# ------------------------------------------------------------------

def _get_docs_summary(cls: Type) -> str:
    """Return the one-line docstring summary with proper inheritance, falls back to parent docs if child has None or empty docs .

    Empty or whitespace-only docstrings are ignored (treated as absent).

    Parameters
    ----------
    cls : Type
        The exception class.

    Returns
    -------
    str
        First line of the docstring or fallback message.
    """
    doc = inspect.getdoc(cls)

    # Critical: treat None, '', or all-whitespace as "no docstring"
    if doc is None or doc.strip() == "":
        doc = f"Undocumented exception for: {cls.__name__}"

    return doc.partition("\n")[0]


# ------------------------------------------------------------------
# 4. Distill traceback into clean structured format
# ------------------------------------------------------------------
def _distill_traceback(
    exc_type=None,
    exc_value=None,
    tb: Optional[TracebackType] = None,
    max_frames: Optional[int] = 100
) -> Dict[str, Any]:
    """Distill a traceback into a structured dictionary for formatting.

    Parameters
    ----------
    tb : TracebackType or None, optional
        Traceback object to distill. If None, uses sys.exc_info().
    max_frames : int, optional
        Maximum number of frames to include.

    Returns
    -------
    dict
        Structured error data containing exception info, frames, and optional
        caused_by chain.
    """

    # Initiate Timestamp
    timestamp = datetime.utcnow().isoformat()

    if tb is None:
        exc_type, exc_value, tb = sys.exc_info()
        if exc_type is None:
            return {
                "frames": [],
                "exception": {"type": f"NoException", "message": "No active exception"},
                "caused_by": [],
                "context": {},
                "timestamp" : timestamp,
            }


    # Extract frames using the official parser
    extracted_frames = traceback.extract_tb(tb, limit=max_frames)

    frames = []
    for frame in extracted_frames:
        frames.append({
            "file": Path(frame.filename).as_posix(), # <- Converts the path to a POSIX string (forward slashes only)
            "line": frame.lineno,
            "function": frame.name,
            "code": frame.line.strip() if frame.line else None,
        })
    # Build the primary exception info
    primary_exc = {
        "type": exc_type.__name__ if exc_type else "Unknown",
        "module": exc_type.__module__ ,
        "message": str(exc_value) if exc_value else ""
    }

    # Walk the exception chain (cause + context)
    caused_by = []
    current = exc_value
    # Move to the first linked exception (skip the primary)
    while True:
        next_link = None
        if current is None:
            break
        if getattr(current, "__cause__", None) is not None:
            next_link = current.__cause__
        elif (getattr(current, "__context__", None) is not None and
              not getattr(current, "__suppress_context__", False)):
            next_link = current.__context__
        else:
            break

        if next_link is None:
            break

        # Append this linked exception
        caused_by.append({
            "type": type(next_link).__name__,
            "message": str(next_link)
        })

        # Advance
        current = next_link

    return {
        "frames": list(reversed(frames)), # reversed(frames) to restore original frame depth
        "exception": primary_exc,
        "caused_by": caused_by,
        "context": {},
        "timestamp": timestamp,
    }





























