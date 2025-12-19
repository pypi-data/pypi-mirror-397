import unittest
import sys

from unittest.mock import patch, Mock, ANY, MagicMock

from catch_them_all.excepthook import install_excepthook, disable_excepthook


class TestExcepthook(unittest.TestCase):
    """Tests for the global exception handler integration."""

    # The real, immutable built-in handler — never changes
    _builtin_hook = sys.__excepthook__

    def setUp(self):
        # Start every test with the true Python default
        sys.excepthook = self._builtin_hook

    def tearDown(self):
        # Always restore the real default
        sys.excepthook = self._builtin_hook

    def test_install_replaces_excepthook(self):
        """install_excepthook() replaces sys.excepthook with the custom handler."""
        install_excepthook()
        self.assertNotEqual(sys.excepthook, self._builtin_hook)
        self.assertTrue(callable(sys.excepthook))


    def test_disable_restores_original_handler(self):
        """disable_excepthook() restores Python's original built-in exception handler."""

        # Save the real original at the start of the test
        original_hook = sys.__excepthook__

        # Install my handler
        install_excepthook()
        self.assertNotEqual(sys.excepthook, original_hook)

        # Disable — should go back to original
        disable_excepthook()
        self.assertIs(sys.excepthook, original_hook)

    def test_handler_creates_and_displays_report(self):
        """The custom handler builds a PokedexReport report using from_dict() and calls .show()."""

        install_excepthook()

        with patch("catch_them_all.error_report.PokedexReport.from_dict") as mock_from:
            mock_report = Mock()
            mock_report.show.return_value = None
            mock_from.return_value = mock_report

            # Simulate uncaught exception
            sys.excepthook(ValueError, ValueError("boom"), None)

            mock_from.assert_called_once()  # now checking from_dict
            mock_report.show.assert_called_once()

    def test_system_exceptions_pass_through_to_original(self):
        """KeyboardInterrupt, SystemExit, and GeneratorExit call the original handler."""

        install_excepthook()

        with patch("catch_them_all.excepthook._original_excepthook") as mock_original:
            for exc_type in (KeyboardInterrupt, SystemExit, GeneratorExit):
                with self.subTest(exc_type=exc_type):
                    mock_original.reset_mock()

                    sys.excepthook(exc_type, exc_type(), None)

                    mock_original.assert_called_once_with(exc_type, ANY, None)
                    # Optionally also check that the second arg is an instance of exc_type:
                    called_args = mock_original.call_args[0]
                    self.assertIsInstance(called_args[1], exc_type)


    def test_handler_failure_falls_back_to_original(self):
        """If PokedexReport crashes, the handler should fall back to the original excepthook."""

        install_excepthook()

        # Patch PokedexReport.from_current_exception to raise an error
        with patch("catch_them_all.excepthook.PokedexReport") as mock_cta, \
                patch("catch_them_all.excepthook._original_excepthook") as mock_original:
            # Simulate failure inside handler
            mock_cta.from_dict.side_effect = RuntimeError("boom")

            # Trigger an exception through sys.excepthook
            exc_type = ValueError
            exc_value = exc_type("bad value")

            sys.excepthook(exc_type, exc_value, None)

            # Verify that the original excepthook was called as fallback
            mock_original.assert_called_once_with(exc_type, exc_value, None)





