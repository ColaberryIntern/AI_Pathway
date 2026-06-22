"""Tests for LearnerAdjusterAgent (Step 2 of the gap-aware pipeline) with a MOCKED
LLM. Exercises the deterministic post-processing: drop/downgrade/keep application,
the rubric-protected guard, additions validation against the ontology, the
LLM-failure fallback, and the no-op boundaries. Four mandatory types covered.
"""
import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.agents import learner_adjuster as la  # noqa: E402


class FakeOntology:
    def __init__(self, ids):
        self._skills = {i: {"name": i, "domain": "D", "level": 3, "description": "d"} for i in ids}

    def get_all_skill_ids(self):
        return set(self._skills)

    def get_skill(self, sid):
        return self._skills.get(sid)

    def get_proficiency_descriptions(self, sid):
        return []


def _agent(monkeypatch, ontology_ids, llm_result=None, llm_raises=False):
    monkeypatch.setattr(la, "get_ontology_service", lambda: FakeOntology(ontology_ids))
    agent = la.LearnerAdjusterAgent()

    async def fake_llm(prompt, schema, **kw):
        if llm_raises:
            raise RuntimeError("upstream LLM down")
        return llm_result or {}

    agent._call_llm_structured = fake_llm
    return agent


def _cand(sid, importance="medium"):
    return {"skill_id": sid, "skill_name": sid, "importance": importance, "required_level": 3}


def _run(coro):
    return asyncio.run(coro)


# --- happy path ---

def test_keep_downgrade_drop_and_addition(monkeypatch):
    llm = {"adjustments": [
        {"skill_id": "SK.A", "action": "drop", "estimated_current_level": 4},
        {"skill_id": "SK.B", "action": "downgrade", "estimated_current_level": 2},
        {"skill_id": "SK.C", "action": "keep", "estimated_current_level": 1}],
        "additions": [{"skill_id": "SK.NEW", "required_level": 3, "reasoning": "gap"}],
        "summary": "ok"}
    agent = _agent(monkeypatch, ["SK.A", "SK.B", "SK.C", "SK.NEW"], llm_result=llm)
    out = _run(agent.execute({"candidates": [_cand("SK.A"), _cand("SK.B"), _cand("SK.C")],
                              "learner_profile": {"technical_background": "Python"},
                              "target_role": "Software Engineer"}))
    ids = [c["skill_id"] for c in out["adjusted_candidates"]]
    assert "SK.A" not in ids                       # dropped
    assert "SK.NEW" in ids                         # added
    b = next(c for c in out["adjusted_candidates"] if c["skill_id"] == "SK.B")
    assert b["importance"] == "low"                # downgraded
    assert [c["rank"] for c in out["adjusted_candidates"]] == list(
        range(1, len(out["adjusted_candidates"]) + 1))  # renumbered


# --- failure path: LLM error falls back to unchanged candidates ---

def test_llm_failure_falls_back_to_noop(monkeypatch):
    agent = _agent(monkeypatch, ["SK.A"], llm_raises=True)
    cands = [_cand("SK.A")]
    out = _run(agent.execute({"candidates": cands, "learner_profile": {"x": 1},
                              "target_role": "Engineer"}))
    assert [c["skill_id"] for c in out["adjusted_candidates"]] == ["SK.A"]
    assert "LLM call failed" in out.get("summary", "") or out.get("adjustments") == []


# --- structural guard: protected role-essence skill cannot be dropped ---

def test_role_essence_drop_is_guarded(monkeypatch):
    essence = la.ROLE_ESSENCE_SKILLS[0]
    llm = {"adjustments": [{"skill_id": essence, "action": "drop", "estimated_current_level": 5}],
           "additions": [], "summary": "tried to drop essence"}
    agent = _agent(monkeypatch, [essence], llm_result=llm)
    out = _run(agent.execute({"candidates": [_cand(essence)],
                              "learner_profile": {"x": 1},
                              "target_role": "Senior AI Product Marketing Manager"}))
    ids = [c["skill_id"] for c in out["adjusted_candidates"]]
    assert essence in ids                          # guard restored it
    assert essence in out["guard_restored"]


# --- additions validated against the ontology ---

def test_invalid_addition_is_rejected(monkeypatch):
    llm = {"adjustments": [], "additions": [{"skill_id": "SK.BOGUS", "required_level": 3}],
           "summary": "x"}
    agent = _agent(monkeypatch, ["SK.A"], llm_result=llm)  # SK.BOGUS not in ontology
    out = _run(agent.execute({"candidates": [_cand("SK.A")], "learner_profile": {"x": 1},
                              "target_role": "Engineer"}))
    assert "SK.BOGUS" not in [c["skill_id"] for c in out["adjusted_candidates"]]


# --- boundary cases: no-op safeguards ---

def test_no_candidates_is_noop(monkeypatch):
    agent = _agent(monkeypatch, [], llm_result={})
    out = _run(agent.execute({"candidates": [], "learner_profile": {"x": 1}, "target_role": "X"}))
    assert out["adjusted_candidates"] == []


def test_no_learner_profile_is_noop(monkeypatch):
    agent = _agent(monkeypatch, ["SK.A"], llm_result={})
    out = _run(agent.execute({"candidates": [_cand("SK.A")], "learner_profile": {}, "target_role": "X"}))
    assert [c["skill_id"] for c in out["adjusted_candidates"]] == ["SK.A"]


# --- idempotency ---

def test_idempotent(monkeypatch):
    llm = {"adjustments": [{"skill_id": "SK.B", "action": "downgrade", "estimated_current_level": 2}],
           "additions": [], "summary": "ok"}

    def run_once():
        agent = _agent(monkeypatch, ["SK.A", "SK.B"], llm_result=llm)
        out = _run(agent.execute({"candidates": [_cand("SK.A"), _cand("SK.B")],
                                  "learner_profile": {"x": 1}, "target_role": "Engineer"}))
        return [(c["skill_id"], c.get("importance")) for c in out["adjusted_candidates"]]

    assert run_once() == run_once()
