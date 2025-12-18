import unittest
from unittest.mock import patch
from pathlib import Path

from catch_them_all.themes import Style
import json

class TestStyle(unittest.TestCase):
    """Tests for the Style theme system — file loading, defaults, and export."""

    def setUp(self):
        # Ensure no user theme interferes with tests
        self.default_path = Path.home() / ".catch_them_all" / "style.json"
        if self.default_path.exists():
            self.default_path.unlink()

    def tearDown(self):
        # Remove test-generated config if present
        if self.default_path.exists():
            self.default_path.unlink()

    def test_default_style_when_no_file(self):
        """Style.load_style() returns built-in defaults when no config file exists."""
        with patch.object(Path, "exists", return_value=False):
            style = Style.load_style()

        # Verify all default values from Style.__init__
        self.assertEqual(style.stack_indent, 2)
        self.assertEqual(style.labels, "light_goldenrod2")

        self.assertEqual(style.header_border, "light_slate_blue")
        self.assertEqual(style.header_exception, "bold sea_green1 on grey15")
        self.assertEqual(style.header_timestamp, "plum1 on grey3")
        self.assertEqual(style.header_summary, "bright_white")
        self.assertEqual(style.header_message, "bright_white")
        self.assertEqual(style.header_cause, "bright_white on grey23")

        self.assertEqual(style.stack_border, "#3b96ff")
        self.assertEqual(style.stack_func_and_line_no, "light_green on grey11")
        self.assertEqual(style.stack_code, "bold medium_turquoise on grey11")
        self.assertEqual(style.stack_file_path, "italic bright_white")

        self.assertEqual(style.context_border, "plum1")
        self.assertEqual(style.context_keys, "light_goldenrod2")
        self.assertEqual(style.context_values, "bold bright_white")

    def test_loads_valid_json_theme(self):
        """Style.load_style() correctly loads a valid theme file from disk."""
        # Create valid theme JSON in real user config location
        theme_data = {
            "stack_indent": 4,
            "labels": "bright_cyan",
            "header_border": "bold red",
            "header_exception": "bold bright_magenta",
            "context_values": "italic white"
        }
        config_dir = Path.home() / ".catch_them_all"
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "style.json"
        config_path.write_text(json.dumps(theme_data), encoding="utf-8")

        try:
            style = Style.load_style()

            # Verify custom values were applied
            self.assertEqual(style.stack_indent, 4)
            self.assertEqual(style.labels, "bright_cyan")
            self.assertEqual(style.header_border, "bold red")
            self.assertEqual(style.header_exception, "bold bright_magenta")
            self.assertEqual(style.context_values, "italic white")

            # Verify defaults remain untouched when not overridden

            self.assertEqual(style.header_timestamp, "plum1 on grey3")  # unchanged

        finally:
            # Clean up
            if config_path.exists():
                config_path.unlink()
            if config_dir.exists() and not list(config_dir.iterdir()):
                config_dir.rmdir()

    def test_export_creates_file_and_directory(self):
        """Style.export_style() creates the config directory and file if they don't exist."""

        config_dir = Path.home() / ".catch_them_all"
        config_path = config_dir / "style.json"

        # Ensure clean slate — remove if exists
        if config_path.exists():
            config_path.unlink()
        if config_dir.exists():
            config_dir.rmdir()

        # Create custom style
        custom_style = Style(
            stack_indent=0,
            labels="bright_red",
            header_border="bold yellow"
        )

        # Export — this should create both dir and file
        returned_path = custom_style.export_style()

        # Verify directory and file were created
        self.assertTrue(config_dir.is_dir())
        self.assertTrue(config_path.is_file())
        self.assertEqual(returned_path, config_path)

        # Verify content is correct JSON and matches the style
        loaded_data = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded_data["stack_indent"], 0)
        self.assertEqual(loaded_data["labels"], "bright_red")
        self.assertEqual(loaded_data["header_border"], "bold yellow")

        # Clean up
        config_path.unlink()
        config_dir.rmdir()

    def test_load_corrupted_json_returns_default(self):
        """Style.load_style() returns defaults when config file contains invalid JSON."""

        config_dir = Path.home() / ".catch_them_all"
        config_path = config_dir / "style.json"

        # Ensure clean state
        if config_path.exists():
            config_path.unlink()
        if config_dir.exists() and not list(config_dir.iterdir()):
            config_dir.rmdir()

        # Create directory and write invalid JSON
        config_dir.mkdir(exist_ok=True)
        config_path.write_text("this is not valid json {[{", encoding="utf-8")

        try:
            style = Style.load_style()

            # Must fall back to defaults — no exception, no partial load
            self.assertEqual(style.stack_indent, 2)
            self.assertEqual(style.labels, "light_goldenrod2")
            self.assertEqual(style.header_border, "light_slate_blue")
            self.assertEqual(style.header_exception, "bold sea_green1 on grey15")
            self.assertEqual(style.header_timestamp, "plum1 on grey3")

        finally:
            # Clean up
            if config_path.exists():
                config_path.unlink()
            if config_dir.exists() and not list(config_dir.iterdir()):
                config_dir.rmdir()

    def test_clamps_stack_indent_on_load(self):
        """Style.load_style() clamps invalid stack_indent values to 0–6 range."""

        config_dir = Path.home() / ".catch_them_all"
        config_path = config_dir / "style.json"

        # Clean state
        if config_path.exists():
            config_path.unlink()
        if config_dir.exists() and not list(config_dir.iterdir()):
            config_dir.rmdir()

        # Write theme with illegal values
        invalid_theme = {
            "stack_indent": 999,  # way too high
            "labels": "bright_red"
        }
        config_dir.mkdir(exist_ok=True)
        config_path.write_text(json.dumps(invalid_theme), encoding="utf-8")

        try:
            style = Style.load_style()

            # Must be clamped to maximum allowed
            self.assertEqual(style.stack_indent, 6)

            # Other values should still load correctly
            self.assertEqual(style.labels, "bright_red")

            # Defaults preserved where not overridden
            self.assertEqual(style.header_border, "light_slate_blue")

        finally:
            if config_path.exists():
                config_path.unlink()
            if config_dir.exists() and not list(config_dir.iterdir()):
                config_dir.rmdir()

    def test_global_style_auto_loaded_on_import(self):
        """formatter._CURRENT_STYLE reflects disk theme on module import/reload."""

        from catch_them_all.formatter import _CURRENT_STYLE

        # 1. Initial import — should be defaults
        self.assertEqual(_CURRENT_STYLE.stack_indent, 2)
        self.assertEqual(_CURRENT_STYLE.labels, "light_goldenrod2")

        # 2. Export a custom theme
        custom = Style(stack_indent=0, labels="bright_red")
        custom.export_style()  # writes to real ~/.catch_them_all/style.json

        # 3. Force module reload — triggers _CURRENT_STYLE = Style.load_style()
        import importlib
        import catch_them_all.formatter
        importlib.reload(catch_them_all.formatter)

        # 4. Now global should reflect the file
        self.assertEqual(catch_them_all.formatter._CURRENT_STYLE.stack_indent, 0)
        self.assertEqual(catch_them_all.formatter._CURRENT_STYLE.labels, "bright_red")

        # The reloaded global style is a new instance (reconstructed from JSON),
        # not the original object — this is the intended behavior.
        self.assertIsNot(catch_them_all.formatter._CURRENT_STYLE, custom)



if __name__ == "__main__":
    unittest.main(verbosity=2)
