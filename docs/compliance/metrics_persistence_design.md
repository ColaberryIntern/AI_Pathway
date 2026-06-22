# Metrics persistence + dashboards - design (Transparent -> 6)

The in-process metrics (`app/metrics.py`, exposed at `/metrics`) compute the
Observability framework's required metrics but reset on restart and aren't queryable
historically. This is the design to make them **persisted + dashboarded** - the final
increment that takes Transparent from 5 to 6.

## Requirements (from the Observability framework in CLAUDE.md)
- Rolling 24h success rate / failure rate (by `error_class`), retry count, latency
  p50/p95/p99 - already computed in `snapshot()`.
- Survive restarts; queryable over time; viewable on a dashboard.
- Per-execution telemetry already carries `correlation_id`, `duration_ms`, `status`,
  `error_class` (Phase 1b) - the inputs are in place.

## Options

| Option | How | Pros | Cons / deps |
|---|---|---|---|
| **A. Prometheus + Grafana** (recommended) | add `prometheus_client`; expose `/metrics` in Prom text format (Counter for requests/llm calls by status+error_class, Histogram for latency); scrape with Prometheus; Grafana dashboard | industry standard; real percentiles via histogram buckets; free dashboards/alerting; no app-side storage | **infra**: run Prometheus + Grafana containers; one new dependency |
| B. DB table + periodic flush | append events to a `telemetry` table; a periodic job rolls up; a small admin page renders | no new infra (reuses the DB) | reinvents histograms/retention; dashboard is bespoke; write load on the app DB |
| C. Managed (Datadog / GCP Cloud Monitoring) | ship metrics to a SaaS/agent | least ops; alerting included | cost; vendor; egress/credentials |

**Recommendation: A.** It's the standard, gives correct percentiles (histogram
buckets, not sampled), and decouples storage/dashboards from the app. B is the
fallback if no infra can be added. C if a managed stack already exists.

## Drop-in seam shipped with this design (the "stub")
`app/metrics.py` now has a **sink hook**: `register_sink(fn)` registers a callable
that `record()` forwards every event to (best-effort, never raises). Today no sink is
registered, so behavior is unchanged. A persistence layer plugs in without touching
any call site:

```python
# app/metrics_prometheus.py (future, Option A)
from prometheus_client import Counter, Histogram
from app import metrics
_calls = Counter("llm_calls_total", "...", ["category", "status", "error_class"])
_lat   = Histogram("llm_latency_ms", "...", ["category"])
def _sink(category, status, duration_ms, error_class, ts):
    _calls.labels(category, status, error_class or "").inc()
    if duration_ms is not None:
        _lat.labels(category).observe(duration_ms)
metrics.register_sink(_sink)   # called once at startup
```

## Rollout
1. Add `prometheus_client`; implement `metrics_prometheus.py` + register the sink at
   startup; expose `/metrics/prom` (or repoint `/metrics`) in Prometheus format.
2. Stand up Prometheus + Grafana (infra - owner action) and point a scrape at the
   backend.
3. Build the Grafana dashboard: success/failure rate, failures by `error_class`,
   retry rate, latency p50/p95/p99, per `http_request` and `llm_call`.
4. Add alerts (e.g. llm_call failure_rate > X% over 15m).

Steps 1 + 3 are app/config work; step 2 (+ 4) is infra the owner provisions. Until
then, the in-process `/metrics` endpoint + the structured logs remain the source.
