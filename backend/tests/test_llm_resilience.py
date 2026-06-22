"""Tests for the LLM resilience wrapper (timeout + capped retry + categorization).

Covers the four mandatory types: happy path, failure path (fatal + exhaustion),
boundary (max_retries=0, timeout), idempotency (fresh awaitable per attempt).
base_delay=0 keeps backoff instant so the suite stays fast.
"""
import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.llm._resilience import call_with_resilience, is_retryable  # noqa: E402


# Exception names that match the transient set / carry a retryable status code.
class RateLimitError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class HTTPError(Exception):
    def __init__(self, status):
        super().__init__(f"http {status}")
        self.status_code = status


def _run(coro):
    return asyncio.run(coro)


def _factory(seq):
    """Return (make_awaitable, calls) where each call pops the next item in seq;
    an Exception instance is raised, anything else is returned."""
    state = {"n": 0}

    async def make():
        i = state["n"]
        state["n"] += 1
        item = seq[i] if i < len(seq) else seq[-1]
        if isinstance(item, BaseException):
            raise item
        return item

    return make, state


# --- classification ---

def test_is_retryable_by_name_and_status():
    assert is_retryable(RateLimitError("x")) is True
    assert is_retryable(HTTPError(503)) is True
    assert is_retryable(HTTPError(429)) is True
    assert is_retryable(asyncio.TimeoutError()) is True
    assert is_retryable(AuthenticationError("bad key")) is False
    assert is_retryable(HTTPError(400)) is False
    assert is_retryable(ValueError("nope")) is False


# --- happy path ---

def test_happy_first_try():
    make, state = _factory(["ok"])
    out = _run(call_with_resilience(make, provider="t", op="o",
                                    timeout=1, max_retries=2, base_delay=0))
    assert out == "ok" and state["n"] == 1


# --- retry then succeed ---

def test_retry_then_succeed():
    make, state = _factory([RateLimitError("slow down"), "ok"])
    out = _run(call_with_resilience(make, provider="t", op="o",
                                    timeout=1, max_retries=2, base_delay=0))
    assert out == "ok" and state["n"] == 2  # one retry consumed


# --- failure path: fatal error is not retried ---

def test_fatal_error_not_retried():
    make, state = _factory([AuthenticationError("bad key"), "ok"])
    with pytest.raises(AuthenticationError):
        _run(call_with_resilience(make, provider="t", op="o",
                                  timeout=1, max_retries=3, base_delay=0))
    assert state["n"] == 1  # raised immediately, no retry


# --- failure path: transient errors exhaust the budget then raise ---

def test_exhaust_retries_raises():
    make, state = _factory([HTTPError(503), HTTPError(503), HTTPError(503), HTTPError(503)])
    with pytest.raises(HTTPError):
        _run(call_with_resilience(make, provider="t", op="o",
                                  timeout=1, max_retries=2, base_delay=0))
    assert state["n"] == 3  # 1 + 2 retries


# --- boundary: timeout is enforced and is retryable ---

def test_timeout_enforced_and_retried():
    state = {"n": 0}

    async def slow():
        state["n"] += 1
        await asyncio.sleep(5)  # far longer than the timeout

    with pytest.raises(asyncio.TimeoutError):
        _run(call_with_resilience(slow, provider="t", op="o",
                                  timeout=0.01, max_retries=1, base_delay=0))
    assert state["n"] == 2  # initial + 1 retry, each timed out


# --- boundary: max_retries=0 means exactly one attempt ---

def test_no_retries_single_attempt():
    make, state = _factory([RateLimitError("x"), "ok"])
    with pytest.raises(RateLimitError):
        _run(call_with_resilience(make, provider="t", op="o",
                                  timeout=1, max_retries=0, base_delay=0))
    assert state["n"] == 1


# --- idempotency: a fresh awaitable is built each attempt (no double-await) ---

def test_fresh_awaitable_each_attempt():
    # If the wrapper re-awaited a spent coroutine it would raise RuntimeError;
    # success after a retry proves a new awaitable is created per attempt.
    make, state = _factory([HTTPError(500), HTTPError(500), "recovered"])
    out = _run(call_with_resilience(make, provider="t", op="o",
                                    timeout=1, max_retries=3, base_delay=0))
    assert out == "recovered" and state["n"] == 3
