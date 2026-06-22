"""Resilience wrapper for external LLM calls (Trust Before Intelligence -
Failure-First Design + Security Enforcement Layer + Observability).

Every provider routes its single network call through call_with_resilience, which
gives the three things CLAUDE.md mandates for an external call:

  - Timeout: an explicit hard ceiling (asyncio.wait_for), never unbounded.
  - Retry: capped exponential backoff with jitter, only on TRANSIENT failures
    (timeout, connection, rate limit, 5xx). LLM generation is read-only, so a
    retry is idempotency-safe.
  - Error handling: failures are categorized (error_class) and either retried or
    raised immediately; nothing is silently swallowed.

It also emits per-call telemetry (provider, op, attempt, duration_ms, status,
error_class) so a single LLM call is traceable - the start of the Observability
layer. A correlation_id is included when one is bound to the call context.

Contract:
    await call_with_resilience(make_awaitable, *, provider, op,
                               timeout=None, max_retries=None, base_delay=None)
    make_awaitable: zero-arg callable returning a FRESH awaitable each attempt
                    (a coroutine cannot be awaited twice).
"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Awaitable, Callable, TypeVar

from app.config import get_settings
from app.correlation import get_correlation_id

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Transient failure signatures (provider-agnostic, matched on exception class name
# so we do not couple to each SDK's exception hierarchy).
_RETRYABLE_NAMES = {
    "APITimeoutError", "APIConnectionError", "APIError", "RateLimitError",
    "InternalServerError", "ServiceUnavailable", "DeadlineExceeded",
    "ResourceExhausted", "TooManyRequests", "ServerError", "OverloadedError",
    "Timeout", "ConnectionError", "ConnectError", "ReadTimeout",
}
_RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


def _error_class(exc: BaseException) -> str:
    return type(exc).__name__


def is_retryable(exc: BaseException) -> bool:
    """A transient error worth retrying (vs a fatal auth/validation error)."""
    if isinstance(exc, asyncio.TimeoutError):
        return True
    if type(exc).__name__ in _RETRYABLE_NAMES:
        return True
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    try:
        if status is not None and int(status) in _RETRYABLE_STATUS:
            return True
    except (TypeError, ValueError):
        pass
    return False


async def call_with_resilience(
    make_awaitable: Callable[[], Awaitable[T]],
    *,
    provider: str,
    op: str,
    timeout: float | None = None,
    max_retries: int | None = None,
    base_delay: float | None = None,
    correlation_id: str | None = None,
) -> T:
    """Run an external LLM call with timeout + capped backoff + categorized errors."""
    settings = get_settings()
    timeout = settings.llm_timeout_seconds if timeout is None else timeout
    max_retries = settings.llm_max_retries if max_retries is None else max_retries
    base_delay = settings.llm_retry_base_delay if base_delay is None else base_delay
    if correlation_id is None:
        correlation_id = get_correlation_id()  # trace LLM calls back to the request

    attempts = max(1, max_retries + 1)
    last_exc: BaseException | None = None

    for attempt in range(1, attempts + 1):
        started = time.monotonic()
        try:
            result = await asyncio.wait_for(make_awaitable(), timeout=timeout)
            logger.info(
                "llm_call",
                extra={"provider": provider, "op": op, "attempt": attempt,
                       "duration_ms": round((time.monotonic() - started) * 1000, 1),
                       "status": "success", "correlation_id": correlation_id},
            )
            return result
        except BaseException as exc:  # noqa: BLE001 - categorize, then retry or raise
            last_exc = exc
            error_class = "TimeoutError" if isinstance(exc, asyncio.TimeoutError) else _error_class(exc)
            duration_ms = round((time.monotonic() - started) * 1000, 1)
            retryable = is_retryable(exc)
            if attempt < attempts and retryable:
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
                logger.warning(
                    "llm_call retry",
                    extra={"provider": provider, "op": op, "attempt": attempt,
                           "duration_ms": duration_ms, "status": "retry",
                           "error_class": error_class, "retry_in_s": round(delay, 2),
                           "correlation_id": correlation_id},
                )
                await asyncio.sleep(delay)
                continue
            logger.error(
                "llm_call failed",
                extra={"provider": provider, "op": op, "attempt": attempt,
                       "duration_ms": duration_ms,
                       "status": "failure" if retryable else "fatal",
                       "error_class": error_class, "correlation_id": correlation_id},
            )
            raise

    # Unreachable (loop either returns or raises), but keeps type-checkers happy.
    assert last_exc is not None
    raise last_exc
