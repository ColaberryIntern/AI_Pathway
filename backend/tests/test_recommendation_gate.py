"""Tests for the recommendation gate regeneration fallback (deterministic).

The judge is injected via judge_fn so these run with no LLM. Covers the four
mandatory types: happy path, failure path, boundary cases, idempotency - plus the
regenerate-then-pass and graceful-degradation scenarios that make hard-gating safe.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.recommendation_gate import gated_recommendation  # noqa: E402


def _skills(*ids):
    return [{"skill_id": i, "skill_name": i} for i in ids]


def _verdict(composite, gate_failures):
    if gate_failures or composite < 0.70:
        return "REJECT"
    return "ACCEPT" if composite >= 0.85 else "ACCEPT_WITH_REVIEW"


class FakeJudge:
    """Scriptable judge. `rule(ids)` -> (composite, gate_failures, weak_ids)."""

    def __init__(self, rule):
        self.rule = rule
        self.calls = []

    async def __call__(self, *, jd_text, li_text, skills, k=None):
        ids = [s["skill_id"] for s in skills]
        self.calls.append(list(ids))
        composite, gate_failures, weak = self.rule(ids)
        return {
            "overall_verdict": _verdict(composite, gate_failures),
            "composite": composite,
            "gate_failures": list(gate_failures),
            "weak_skill_ids": list(weak),
            "scores": {},
        }


def _run(coro):
    return asyncio.run(coro)


# --- happy path ---

def test_happy_first_try_accept():
    judge = FakeJudge(lambda ids: (0.92, [], []))
    out = _run(gated_recommendation("jd", "li", _skills("A", "B", "C"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    assert out["decision"]["verdict"] == "ACCEPT"
    assert out["regenerated"] is False and out["needs_human_review"] is False
    assert out["exhausted"] is False
    assert len(judge.calls) == 1


def test_review_verdict_accepted_but_flagged():
    judge = FakeJudge(lambda ids: (0.78, [], []))
    out = _run(gated_recommendation("jd", "li", _skills("A", "B", "C"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    assert out["decision"]["verdict"] == "ACCEPT_WITH_REVIEW"
    assert out["needs_human_review"] is True and out["exhausted"] is False
    assert out["regenerated"] is False


# --- regenerate then pass ---

def test_regenerate_swaps_weak_skill_then_passes():
    # Reject while weak skill 'B' is present; 'B' is swapped for the next-ranked
    # pool candidate 'C', after which the set passes. 'A' is never weak.
    def rule(ids):
        if "B" in ids:
            return 0.5, ["role_fit_strength"], ["B"]
        return 0.9, [], []
    judge = FakeJudge(rule)
    out = _run(gated_recommendation("jd", "li", _skills("A", "B", "C", "D"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    assert out["decision"]["verdict"] == "ACCEPT"
    assert out["regenerated"] is True and out["needs_human_review"] is False
    final_ids = [s["skill_id"] for s in out["skills"]]
    assert "B" not in final_ids and "C" in final_ids and "A" in final_ids


def test_no_weak_flag_still_progresses_by_swapping_lowest():
    # Always reject but never flag a weak skill -> the loop must still change the
    # set (swap the lowest-ranked) rather than re-judge the identical top-N.
    judge = FakeJudge(lambda ids: (0.5, ["jd_coverage"], []))
    out = _run(gated_recommendation("jd", "li", _skills("A", "B", "C", "D"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    # three attempts, each a distinct set
    assert len(judge.calls) == 3
    assert len({tuple(c) for c in judge.calls}) == 3


# --- graceful degradation / failure path ---

def test_exhaust_degrades_to_best_attempt():
    # composite improves across attempts; final result must be the best one, flagged.
    scores = {("A", "B"): 0.40, ("A", "C"): 0.66, ("A", "D"): 0.55}
    def rule(ids):
        c = scores.get(tuple(ids), 0.30)
        return c, ["jd_coverage"], ["B"]  # always reject
    judge = FakeJudge(rule)
    out = _run(gated_recommendation("jd", "li", _skills("A", "B", "C", "D"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    assert out["exhausted"] is True and out["needs_human_review"] is True
    assert out["decision"]["composite"] == 0.66  # the best attempt
    assert [s["skill_id"] for s in out["skills"]] == ["A", "C"]


# --- boundary cases ---

def test_boundary_empty_pool():
    judge = FakeJudge(lambda ids: (0.9, [], []))
    out = _run(gated_recommendation("jd", "li", [], top_n=5, judge_fn=judge))
    assert out["skills"] == [] and out["needs_human_review"] is True
    assert out["exhausted"] is True and len(judge.calls) == 0


def test_boundary_no_replacements_degrades_after_one_attempt():
    # pool exactly fills top_n; on reject there is nothing to swap in.
    judge = FakeJudge(lambda ids: (0.4, ["jd_coverage"], ["A"]))
    out = _run(gated_recommendation("jd", "li", _skills("A", "B"),
                                    top_n=2, max_attempts=3, judge_fn=judge))
    assert len(judge.calls) == 1 and out["exhausted"] is True
    assert out["needs_human_review"] is True


def test_boundary_skips_pool_entries_without_id():
    pool = _skills("A", "B") + [{"skill_name": "no id"}] + _skills("C")
    judge = FakeJudge(lambda ids: (0.92, [], []))
    out = _run(gated_recommendation("jd", "li", pool, top_n=2, judge_fn=judge))
    assert out["decision"]["verdict"] == "ACCEPT"
    # the id-less entry is filtered out of the pool entirely
    assert all(s.get("skill_id") for s in out["skills"])


# --- idempotency ---

def test_idempotent():
    rule = lambda ids: (0.5, ["role_fit_strength"], ["B"]) if "B" in ids else (0.9, [], [])
    out1 = _run(gated_recommendation("jd", "li", _skills("A", "B", "C", "D"),
                                     top_n=2, max_attempts=3, judge_fn=FakeJudge(rule)))
    out2 = _run(gated_recommendation("jd", "li", _skills("A", "B", "C", "D"),
                                     top_n=2, max_attempts=3, judge_fn=FakeJudge(rule)))
    assert out1 == out2
