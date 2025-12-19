import unittest
from unittest.mock import patch, mock_open, Mock
from io import StringIO
import sys

import catch_them_all.formatter
from catch_them_all.error_report import PokedexReport



class Evil:
    def __str__(self):
        raise RuntimeError("boom")


def render(obj):
    from rich.console import Console
    console = Console(record=True, width=120)
    console.print(obj)
    return console.export_text()


class TestPokedexReport(unittest.TestCase):

    def setUp(self):
        self.minimal_data = {
            "exception": {
                "type": "MyCustomError",
                "message": "something went wrong",
                "module": "myModule"
            },
            "summary": "Test error",
            "timestamp": "2025-12-11T12:00:00Z",
            "frames": [],
            "caused_by": [],
            "context": {}
        }

    def test_minimal_creation_and_rendering(self):
        # No frames — expect single header in both rich and plain
        # note the double header appears only if there are more than two frames

        obj = PokedexReport.from_dict(self.minimal_data)
        rich = render(obj.rich_format)
        plain = obj.log_format

        self.assertIn("MyCustomError", rich)
        self.assertIn("something went wrong", rich)
        self.assertIn("No Summary Available!", rich)
        self.assertIn("No Cause Available.", rich)

        self.assertEqual(rich.count("Exception: MyCustomError"), 1)  # single header
        self.assertEqual(plain.count("Exception: MyCustomError"), 1)  # single header

        # With frames — expect double header in rich, single in plain
        data_with_frames = self.minimal_data.copy()
        data_with_frames["frames"] = [
            {"file": "app.py", "line": 42, "function": "boom", "code": "1/0"}
        ]
        obj_with_frames = PokedexReport.from_dict(data_with_frames)
        rich_with = render(obj_with_frames.rich_format)
        plain_with = obj_with_frames.log_format

        self.assertEqual(rich_with.count("Exception: MyCustomError"), 1)  # single header in rich if frames [] is empty
        self.assertEqual(plain_with.count("Exception: MyCustomError"), 1)  # still single in plain

    def test_full_data_with_caused_by_chain_and_context(self):
        data = self.minimal_data.copy()
        data["frames"] = [
            {"file": "a.py", "line": 10, "function": "main", "code": "do()"}
        ]
        data["caused_by"] = [
            {"type": "KeyError", "message": "missing key"},
            {"type": "RuntimeError", "message": "failed hard"},
            {"type": "ValueError", "message": "deepest problem"},
            {"type": "TimeoutError", "message": "too slow"}
        ]

        obj = PokedexReport.from_dict(data)

        # Inject context
        obj.inject_context({"user": "john", "ip": "1.2.3.4"})

        rich = render(obj.rich_format)

        # Caused by chain
        self.assertIn("Caused by: KeyError: missing key", rich)
        self.assertIn("Caused by: RuntimeError: failed hard", rich)
        self.assertIn("Caused by: ValueError: deepest problem", rich)
        self.assertIn("Caused by: TimeoutError: too slow", rich)

        # Context panel (separate box)
        self.assertIn("user: john", rich)
        self.assertIn("ip: 1.2.3.4", rich)

        # Frames
        self.assertIn("line 10 in /a.py", rich)

    def test_caused_by_with_evil_message(self):
        data = self.minimal_data.copy()
        data["caused_by"] = [{"type": "BadError", "message": Evil()}]

        obj = PokedexReport.from_dict(data)
        rich = render(obj.rich_format)
        self.assertIn("<unprintable>", rich)

    def test_inject_context(self):
        obj = PokedexReport.from_dict(self.minimal_data)
        rich1 = render(obj.rich_format)
        self.assertNotIn("user:", rich1)

        obj.inject_context({"user": "alice", "session": 123})
        rich2 = render(obj.rich_format)
        self.assertIn("user: alice", rich2)
        self.assertIn("session: 123", rich2)

        obj.inject_context({"user": "bob"})  # replace
        rich3 = render(obj.rich_format)
        self.assertNotIn("alice", rich3)
        self.assertIn("user: bob", rich3)

    def test_to_log_none_prints_to_stderr(self):
        obj = PokedexReport.from_dict(self.minimal_data)
        with patch('sys.stderr', new=StringIO()) as fake_err:
            obj.to_log()
            output = fake_err.getvalue()
            self.assertIn("MyCustomError", output)
            self.assertIn("something went wrong", output)

    def test_to_log_txt_appends_plain(self):
        obj = PokedexReport.from_dict(self.minimal_data)
        m = mock_open()
        with patch('builtins.open', m, create=True):
            obj.to_log("test.txt")
        m().write.assert_called_with(obj.log_format + "\n\n\n")

    def test_to_json_appends_jsonl(self):
        import json
        obj = PokedexReport.from_dict(self.minimal_data)
        m = mock_open()
        with patch('builtins.open', m, create=True):
            obj.to_json("test.jsonl")

        # Capture ALL writes and join them
        written = ''.join(call[0][0] for call in m().write.call_args_list)
        lines = [line for line in written.splitlines() if line.strip()]

        self.assertEqual(len(lines), 1)  # one JSON line
        parsed = json.loads(lines[0])
        self.assertEqual(parsed["exception"]["type"], "MyCustomError")

    def test_write_failure_fallback(self):
        """If no path is provided, fallback is to print to stderr."""

        obj = PokedexReport.from_dict(self.minimal_data)

        # Patch builtins.print, since to_log(file_path=None) calls print(..., file=sys.stderr)
        with patch("builtins.print") as mock_print:
            obj.to_log(file_path=None)

        mock_print.assert_called_once()
        # Optionally check that it printed to stderr
        args, kwargs = mock_print.call_args
        self.assertEqual(kwargs.get("file"), sys.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
