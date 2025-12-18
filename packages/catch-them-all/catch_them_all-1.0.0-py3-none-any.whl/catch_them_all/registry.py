# catch_them_all/core.py supp= python 3.8+
"""Maintain a global registry of exception summaries.

This module dynamically builds and updates a registry of exception classes
and their docstring summaries. On import, the registry is populated with
built‑in exceptions and can be extended via ``rescan()`` to include those
from newly imported third‑party modules.

The formatter uses this registry to display human‑readable summaries in
error_report.
"""

from __future__ import annotations

from typing import Dict

from .utils import _scan_for_candidate_modules, _extract_exceptions_from_modules, _get_docs_summary

# ──────────────────────── BUILT-IN EXCEPTION SUMMARIES  ────────────────────────
BUILTIN_EXCEPTION_SUMMARIES: Dict[str, str] = {
    "builtins.BaseException": "The base class for all built-in exceptions. It is not meant to be directly inherited by user-defined classes (for that, use Exception).",
    "builtins.Exception": "All built-in, non-system-exiting exceptions are derived from this class. All user-defined exceptions should also be derived from this class.",
    "builtins.ArithmeticError": "The base class for those built-in exceptions that are raised for various arithmetic errors: OverflowError, ZeroDivisionError, FloatingPointError.",
    "builtins.FloatingPointError": "Not currently used.",
    "builtins.OverflowError": "Raised when the result of an arithmetic operation is too large to be represented.",
    "builtins.ZeroDivisionError": "Raised when the second argument of a division or modulo operation is zero.",
    "builtins.AssertionError": "Raised when an assert statement fails.",
    "builtins.AttributeError": "Raised when an attribute reference or assignment fails.",
    "builtins.BufferError": "Raised when a buffer related operation cannot be performed.",
    "builtins.EOFError": "Raised when the input() function hits an end-of-file condition (EOF) without reading any data.",
    "builtins.ImportError": "Raised when the import statement has troubles trying to load a module.",
    "builtins.ModuleNotFoundError": "A subclass of ImportError which is raised when a module could not be located.",
    "builtins.LookupError": "The base class for the exceptions that are raised when a key or index used on a mapping or sequence is invalid: IndexError, KeyError.",
    "builtins.IndexError": "Raised when a sequence subscript is out of range.",
    "builtins.KeyError": "Raised when a mapping (dictionary) key is not found in the set of existing keys.",
    "builtins.MemoryError": "Raised when an operation runs out of memory but the situation may still be rescued.",
    "builtins.NameError": "Raised when a local or global name is not found.",
    "builtins.UnboundLocalError": "Raised when a reference is made to a local variable in a function or method, but no value has been bound to that variable.",
    "builtins.OSError": "Raised when a system function returns a system-related error, including I/O failures such as “file not found” or “disk full”.",
    "builtins.BlockingIOError": "Raised when an operation would block on an object set for non-blocking operation.",
    "builtins.ChildProcessError": "Raised when an operation on a child process failed.",
    "builtins.ConnectionError": "Base class for connection-related issues.",
    "builtins.BrokenPipeError": "A subclass of ConnectionError, raised when trying to write on a pipe while the other end has been closed.",
    "builtins.ConnectionAbortedError": "A subclass of ConnectionError, raised when a connection attempt is aborted by the peer.",
    "builtins.ConnectionRefusedError": "A subclass of ConnectionError, raised when a connection attempt is refused by the peer.",
    "builtins.ConnectionResetError": "A subclass of ConnectionError, raised when a connection is reset by the peer.",
    "builtins.FileExistsError": "Raised when trying to create a file or directory which already exists.",
    "builtins.FileNotFoundError": "Raised when a file or directory is requested but doesn't exist.",
    "builtins.InterruptedError": "Raised when a system call is interrupted by an incoming signal.",
    "builtins.IsADirectoryError": "Raised when a file operation is requested on a directory.",
    "builtins.NotADirectoryError": "Raised when a directory operation is requested on something which is not a directory.",
    "builtins.PermissionError": "Raised when trying to run an operation without adequate access rights.",
    "builtins.ProcessLookupError": "Raised when a given process doesn't exist.",
    "builtins.TimeoutError": "Raised when a system function timed out at the system level.",
    "builtins.ReferenceError": "Raised when a weak reference proxy is used to access an attribute of the referent after it has been garbage collected.",
    "builtins.RuntimeError": "Raised when an error is detected that doesn't fall in any of the other categories.",
    "builtins.NotImplementedError": "Raised when an abstract method requires derived classes to override the method.",
    "builtins.RecursionError": "Raised when the maximum recursion depth has been exceeded.",
    "builtins.StopIteration": "Raised by built-in function next() and an iterator’s __next__() method to signal that there are no further items.",
    "builtins.StopAsyncIteration": "Must be raised by __anext__() method of an async iterator to stop the iteration.",
    "builtins.SyntaxError": "Raised when the parser encounters a syntax error.",
    "builtins.IndentationError": "Base class for syntax errors related to incorrect indentation.",
    "builtins.TabError": "Raised when indentation contains mixed tabs and spaces.",
    "builtins.SystemError": "Raised when the interpreter finds an internal error.",
    "builtins.TypeError": "Raised when an operation or function is applied to an object of inappropriate type.",
    "builtins.ValueError": "Raised when an operation or function receives an argument that has the right type but an inappropriate value.",
    "builtins.UnicodeError": "Raised when a Unicode-related encoding or decoding error occurs.",
    "builtins.UnicodeDecodeError": "Raised when a Unicode-related decoding error occurs.",
    "builtins.UnicodeEncodeError": "Raised when a Unicode-related encoding error occurs.",
    "builtins.UnicodeTranslateError": "Raised when a Unicode-related translation error occurs.",
    "builtins.Warning": "Base class for warning categories.",
    "builtins.UserWarning": "Base class for warnings generated by user code.",
    "builtins.DeprecationWarning": "Base class for warnings about deprecated features.",
    "builtins.PendingDeprecationWarning": "Base class for warnings about features which will be deprecated in the future.",
    "builtins.SyntaxWarning": "Base class for warnings about dubious syntax.",
    "builtins.RuntimeWarning": "Base class for warnings about dubious runtime behavior.",
    "builtins.FutureWarning": "Base class for warnings about constructs that will change semantically in the future.",
    "builtins.ImportWarning": "Base class for warnings about probable mistakes in module imports.",
    "builtins.UnicodeWarning": "Base class for warnings related to Unicode.",
    "builtins.BytesWarning": "Base class for warnings related to bytes and bytearray.",
    "builtins.ResourceWarning": "Base class for warnings related to resource usage.",
}

# ──────────────────────── THE ONE AND ONLY REGISTRY ────────────────────────
_registry: Dict[str, str] = BUILTIN_EXCEPTION_SUMMARIES.copy()  # ← start with built-ins

def _build_registry() -> None:
    """Build the exception summary registry from built-ins and loaded modules.

    Scans all currently imported modules for Exception subclasses and
    extracts their docstrings as summaries. Falls back to parent class
    docstrings if none is available.
        """
    modules = _scan_for_candidate_modules()
    exceptions = _extract_exceptions_from_modules(modules)

    for exc_name, exc_object in exceptions.items():
        _registry[f'{exc_object.__module__}.{exc_object.__name__}'] = _get_docs_summary(exc_object)



def rescan_imports() -> None:
    """Rebuild the registry by rescanning new non-cashed modules.

    Useful when new modules with exceptions have been imported after
    initial registry construction.
    """
    _build_registry()


__all__ = ["rescan_imports"]
