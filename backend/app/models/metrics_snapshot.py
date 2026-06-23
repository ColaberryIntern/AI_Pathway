"""MetricsSnapshot model - persisted observability history (Transparent layer).

Periodically captures the in-process /metrics rolling window so the TBI dashboard
can show trends that survive restarts (the persistence half of Transparent -> 6).
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MetricsSnapshot(Base):
    """One persisted observability sample for one metric category."""

    __tablename__ = "metrics_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    failure_rate: Mapped[float] = mapped_column(Float, default=0.0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    p50: Mapped[float] = mapped_column(Float, nullable=True)
    p95: Mapped[float] = mapped_column(Float, nullable=True)
    p99: Mapped[float] = mapped_column(Float, nullable=True)
