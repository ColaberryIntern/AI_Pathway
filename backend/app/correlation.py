"""Correlation ID context (Trust Before Intelligence - Observability).

A single user action gets one correlation_id, generated at the request entry point
and propagated to every downstream log line (including the LLM resilience telemetry)
via a contextvar - no need to thread it through every call signature.

Kept dependency-free (no FastAPI/Starlette imports) so low-level modules like the
LLM resilience wrapper can read the current id without pulling in the web stack.
"""
from __future__ import annotations

import contextvars
import uuid

_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


def new_correlation_id() -> str:
    """A fresh correlation id (hex, no dashes)."""
    return uuid.uuid4().hex


def get_correlation_id() -> str | None:
    """The correlation id bound to the current context, or None."""
    return _correlation_id.get()


def set_correlation_id(cid: str | None) -> contextvars.Token:
    """Bind a correlation id to the current context. Returns a reset token."""
    return _correlation_id.set(cid)


def reset_correlation_id(token: contextvars.Token) -> None:
    """Restore the previous correlation id (use the token from set_correlation_id)."""
    _correlation_id.reset(token)
