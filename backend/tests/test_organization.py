"""Tests for multi-tenancy increment 1: the pure learner-progress aggregator
and the idempotent default-org backfill.

Mandatory types: happy / failure / boundary / idempotency.
"""
import asyncio
from dataclasses import dataclass, field

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401  - register all models on Base.metadata
from app.database import Base
from app.models.organization import DEFAULT_ORG_ID, Organization
from app.models.user import User
from app.services.organization_service import (
    ensure_default_org_and_backfill,
    summarize_learner_paths,
)


# --- pure aggregator fixtures -------------------------------------------------

@dataclass
class FakePath:
    id: str
    title: str
    total_chapters: int


@dataclass
class FakeProgress:
    chapter_status: dict = field(default_factory=dict)


def _run(coro):
    return asyncio.run(coro)


# --- summarize_learner_paths: happy -------------------------------------------

def test_mixed_active_and_completed():
    paths = [FakePath("p1", "A", 4), FakePath("p2", "B", 2)]
    prog = {
        "p1": FakeProgress({"0": "completed", "1": "completed", "2": "not_started", "3": "not_started"}),
        "p2": FakeProgress({"0": "completed", "1": "completed"}),
    }
    s = summarize_learner_paths(paths, prog)
    assert s["total_paths"] == 2
    assert len(s["completed_paths"]) == 1 and s["completed_paths"][0]["id"] == "p2"
    assert len(s["active_paths"]) == 1 and s["active_paths"][0]["completed_chapters"] == 2
    assert s["total_skills_learned"] == 2          # only p2's chapters count
    assert s["overall_completion_percentage"] == round(4 / 6 * 100, 1)


# --- failure / boundary -------------------------------------------------------

def test_no_paths():
    s = summarize_learner_paths([], {})
    assert s == {
        "total_paths": 0, "active_paths": [], "completed_paths": [],
        "total_skills_learned": 0, "overall_completion_percentage": 0.0,
    }


def test_path_with_no_progress_record():
    paths = [FakePath("p1", "A", 3)]
    s = summarize_learner_paths(paths, {"p1": None})
    assert s["active_paths"][0]["completed_chapters"] == 0
    assert s["overall_completion_percentage"] == 0.0


def test_zero_chapter_path_is_not_completed():
    # total_chapters == 0 must never count as a completed path (div-by-zero guard)
    paths = [FakePath("p1", "A", 0)]
    s = summarize_learner_paths(paths, {"p1": FakeProgress({})})
    assert s["completed_paths"] == []
    assert s["active_paths"][0]["completion_percentage"] == 0.0


def test_all_completed():
    paths = [FakePath("p1", "A", 2)]
    s = summarize_learner_paths(paths, {"p1": FakeProgress({"0": "completed", "1": "completed"})})
    assert len(s["completed_paths"]) == 1
    assert s["overall_completion_percentage"] == 100.0


# --- idempotency --------------------------------------------------------------

def test_aggregator_idempotent():
    paths = [FakePath("p1", "A", 4)]
    prog = {"p1": FakeProgress({"0": "completed"})}
    a = summarize_learner_paths(paths, prog)
    b = summarize_learner_paths(paths, prog)
    assert a == b


# --- backfill integration (real throwaway SQLite) -----------------------------

async def _make_session(tmp_path) -> AsyncSession:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def test_backfill_creates_default_org_and_assigns(tmp_path):
    async def scenario():
        Session = await _make_session(tmp_path)
        async with Session() as db:
            db.add_all([User(id="u1", email="a@x.com"), User(id="u2", email="b@x.com")])
            await db.commit()
            r1 = await ensure_default_org_and_backfill(db)
            assert r1["default_org_created"] is True
            assert r1["users_backfilled"] == 2
            org = (await db.execute(
                select(Organization).where(Organization.id == DEFAULT_ORG_ID)
            )).scalars().first()
            assert org is not None
            users = (await db.execute(select(User))).scalars().all()
            assert all(u.org_id == DEFAULT_ORG_ID for u in users)
        return True
    assert _run(scenario())


def test_backfill_idempotent(tmp_path):
    async def scenario():
        Session = await _make_session(tmp_path)
        async with Session() as db:
            db.add(User(id="u1", email="a@x.com"))
            await db.commit()
            await ensure_default_org_and_backfill(db)
            # second run: no new org, nothing left to backfill
            r2 = await ensure_default_org_and_backfill(db)
            assert r2["default_org_created"] is False
            assert r2["users_backfilled"] == 0
            count = (await db.execute(
                select(Organization)
            )).scalars().all()
            assert len(count) == 1
        return True
    assert _run(scenario())


def test_backfill_preserves_explicit_org(tmp_path):
    async def scenario():
        Session = await _make_session(tmp_path)
        async with Session() as db:
            db.add(Organization(id="acme", name="Acme"))
            db.add(User(id="u1", email="a@x.com", org_id="acme"))
            db.add(User(id="u2", email="b@x.com"))  # null -> should get default
            await db.commit()
            await ensure_default_org_and_backfill(db)
            u1 = (await db.execute(select(User).where(User.id == "u1"))).scalars().first()
            u2 = (await db.execute(select(User).where(User.id == "u2"))).scalars().first()
            assert u1.org_id == "acme"            # explicit org preserved
            assert u2.org_id == DEFAULT_ORG_ID    # null backfilled
        return True
    assert _run(scenario())
