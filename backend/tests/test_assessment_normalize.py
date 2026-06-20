"""Tests for the assessment deterministic guard (Trust Before Intelligence)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.agents.assessment_agent import normalize_skill_scores  # noqa: E402


def test_happy_path_and_derives_state_a():
    raw = {"skill_scores": [
        {"skill_id": "SK.PRD.001", "assessed_level": 3, "confidence": 0.8},
        {"skill_id": "SK.EVL.001", "assessed_level": 5, "confidence": 0.9},
    ], "state_a_skills": {"SK.WRONG": 1}}  # divergent LLM map must be overridden
    out = normalize_skill_scores(raw)
    assert out["state_a_skills"] == {"SK.PRD.001": 3, "SK.EVL.001": 5}


def test_clamps_out_of_range():
    raw = {"skill_scores": [
        {"skill_id": "A", "assessed_level": 9, "confidence": 1.7},
        {"skill_id": "B", "assessed_level": -2, "confidence": -0.5},
        {"skill_id": "C", "assessed_level": "expert", "confidence": "high"},
    ]}
    out = {s["skill_id"]: s for s in normalize_skill_scores(raw)["skill_scores"]}
    assert out["A"]["assessed_level"] == 5 and out["A"]["confidence"] == 1.0
    assert out["B"]["assessed_level"] == 0 and out["B"]["confidence"] == 0.0
    assert out["C"]["assessed_level"] == 0  # non-numeric -> 0, not trusted


def test_failure_path_invalid_ontology_id_dropped():
    raw = {"skill_scores": [
        {"skill_id": "SK.PRD.001", "assessed_level": 2},
        {"skill_id": "SK.FAKE.999", "assessed_level": 4},
    ]}
    out = normalize_skill_scores(raw, valid_skill_ids={"SK.PRD.001"})
    assert [s["skill_id"] for s in out["skill_scores"]] == ["SK.PRD.001"]
    assert "SK.FAKE.999" not in out["state_a_skills"]


def test_boundary_empty():
    assert normalize_skill_scores({})["skill_scores"] == []
    assert normalize_skill_scores({})["state_a_skills"] == {}
    assert normalize_skill_scores({"skill_scores": [{"assessed_level": 3}]})["skill_scores"] == []  # no id


def test_idempotency():
    raw = {"skill_scores": [{"skill_id": "A", "assessed_level": 9, "confidence": 2}]}
    once = normalize_skill_scores(raw)
    assert normalize_skill_scores(once) == once
