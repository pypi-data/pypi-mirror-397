# catch_them_all/core.py supp= python 3.8+
"""Core functionality — the @pokeball decorator and exception capture.

Contains the pokeball decorator that catches exceptions and returns
a PokedexReport object. Preserves function metadata and supports
optional on_catch callbacks.
"""
from __future__ import annotations

import sys
from functools import wraps
from typing import Callable, Any

from .error_report import PokedexReport


def pokeball(
    *,
    on_catch: Callable[..., Any] | None = None,   # accept any callable
    on_catch_args: tuple = (),
    on_catch_kwargs: dict | None = None,
    log: str | None = None
) -> Callable[[Callable], Callable]:
    """Wrap a function to catch exceptions and return a PokedexReport exception report.

    On success, the original return value is preserved. On failure, a PokedexReport
    report is returned instead of raising. Critical system exceptions
    (KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError) propagate
    immediately.

    Parameters
    ----------
    on_catch : callable, optional
        Callback invoked when an exception is caught. Receives the PokedexReport
        report as the first argument, followed by any additional positional
        and keyword arguments from ``on_catch_args`` and ``on_catch_kwargs``.

        on_catch_args : tuple, optional
            Additional positional arguments passed to ``on_catch``.
        on_catch_kwargs : dict, optional
            Additional keyword arguments passed to ``on_catch``.

    log : str, optional
        If provided, the file path is passed to the report’s `.to_log()` method.
        The caught exception will be appended to the specified log file.
        If omitted, no logging is performed.

    Returns
    -------
    callable
        Decorator that can be applied to any function or async function.

    Notes
    -----
    - Preserves function metadata using ``functools.wraps``.
    - Failures in ``on_catch`` are caught and warned to ``sys.stderr``.
    """

    if on_catch is not None and not callable(on_catch):
        raise TypeError("on_catch must be callable or None")

    if on_catch_kwargs is None:
        on_catch_kwargs = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)

            except (KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError):
                raise

            except Exception:
                report = PokedexReport.from_current_exception()

                if log:
                    report.to_log(log)

                if on_catch:
                    try:
                        on_catch(report, *on_catch_args, **on_catch_kwargs)
                    except Exception as e :
                        sys.stderr.write(
                            f"Warning: on_catch handler raised {e!r} during exception handling."
                        )

                return report

        return wrapper

    return decorator



__all__ = ["pokeball"]
