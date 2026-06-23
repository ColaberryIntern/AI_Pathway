"""Persist the in-process /metrics rolling window to the DB on a timer, so the TBI
dashboard can show trends that survive restarts (Transparent -> 6, persistence half).

persist_current(db)  - write one row per metric category from the current snapshot.
recent_trends(db)    - recent rows grouped by category (chronological) for the dashboard.
run_persistence_loop - the lifespan background task (sleep -> persist, exception-safe).
"""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.metrics import snapshot
from app.models.metrics_snapshot import MetricsSnapshot

logger = logging.getLogger(__name__)


async def persist_current(db: AsyncSession) -> int:
    """Write one MetricsSnapshot row per category in the current snapshot. Returns
    the number of rows written (0 when there is no traffic in the window)."""
    snap = snapshot()
    n = 0
    for category, m in snap.items():
        lat = m.get("latency_ms", {}) or {}
        db.add(MetricsSnapshot(
            category=category,
            count=m.get("count", 0),
            success_rate=m.get("success_rate", 0.0),
            failure_rate=m.get("failure_rate", 0.0),
            retry_count=m.get("retry_count", 0),
            p50=lat.get("p50"), p95=lat.get("p95"), p99=lat.get("p99"),
        ))
        n += 1
    if n:
        await db.commit()
    return n


async def recent_trends(db: AsyncSession, limit_per_cat: int = 24) -> dict:
    """Recent persisted samples grouped by category, oldest-first per category."""
    result = await db.execute(
        select(MetricsSnapshot).order_by(MetricsSnapshot.created_at.desc())
        .limit(limit_per_cat * 12)
    )
    out: dict[str, list] = {}
    for row in result.scalars().all():
        bucket = out.setdefault(row.category, [])
        if len(bucket) < limit_per_cat:
            bucket.append({
                "t": row.created_at.isoformat() if row.created_at else None,
                "success_rate": row.success_rate,
                "p95": row.p95,
                "count": row.count,
            })
    for bucket in out.values():
        bucket.reverse()  # chronological
    return out


async def run_persistence_loop(interval_s: int) -> None:
    """Background task: every interval_s, snapshot -> DB. Exception-safe; runs until
    cancelled at shutdown."""
    from app.database import AsyncSessionLocal
    while True:
        try:
            await asyncio.sleep(interval_s)
            async with AsyncSessionLocal() as db:
                written = await persist_current(db)
            if written:
                logger.info("metrics_persisted", extra={"rows": written})
        except asyncio.CancelledError:
            raise
        except Exception as e:  # noqa: BLE001 - never let the loop die
            logger.warning("metrics_persist_failed", extra={"error": str(e)})
