"""Tests for the in-process observability metrics (success/failure rates,
error_class breakdown, retry count, latency percentiles, rolling window).
Four mandatory types covered.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import metrics  # noqa: E402


@pytest.fixture(autouse=True)
def _clean():
    metrics.reset()
    metrics.register_sink(None)
    yield
    metrics.reset()
    metrics.register_sink(None)


# --- happy path ---

def test_success_and_failure_rates_and_error_class():
    for _ in range(7):
        metrics.record("llm_call", "success", 10.0)
    metrics.record("llm_call", "failure", 20.0, "RateLimitError")
    metrics.record("llm_call", "fatal", 30.0, "AuthError")
    snap = metrics.snapshot()["llm_call"]
    assert snap["count"] == 9
    assert snap["success_rate"] == round(7 / 9, 4)
    assert snap["failure_rate"] == round(2 / 9, 4)
    assert snap["failures_by_error_class"] == {"RateLimitError": 1, "AuthError": 1}


def test_latency_percentiles():
    for d in range(1, 101):  # 1..100 ms -> sorted index p = round(p/100*(n-1))
        metrics.record("http_request", "success", float(d))
    lat = metrics.snapshot()["http_request"]["latency_ms"]
    assert lat["p50"] == 51.0 and lat["p95"] == 95.0 and lat["p99"] == 99.0


# --- retry count is separate from terminal success/failure ---

def test_retry_count_excluded_from_terminal():
    metrics.record("llm_call", "success", 5.0)
    metrics.record("llm_call", "retry", 5.0, "TimeoutError")
    metrics.record("llm_call", "retry", 5.0, "TimeoutError")
    snap = metrics.snapshot()["llm_call"]
    assert snap["count"] == 1            # only the terminal success
    assert snap["success_rate"] == 1.0
    assert snap["retry_count"] == 2


# --- boundary cases ---

def test_empty_snapshot():
    assert metrics.snapshot() == {}


def test_single_sample_percentiles():
    metrics.record("x", "success", 42.0)
    assert metrics.snapshot()["x"]["latency_ms"] == {"p50": 42.0, "p95": 42.0, "p99": 42.0}


def test_window_excludes_old_samples(monkeypatch):
    class FakeClock:
        def __init__(self, t): self.t = t
        def time(self): return self.t
    clock = FakeClock(1000.0)
    monkeypatch.setattr(metrics, "time", clock)
    metrics.record("x", "success", 1.0)   # recorded at t=1000
    clock.t = 1000.0 + 200                 # 200s later
    assert metrics.snapshot(window_s=100) == {}   # sample is older than the window
    assert metrics.snapshot(window_s=300)["x"]["count"] == 1  # within the window


def test_record_never_raises_on_bad_input():
    metrics.record("x", "success", None)  # missing duration is fine
    assert metrics.snapshot()["x"]["count"] == 1
    assert metrics.snapshot()["x"]["latency_ms"] == {}  # no durations -> empty


# --- persistence sink hook (drop-in seam) ---

def test_sink_receives_events():
    seen = []
    metrics.register_sink(lambda cat, status, dur, err, ts: seen.append((cat, status, dur, err)))
    metrics.record("llm_call", "failure", 12.0, "RateLimitError")
    assert seen == [("llm_call", "failure", 12.0, "RateLimitError")]


def test_failing_sink_never_breaks_record():
    def boom(*a):
        raise RuntimeError("sink down")
    metrics.register_sink(boom)
    metrics.record("x", "success", 1.0)          # must not raise
    assert metrics.snapshot()["x"]["count"] == 1  # event still recorded in-process


def test_sink_can_be_cleared():
    seen = []
    metrics.register_sink(lambda *a: seen.append(a))
    metrics.register_sink(None)
    metrics.record("x", "success", 1.0)
    assert seen == []


# --- idempotency ---

def test_snapshot_is_read_only():
    metrics.record("x", "success", 3.0)
    a = metrics.snapshot()
    b = metrics.snapshot()
    assert a == b  # snapshot does not mutate the series
