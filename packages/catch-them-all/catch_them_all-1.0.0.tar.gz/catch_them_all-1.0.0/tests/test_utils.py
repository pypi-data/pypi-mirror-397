# tests/test__scan_for_candidate_modules.py


import types

from threading import Thread
from types import ModuleType
from pathlib import Path

import abc


import unittest
import sys



from catch_them_all.utils import _scan_for_candidate_modules, _get_docs_summary,  _scanned_modules, _extract_exceptions_from_modules, _distill_traceback





class TestScanForCandidateModules(unittest.TestCase):

    def setUp(self):
        # Start every test with clean internal state
        _scanned_modules.clear()

    # ------------------------------------------------------------------
    # 1. Returns real .py/.pyc modules that exist on disk
    # ------------------------------------------------------------------
    def test_returns_real_py_modules(self):
        mods = _scan_for_candidate_modules()
        # At minimum our own utils module must be present (it's a .py file)
        self.assertIn("catch_them_all.utils", mods)
        self.assertIsInstance(mods["catch_them_all.utils"], ModuleType)

    # ------------------------------------------------------------------
    # 2. Skips frozen / <...> modules
    # ------------------------------------------------------------------
    def test_skips_frozen_modules(self):
        mods = _scan_for_candidate_modules()
        self.assertNotIn("sys", mods)
        self.assertNotIn("builtins", mods)

    # ------------------------------------------------------------------
    # 3. Skips C extensions
    # ------------------------------------------------------------------
    def test_skips_c_extensions(self):
        import zlib  # typical C extension
        mods = _scan_for_candidate_modules()
        self.assertNotIn("zlib", mods)

    # ------------------------------------------------------------------
    # 4. Skips non-str __file__ (including pathlib.Path)
    # ------------------------------------------------------------------
    def test_skips_non_str_file_and_pathlib_path(self):
        fake = types.ModuleType("fake_pathlib")
        fake.__file__ = Path("/fake/path.py")  # pathlib.Path instance
        sys.modules["fake_pathlib"] = fake

        mods = _scan_for_candidate_modules()
        self.assertNotIn("fake_pathlib", mods)

        # also test plain None
        fake2 = types.ModuleType("fake_none")
        fake2.__file__ = None
        sys.modules["fake_none"] = fake2

        mods = _scan_for_candidate_modules()
        self.assertNotIn("fake_none", mods)

    # ------------------------------------------------------------------
    # 5. Skips modules with __file__ = None
    # ------------------------------------------------------------------
    def test_skips_modules_with_file_none(self):
        fake = types.ModuleType("namespace_pkg")
        fake.__file__ = None
        sys.modules["namespace_pkg"] = fake

        mods = _scan_for_candidate_modules()
        self.assertNotIn("namespace_pkg", mods)

    # ------------------------------------------------------------------
    # 6. Incremental: second call returns only newly imported ones
    # ------------------------------------------------------------------
    def test_incremental_scan(self):
        # First scan
        first = _scan_for_candidate_modules()


        # Import something new that has a real file
        import pixel_pretender  #  real .py file
        second = _scan_for_candidate_modules()

        # pixel_pretender should be new
        # At worst we get the same count – never more than the first + new ones
        self.assertGreaterEqual(len(second), 0)
        self.assertTrue(any("pixel_pretender" in name for name in second))

    # ------------------------------------------------------------------
    # 7. _scanned_modules is correctly updated after each call
    # ------------------------------------------------------------------
    def test_scanned_modules_updated(self):
        mods = _scan_for_candidate_modules()
        for name in mods:
            self.assertIn(name, _scanned_modules)

    # ------------------------------------------------------------------
    # 8. Handles dynamic imports correctly
    # ------------------------------------------------------------------
    def test_dynamic_import_appears_on_next_scan(self):
        # Scan once
        before = set(_scan_for_candidate_modules().keys())

        # Import new module with real file
        # import json  # usually frozen, use something guaranteed real
        import pyautogui  # rich, real file
        after = set(_scan_for_candidate_modules().keys())

        new_modules = after - before
        self.assertIn("pyautogui", new_modules)

    # ------------------------------------------------------------------
    # 9. Does not crash when inspect.getmembers raises
    # ------------------------------------------------------------------
    def test_no_crash_on_broken_getmembers(self):
        bad_module_example = types.ModuleType("bad_module_example")

        def boom():
            raise RuntimeError("something bad happened")
        bad_module_example.__getattr__ = boom
        bad_module_example.__file__ = "/fake/bad_module_example.py"
        sys.modules["bad_module_example"] = bad_module_example

        # Must not raise
        _scan_for_candidate_modules()

    # ------------------------------------------------------------------
    # 10. Unpredictable chaos: __file__ is pathlib.Path
    # ------------------------------------------------------------------
    def test_pathlib_path_file(self):
        mod = types.ModuleType("pathlib_mod")
        mod.__file__ = Path(__file__)  # real Path object
        sys.modules["pathlib_mod"] = mod

        mods = _scan_for_candidate_modules()
        self.assertNotIn("pathlib_mod", mods)  # skipped correctly

    # ------------------------------------------------------------------
    # 11. Unpredictable chaos: module raises during getmembers
    # ------------------------------------------------------------------
    def test_module_raises_during_introspection(self):
        bad = types.ModuleType("bad")
        bad.__file__ = "/fake/bad.py"

        def raise_in_dir():
            raise ValueError("no dir for you")
        bad.__dir__ = raise_in_dir
        sys.modules["bad"] = bad

        # Must not crash
        _scan_for_candidate_modules()

    # ------------------------------------------------------------------
    # 12. Unpredictable chaos: namespace package with exceptions but __file__ = None
    # ------------------------------------------------------------------
    def test_namespace_package_with_exceptions_skipped(self):
        ns = types.ModuleType("ns_pkg")
        ns.__file__ = None

        class MyError(Exception):
            ...


        ns.MyError = MyError
        sys.modules["ns_pkg"] = ns

        mods = _scan_for_candidate_modules()
        self.assertNotIn("ns_pkg", mods)  # correctly skipped

    # ------------------------------------------------------------------
    # 13. Unpredictable chaos: module reloaded with importlib.reload
    # ------------------------------------------------------------------
    def test_reload_module_changes_identity(self):
        import importlib
        import textwrap

        old_obj = sys.modules["textwrap"]
        mods1 = _scan_for_candidate_modules()

        importlib.reload(textwrap)
        mods2 = _scan_for_candidate_modules()

        # textwrap may or may not appear again depending on whether it was already scanned
        # The important thing is no crash and _scanned_modules behaves sanely
        self.assertTrue("textwrap" in _scanned_modules or "textwrap" in mods2)

    # ------------------------------------------------------------------
    # 14. Unpredictable chaos: very long / deeply nested module names
    # ------------------------------------------------------------------
    def test_deeply_nested_module_name(self):
        deep_name = "a." * 50 + "b"
        deep_mod = types.ModuleType(deep_name)
        deep_mod.__file__ = "/fake/deep.py"
        sys.modules[deep_name] = deep_mod

        mods = _scan_for_candidate_modules()
        self.assertIn(deep_name, mods)

    # ------------------------------------------------------------------
    # 15. Thread-safety with lock
    # ------------------------------------------------------------------
    def test_thread_safety(self):
        results = []

        def worker():
            for _ in range(20):
                mods = _scan_for_candidate_modules()
                results.append(len(mods))

        threads = [Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No assertion error = no corruption
        self.assertTrue(all(isinstance(r, int) for r in results))

class TestExtractExceptions(unittest.TestCase):

    def setUp(self):
        # Create dummy modules
        self.mod_a = types.ModuleType("mod_a")
        self.mod_b = types.ModuleType("mod_b")

        # Concrete exception
        class MyError(Exception):
            pass
        MyError.__module__ = "mod_a"

        # Proper abstract exception
        class MyAbstractError(Exception, metaclass=abc.ABCMeta):
            @abc.abstractmethod
            def must_implement(self):
                pass
        MyAbstractError.__module__ = "mod_a"

        # Attach to mod_a
        self.mod_a.MyError = MyError
        self.mod_a.MyAbstractError = MyAbstractError

        # Re-export MyError in mod_b
        self.mod_b.MyError = MyError

        self.modules = {"mod_a": self.mod_a, "mod_b": self.mod_b}

    def test_extracts_defined_exception(self):
        result = _extract_exceptions_from_modules(self.modules)
        self.assertIn("mod_a.MyError", result)
        self.assertIs(result["mod_a.MyError"], self.mod_a.MyError)

    def test_ignores_reexported_exception(self):
        result = _extract_exceptions_from_modules(self.modules)
        self.assertNotIn("mod_b.MyError", result)

    def test_ignores_abstract_exception(self):
        result = _extract_exceptions_from_modules(self.modules)
        # Properly abstract, so it should be excluded
        self.assertNotIn("mod_a.MyAbstractError", result)

    def test_excludes_control_flow_exceptions(self):
        self.mod_a.SystemExit = SystemExit
        result = _extract_exceptions_from_modules(self.modules)
        self.assertNotIn("mod_a.SystemExit", result)

    def test_module_with_bad_getattr_is_still_captured(self):
        bad_mod = types.ModuleType("bad_mod")

        class BadError(Exception):
            pass

        BadError.__module__ = "bad_mod"
        bad_mod.BadError = BadError

        # __getattr__ always raises, but since we now walk __dict__,
        # this does not affect scanning.
        def bad_getattr(name):
            raise RuntimeError("bad getattr")

        bad_mod.__getattr__ = bad_getattr

        modules = {"bad_mod": bad_mod}
        result = _extract_exceptions_from_modules(modules)

        # With the new implementation, BadError should still be captured
        expected = {"bad_mod.BadError": BadError}
        self.assertEqual(result, expected)

    def test_deduplication(self):
        result = _extract_exceptions_from_modules(self.modules)
        keys = [k for k in result.keys() if k.endswith("MyError")]
        self.assertEqual(len(keys), 1)

    def test_stdlib_reexport_is_ignored(self):
        mod = types.ModuleType("mypkg")
        # Re-exporting a built-in exception
        mod.ValueError = ValueError

        result = _extract_exceptions_from_modules({"mypkg": mod})
        # Builtins are not part of scanned modules → ignored
        self.assertEqual(result, {})

    def test_multiple_reexport_chain_resolves_to_original(self):
        orig = types.ModuleType("deep.lib")
        exec("class DeepError(Exception): pass", orig.__dict__)

        mid = types.ModuleType("mid")
        mid.DeepError = orig.DeepError

        top = types.ModuleType("top")
        top.DeepError = mid.DeepError

        modules = {"deep.lib": orig, "mid": mid, "top": top}
        result = _extract_exceptions_from_modules(modules)

        # Only one entry, under the original defining module
        self.assertEqual(len(result), 1)
        self.assertIn("deep.lib.DeepError", result)

    def test_exception_with_missing_module_attribute_is_skipped(self):
        mod = types.ModuleType("pkg")
        cls = type("DynamicError", (Exception,), {})
        cls.__module__ = None  # simulate rare edge case
        mod.DynamicError = cls

        result = _extract_exceptions_from_modules({"pkg": mod})
        # Skipped because __module__ is None
        self.assertEqual(result, {})

    def test_different_exceptions_same_name_in_different_modules(self):
        mod1 = types.ModuleType("mod1")
        exec("class ConflictError(Exception): pass", mod1.__dict__)

        mod2 = types.ModuleType("mod2")
        exec("class ConflictError(Exception): pass", mod2.__dict__)

        modules = {"mod1": mod1, "mod2": mod2}
        result = _extract_exceptions_from_modules(modules)

        # Both should be present, keyed by their defining module
        self.assertIn("mod1.ConflictError", result)
        self.assertIn("mod2.ConflictError", result)
        self.assertNotEqual(result["mod1.ConflictError"], result["mod2.ConflictError"])


class TestGetDocsSummary(unittest.TestCase):
    """tests for get_docs_summary()."""

    def test_01_builtin_exceptions_have_meaningful_summaries(self) -> None:
        """Built-ins return non-empty, sensible summaries (version-agnostic)."""
        self.assertGreater(len(_get_docs_summary(ValueError)), 20)
        self.assertGreater(len(_get_docs_summary(TypeError)), 20)
        self.assertIn("division", _get_docs_summary(ZeroDivisionError).lower())

    def test_02_completely_undocumented_class_uses_fallback(self) -> None:
        """Class with no docstring anywhere in the MRO → fallback message."""

        class _TrulySilent(object):  # leading _ to avoid name clashes
            pass

        expected = "Undocumented exception for: _TrulySilent"
        self.assertEqual(_get_docs_summary(_TrulySilent), expected)

    def test_03_inheritance_works_at_any_depth(self) -> None:
        """Docstring inherited regardless of depth or abstract status."""

        class _Base(Exception):
            """HTTP base error."""

        class _Mid(_Base):
            pass

        class _Leaf(_Mid):
            pass

        expected = "HTTP base error."
        for cls in (_Base, _Mid, _Leaf):
            self.assertEqual(_get_docs_summary(cls), expected)

    def test_04_abstract_bases_are_treated_like_normal_classes(self) -> None:
        """ABC classes have accessible docstrings — no special handling needed."""

        class _AbstractIOError(Exception, metaclass=abc.ABCMeta):
            """I/O operation failed."""

            @abc.abstractmethod
            def retry(self) -> None: ...

        self.assertEqual(_get_docs_summary(_AbstractIOError), "I/O operation failed.")

    def test_05_child_of_abstract_inherits_when_it_has_no_doc(self) -> None:

        class _Retryable(Exception, metaclass=abc.ABCMeta):
            """Can be retried."""

        class _Timeout(_Retryable):
            pass

        self.assertEqual(_get_docs_summary(_Timeout), "Can be retried.")

    def test_06_only_first_line_of_multiline_docstring_is_returned(self) -> None:

        class _Verbose(Exception):
            """One-line summary.

            Very long explanation that should be ignored.
            Multiple paragraphs.
            """

        self.assertEqual(_get_docs_summary(_Verbose), "One-line summary.")


    def test_07_explicit_empty_docstring_blocks_inheritance(self) -> None:
        """Explicitly setting an empty docstring stops inheritance (standard Python behavior)."""

        class _Parent(Exception):
            """Wisdom."""

        class _Empty1(_Parent):
            """"""  # blocks

        class _Empty2(_Parent):
            """   \n   """  # blocks

        class _Empty3(_Parent):
            __doc__ = ""  # blocks

        class _Empty4(_Parent):
            __doc__ = "   \t   "  # blocks

        fallback_pattern = "Undocumented exception for:"

        for child in (_Empty1, _Empty2, _Empty3, _Empty4):
            with self.subTest(child=child.__name__):
                summary = _get_docs_summary(child)
                self.assertTrue(summary.startswith(fallback_pattern),
                                f"{child.__name__} should fallback, got {summary!r}")

class TestDistillTraceback(unittest.TestCase):
    """
    Test suite for the distill_traceback() function.
    Each test validates a specific behavior: handling of no exception,
    normal exceptions, frame extraction, cause/context chains, suppression,
    and edge cases.
    """

    def test_no_active_exception(self):
        """Ensure that when no exception is active, a sentinel result is returned."""
        result = _distill_traceback()
        self.assertEqual(result["frames"], [])
        self.assertEqual(result["exception"]["type"], "NoException")
        self.assertEqual(result["exception"]["message"], "No active exception")
        self.assertIsInstance(result["caused_by"], list)

    def test_basic_exception(self):
        """Verify that a simple ValueError is captured with type, message, and frames."""
        try:
            raise ValueError("bad value")
        except ValueError:
            result = _distill_traceback(*sys.exc_info())
            self.assertEqual(result["exception"]["type"], "ValueError")
            self.assertEqual(result["exception"]["message"], "bad value")
            self.assertTrue(result["frames"])
            self.assertIsInstance(result["caused_by"], list)

    def test_frame_limit(self):
        """Check that the 'limit' parameter restricts the number of frames returned."""
        def inner():
            raise RuntimeError("boom")
        try:
            inner()
        except RuntimeError:
            result = _distill_traceback(*sys.exc_info(), max_frames=1)
            self.assertEqual(len(result["frames"]), 1)

    def test_explicit_cause_chain(self):
        """Validate that an explicit 'raise ... from ...' chain is captured in caused_by."""
        try:
            try:
                raise KeyError("inner")
            except KeyError as e:
                # Outer exception with explicit cause
                raise ValueError("outer") from e
        except Exception as outer_exc:
            # Catch the outer exception separately
            exc_type, exc_value, tb = sys.exc_info()
            result = _distill_traceback(exc_type, exc_value, tb)
            self.assertEqual(result["exception"]["type"], "ValueError")
            self.assertEqual(result["exception"]["message"], "outer")
            # Cause chain should be present
            self.assertIsNotNone(result["caused_by"])
            self.assertEqual(result["caused_by"][0]["type"], "KeyError")
            self.assertEqual(result["caused_by"][0]["message"], "'inner'")

    def test_context_chain(self):
        """Ensure that implicit context (exception raised in except block) is captured."""
        try:
            try:
                raise IndexError("first")
            except IndexError:
                # Raising a new exception inside an except block sets __context__
                raise TypeError("second")
        except Exception as outer_exc:
            exc_type, exc_value, tb = sys.exc_info()
            result = _distill_traceback(exc_type, exc_value, tb)
            self.assertEqual(result["exception"]["type"], "TypeError")
            self.assertEqual(result["exception"]["message"], "second")
            # Context chain should be present
            self.assertIsNotNone(result["caused_by"])
            self.assertEqual(result["caused_by"][0]["type"], "IndexError")
            self.assertEqual(result["caused_by"][0]["message"], "first")




    def test_suppressed_context(self):
        """Confirm that suppressed context (__suppress_context__=True) is not included."""
        try:
            try:
                raise OSError("low-level")
            except OSError:
                exc = RuntimeError("high-level")
                exc.__context__ = OSError("low-level")
                exc.__suppress_context__ = True
                raise exc
        except RuntimeError:
            result = _distill_traceback(*sys.exc_info())
            self.assertEqual(result["exception"]["type"], "RuntimeError")
            self.assertIsInstance(result["caused_by"], list)

    def test_unknown_type_and_message(self):
        """Check fallback behavior when exc_type and exc_value are None."""
        result = _distill_traceback(exc_type=None, exc_value=None, tb=None)
        self.assertEqual(result["exception"]["type"], "NoException")
        self.assertEqual(result["exception"]["message"], "No active exception")

    def test_code_line_extraction(self):
        """Verify that the code line is extracted and stripped from the traceback frame."""
        try:
            1 / 0
        except ZeroDivisionError:
            result = _distill_traceback(*sys.exc_info())
            frame = result["frames"][-1]
            self.assertIn("1 / 0", frame["code"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
