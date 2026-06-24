"""Tests for the LinkedIn parser judge deterministic core.

Covers the four mandatory types (happy/failure/boundary/idempotency) on the
pure functions: ontology_precision_score, compute_composite, gate_failures,
determine_verdict, assemble_result. No LLM needed.
"""
from app.services.linkedin_parse_judge import (
    ACCEPT_THRESHOLD,
    GATES,
    REVIEW_THRESHOLD,
    WEIGHTS,
    assemble_result,
    compute_composite,
    determine_verdict,
    gate_failures,
    ontology_precision_score,
)

VALID = {"SK.A", "SK.B", "SK.C"}


def _parse(*ids):
    return {"existing_skills": [{"skill_id": i, "estimated_current_level": 3,
                                 "confidence": "medium", "evidence": "x"} for i in ids]}


# --- ontology_precision_score -------------------------------------------------

def test_precision_all_valid():
    score, invalid = ontology_precision_score(_parse("SK.A", "SK.B"), VALID)
    assert score == 1.0 and invalid == []


def test_precision_some_invalid():
    score, invalid = ontology_precision_score(_parse("SK.A", "BOGUS"), VALID)
    assert score == 0.5 and invalid == ["BOGUS"]


def test_precision_empty_claims_is_one():
    score, invalid = ontology_precision_score({"existing_skills": []}, VALID)
    assert score == 1.0 and invalid == []


def test_precision_missing_key_is_one():
    score, invalid = ontology_precision_score({}, VALID)
    assert score == 1.0 and invalid == []


# --- compute_composite --------------------------------------------------------

def test_composite_all_one():
    scores = {k: 1.0 for k in WEIGHTS}
    assert compute_composite(scores) == 1.0


def test_composite_weighted():
    scores = {"ontology_precision": 1.0, "evidence_quality": 1.0,
              "conservativeness": 0.0, "coverage": 0.0}
    # 0.20 + 0.35 = 0.55
    assert compute_composite(scores) == 0.55


def test_composite_missing_param_counts_zero():
    assert compute_composite({"ontology_precision": 1.0}) == round(WEIGHTS["ontology_precision"], 4)


# --- gate_failures ------------------------------------------------------------

def test_no_gate_failures_when_all_pass():
    scores = {"ontology_precision": 1.0, "evidence_quality": 0.8, "conservativeness": 0.8}
    assert gate_failures(scores) == []


def test_gate_failure_detected():
    scores = {"ontology_precision": 0.5, "evidence_quality": 0.8, "conservativeness": 0.8}
    assert "ontology_precision" in gate_failures(scores)


def test_coverage_has_no_gate():
    # coverage absent / 0 must never be a gate failure (no gate on coverage)
    scores = {"ontology_precision": 1.0, "evidence_quality": 0.8,
              "conservativeness": 0.8, "coverage": 0.0}
    assert gate_failures(scores) == []


# --- determine_verdict --------------------------------------------------------

def test_verdict_reject_on_gate():
    assert determine_verdict(0.99, ["evidence_quality"]) == "REJECT"


def test_verdict_reject_low_composite():
    assert determine_verdict(REVIEW_THRESHOLD - 0.01, []) == "REJECT"


def test_verdict_review_band():
    assert determine_verdict(REVIEW_THRESHOLD, []) == "ACCEPT_WITH_REVIEW"
    assert determine_verdict(ACCEPT_THRESHOLD - 0.001, []) == "ACCEPT_WITH_REVIEW"


def test_verdict_accept():
    assert determine_verdict(ACCEPT_THRESHOLD, []) == "ACCEPT"
    assert determine_verdict(1.0, []) == "ACCEPT"


# --- assemble_result (happy / failure / boundary) -----------------------------

def test_assemble_clean_accept():
    res = assemble_result(_parse("SK.A", "SK.B"), VALID,
                          {"evidence_quality": 1.0, "conservativeness": 1.0, "coverage": 1.0})
    assert res.verdict == "ACCEPT"
    assert res.composite == 1.0
    assert res.gate_failures == []
    assert res.invalid_skill_ids == []


def test_assemble_invalid_id_forces_reject_via_precision_gate():
    # 1 of 2 ids invalid -> precision 0.5 < 0.95 gate -> REJECT
    res = assemble_result(_parse("SK.A", "BOGUS"), VALID,
                          {"evidence_quality": 1.0, "conservativeness": 1.0, "coverage": 1.0})
    assert "ontology_precision" in res.gate_failures
    assert res.verdict == "REJECT"
    assert res.invalid_skill_ids == ["BOGUS"]


def test_assemble_low_evidence_rejects():
    res = assemble_result(_parse("SK.A"), VALID,
                          {"evidence_quality": 0.3, "conservativeness": 1.0, "coverage": 1.0})
    assert "evidence_quality" in res.gate_failures
    assert res.verdict == "REJECT"


def test_assemble_clamps_out_of_range_llm_scores():
    res = assemble_result(_parse("SK.A"), VALID,
                          {"evidence_quality": 5.0, "conservativeness": -2.0, "coverage": 0.5})
    assert res.parameter_scores["evidence_quality"] == 1.0
    assert res.parameter_scores["conservativeness"] == 0.0


# --- idempotency --------------------------------------------------------------

def test_assemble_idempotent():
    args = (_parse("SK.A", "SK.B"), VALID,
            {"evidence_quality": 0.9, "conservativeness": 0.8, "coverage": 0.7})
    runs = [assemble_result(*args) for _ in range(5)]
    first = (runs[0].verdict, runs[0].composite, runs[0].gate_failures)
    for r in runs:
        assert (r.verdict, r.composite, r.gate_failures) == first
