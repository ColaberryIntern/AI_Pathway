"""Tests for the recommendation judge gate (deterministic parts).
The LLM call (evaluate_recommendation) is integration-tested separately; here we
verify the spec loads and the deterministic gate decision behaves correctly."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.recommendation_judge import (  # noqa: E402
    gate_decision,
    aggregate_results,
    _SYSTEM_PROMPT,
    _SCHEMA,
)
from app.services.judge_scoring import verdict_from_scores  # noqa: E402


def _result(jdc, rf, ont, gap):
    """Build a JudgeResult from sub-scores via the canonical gate logic."""
    scores = {"jd_coverage": jdc, "role_fit_strength": rf,
              "ontology_precision": ont, "gap_validity": gap}
    composite, gate_failures, verdict = verdict_from_scores(scores)
    return {"composite": composite, "overall_verdict": verdict,
            "gate_failures": gate_failures, "scores": scores,
            "regeneration_recommended": verdict == "REJECT"}


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


# --- ensemble aggregation (Trust Before Intelligence determinism) ---

def test_aggregate_happy_unanimous_accept():
    """Happy path: K unanimous strong results aggregate to a clean ACCEPT."""
    runs = [_result(1.0, 0.9, 1.0, 0.8) for _ in range(5)]
    agg = aggregate_results(runs, k=5)
    assert agg["overall_verdict"] == "ACCEPT"
    assert agg["unanimous"] is True
    assert agg["routed_to_review_on_disagreement"] is False
    assert agg["n_runs"] == 5 and agg["composite_spread"] == 0.0


def test_aggregate_disagreement_routes_to_review():
    """The headline guard: a non-unanimous panel whose median would ACCEPT/REJECT
    is routed to ACCEPT_WITH_REVIEW instead of hard-acting on a coin flip."""
    # Two ACCEPTs and one REJECT; median sub-scores still clear the gates -> ACCEPT,
    # but the panel disagreed, so it must be downgraded to review.
    runs = [_result(1.0, 0.9, 1.0, 0.8),   # ACCEPT
            _result(1.0, 0.9, 1.0, 0.8),   # ACCEPT
            _result(0.5, 0.5, 1.0, 0.4)]   # REJECT (gates fail)
    agg = aggregate_results(runs, k=3)
    assert agg["unanimous"] is False
    assert agg["overall_verdict"] == "ACCEPT_WITH_REVIEW"
    assert agg["routed_to_review_on_disagreement"] is True
    assert agg["verdict_counts"]["ACCEPT"] == 2 and agg["verdict_counts"]["REJECT"] == 1


def test_aggregate_unanimous_reject_stays_reject():
    """A unanimous REJECT panel is a true positive and must NOT be softened."""
    runs = [_result(0.6, 0.5, 1.0, 0.4) for _ in range(5)]
    agg = aggregate_results(runs, k=5)
    assert agg["overall_verdict"] == "REJECT"
    assert agg["unanimous"] is True
    assert agg["routed_to_review_on_disagreement"] is False


def test_aggregate_boundary_k1_passthrough():
    """Boundary: K=1 reproduces the single-shot verdict exactly."""
    one = _result(1.0, 0.9, 1.0, 0.8)
    agg = aggregate_results([one], k=1)
    assert agg["overall_verdict"] == one["overall_verdict"]
    assert agg["composite"] == one["composite"]
    assert agg["unanimous"] is True and agg["composite_spread"] == 0.0


def test_aggregate_uses_median_not_mean():
    """Boundary: an outlier run must not drag the aggregate (median, not mean)."""
    runs = [_result(1.0, 0.9, 1.0, 0.8),
            _result(1.0, 0.9, 1.0, 0.8),
            _result(1.0, 0.9, 1.0, 0.8),
            _result(1.0, 0.9, 1.0, 0.8),
            _result(0.0, 0.0, 0.0, 0.0)]  # single garbage outlier
    agg = aggregate_results(runs, k=5)
    assert agg["scores"]["jd_coverage"] == 1.0  # median ignores the outlier


def test_aggregate_empty_raises():
    """Failure path: no samples is a programming error, surfaced loudly."""
    with pytest.raises(ValueError):
        aggregate_results([], k=5)


def test_aggregate_idempotent():
    """Idempotency: same K results -> identical aggregate, no side effects."""
    runs = [_result(0.8, 0.75, 1.0, 0.6), _result(0.9, 0.8, 1.0, 0.6),
            _result(0.7, 0.7, 1.0, 0.6)]
    a = aggregate_results(runs, k=3)
    b = aggregate_results(runs, k=3)
    assert a == b
