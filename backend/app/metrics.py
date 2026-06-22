"""In-process rolling metrics (Trust Before Intelligence - Observability).

Phase 1b emits per-call/per-request telemetry to the logs; this aggregates the same
events into the Observability framework's required metrics so they are queryable at a
glance via /metrics:
  - success rate / failure rate (rolling window)
  - failures broken down by error_class
  - retry count
  - latency p50/p95/p99

Scope: in-process, bounded, resets on restart. A persistent/queryable store
(Prometheus or a metrics table) + dashboards is the follow-up that fully closes the
Transparent dimension; this is the computation + exposure step that makes that swap
a drop-in.

Status vocabulary: "success" and "retry" are special; every other status (failure,
fatal, error, ...) counts as a terminal failure. "retry" is non-terminal and only
feeds retry_count.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

_MAXLEN = 5000          # bounded samples per category
_WINDOW_S = 24 * 3600   # default rolling window (24h)

# category -> deque[(ts, status, duration_ms, error_class)]
_series: dict[str, deque] = defaultdict(lambda: deque(maxlen=_MAXLEN))
_lock = Lock()


def record(category: str, status: str, duration_ms: float | None = None,
           error_class: str | None = None) -> None:
    """Record one telemetry event. Cheap + non-blocking; never raises."""
    try:
        with _lock:
            _series[category].append((time.time(), status, duration_ms, error_class))
    except Exception:
        pass  # metrics must never break the caller


def _percentiles(values: list[float]) -> dict:
    if not values:
        return {}
    s = sorted(values)
    n = len(s)

    def pc(p: float) -> float:
        if n == 1:
            return round(s[0], 1)
        idx = int(round((p / 100) * (n - 1)))
        return round(s[min(idx, n - 1)], 1)

    return {"p50": pc(50), "p95": pc(95), "p99": pc(99)}


def snapshot(window_s: float = _WINDOW_S) -> dict:
    """Aggregate all categories over the rolling window."""
    now = time.time()
    out: dict[str, dict] = {}
    with _lock:
        items = {cat: list(series) for cat, series in _series.items()}
    for cat, rows in items.items():
        rows = [r for r in rows if now - r[0] <= window_s]
        if not rows:
            continue
        retries = [r for r in rows if r[1] == "retry"]
        terminal = [r for r in rows if r[1] != "retry"]
        n_term = len(terminal)
        succ = sum(1 for r in terminal if r[1] == "success")
        by_err: dict[str, int] = {}
        for r in terminal:
            if r[1] != "success" and r[3]:
                by_err[r[3]] = by_err.get(r[3], 0) + 1
        durs = [r[2] for r in terminal if r[2] is not None]
        out[cat] = {
            "count": n_term,
            "success_rate": round(succ / n_term, 4) if n_term else 0.0,
            "failure_rate": round((n_term - succ) / n_term, 4) if n_term else 0.0,
            "failures_by_error_class": by_err,
            "retry_count": len(retries),
            "latency_ms": _percentiles(durs),
        }
    return out


def reset() -> None:
    """Clear all series (tests)."""
    with _lock:
        _series.clear()
