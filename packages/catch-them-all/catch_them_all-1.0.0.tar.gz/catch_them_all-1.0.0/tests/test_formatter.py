# tests/test_formatter_unittest.py
import unittest
from rich.console import Console

from catch_them_all.formatter import Formatter,  set_global_style
from catch_them_all.themes import Style

import catch_them_all.formatter as cta_formatter



class Evil:
    def __str__(self):
        raise RuntimeError("boom")


def render(obj):
    """Render any Rich object to actual visible text (not repr)."""
    console = Console(record=True, width=200, legacy_windows=False)
    console.print(obj)
    return console.export_text()


class TestFormatterTest(unittest.TestCase):

    def setUp(self):
        self.original_style = cta_formatter._CURRENT_STYLE
        set_global_style(Style())  # reset to defaults

    def tearDown(self):
        set_global_style(self.original_style)

    def test_happy_path(self):
        data = {
            "exception": {"type": "TimeoutError", "message": "waiting too long"},
            "summary": "Login failed",
            "timestamp": "2025-12-10T12:00:00Z",
            "frames": [
                {"file": "/app/main.py", "line": 42, "function": "login", "code": "page.click()"}
            ]
        }
        f = Formatter(data)
        output = render(f.rich_format)
        self.assertIn("TimeoutError", output)
        self.assertIn("login()", output)
        self.assertIn("42", output)
        self.assertIn("Login failed", output)

    def test_long_message_truncated(self):
        data = {
            "exception": {"type": "Error", "message": "A" * 10000}
        }
        f = Formatter(data)
        output = render(f.rich_format)
        lines = [line for line in output.splitlines() if "A" in line]
        for line in lines:
            self.assertLessEqual(len(line), 403)  # 400 + "..."

    def test_evil_context(self):
        f = Formatter({"exception": {"type": "Error", "message": "x"}})
        f.inject_and_update_context({"user": Evil()})
        output = render(f.rich_format)
        self.assertIn("<unprintable>", output)

    def test_stack_indent_zero_no_leading_spaces_in_log(self):
        set_global_style(Style(stack_indent=0))
        f = Formatter({
            "exception": {"type": "Error", "message": "x"},
            "frames": [{"file": "a.py", "line": 1, "function": "main", "code": "run()"}]
        })
        # str_log_version is already plain string — no Rich object
        for line in f.str_format.splitlines():
            if "• file:" in line:
                self.assertFalse(line[0].isspace(), f"Leading space found: {line!r}")

    def test_headers_match_expected_pattern(self):
        # With frames → double header
        # note the double header appears only if there are more than two frames
        data_with_frames = {
            "exception": {"type": "MyError", "message": "boom"},
            "frames": [{"file": "x.py", "line": 1, "function_1": "f", "code": "boom()"},
                       {"file": "y.py", "line": 2, "function_2": "f", "code": "ka-boom()"},
                       {"file": "z.py", "line": 3, "function_3": "f", "code": "mega_boom()"}]
        }
        f1 = Formatter(data_with_frames)
        rich1 = render(f1.rich_format)

        self.assertEqual(rich1.count("Exception: MyError"), 2)

        # Without frames → single header
        data_no_frames = {
            "exception": {"type": "MyError", "message": "boom"},
            "frames": []
        }
        f2 = Formatter(data_no_frames)
        rich2 = render(f2.rich_format)
        self.assertEqual(rich2.count("Exception: MyError"), 1)

        # Log version always single
        self.assertEqual(f2.log_format.count("Exception: MyError"), 1)

    def test_malformed_timestamp_fallback(self):
        data = {
            "exception": {"type": "Error", "message": "boom"},
            "timestamp": "this is garbage not ISO",

        }
        f = Formatter(data)
        output = render(f.rich_format)
        self.assertIn("Unknown Time!", output)  # raw fallback

    def test_frames_with_evil_code(self):
        data = {
            "exception": {"type": "Error", "message": "boom"},
            "frames": [
                {"file": "evil.py", "line": 42, "function": "die", "code": Evil()}
            ]
        }
        f = Formatter(data)
        output = render(f.rich_format)
        self.assertIn("<unprintable>", output)
        self.assertIn("evil.py", output)
        self.assertIn("42", output)
        self.assertIn("die()", output)

    def test_very_long_message_height_control(self):
        long_msg = "\n".join(f"Line {i}: " + "A" * 400 for i in range(50))
        data = {
            "exception": {"type": "Error", "message": long_msg}
        }
        f = Formatter(data)
        output = render(f.rich_format)

        # Find all visual lines that belong to the message block
        message_section = [
            line for line in output.splitlines()
            if "AAA" in line or "... (truncated)" in line or "Line " in line

        ]
        print(f">{message_section}<")

        # With current logic:
        # - 6 headlines (each truncated to 100 chars → 1 visual line each)
        # - 1 "... (truncated)" line
        # - 1 last line (truncated to 100 chars → 1 visual line)
        # → max 8 visual lines in the message section
        self.assertLessEqual(len(message_section) , 8)

        # Truncation indicator must be present when >7 logical lines
        self.assertIn("... (truncated)", output)

        # Last original line must be visible (proves tail logic works)
        self.assertIn("Line 49:", output)


class TestFormatterHelpers(unittest.TestCase):

    def test_safe_str_handles_unprintable(self):

        self.assertEqual(Formatter._safe_str(Evil()), "<unprintable>")

    def test_shorten_path_windows(self):
        path = "C:\\Users\\asus\\PycharmProjects\\MyApp\\src\\main.py"
        self.assertEqual(Formatter._shorten_path(path), "C:/src/main.py")

        path = "D:/work/cool-tool/app/core.py"
        self.assertEqual(Formatter._shorten_path(path), "D:/app/core.py")

    def test_shorten_path_unix(self):
        path = "/home/asus/projects/myapp/utils/helpers.py"
        self.assertEqual(Formatter._shorten_path(path), "utils/helpers.py")

        path = "/opt/services/backend/api/views.py"
        self.assertEqual(Formatter._shorten_path(path), "api/views.py")

    def test_shorten_path_root_cases(self):
        self.assertEqual(Formatter._shorten_path("C:\\file.py"), "C:/file.py")
        self.assertEqual(Formatter._shorten_path("/file.py"), "/file.py")
        self.assertEqual(Formatter._shorten_path(""), "/")

class TestSetGlobalStyle(unittest.TestCase):

    def setUp(self):
        # Save original to restore later
        self.original_style = cta_formatter._CURRENT_STYLE

    def tearDown(self):
        # Always restore the original global style
        set_global_style(self.original_style)

    def test_default_style_is_standard(self):
        set_global_style(Style())  # reset to defaults
        self.assertEqual(cta_formatter._CURRENT_STYLE.stack_indent, 2)
        self.assertEqual(cta_formatter._CURRENT_STYLE.labels, "light_goldenrod2")

    def test_set_global_style_replaces_global_correctly(self):
        custom = Style(stack_indent=0, labels="bright_cyan")
        set_global_style(custom)

        self.assertIs(cta_formatter._CURRENT_STYLE, custom)  # exact same object
        self.assertEqual(cta_formatter._CURRENT_STYLE.stack_indent, 0)
        self.assertEqual(cta_formatter._CURRENT_STYLE.labels, "bright_cyan")

    def test_multiple_calls_update_global(self):
        first = Style(stack_indent=4)
        set_global_style(first)
        self.assertEqual(cta_formatter._CURRENT_STYLE.stack_indent, 4)

        second = Style(stack_indent=6, header_border="red")
        set_global_style(second)
        self.assertEqual(cta_formatter._CURRENT_STYLE.stack_indent, 6)
        self.assertEqual(cta_formatter._CURRENT_STYLE.header_border, "red")

    def test_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError) as cm:
            set_global_style("not a Style instance")

        self.assertIn("Is not an intense of the Style class", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
