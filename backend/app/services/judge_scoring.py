"""Deterministic judge scoring (Trust Before Intelligence - Governance layer).

The LLM produces ONLY per-item judgments (the requirement-analysis rows, per-skill
fit_level, per-skill gap_level, and the recommended skill IDs). This module computes
every numeric score, the composite, the gates, and the verdict in pure Python. The
LLM's self-reported numbers are never trusted: it under-reports coverage and
over-reports role fit, so all of it is recomputed here.

This is the app-level promotion of backend/scripts/judge_deterministic.py so the
judge gate can run inside the production pipeline.

Contract:
    deterministic_score(parameters, total_skills=None, recommended_ids=None,
                        valid_skill_ids=None) -> JudgeResult
"""
from __future__ import annotations

from typing import Iterable, TypedDict

WEIGHTS = {"jd_coverage": 0.45, "role_fit_strength": 0.30,
           "ontology_precision": 0.15, "gap_validity": 0.10}
GATES = {"jd_coverage": 0.70, "role_fit_strength": 0.70, "ontology_precision": 0.90}

TIER_WEIGHT = {"T1": 3, "T2": 2, "T3": 1}
COVERAGE_MULT = {"full": 1.0, "partial": 0.5, "none": 0.0}
FIT_SCORE = {"role_specific": 1.0, "contextually_relevant": 0.5, "generic": 0.0}
GAP_SCORE = {"genuine_gap": 1.0, "partial_gap": 0.5, "already_acquired": 0.0}


class JudgeResult(TypedDict):
    composite: float
    overall_verdict: str           # ACCEPT | ACCEPT_WITH_REVIEW | REJECT
    gate_failures: list[str]
    scores: dict[str, float]
    regeneration_recommended: bool


def coverage_from_rows(jd_coverage: dict | None) -> float:
    """Sum(tier_weight x coverage_mult) / Sum(tier_weight) over Explicit+Implied rows only."""
    rows = (jd_coverage or {}).get("requirement_analysis") or []
    num = den = 0.0
    for r in rows:
        if r.get("ai_type") not in ("explicit", "implied"):
            continue
        w = TIER_WEIGHT.get(r.get("tier"))
        if w is None:
            continue
        num += w * COVERAGE_MULT.get(r.get("coverage"), 0.0)
        den += w
    return (num / den) if den else 0.0


def role_fit_from_skills(role_fit: dict | None) -> float:
    skills = (role_fit or {}).get("skills") or []
    vals = [FIT_SCORE.get(s.get("fit_level"), 0.0) for s in skills]
    return (sum(vals) / len(vals)) if vals else 0.0


def ontology_from_invalid(ontology: dict | None, total_skills: int) -> float:
    if not total_skills:
        return 0.0
    invalid = len((ontology or {}).get("invalid_skills") or [])
    return max(0.0, (total_skills - invalid) / total_skills)


def ontology_from_ids(recommended_ids: Iterable[str] | None, valid_skill_ids) -> float:
    """Deterministic ontology precision: validate recommended skill IDs against the
    real ontology, instead of trusting the LLM's invalid list."""
    ids = list(recommended_ids or [])
    if not ids:
        return 0.0
    return sum(1 for i in ids if i in valid_skill_ids) / len(ids)


def gap_from_skills(gap: dict | None) -> float:
    skills = (gap or {}).get("skills") or []
    vals = [GAP_SCORE.get(s.get("gap_level"), 0.0) for s in skills]
    return (sum(vals) / len(vals)) if vals else 0.0


def verdict_from_scores(scores: dict[str, float]) -> tuple[float, list[str], str]:
    """Pure: turn the four sub-scores into (composite, gate_failures, verdict).
    Single source of truth for the gate thresholds, reused by the ensemble path."""
    composite = round(sum(scores[k] * w for k, w in WEIGHTS.items()), 4)
    gate_failures = [k for k, g in GATES.items() if scores[k] < g]
    if gate_failures or composite < 0.70:
        verdict = "REJECT"
    elif composite >= 0.85:
        verdict = "ACCEPT"
    else:
        verdict = "ACCEPT_WITH_REVIEW"
    return composite, gate_failures, verdict


def deterministic_score(parameters: dict, total_skills: int | None = None,
                        recommended_ids=None, valid_skill_ids=None) -> JudgeResult:
    p = parameters or {}
    if total_skills is None:
        total_skills = len((p.get("role_fit_strength") or {}).get("skills") or []) or \
                       len((p.get("gap_validity") or {}).get("skills") or [])
    if recommended_ids is not None and valid_skill_ids is not None:
        ont = ontology_from_ids(recommended_ids, valid_skill_ids)
    else:
        ont = ontology_from_invalid(p.get("ontology_precision"), total_skills)
    scores = {
        "jd_coverage": round(coverage_from_rows(p.get("jd_coverage")), 4),
        "role_fit_strength": round(role_fit_from_skills(p.get("role_fit_strength")), 4),
        "ontology_precision": round(ont, 4),
        "gap_validity": round(gap_from_skills(p.get("gap_validity")), 4),
    }
    composite, gate_failures, verdict = verdict_from_scores(scores)
    return JudgeResult(
        composite=composite, overall_verdict=verdict, gate_failures=gate_failures,
        scores=scores, regeneration_recommended=verdict == "REJECT",
    )
