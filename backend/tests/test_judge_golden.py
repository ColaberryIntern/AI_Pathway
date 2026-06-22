"""Golden regression test for the deterministic judge scorer (Trust Before
Intelligence - Lexicon/Adaptive).

Frozen raw judge parameters (real v4 outputs on expert-anchored cases) are scored
by deterministic_score; the expected output is the trustworthy recomputation, NOT
the LLM self-report. This pins the deterministic scoring contract: any change to
weights, tier weights, coverage/fit mapping, or gate thresholds that moves a golden
case breaks this test and forces a deliberate recalibration.

The fixture (tests/golden/judge_golden.json) is self-contained - it does not read
from docs/ at test time.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.judge_scoring import deterministic_score  # noqa: E402

_GOLDEN = json.loads((Path(__file__).parent / "golden" / "judge_golden.json").read_text())
_CASES = _GOLDEN["cases"]


def _score(case):
    ids = case["skill_ids"]
    return deterministic_score(
        case["parameters"], total_skills=len(ids),
        recommended_ids=ids, valid_skill_ids=set(ids),
    )


def test_fixture_present():
    assert len(_CASES) >= 3  # halyna_set_a/b, brittany_set_a


def test_golden_cases_reproduce():
    """Happy path: every golden case reproduces its frozen deterministic output."""
    for case in _CASES:
        res = _score(case)
        exp = case["expected"]
        assert res["overall_verdict"] == exp["overall_verdict"], case["label"]
        assert res["composite"] == exp["composite"], case["label"]
        assert res["gate_failures"] == exp["gate_failures"], case["label"]
        for k, v in exp["scores"].items():
            assert res["scores"][k] == v, f"{case['label']} {k}: {res['scores'][k]} != {v}"


def test_deterministic_diverges_from_llm_selfreport():
    """The reason the deterministic layer exists: the LLM's self-reported parameter
    scores must NOT be trusted. On at least one golden case the recomputed score
    differs materially from what the model reported about itself."""
    diverged = False
    for case in _CASES:
        res = _score(case)
        params = case["parameters"]
        for key in ("jd_coverage", "role_fit_strength"):
            self_report = (params.get(key) or {}).get("score")
            if self_report is not None and abs(res["scores"][key] - self_report) >= 0.1:
                diverged = True
    assert diverged, "expected deterministic recomputation to diverge from LLM self-report"


def test_idempotent():
    """Pure function: scoring the same case twice yields identical output."""
    for case in _CASES:
        assert _score(case) == _score(case), case["label"]


def test_boundary_empty_parameters():
    """Boundary/failure: empty params -> all-zero scores and a REJECT, no crash."""
    res = deterministic_score({}, total_skills=0, recommended_ids=[], valid_skill_ids=set())
    assert res["overall_verdict"] == "REJECT"
    assert all(v == 0.0 for v in res["scores"].values())
