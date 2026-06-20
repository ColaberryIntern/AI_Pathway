"""Tests for the recommendation judge gate (deterministic parts).
The LLM call (evaluate_recommendation) is integration-tested separately; here we
verify the spec loads and the deterministic gate decision behaves correctly."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.recommendation_judge import gate_decision, _SYSTEM_PROMPT, _SCHEMA  # noqa: E402


def test_spec_loads():
    assert "PARAMETER 1" in _SYSTEM_PROMPT and "JD COVERAGE" in _SYSTEM_PROMPT
    assert _SCHEMA.get("type") == "object" and "parameters" in _SCHEMA["properties"]


def test_gate_accept():
    d = gate_decision({"overall_verdict": "ACCEPT", "composite": 0.9, "gate_failures": []})
    assert d["pass"] is True and d["action"] == "accept"


def test_gate_review():
    d = gate_decision({"overall_verdict": "ACCEPT_WITH_REVIEW", "composite": 0.78, "gate_failures": []})
    assert d["pass"] is True and d["action"] == "review"


def test_gate_reject_regenerates():
    d = gate_decision({"overall_verdict": "REJECT", "composite": 0.6, "gate_failures": ["role_fit_strength"]})
    assert d["pass"] is False and d["action"] == "regenerate"
