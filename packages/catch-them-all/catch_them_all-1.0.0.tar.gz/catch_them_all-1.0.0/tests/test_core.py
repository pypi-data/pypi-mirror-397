import unittest
from catch_them_all.core import pokeball
from catch_them_all.error_report import PokedexReport

class ServiceForTesting:
    @classmethod
    @pokeball()
    def cls_method(cls):
        raise ValueError("boom")

    @staticmethod
    @pokeball()
    def static_method():
        raise TypeError("fail")


class TestPokeballDecorator(unittest.TestCase):
    """Tests for the @pokeball decorator — the heart of the library."""

    def test_returns_PokedexReport_object_on_exception(self):
        """Functions wrapped with @pokeball return PokedexReport instead of raising."""

        @pokeball()
        def boom():
            raise ValueError("boom")

        result = boom()
        self.assertIsInstance(result, PokedexReport)
        self.assertEqual(result.name, "ValueError")
        self.assertIn("boom", result.message)

    def test_preserve_function_metadata(self):
        """@pokeball preserves name, docstring, and signature."""

        @pokeball()
        def my_func(x: int, y: str = "hello") -> str:
            """This is a test function."""
            raise RuntimeError("fail")

        result = my_func(42)

        self.assertEqual(my_func.__name__, "my_func")
        self.assertEqual(my_func.__doc__, "This is a test function.")
        self.assertEqual(my_func.__annotations__, {"x": int, "y": str, "return": str})

    def test_on_catch_callback_is_called(self):
        """on_catch callback receives the PokedexReport object."""
        log = []

        @pokeball(on_catch=lambda obj: log.append(obj))
        def fail():
            raise KeyError("missing")
        result = fail()
        self.assertEqual(len(log), 1)
        self.assertIs(log[0], result)


    def test_system_exceptions_propagate(self):
        """KeyboardInterrupt, SystemExit, etc. are NOT caught."""
        system_exceptions = [KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError]

        for exc in system_exceptions:
            with self.subTest(exc=exc):
                @pokeball()
                def raise_system():
                    raise exc()

                with self.assertRaises(exc):
                    raise_system()

    def test_normal_return_value_preserved(self):
        """Non-exception paths return the actual value."""

        @pokeball()
        def success():
            return "all good"

        result = success()
        self.assertEqual(result, "all good")

    def test_multiple_calls_work_independently(self):
        """Each call gets its own isolated PokedexReport object."""

        @pokeball()
        def fail_twice():
            var = 1 / 0

        r1 = fail_twice()
        r2 = fail_twice()

        self.assertIsNot(r1, r2)
        self.assertNotEqual(r1.timestamp, r2.timestamp)

# ________________________________________________________________________________________________________________



    def test_class_and_static_methods_preserve_metadata(self):
        """@pokeball on classmethod/staticmethod preserves __name__, __qualname__, and behavior."""

        result1 = ServiceForTesting.cls_method()
        result2 = ServiceForTesting.static_method()

        self.assertIsInstance(result1, PokedexReport)
        self.assertIsInstance(result2, PokedexReport)

        self.assertEqual(ServiceForTesting.cls_method.__name__, "cls_method")
        self.assertEqual(ServiceForTesting.cls_method.__qualname__, "ServiceForTesting.cls_method")

        self.assertEqual(ServiceForTesting.static_method.__name__, "static_method")
        self.assertEqual(ServiceForTesting.static_method.__qualname__, "ServiceForTesting.static_method")

    def test_nested_decorators_work_in_any_order(self):
        """@pokeball composes correctly with other decorators (lru_cache, etc.)."""
        from functools import lru_cache

        # Order 1: pokeball outer
        @pokeball()
        @lru_cache
        def func1(x):
            raise KeyError("cache miss")

        # Order 2: pokeball inner
        @lru_cache
        @pokeball()
        def func2(x):
            raise KeyError("cache miss")

        r1 = func1(42)
        r2 = func2(42)

        self.assertIsInstance(r1, PokedexReport)
        self.assertIsInstance(r2, PokedexReport)
        self.assertEqual(r1.name, "KeyError")
        self.assertEqual(r2.name, "KeyError")



if __name__ == "__main__":
    unittest.main(verbosity=2)
