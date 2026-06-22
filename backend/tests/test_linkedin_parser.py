"""Tests for LinkedInParserAgent with a MOCKED LLM. Covers the no-op boundary,
ontology-validated skill enrichment, the LLM-failure fallback, and idempotency.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.agents import linkedin_parser as lp  # noqa: E402


class FakeOntology:
    def __init__(self, ids):
        self._skills = {i: {"name": f"name-{i}", "domain": "D.X", "level": 2} for i in ids}

    def get_all_skill_ids(self):
        return set(self._skills)

    def get_skill(self, sid):
        return self._skills.get(sid)


def _agent(monkeypatch, ids, llm_result=None, llm_raises=False):
    monkeypatch.setattr(lp, "get_ontology_service", lambda: FakeOntology(ids))
    agent = lp.LinkedInParserAgent()

    async def fake_llm(prompt, schema, **kw):
        if llm_raises:
            raise RuntimeError("LLM down")
        return llm_result or {}

    agent._call_llm_structured = fake_llm
    return agent


def _run(c):
    return asyncio.run(c)


# --- boundary: no LinkedIn text -> deterministic no-op ---

def test_empty_text_noop(monkeypatch):
    agent = _agent(monkeypatch, ["SK.A"])
    out = _run(agent.execute({"linkedin_text": ""}))
    assert out["existing_skills"] == []
    assert out["ai_fluency_assessment"]["level"] == "aware"


# --- happy path: invalid skill ids filtered, valid ones enriched from ontology ---

def test_valid_skills_enriched_invalid_dropped(monkeypatch):
    llm = {"existing_skills": [{"skill_id": "SK.A", "confidence": 0.9},
                              {"skill_id": "SK.BOGUS", "confidence": 0.5}],
           "transferable_skills": [{"name": "leadership"}],
           "ai_fluency_assessment": {"level": "intermediate", "reasoning": "r"},
           "summary": "ok"}
    agent = _agent(monkeypatch, ["SK.A"], llm_result=llm)
    out = _run(agent.execute({"linkedin_text": "10 years marketing, used ChatGPT",
                              "current_role": "Marketer"}))
    ids = [s["skill_id"] for s in out["existing_skills"]]
    assert ids == ["SK.A"]                       # SK.BOGUS dropped (not in ontology)
    assert out["existing_skills"][0]["skill_name"] == "name-SK.A"  # enriched
    assert out["transferable_skills"] == [{"name": "leadership"}]
    assert out["ai_fluency_assessment"]["level"] == "intermediate"


# --- failure path: LLM error -> safe fallback ---

def test_llm_failure_fallback(monkeypatch):
    agent = _agent(monkeypatch, ["SK.A"], llm_raises=True)
    out = _run(agent.execute({"linkedin_text": "some text"}))
    assert out["existing_skills"] == []
    assert out["ai_fluency_assessment"]["level"] == "aware"
    assert "failed" in out["summary"].lower()


# --- idempotency ---

def test_idempotent(monkeypatch):
    llm = {"existing_skills": [{"skill_id": "SK.A"}], "transferable_skills": [],
           "ai_fluency_assessment": {"level": "aware"}, "summary": "s"}

    def once():
        agent = _agent(monkeypatch, ["SK.A"], llm_result=llm)
        out = _run(agent.execute({"linkedin_text": "t"}))
        return [s["skill_id"] for s in out["existing_skills"]], out["summary"]

    assert once() == once()
