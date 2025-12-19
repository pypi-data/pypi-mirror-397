import unittest



from catch_them_all.registry import _registry, BUILTIN_EXCEPTION_SUMMARIES



class TestExceptionRegistry(unittest.TestCase):
    """Tests for the exception summary registry — loading, content, and rescan."""

    def setUp(self):
        # Capture initial state
        self.initial_registry = _registry.copy()
        self.initial_size = len(_registry)

    def tearDown(self):
        # Restore original registry state — no pollution
        global _registry
        _registry = self.initial_registry.copy()

    def test_registry_contains_all_builtins_on_import(self):
        """Registry is populated with all built-in exceptions and their summaries on module import."""

        # Must contain every key from BUILTIN_EXCEPTION_SUMMARIES
        expected_keys = set(BUILTIN_EXCEPTION_SUMMARIES.keys())
        actual_keys = set(_registry.keys())

        # All built-ins must be present
        missing = expected_keys - actual_keys
        self.assertEqual(
            missing,
            set(),
            f"Registry missing {len(missing)} built-in exceptions: {sorted(missing)}"
        )

        # Total size must be at least the number of builtins
        self.assertGreaterEqual(
            len(_registry),
            len(BUILTIN_EXCEPTION_SUMMARIES),
            "Registry should contain at least all built-in exceptions"
        )

        # Spot-check a few well-known ones
        self.assertIn("builtins.ValueError", _registry)
        self.assertIn("builtins.KeyError", _registry)
        self.assertIn("builtins.BaseException", _registry)
        self.assertIn("builtins.Exception", _registry)
        self.assertIn("builtins.ConnectionError", _registry)

    def test_builtin_summaries_are_correct(self):
        """Verify that built-in exception summaries match the official Python documentation.

        Additionally, when third-party libraries such as ``requests`` or ``numpy`` are importable,
        ``rescan()`` is invoked to ensure their exceptions are discovered and documented.
        The test is skipped for libraries that are not installed in the environment.
        """

        # Core built-in exceptions – summaries must be exact
        self.assertEqual(
            _registry["builtins.ValueError"],
            "Raised when an operation or function receives an argument that has the right type but an inappropriate value."
        )
        self.assertEqual(
            _registry["builtins.KeyError"],
            "Raised when a mapping (dictionary) key is not found in the set of existing keys."
        )
        self.assertEqual(
            _registry["builtins.AttributeError"],
            "Raised when an attribute reference or assignment fails."
        )
        self.assertIn(
            "base class for all built-in exceptions",
            _registry["builtins.BaseException"]
        )

        # Optional third-party libraries – only checked when available
        try:
            import requests
            from registry import rescan
            rescan()

            requests_doc_msg = "there was an ambiguous exception that occurred while handling"

            self.assertIn("requests.exceptions.RequestException", _registry)
            summary = _registry["requests.exceptions.RequestException"]
            self.assertIn(requests_doc_msg, summary.lower())

        except ImportError:
            pass  # requests not installed – test is optional

        try:
            import numpy
            from registry import rescan
            rescan()

            # Any numpy exception is sufficient proof of discovery
            self.assertTrue(
                any(key.startswith("numpy.exceptions.") for key in _registry),
                "No NumPy exceptions discovered after rescan()"
            )
        except ImportError:
            pass  # numpy not installed – test is optional

    def test_rescan_discovers_newly_imported_modules_with_parent_fallback(self):
        """rescan() discovers exceptions and correctly falls back to parent docstrings when needed."""

        from catch_them_all.registry import rescan_imports, _registry
        import sys

        # Clean import state
        self.assertNotIn("playwright", sys.modules)
        self.assertNotIn("sqlalchemy", sys.modules)

        # Initial — nothing discovered
        self.assertNotIn("playwright._impl._errors.TimeoutError", _registry)
        self.assertNotIn("sqlalchemy.exc.ProgrammingError", _registry)

        # Import libraries
        import playwright.sync_api  # noqa: F401
        import sqlalchemy.exc  # noqa: F401

        # Still not in registry until rescan
        self.assertNotIn("playwright._impl._errors.TimeoutError", _registry)

        # Trigger discovery
        rescan_imports()

        # Now discovered
        self.assertIn("playwright._impl._errors.TimeoutError", _registry)
        self.assertIn("sqlalchemy.exc.ProgrammingError", _registry)

        # TimeoutError has no docstring → must fall back to parent `Error`
        timeout_summary = _registry["playwright._impl._errors.TimeoutError"]
        error_summary = _registry["playwright._impl._errors.Error"]

        self.assertEqual(timeout_summary, error_summary)
        self.assertIn("Common base class for all non-exit exceptions.", timeout_summary)
        self.assertTrue(len(timeout_summary) > 30)

        # InvalidRequestError has its own docstring → used directly
        sql_err_1_summary = _registry["sqlalchemy.exc.ProgrammingError"]
        sql_err_2_summary = _registry["sqlalchemy.exc.NoResultFound"]
        self.assertIn("Wraps a DB-API ProgrammingError.", sql_err_1_summary)
        self.assertIn("A database result was required but none was found.", sql_err_2_summary)



if __name__ == "__main__":
    unittest.main(verbosity=2)
