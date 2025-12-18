from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(kw_only=True)
class _ChalkDataFrameDebugContext:
    on_run: "Callable[[DataFrame], None] | None" = None


chalk_dataframe_debug_context_ob = ContextVar[_ChalkDataFrameDebugContext | None](
    "_chalk_dataframe_debug_context", default=None
)


@contextmanager
def chalk_dataframe_debug_context(
    *,
    on_run: "Callable[[DataFrame], None] | None" = None,
):
    """
    This contextmanager sets the debug context for `ChalkDataFrame`, allowing calls to important methods
    like `.on_run()` to be captured by an enclosing context for debugging or testing purposes.
    """
    reset_token = chalk_dataframe_debug_context_ob.set(
        _ChalkDataFrameDebugContext(
            on_run=on_run,
        )
    )
    try:
        yield
    finally:
        chalk_dataframe_debug_context_ob.reset(reset_token)
