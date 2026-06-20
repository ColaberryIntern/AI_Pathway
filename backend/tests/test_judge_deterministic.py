"""Tests for deterministic judge scoring (4 mandatory types per CLAUDE.md)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from judge_deterministic import deterministic_score  # noqa: E402


def _params(cov_rows, fit_levels, gap_levels, invalid=None):
    return {
        "jd_coverage": {"requirement_analysis": cov_rows},
        "role_fit_strength": {"skills": [{"id": f"S{i}", "fit_level": f} for i, f in enumerate(fit_levels)]},
        "ontology_precision": {"invalid_skills": invalid or []},
        "gap_validity": {"skills": [{"id": f"S{i}", "gap_level": g} for i, g in enumerate(gap_levels)]},
    }


def test_happy_path_accept():
    # all role_specific, full coverage, genuine gaps, no invalid -> ACCEPT
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "explicit", "tier": "T2", "coverage": "full"}]
    r = deterministic_score(_params(rows, ["role_specific"] * 4, ["genuine_gap"] * 4))
    assert r["scores"]["jd_coverage"] == 1.0
    assert r["scores"]["role_fit_strength"] == 1.0
    assert r["overall_verdict"] == "ACCEPT"
    assert r["gate_failures"] == []


def test_none_rows_excluded_from_denominator():
    # the v4 fix: None rows must not dilute coverage
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}] + \
           [{"ai_type": "none", "tier": None, "coverage": None} for _ in range(10)]
    r = deterministic_score(_params(rows, ["role_specific"], ["genuine_gap"]))
    assert r["scores"]["jd_coverage"] == 1.0  # not diluted by the 10 None rows


def test_failure_path_role_fit_gate():
    # coverage passes but role fit fails the gate -> REJECT
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "implied", "tier": "T2", "coverage": "full"}]
    r = deterministic_score(_params(rows, ["generic", "generic", "role_specific"], ["genuine_gap"] * 3))
    assert r["scores"]["jd_coverage"] >= 0.70
    assert r["scores"]["role_fit_strength"] < 0.70
    assert "role_fit_strength" in r["gate_failures"]
    assert r["overall_verdict"] == "REJECT"


def test_halyna_coverage_artifact():
    # Halyna real rows: LLM reported 0.50, deterministic should be 0.857
    rows = [{"ai_type": "explicit", "tier": "T2", "coverage": "full"},
            {"ai_type": "implied", "tier": "T1", "coverage": "full"},
            {"ai_type": "implied", "tier": "T2", "coverage": "partial"},
            {"ai_type": "none", "tier": None, "coverage": None},
            {"ai_type": "none", "tier": None, "coverage": None},
            {"ai_type": "none", "tier": None, "coverage": None}]
    r = deterministic_score(_params(rows, ["role_specific"] * 3 + ["generic"] * 4, ["genuine_gap"] * 7))
    assert abs(r["scores"]["jd_coverage"] - 0.8571) < 0.01  # passes, not the LLM's 0.50


def test_boundary_empty():
    r = deterministic_score(_params([], [], []))
    assert r["scores"]["jd_coverage"] == 0.0
    assert r["overall_verdict"] == "REJECT"


def test_boundary_ontology_invalid():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}]
    r = deterministic_score(_params(rows, ["role_specific"] * 5, ["genuine_gap"] * 5, invalid=["SK.FAKE.001"]))
    assert r["scores"]["ontology_precision"] == 0.8  # 4/5
    assert "ontology_precision" in r["gate_failures"]


def test_deterministic_ontology_validation():
    # ontology precision computed from real IDs, not the LLM's invalid list
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}]
    p = _params(rows, ["role_specific"] * 4, ["genuine_gap"] * 4, invalid=[])  # LLM says all valid
    valid = {"SK.PRD.001", "SK.PRD.002", "SK.EVL.001"}
    # one recommended ID is NOT in the ontology -> deterministic catches it even though LLM said valid
    r = deterministic_score(p, recommended_ids=["SK.PRD.001", "SK.PRD.002", "SK.EVL.001", "SK.FAKE.999"],
                            valid_skill_ids=valid)
    assert r["scores"]["ontology_precision"] == 0.75  # 3/4
    # all valid -> 1.0 (fixes the LLM false-flag that rejected Halyna)
    r2 = deterministic_score(p, recommended_ids=["SK.PRD.001", "SK.PRD.002"], valid_skill_ids=valid)
    assert r2["scores"]["ontology_precision"] == 1.0


def test_idempotency():
    rows = [{"ai_type": "implied", "tier": "T1", "coverage": "full"}]
    p = _params(rows, ["role_specific"] * 3, ["genuine_gap"] * 3)
    first = deterministic_score(p)
    for _ in range(5):
        assert deterministic_score(p) == first
