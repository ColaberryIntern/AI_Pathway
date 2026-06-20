"""Tests for the app-level deterministic judge scoring (Governance layer).
Four mandatory test types per CLAUDE.md: happy, failure, boundary, idempotency."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.judge_scoring import deterministic_score  # noqa: E402


def _params(cov_rows, fit_levels, gap_levels, invalid=None):
    return {
        "jd_coverage": {"requirement_analysis": cov_rows},
        "role_fit_strength": {"skills": [{"id": f"S{i}", "fit_level": f} for i, f in enumerate(fit_levels)]},
        "ontology_precision": {"invalid_skills": invalid or []},
        "gap_validity": {"skills": [{"id": f"S{i}", "gap_level": g} for i, g in enumerate(gap_levels)]},
    }


def test_happy_path_accept():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "explicit", "tier": "T2", "coverage": "full"}]
    r = deterministic_score(_params(rows, ["role_specific"] * 4, ["genuine_gap"] * 4))
    assert r["scores"]["jd_coverage"] == 1.0 and r["scores"]["role_fit_strength"] == 1.0
    assert r["overall_verdict"] == "ACCEPT" and r["gate_failures"] == []


def test_none_rows_excluded():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}] + \
           [{"ai_type": "none", "tier": None, "coverage": None} for _ in range(10)]
    r = deterministic_score(_params(rows, ["role_specific"], ["genuine_gap"]))
    assert r["scores"]["jd_coverage"] == 1.0  # None rows do not dilute


def test_failure_path_role_fit_gate():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "implied", "tier": "T2", "coverage": "full"}]
    r = deterministic_score(_params(rows, ["generic", "generic", "role_specific"], ["genuine_gap"] * 3))
    assert "role_fit_strength" in r["gate_failures"] and r["overall_verdict"] == "REJECT"


def test_llm_score_cannot_override_computed():
    # The LLM 'score' fields are ignored; only row/skill judgments drive the result.
    rows = [{"ai_type": "explicit", "tier": "T2", "coverage": "full"},
            {"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "implied", "tier": "T2", "coverage": "partial"},
            {"ai_type": "none", "tier": None, "coverage": None}]
    p = _params(rows, ["role_specific"] * 3 + ["generic"] * 4, ["genuine_gap"] * 7)
    p["jd_coverage"]["score"] = 0.50  # LLM lies low; must be ignored
    r = deterministic_score(p)
    assert abs(r["scores"]["jd_coverage"] - 0.8571) < 0.01


def test_deterministic_ontology_validation():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}]
    p = _params(rows, ["role_specific"] * 4, ["genuine_gap"] * 4, invalid=[])
    valid = {"SK.PRD.001", "SK.PRD.002", "SK.EVL.001"}
    r = deterministic_score(p, recommended_ids=["SK.PRD.001", "SK.PRD.002", "SK.EVL.001", "SK.FAKE.999"], valid_skill_ids=valid)
    assert r["scores"]["ontology_precision"] == 0.75  # 3/4 even though LLM said all valid


def test_boundary_empty():
    r = deterministic_score(_params([], [], []))
    assert r["scores"]["jd_coverage"] == 0.0 and r["overall_verdict"] == "REJECT"


def test_idempotency():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}]
    p = _params(rows, ["role_specific"] * 3, ["genuine_gap"] * 3)
    first = deterministic_score(p)
    for _ in range(5):
        assert deterministic_score(p) == first
