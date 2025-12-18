"""
Lightweight observability helpers.

This module is dependency‑free and provides a context‑local request/correlation id
that can be used for structured logging and tracing.

Usage:
    from saptiva_agents.core import request_id_context

    with request_id_context("req-123"):
        result = await team.run(task="...")
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional


_request_id_var: ContextVar[Optional[str]] = ContextVar("saptiva_request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get the current request/correlation id from context (if any)."""
    return _request_id_var.get()


@contextmanager
def request_id_context(request_id: Optional[str]) -> Iterator[None]:
    """
    Set a request/correlation id for the current async context.

    If request_id is falsy, this is a no‑op.
    """
    if not request_id:
        yield
        return

    token = _request_id_var.set(str(request_id))
    try:
        yield
    finally:
        _request_id_var.reset(token)

