# catch_them_all/formatter.py supp= python 3.8+
"""Render PokedexReport error data into rich and plain text reports.

This module converts distilled traceback information into visually enhanced
terminal output using Rich primitives, while also maintaining a clean
plain‑text format for logging. It manages theming, safe rendering, path
shortening, and height/width control without side effects on import.
"""

from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.style import Style as rich_Style
from rich.padding import Padding
from rich import box
from datetime import datetime

from .console import console
from .themes import Style

_CURRENT_STYLE = Style.load_style()  # autoload user theme or defaults

_RECORDING_CONSOL = Console(
    force_terminal=False,  # no colors
    record=True,
    width=console.width  # capture output

)


def set_global_style(new_style: Style) -> None:
    """Set the global Style instance used by all formatters.

        Parameters
        ----------
        new_style
            The new Style instance to use globally.

        Raises
        ------
        TypeError
            If new_style is not an instance of Style.
        """
    global _CURRENT_STYLE

    if isinstance(new_style, Style):
        _CURRENT_STYLE = new_style

    else:
        err_msg = f"\n\t- >{new_style}< Is not an intense of the Style class make sure to pass an instance of Style\n"
        raise TypeError(err_msg)


def restore_default_style():
    """
    Restore the default theme for excepthook and pokeball.

    Resets styling and colors back to the built‑in defaults.
    """

    # Create an instance of Style it uses the default theme automatically > Style()
    # export theme, so it loads automatically on import > .export_style()
    default_theme = Style()
    default_theme.export_style()
    # load it for the current session
    set_global_style(default_theme)


@dataclass
class Formatter:
    """Renders error data into rich terminal output and plain text logs.

        Takes structured error data as a dict and produces a
        visually ordered, and organized report using Rich primitives while maintaining a clean
        plain-text version for logging. Supports global theming, safe handling
        of unprintable objects, path shortening, and height/width control to
        prevent terminal overflow.
        """
    data: dict
    header: Any = field(init=False)  # report header
    frames: Any = field(init=False)  # report trace frames
    context_panel: Any = field(default=None, init=False)  # user context if provided
    str_format: str = field(init=False)  # a string version of the report CLI friendly
    log_format: str = field(init=False)  # same as str_format but without the bottom exception box

    rich_format: Any = field(
        init=False)  # a rich object version of the report with additional header at the bottom

    def __post_init__(self) -> None:
        """Build the complete rich and plain reports after dataclass initialization.
            """

        self.style: Style = _CURRENT_STYLE  # initiate style attribute

        self._build_header_and_frames()  # fill header and frames attributes

        self.assemble_all()

    def assemble_all(self) -> None:
        """Combine all panels into the final rich Group and plain string reports.
            """

        # ╭────────── Build The Two Versions Of The Formatted Report─────────────────╮
        self.log_format = self._to_str(
            Group(self.header,
                  self.context_panel if self.context_panel is not None else "",
                  *self.frames
                  ))

        self.str_format = self._to_str(
            Group("",  # a little spacer from the top edge
                  self.header,
                  self.context_panel if self.context_panel is not None else "",
                  *self.frames,
                  self.header if len(self.frames) > 2 else ""
                  ))

        # ╭───────────────────────────────────────────────────────────────────────────────────────────╮
        self.rich_format = Group("",  # a little spacer from the top edge
                                 self.header,
                                 self.context_panel if self.context_panel is not None else "",
                                 *self.frames,
                                 self.header if len(self.frames) > 2 else ""
                                 )

    def _build_header_and_frames(self) -> None:
        """Construct the header panels and stack frame panels from the error data.
            """

        # ╭───────────────────────── 1. Extract core exception data ─────────────────────────╮
        # ╭──── 1. Safe extraction ──────────────────────────────────╮
        exc = self.data.get("exception") or {}
        exc_name = exc.get("type", "UnknownError!")
        exc_module = exc.get("module", "")
        exc_message = exc.get("message", "")
        summary = self.data.get("summary", "No Summary Available!")

        caused_by: list[dict] = self.data.get("caused_by", [])
        frames: list[dict] = self.data.get("frames", [])
        raw_timestamp = self.data.get("timestamp", None)
        # ╰──────────────────────────────────────────────────────────╯

        # ╭─── 2. Safe timestamp  ─────────────────╮
        parsed_timestamp = self._parse_timestamp(raw_timestamp)
        # ╰──────────────────────────────────────╯

        # ╭───────────────────────── 3. Build header title (left-aligned) ─────────────────────────────────────────╮
        header_title = Text()
        header_title.append("Exception: ", f" {self.style.labels}")
        header_title.append(exc_name, self.style.header_exception)
        header_title.append(" ── ", self.style.header_border)
        header_title.append("Timestamp: ", self.style.labels)
        header_title.append(parsed_timestamp, self.style.header_timestamp)
        # ╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

        # ╭───────────────────────── 4. Build header content  ──────────── Exception info (top part)───────────────╮
        header_content = Text()

        # ╭─ 4.1. ──────────────────────── 1. Build Summary  ────────────────────────────────────────────────────╮
        header_content.append("  Summary: ", self.style.labels)
        header_content.append(summary,
                              self.style.header_summary if summary != "No Summary Available!" else self.style.muted)
        if summary != "No Summary Available!":
            if exc_module:
                header_content.append(f"\n      ╰─>: From '{exc_module}.{exc_name}' Docs.", self.style.labels)
            else:
                pass
        # ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯

        # ╭─ 4.2.──────────────────────── 2. Build Message  ─────────────────────────────────────────────────────╮
        # ╭──── _build_truncated_message ────────────────────╮
        msg_text = self._build_truncated_message(exc_message)

        header_content.append("\n  Message: ", self.style.labels)
        header_content.append(msg_text or Text("<no message>", style=self.style.muted),

                              )
        # ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯

        # ╭─ 4.2.──────────────────────── 3. Build Cause ────────────────────────────────────────────────────────╮
        if caused_by:
            header_content.append(f"\n")
            for item in caused_by:
                header_content.append("\n  Caused by: ", self.style.labels)
                header_content.append(f"{item.get('type')}: ", self.style.header_exception)
                header_content.append(f"{self._safe_str(item.get('message'))} ", self.style.header_cause)
                header_content.append(f"\n")

        else:
            header_content.append("\n    Cause: ", self.style.labels)
            header_content.append("No Cause Available.", self.style.muted)

        # ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯

        # ╭───────────────────────── 5. Apply header + build final layout ────────────────╮
        _header_panel = Panel(
            header_content,
            title=header_title,
            subtitle="",
            border_style=self.style.header_border,
            title_align="left",
            box=box.ROUNDED,
            padding=(0, 0, 0, 3),  # (top, right, bottom, left)
            expand=False,  # ← So text does not wrap prematurely

        )
        self.header = _header_panel  # 5. Store the built header
        # ╰─────────────────────────────────────────────────────────────────────────────────╯

        # ╭─Build frames───────────────────────────────────╮
        frame_panels = []

        for i, frame in enumerate(frames):
            panel = self._build_frame_panel(frame)
            indent = min(i * self.style.stack_indent, 40)
            indented = Padding(panel, pad=(0, 0, 0, indent))  # 40 is the maximum indent level
            frame_panels.append(indented)

        # ╭── 6.  Store the built frames ──╮
        self.frames = frame_panels

    def _build_context_panel(self, context_dict: dict) -> None:
        """Build the context information panel.

            Parameters
            ----------
            context_dict : dict
                Context data to display.

            Returns
            -------
            Panel
                Styled context panel.
            """

        # Build context panel
        ctx_lines = Text()
        for i, (key, value) in enumerate(context_dict.items()):
            if i > 0:
                ctx_lines.append("\n")
            ctx_lines.append(f"  • {key}: ", self.style.context_keys)
            ctx_lines.append(self._safe_str(value), self.style.context_values)

        context_panel = Panel(
            ctx_lines,
            title=Text("Context:", style=self.style.labels),
            title_align="left",
            border_style=self.style.context_border,
            box=box.ROUNDED,
            padding=(0, 1, 0, 1),
            expand=False
        )

        self.context_panel = context_panel  # Storing the finished panel

    @staticmethod
    def _to_str(object_to_transform: Group) -> str:
        """Convert a Rich Group object to a plain text string for logging.

            Parameters
            ----------
            group : Group
                The Rich Group object containing the formatted report panels.

            Returns
            -------
            str
                Plain text representation of the report, suitable for log files.
            """

        with _RECORDING_CONSOL.capture() as capture:
            _RECORDING_CONSOL.print(object_to_transform)
        return str(capture.get())

    def inject_and_update_context(self, context_dict: dict) -> None:
        """Update context data and rebuild the report.

            Parameters
            ----------
            context_dict : dict
                context dictionary to inject.
            """
        self._build_context_panel(context_dict)
        self.assemble_all()

    @staticmethod
    def _safe_str(obj: Any) -> str:
        """Convert object to string safely, returning "<unprintable>" on failure.

            Parameters
            ----------
            obj : Any
                Object to convert.

            Returns
            -------
            str
                String representation or fallback.
            """
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"

    @staticmethod
    def _parse_timestamp(timestamp: str | None) -> str:
        """Parse raw timestamp string or return fallback.

        Parameters
        ----------
        timestamp : str or None
            The raw timestamp value from error data.

        Returns
        -------
        str
            Formatted timestamp or fallback string.
        """
        UNKNOWN_TIME = "Unknown Time!"

        if timestamp is None:
            return UNKNOWN_TIME
        else:
            try:
                # Safe Z replace — only if it's at the end
                parsed = timestamp
                if parsed.endswith("Z"):
                    parsed = parsed[:-1] + "+00:00"
                ts = datetime.fromisoformat(parsed)
                timestamp_str = ts.strftime("%Y-%m-%d %H:%M:%S")
                return timestamp_str
            except Exception:  # Exception is Broad Intentionally
                timestamp_str = UNKNOWN_TIME
                return timestamp_str

    @staticmethod
    def _shorten_path(full_path: str) -> str:
        """Shorten a file path to show only the immediate parent folder and filename.

            Parameters
            ----------
            full_path : str
                Full file path.

            Returns
            -------
            str
                Shortened path.
            """
        try:
            p = Path(full_path)
            if p.drive:
                # Use .as_posix() → forces forward slashes
                short = Path(p.drive, p.anchor, p.parent.name, p.name).as_posix()
                return short
            else:
                return f"{p.parent.name}/{p.name}"
        except Exception:  # ← yes, broad on purpose
            return "<invalid path>"

    def _build_truncated_message(self, exc_message: str) -> Text:
        """Create a height- and width-safe message Text object with head+tail logic.

            Parameters
            ----------
            exc_message : str
                The raw exception message.

            Returns
            -------
            Text
                Truncated and styled message ready for rendering.
            """

        # ╭──── 4.2 ── Format and Limit Exception Message  ────────────────────────────────────╮

        raw_lines = (exc_message or "").splitlines()
        max_visual_chars = console.width - 20  # 20 for borders/padding
        msg_text = Text(overflow="fold", style=self.style.header_message)  # let Rich fold long lines
        if len(raw_lines) <= 7:
            lines = raw_lines
        else:
            lines = raw_lines[:6] + ["..."] + raw_lines[-1:]

        for line in lines:
            if line == "...":
                msg_text.append("... (truncated)", style="dim italic")
            else:
                truncated = line[:max_visual_chars - 3] + "..." if len(line) > max_visual_chars else line
                msg_text.append(truncated)

            # Only add real newline between logical lines
            if line is not lines[-1]:  # not the last one
                msg_text.append("\n")

        return msg_text

    def _build_frame_panel(self, frame_data: dict) -> Panel:
        """Build a single stack frame panel with indentation and source code.

            Parameters
            ----------
            frame_data : dict
                Single frame data from traceback.

            Returns
            -------
            Panel
                Indented frame panel.
            """

        # ╭─── Safe extraction  ──────────────────────────────────────────────────────╮
        full_path = self._safe_str(frame_data.get("file") or "<╰>: No File!>")
        line_no = frame_data.get("line", 0)
        function = self._safe_str(frame_data.get("function") or "<╰>: No Function!>")
        code_line = self._safe_str(frame_data.get("code") or "<╰>: No Source Code!>")

        # ╭─── Safe path shortening ──────────────╮
        short_path = self._shorten_path(full_path)

        truncated_code_line = code_line.strip()[:500] + ("..." if len(code_line.strip()) > 500 else "")

        # ╭─── Content — safe even if code_line is large ───────────────────────────╮
        content = Text()
        content.append("• file:", self.style.labels)  #
        content.append(" line ", self.style.stack_file_path)
        content.append(self._safe_str(line_no), self.style.stack_func_and_line_no)
        content.append(" in ", rich_Style.parse(self.style.labels).color.name)  # use color name without bg_color
        content.append(short_path or "<no path>", self.style.stack_file_path)
        content.append("\n")
        content.append("• code: ", self.style.labels)
        content.append(self._safe_str(truncated_code_line),
                       self.style.stack_code)

        # ╭─── Title ───────────────────────────────────────────────╮
        title = Text()
        title.append(function, self.style.stack_func_and_line_no)
        if not function.endswith(">"):
            title.append("()", self.style.stack_func_parenthesis)

        return Panel(
            content,
            title=title,
            title_align="left",
            border_style=self.style.stack_border,
            box=box.ROUNDED,
            padding=(0, 2, 0, 3),  # (top, right, bottom, left)
            expand=False,  # ← So text does not wrap prematurely

        )


__all__ = ["set_global_style", "restore_default_style"]
