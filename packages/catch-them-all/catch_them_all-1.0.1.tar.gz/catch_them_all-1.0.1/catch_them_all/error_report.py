# catch_them_all/error_report.py supp= python 3.8+
"""Define the PokedexReport class, a structured error reporting object.

This module builds, renders, logs, and serializes error reports distilled
from traceback data. It supports rich terminal output, plain text logging,
JSON export, and context injection, all without side effects on import.
"""

import json
import sys
from typing import Callable, Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

from .console import console
from .utils import _distill_traceback
from .registry import _registry
from .formatter import Formatter


@dataclass
class PokedexReport:
    """A rich, structured representation of a Python exception.

        Encapsulates exception details, stack frames, summary information,
        timestamp, optional context, and chain of caused exceptions.
        Provides methods for rendering (rich/plain), logging (text/JSONL),
        and context injection.

        Attributes
        ----------
        name : str
            Name of the exception class (e.g., "ValueError").
        module : str
            Module where the exception is defined (e.g., "builtins").
        message : str
            The exception message/string representation.
        summary : str
            Human-readable one-line summary from the registry.

        frames : list[dict]
            List of distilled stack frame dictionaries.
        timestamp : str
            ISO-formatted timestamp when the exception occurred.
        caused_by : list[dict] | None
            Optional chain of causing exceptions (for exception chaining).
        context : dict
            User-provided additional context (e.g., user_id, request data).

        formatted_object : Formatter
            Internal Formatter instance used for rendering.
        json_format : dict
              Error info fo json dictionary
        log_format :  str
            Pre-rendered plain-text version of the report + footer for CLI output.
        rich_format : Group
            Pre-rendered Rich object for terminal display.
        str_format : str
            Pre-rendered plain-text version of the report.

        ╭── PokedexReport Instance Digram:
        │
        ├── Attributes:
        │:str  ├── name          : Exception class name (e.g., "ConnectionError"). ─────────────────────╮
        │:str  ├── module        : Module where the exception is defined (e.g., "requests.exceptions")  │
        │:str  ├── msg           : Exception message / string representation.                           │
        │:str  ├── summary       : One-line human-readable summary from the registry.                   │
        │:list ├── frames        : List of distilled stack frame dicts.(e.g., line_no, file...).        ├── Error Info
        │:str  ├── timestamp     : ISO timestamp when the exception occurred.                           │
        │:dict ├── caused_by     : Chain of causing exceptions (if any).                                │
        │:dict ├── user_context  : User-provided context (e.g., user_id, request data). ────────────────╯
        │      │
        │      ├── formatted_object : Internal Formatter instance for rendering. ───────────────────────╮
        │      │Panel        ├── header        : Exception box (summary + metadata).                    ├── Formatter components
        │      │:Panel       ├── frames        : Stack trace frames.                                    │
        │      │:Panel       └── context_panel : Injected user context. ────────────────────────────────╯
        │      │        (In case a user requires specific component)
        │      │
        │:dict ├── json_format   : Cached dict representation. ───────────────────────────────────╮
        │:str  ├── log_format    : Plain-text version without footer, suitable for logs.          ├── Output formats
        │:Group├── rich_format   : Rich object for styled terminal display.                       │
        │:str  ╰── str_format    : Plain-text CLI-friendly version. ──────────────────────────────╯
        │
        ├── Methods:
        │      ├── .to_dict()          : Return attributes as a Python dict. ──────────────────────╮
        │      ├── .to_log(path)       : Append plain-text report to a log file.                   │
        │      ├── .to_json(path=None) : Serialize to JSON string, or write to file if path given. ├── Report methods
        │      ├── .show()             : Render rich report to console.                            │
        │      ╰── .inject_context(ctx): Add user-defined context dictionary. ─────────────────────╯
        │
        ╰──────────────────────────────────────────────────────────────────────────────────────────╯
        """
    name: str
    module: str
    message: str
    summary: str
    frames: list[dict]
    timestamp: str
    caused_by: str | None = field(default_factory=list[dict])
    context: dict = field(default_factory=dict)

    formatted_object: Formatter = field(init=False)
    json_format: Dict = field(init=False)
    log_format: str = field(init=False)
    rich_format: Any = field(init=False)
    str_format: str = field(init=False)

    def __post_init__(self):
        """Build the formatted error report after dataclass initialization.

        Creates a Formatter instance from the current report data and
        assigns the pre-rendered rich and plain-text versions to the
        corresponding attributes.
        """
        self.formatted_object = Formatter(self.to_dict())  # build formatted error report

        self.rich_format = self.formatted_object.rich_format
        self.str_format = self.formatted_object.str_format
        self.log_format = self.formatted_object.log_format
        self.json_format = self.to_dict()

    @classmethod
    def from_dict(cls, data: dict) -> "PokedexReport":
        """Create a PokedexReport report from a pre-distilled error dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing distilled traceback data as produced by
            ``_distill_traceback()``.

        Returns
        -------
        PokedexReport
            Fully constructed error report ready for display or serialization.
        """
        exception = data.get("exception")
        err_name = exception.get("type")
        err_module = exception.get("module")
        err_msg = exception.get("message")

        err_obj = cls(
            name=err_name,
            message=err_msg,
            module=err_module,
            summary=_registry.get(f'{err_module}.{err_name}', "No Summary Available!"),
            # Human-readable summary from registry
            frames=data.get("frames", []),  # Stack frames (structured)
            timestamp=data.get("timestamp"),  # ISO timestamp when error occurred
            context=data.get("context", {}),
            caused_by=data.get("caused_by")
        )

        return err_obj

    def to_dict(self) -> dict:
        """
        Serialize the error into a clean, machine-readable dictionary.

        This is the canonical format for:
          • JSON logging
          • Sending to error tracking services
          • Storing in databases

        Returns:
            dict: Structured representation of the error.
        """
        return {
            "exception": {
                "type": self.name,
                "module": self.module,
                "message": self.message,

            },
            "summary": self.summary,  # One-line explanation from summary registry
            "frames": self.frames,  # List of structured stack frames
            "context": self.context,  # User/context data
            "timestamp": self.timestamp,  # Exception timestamp
            "caused_by": self.caused_by  # Error cause
        }

    def to_json(self, file_path: str | Path) -> None:
        """Append the report as a JSON line to the specified file."""
        # ╭─────────────────────────────────────────────────────────────╮
        file_path_to_str = str(file_path)  # better safe than sorry
        file_path = Path(file_path_to_str)

        # ╭──────────────────────────────────────────────────────────────────────╮
        with open(file_path, "a", encoding="utf-8") as f:
            json.dump(self.json_format, f, ensure_ascii=False)
            f.write("\n")  # One error per line → valid JSON Lines (.jsonl)

    def inject_context(self, context_dict: dict) -> None:
        """Inject additional contextual information and refresh the report."""

        self.context = context_dict  # save context to attribute
        self.formatted_object.inject_and_update_context(context_dict)
        self.rich_format = self.formatted_object.rich_format
        self.str_format = self.formatted_object.str_format

    def to_log(self, file_path: str | Path | None = None) -> None:
        """Write the report to a log file or stderr.

        Parameters
        ----------
        file_path : str, Path, or None
            Destination path. ``.txt`` files receive plain text, ``.jsonl`` files
            receive JSON lines. ``None`` writes plain text to ``sys.stderr``.
        """

        # ╭─────────────────────────────────────────────╮
        if file_path is None:
            print(self.str_format, file=sys.stderr)
            return
        # ╭──────────────────────────────────────────────────────────────╮
        file_path_to_str = str(file_path)  # Better safe than sorry
        safe_path = Path(file_path_to_str)

        # ╭─────────────────────────────────────────────────────────────────────╮
        # Get the extension (including the dot)
        suffix = safe_path.suffix.lower()  # → ".txt", ".jsonl", ".log", ""

        # ╭───────────────────────────────╮
        if suffix in {".json", ".jsonl"}:
            self.to_json(str(safe_path))

        else:
            # No extension? -> force .txt
            if not safe_path.suffix:  # if suffix is empty string
                safe_path = safe_path.with_suffix(".txt")
            # ╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮
            # Structured traceback to -> log file
            with open(safe_path, "a", encoding="utf-8") as f:
                f.write(f"{self.log_format}\n\n\n")

    def show(self) -> None:
        """Display the rich formatted error report in the terminal︵◓."""

        console.print(self.rich_format)

    @classmethod
    def from_current_exception(cls, context: dict | None = None) -> "PokedexReport":
        """Create a PokedexReport report from the currently active exception.

        Uses ``_distill_traceback()`` to capture the current exception state.

        Parameters
        ----------
        context : dict, optional
            Additional contextual data to inject into the report.

        Returns
        -------
        PokedexReport
            Report representing the current exception.
        """

        exception_data = _distill_traceback()
        error_report = cls.from_dict(exception_data)

        if context is not None:  # if context -> inject
            error_report.inject_context(context)
            return error_report
        else:
            return error_report

    def __str__(self):
        return self.str_format
