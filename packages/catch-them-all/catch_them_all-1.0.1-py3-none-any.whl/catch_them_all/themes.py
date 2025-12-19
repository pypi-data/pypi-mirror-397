# catch_the_all/themes.py supp= python 3.8+
"""Define a theming system for error report appearance.

This module provides the Style dataclass for customizing colors, borders,
and layout. It supports loading and exporting user themes from
~/.catch_them_all/style.json and applying styles globally.
"""
import json
import sys
from typing import Dict
from pathlib import Path
from rich.text import Text
from rich.style import Style as rich_Style

DEFAULT_STYLE_PATH = Path.home() / ".catch_them_all" / "style.json"


class Style:
    """Configuration class for customizing the visual appearance of error reports.

        Allows full control over colors, text styles, borders, and indentation used
        in the rich terminal rendering of PokedexReport objects. Themes can be saved
        to and loaded from JSON files for persistence.

        All color/style strings follow Rich's syntax (e.g., "bold red", "bright_cyan",
        "underline italic white").

        Attributes
        ----------
        labels : str
            Style for field labels (e.g., "Summary:", "Message:").

        muted : str
            Style for less prominent text.

        header_border : str
            Border color/style for the main header panel.
        header_exception : str
            Style for the exception type name in the header.
        header_timestamp : str
            Style for the timestamp in the header.
        header_summary : str
            Style for the human-readable exception summary.
        header_message : str
            Style for the exception message content.
        header_cause : str
            Style for the "Caused by" label.


        stack_indent : int
            Number of spaces to indent each deeper stack frame (clamped to 0–6).
        stack_border : str
            Border style for individual stack frame panels.
        stack_func_and_line_no : str
            Style for function name and line number in stack frames.
        stack_code : str
            Style for the source code line and parentheses.
        stack_file_path : str
            Style for the file path in stack frames.

        context_border : str
            Border style for the optional context panel.
        context_keys: str
            Style for keys in the injected context dictionary.
        context_values : str
            Style for values in the injected context dictionary.

        ╭── Style Instance Diagram:
        │
        ├── Attributes:
        │:str  ├── labels   : Style for metadata labels (e.g. "message:", "code:", "info:").   ├── Generic
        │:str  ├── muted    : Style for secondary or de‑emphasized text.
        │      │
        │:str  ├── header_border       : Border style for header panel. (e.g., "medium_turquoise") ─────────────────────╮
        │:str  ├── header_exception    : Style for exception type in header. (e.g., "bold yellow")                      │
        │:str  ├── header_timestamp    : Style for timestamp in header. (e.g., "italic #af00ff")                        ├──{Exception Header Propoerties}
        │:str  ├── header_summary      : Style for summary line. (e.g., "italic rgb(175,0,255)")                        │
        │:str  ├── header_message      : Style for message label.                                                       │
        │:str  ├── header_cause        : Style for cause label. ────────────────────────────────────────────────────────╯
        │      │
        │:int  ├── stack_indent               : Indentation spaces per frame level (0–6).─────────────────────╮
        │:str  ├── stack_border               : Border style for frame panels.                                ├──{Traceceback Stack Properties}
        │:str  ├── stack_func_and_line_no     : Style for function name + line number.                        │
        │:str  ├── stack_file_path            : Style for file path. ─────────────────────────────────────────╯
        │      │
        │:str  ├── context_border : Border style for user context panel.────────────────────────────────────────╮
        │:str  ├── context_keys   : Style for user context Dict keys.                                           ├──{User Injected Context Properties}
        │:str  ╰── context_values : Style for user context Dict values.─────────────────────────────────────────╯
        │
        ├── Methods:
        │      ├── styles()       : Return list of available Rich text styles.
        │      ├── colors()       : Return list of available Rich colors.
        │      ├── export_style() : Export current Style to JSON file.
        │      ├── load_style()   : Load Style from JSON file or defaults.
        │      ╰── to_dict()      : Serialize Style instance to dictionary.
        │
        ╰─────────────────────────────────────────────────────────────────╯
        """

    RICH_COLORS = [
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        "bright_black", "bright_red", "bright_green", "bright_yellow",
        "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
        "grey0", "navy_blue", "dark_blue", "blue3", "blue1", "dark_green",
        "deep_sky_blue4", "dodger_blue3", "dodger_blue2", "green4",
        "spring_green4", "turquoise4", "deep_sky_blue3", "dodger_blue1",
        "green3", "spring_green3", "dark_cyan", "light_sea_green",
        "deep_sky_blue2", "deep_sky_blue1", "spring_green2", "cyan3",
        "dark_turquoise", "turquoise2", "green1", "spring_green1",
        "medium_spring_green", "cyan2", "cyan1", "chartreuse4",
        "dark_sea_green4", "pale_turquoise4", "steel_blue", "steel_blue3",
        "cornflower_blue", "chartreuse3", "pale_green3", "sea_green3",
        "aquamarine3", "medium_turquoise", "steel_blue1", "chartreuse2",
        "sea_green2", "sea_green1", "aquamarine1", "dark_slate_gray2",
        "dark_magenta", "dark_violet", "purple", "light_pink4", "plum4",
        "medium_purple3", "slate_blue1", "yellow4", "wheat4", "grey53",
        "light_slate_grey", "medium_purple", "light_slate_blue", "yellow3",
        "dark_olive_green3", "dark_sea_green", "light_sky_blue3", "sky_blue2",
        "chartreuse2", "dark_olive_green3", "pale_green3", "dark_sea_green3",
        "dark_slate_gray3", "sky_blue1", "chartreuse1", "light_green",
        "pale_turquoise1", "red3", "deep_pink4", "medium_violet_red",
        "magenta3", "dark_violet", "purple", "dark_orange3", "indian_red",
        "hot_pink3", "medium_orchid3", "medium_orchid", "medium_purple2",
        "dark_goldenrod", "light_salmon3", "rosy_brown", "grey63",
        "medium_purple3", "gold3", "dark_khaki", "navajo_white3", "grey69",
        "light_steel_blue3", "light_steel_blue", "yellow3",
        "dark_olive_green3", "dark_sea_green3", "light_cyan3",
        "light_sky_blue1", "green_yellow", "dark_olive_green2",
        "pale_green1", "dark_sea_green2", "dark_sea_green1", "pale_turquoise1",
        "red3", "deep_pink3", "deep_pink3", "magenta3", "magenta2",
        "dark_orange3", "indian_red", "hot_pink3", "hot_pink2", "orchid",
        "medium_orchid1", "orange3", "light_salmon3", "light_pink3",
        "pink3", "plum3", "violet", "gold3", "light_goldenrod3", "tan",
        "misty_rose3", "thistle3", "plum2", "yellow3", "khaki3",
        "light_goldenrod2", "light_yellow3", "grey84", "light_steel_blue1",
        "yellow2", "dark_olive_green1", "dark_sea_green", "honeydew2",
        "light_cyan1", "red1"
    ]
    RICH_STYLES = [
        "bold", "dim", "italic", "underline", "blink",
        "reverse", "conceal", "strike", "overline",
        "not_bold", "not_dim", "not_italic", "not_underline",
        "not_blink", "not_reverse", "not_conceal", "not_strike"
    ]

    def __init__(self,
                 labels: str = "light_goldenrod2",
                 muted: str = "white",
                 # Header style:
                 header_border: str = "light_slate_blue",
                 header_exception: str = "bold sea_green1 on grey15",
                 header_timestamp: str = "plum1 on grey3",
                 header_summary: str = "bright_white",
                 header_message: str = "bright_white",
                 header_cause: str = "bright_white on grey23",

                 # Stack Frame style:
                 stack_indent: int = 2,  # max indent is  6
                 stack_border: str = "#3b96ff",
                 stack_func_and_line_no: str = "light_green on grey11",
                 stack_code: str = "bold medium_turquoise on grey11",
                 stack_file_path: str = "italic bright_white",

                 # Context Block style:
                 context_border: str = "plum1",
                 context_keys: str = "light_goldenrod2",
                 context_values: str = "bold bright_white",
                 ):
        """Initialize a Style instance with custom visual configuration.

            Parameters
            ----------
            labels : str, optional
                Rich style for field labels.
                Default text style.
            muted : str, optional
                Muted color style

        # Header style:
            header_border : str, optional
                Border style for header panel.
            header_exception : str, optional
                Style for exception type in header.
            header_timestamp : str, optional
                Style for timestamp in header.
            header_summary : str, optional
                Style for summary line.
            header_message : str, optional
                Style for message label.
            header_cause : str, optional
                Style for cause label.


        # Stack Frame style:
            stack_indent : int, optional
                Indentation spaces per stack frame level (clamped to 0–6).
            stack_border : str, optional
                Border style for frame panels.
            stack_func_and_line_no : str, optional
                Style for function name and line number.
            stack_code_and_parenthesis : str, optional
                Style for source code line.
            stack_file_path : str, optional
                Style for file path.

        # Context Block style:
            context_border : str, optional
                Border style for context panel.
            context_content : str, optional
                Style for context dict value.
            """

        self.labels: str = labels
        self.muted: str = muted
        # Header style:
        self.header_border: str = header_border
        self.header_exception: str = header_exception
        self.header_timestamp: str = header_timestamp
        self.header_summary: str = header_summary
        self.header_message: str = header_message
        self.header_cause: str = header_cause

        # Stack Frame style:
        self.stack_indent = max(0, min(stack_indent, 6))
        self.stack_border: str = stack_border
        self.stack_func_and_line_no: str = stack_func_and_line_no
        self.stack_code: str = stack_code
        self.stack_func_parenthesis: str = rich_Style.parse(self.stack_code).color.name
        self.stack_file_path: str = stack_file_path
        # Context Block style:
        self.context_border: str = context_border
        self.context_keys: str = context_keys
        self.context_values: str = context_values

    @classmethod
    def styles(cls, print_enable=True) -> list:
        """Return the list of available Rich text styles, optionally printing them.

            Parameters
            ----------
            print_enable : bool, optional
                If True, prints the styles to stdout before returning them.

            Returns
            -------
            list
                A list of all available Rich text styles.
            """
        if print_enable:
            print(cls.RICH_STYLES)
            return cls.RICH_STYLES
        else:
            return cls.RICH_STYLES

    @classmethod
    def colors(cls, print_enable=True) -> list:
        """Return the list of available Rich colors, optionally printing them.

            Parameters
            ----------
            print_enable : bool, optional
                If True, prints the colors to stdout before returning them.

            Returns
            -------
            list
                A list of all available Rich colors.
            """
        if print_enable:
            print(cls.RICH_COLORS)
            return cls.RICH_COLORS
        else:
            return cls.RICH_COLORS

    def export_style(self, file_path=None) -> Path:
        """Export the current Style to JSON file.

            Parameters
            ----------
            file_path : str or None, optional
                Destination path. If None, uses default location ``~/.catch_them_all/style.json``.

            Returns
            -------
            Path
                the path to the written file.
            """

        if file_path is None:
            # Default = user home — global theme
            path = DEFAULT_STYLE_PATH
        else:
            # User gave path → project-local
            path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._to_json(), encoding="utf-8")  # to_json uses to_dict internally
        return path

    @classmethod
    def load_style(cls, file_path=None):
        """Load a Style instance from JSON file or return defaults.

        Parameters
        ----------
        file_path : str or None, optional
            Path to JSON file. If None, uses default location ``~/.catch_them_all/style.json``.

        Returns
        -------
        Style
            Loaded style or default Style instance.
        """
        if file_path:
            path = Path(file_path)
        else:
            path = DEFAULT_STYLE_PATH

        if not path.exists():
            return cls()  # return default theme

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(**data)
        except Exception as e:
            print(f"\n\t !!-- exception occured e: {e}\n\tCouldn't load Custom Style, Loaded Default Instead --!\n")
            return cls()  # corrupted → default

    def to_dict(self) -> Dict:
        """Serialize the Style instance to a dictionary.

            Returns
            -------
            dict
                Dictionary representation suitable for JSON export.
            """
        return {
            "labels": self.labels,
            "muted": self.muted,
            # Header style:

            "header_border": self.header_border,
            "header_exception": self.header_exception,
            "header_timestamp": self.header_timestamp,
            "header_summary": self.header_summary,
            "header_message": self.header_message,
            "header_cause": self.header_cause,

            # Stack Frame style:
            "stack_indent": self.stack_indent,
            "stack_border": self.stack_border,
            "stack_func_and_line_no": self.stack_func_and_line_no,
            "stack_code": self.stack_code,
            "stack_file_path": self.stack_file_path,

            # Context Block style:

            "context_border": self.context_border,
            "context_keys": self.context_keys,
            "context_values": self.context_values,

        }

    def _to_json(self) -> str:
        """Helper, Serialize the Style instance to a formatted JSON string.

            Returns
            -------
            str
                Human-readable JSON representation of the style.
            """

        return json.dumps(self.to_dict(), indent=2)


__all__ = ["Style"]
