"""Tests for metrics DB persistence + trend rendering (Transparent persistence half).
Uses a throwaway in-memory async SQLite engine; no real DB touched.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base  # noqa: E402
from app import metrics  # noqa: E402
from app.services.metrics_persistence import persist_current, recent_trends  # noqa: E402
from app.services.tbi import render_dashboard_html  # noqa: E402


async def _make_session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _run(coro):
    return asyncio.run(coro)


# --- happy path: persist a snapshot, read it back as a trend ---

def test_persist_and_read_trend():
    async def scenario():
        engine, Session = await _make_session_factory()
        metrics.reset()
        for _ in range(8):
            metrics.record("llm_call", "success", 10.0)
        metrics.record("llm_call", "failure", 20.0, "RateLimitError")
        async with Session() as db:
            n = await persist_current(db)
        async with Session() as db:
            trends = await recent_trends(db)
        await engine.dispose()
        return n, trends
    n, trends = _run(scenario())
    assert n == 1                                  # one category persisted
    assert "llm_call" in trends and len(trends["llm_call"]) == 1
    assert trends["llm_call"][0]["success_rate"] == round(8 / 9, 4)


# --- failure/boundary: no traffic -> nothing persisted ---

def test_empty_snapshot_persists_nothing():
    async def scenario():
        engine, Session = await _make_session_factory()
        metrics.reset()
        async with Session() as db:
            n = await persist_current(db)
        async with Session() as db:
            trends = await recent_trends(db)
        await engine.dispose()
        return n, trends
    n, trends = _run(scenario())
    assert n == 0 and trends == {}


# --- boundary: multiple samples come back chronological ---

def test_multiple_samples_chronological():
    async def scenario():
        engine, Session = await _make_session_factory()
        metrics.reset()
        metrics.record("http_request", "success", 5.0)
        async with Session() as db:
            await persist_current(db)
        metrics.record("http_request", "failure", 5.0, "HTTP_500")
        async with Session() as db:
            await persist_current(db)
        async with Session() as db:
            trends = await recent_trends(db)
        await engine.dispose()
        return trends
    trends = _run(scenario())
    series = trends["http_request"]
    assert len(series) == 2
    # first sample was all-success (1.0), second includes a failure (<1.0)
    assert series[0]["success_rate"] == 1.0 and series[1]["success_rate"] < 1.0


# --- render: the trend panel + sparkline appears ---

def test_render_includes_trend_panel():
    status = {
        "inpact": {"max_per": 6, "total": 25, "max": 36, "pct": 69, "production_line": 80,
                   "dimensions": [{"name": "Adaptive", "score": 5, "basis": "x"}]},
        "layers": [], "goals": {"governance": {}, "observability": {}, "availability": {"rag": {}},
                                "lexicon": {}, "solid": {}},
        "trends": {"llm_call": [{"success_rate": 1.0, "p95": 12, "count": 5},
                                {"success_rate": 0.8, "p95": 30, "count": 5}]},
    }
    html = render_dashboard_html(status)
    assert "Trends (persisted history)" in html
    assert "success-rate trend" in html
    assert any(ch in html for ch in "▁▂▃▄▅▆▇█")  # a sparkline was drawn


def test_render_trend_panel_empty_state():
    status = {
        "inpact": {"max_per": 6, "total": 25, "max": 36, "pct": 69, "production_line": 80, "dimensions": []},
        "layers": [], "goals": {"governance": {}, "observability": {}, "availability": {"rag": {}},
                                "lexicon": {}, "solid": {}},
        "trends": {},
    }
    html = render_dashboard_html(status)
    assert "No persisted history yet" in html
