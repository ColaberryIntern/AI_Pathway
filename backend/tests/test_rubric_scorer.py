"""Tests for the deterministic rubric scorer - the authoritative final ranker that
decides the top-5 skills shown to every user (highest blast radius, was untested).

Pure/deterministic, so no LLM mock is needed. Covers the four mandatory types plus
the structural guarantees that closed real customer complaints:
  - role-essence floor for cross-functional senior roles (Brittany W),
  - regulatory domain-skill pin vs advisory marketing (Halyna),
  - diversity cap (<=2 per parent domain in top 5),
  - non-technical momentum penalty on advanced prompting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services import rubric_scorer as rs  # noqa: E402


class FakeOntology:
    """Minimal ontology stub: get_skill + get_proficiency_descriptions + skills."""

    def __init__(self, skills=None):
        self.skills = skills or {}

    def get_skill(self, sid):
        return self.skills.get(sid)

    def get_proficiency_descriptions(self, sid):
        return (self.skills.get(sid) or {}).get("prof", [])


def skill(sid, importance="medium", required_level=3, rank=99, **kw):
    return {"skill_id": sid, "importance": importance,
            "required_level": required_level, "rank": rank, **kw}


# --- role / learner detection ---

def test_is_cross_functional_senior():
    assert rs.is_cross_functional_senior("Senior AI Product Marketing Manager")
    assert rs.is_cross_functional_senior("AI Strategy Lead")
    assert rs.is_cross_functional_senior("Director of Product Marketing")
    assert not rs.is_cross_functional_senior("AI Content Editor")
    assert not rs.is_cross_functional_senior("")


def test_mandated_domain_skills_for_role():
    assert rs.mandated_domain_skills_for_role("Director, Global Campaigns (Marketing)") == \
        ["SK.DOM.MKT.001", "SK.COM.005"]
    assert "SK.DOM.EDU.001" in rs.mandated_domain_skills_for_role("Learning and Development Specialist")
    assert "SK.DOM.HC.001" in rs.mandated_domain_skills_for_role("Clinical Documentation Specialist")
    assert rs.mandated_domain_skills_for_role("Software Engineer") == []


def test_is_non_technical_learner():
    assert rs.is_non_technical_learner(None) is True               # boundary: default safe
    assert rs.is_non_technical_learner({"technical_background": "Python developer"}) is False
    assert rs.is_non_technical_learner({"technical_background": "non-technical marketer"}) is True
    assert rs.is_non_technical_learner({"ai_exposure_level": "beginner"}) is True


# --- parameter scorers ---

def test_importance_floor_and_passthrough():
    onto_role = "Senior AI Product Marketing Manager"
    # role-essence floor on a cross-functional senior role
    assert rs.importance_score(skill("SK.PRD.001"), onto_role, []) == 3
    # domain mandate floor
    assert rs.importance_score(skill("SK.DOM.MKT.001"), "Marketing Manager", ["SK.DOM.MKT.001"]) == 3
    # passthrough of LLM importance otherwise
    assert rs.importance_score(skill("SK.XYZ.999", importance="high"), "Engineer", []) == 3
    assert rs.importance_score(skill("SK.XYZ.999", importance="low"), "Engineer", []) == 1
    assert rs.importance_score(skill("SK.XYZ.999", importance="medium"), "Engineer", []) == 2


def test_momentum_non_tech_prm_penalty():
    adv = skill("SK.PRM.020", required_level=3)
    tech = rs.momentum_score(adv, {"technical_background": "Python engineer"})
    non_tech = rs.momentum_score(adv, {"technical_background": "non-technical"})
    assert non_tech == tech - 1  # advanced prompting moves slower for non-tech


def test_connectivity_by_family():
    assert rs.connectivity_score(skill("SK.DOM.MKT.001"), FakeOntology()) == 1
    assert rs.connectivity_score(skill("SK.FND.002"), FakeOntology()) == 3
    assert rs.connectivity_score(skill("SK.PRM.004"), FakeOntology()) == 3  # foundational PRM 000-006
    assert rs.connectivity_score(skill("SK.EVL.001"), FakeOntology()) == 2


def test_score_skill_formula():
    onto = FakeOntology({"SK.FND.002": {"level": 1}})
    s = rs.score_skill(skill("SK.FND.002", importance="high"), "Engineer", None, onto, [])
    expected = s["importance"] * 4 + s["breadth"] * 3 + s["momentum"] * 3 \
        + s["connectivity"] * 2 + s["career_signal"] * 2
    assert s["total_score"] == expected


# --- diversity ---

def test_apply_diversity_caps_parent_domain():
    # 4 PRM + 5 distinct-parent skills so the excess PRM can slide out of top 5.
    items = [skill(f"SK.PRM.0{i}", rank=i) for i in range(1, 5)] + [
        skill("SK.FND.002", rank=5), skill("SK.EVL.001", rank=6),
        skill("SK.COM.001", rank=7), skill("SK.RSN.003", rank=8),
        skill("SK.GOV.001", rank=9)]
    out = rs.apply_diversity(items, max_per_parent=2, top_count=5)
    top5_prm = [s for s in out[:5] if s["skill_id"].startswith("SK.PRM.")]
    assert len(top5_prm) <= 2  # no more than 2 PRM in top 5
    # the demoted PRM slid to the tail (positions 6+)
    assert any(s["skill_id"].startswith("SK.PRM.") for s in out[5:])


def test_apply_diversity_protected_bypass_cap():
    items = [skill("SK.PRD.001"), skill("SK.PRD.021"), skill("SK.PRD.022")]
    protected = {"SK.PRD.001", "SK.PRD.021", "SK.PRD.022"}
    out = rs.apply_diversity(items, max_per_parent=2, top_count=5, protected_ids=protected)
    assert {s["skill_id"] for s in out[:5]} == protected  # all 3 D.PRD survive despite cap


# --- rerank: the authoritative ranker ---

def _filler(n):
    return [skill(f"SK.FIL.{i:03d}", importance="low", rank=10 + i) for i in range(n)]


def test_rerank_role_essence_floor_brittany():
    """Cross-functional senior role -> the 5 role-essence skills land in top 5."""
    cands = [skill(s) for s in rs.ROLE_ESSENCE_SKILLS] + _filler(5)
    out = rs.rerank(cands, "Senior AI Product Marketing Manager", None, FakeOntology())
    assert {s["skill_id"] for s in out[:5]} == set(rs.ROLE_ESSENCE_SKILLS)
    assert out[0]["rank"] == 1 and out[0]["rank_llm"] is not None


def test_rerank_regulatory_domain_is_pinned():
    """Healthcare (regulatory) domain skill stays in top 5 even when LLM-ranked low."""
    cands = [skill("SK.DOM.HC.001", importance="low", rank=9)] + \
            [skill(f"SK.FND.{i:03d}", importance="high", rank=i) for i in range(1, 6)]
    out = rs.rerank(cands, "Clinical Documentation Specialist", None, FakeOntology())
    assert "SK.DOM.HC.001" in {s["skill_id"] for s in out[:5]}


def test_rerank_marketing_domain_is_advisory_not_pinned():
    """Marketing (commercial/advisory) domain skill is NOT guaranteed top 5 - it can be
    displaced by higher-scoring skills from distinct parents."""
    strong = [skill(s, importance="high", rank=i)
              for i, s in enumerate(["SK.FND.002", "SK.PRD.001", "SK.COM.001",
                                     "SK.RSN.003", "SK.GOV.001"], 1)]
    cands = strong + [skill("SK.DOM.MKT.001", importance="low", rank=9)]
    out = rs.rerank(cands, "Marketing Manager", None, FakeOntology())
    ranks = {s["skill_id"]: s["rank"] for s in out}
    assert ranks["SK.DOM.MKT.001"] > 5  # advisory, displaced


def test_rerank_idempotent():
    cands = [skill(s) for s in rs.ROLE_ESSENCE_SKILLS] + _filler(3)
    a = rs.rerank(cands, "AI Strategy Lead", None, FakeOntology())
    b = rs.rerank(cands, "AI Strategy Lead", None, FakeOntology())
    assert [s["skill_id"] for s in a] == [s["skill_id"] for s in b]
    assert [s["total_score"] for s in a] == [s["total_score"] for s in b]


def test_rerank_boundary_empty_and_single():
    assert rs.rerank([], "Engineer", None, FakeOntology()) == []
    one = rs.rerank([skill("SK.FND.002")], "Engineer", None, FakeOntology())
    assert len(one) == 1 and one[0]["rank"] == 1


# --- foundational PRM injection ---

def test_inject_prm_for_vertical_nontech_when_missing():
    onto = FakeOntology({"SK.PRM.000": {"name": "Writing clear requests", "level": 1},
                         "SK.PRM.001": {"name": "Instructions", "level": 1}})
    out = rs.inject_foundational_prm_if_missing(
        [skill("SK.EVL.001")], "Learning and Development Specialist",
        {"technical_background": "non-technical"}, onto, max_inject=2)
    injected = [s for s in out if s.get("_injected_by") == "foundational_prm_injection"]
    assert len(injected) == 2


def test_inject_prm_skipped_for_technical_learner():
    onto = FakeOntology({"SK.PRM.000": {"name": "x", "level": 1}})
    out = rs.inject_foundational_prm_if_missing(
        [skill("SK.EVL.001")], "Learning and Development Specialist",
        {"technical_background": "Python engineer"}, onto)
    assert all(s.get("_injected_by") is None for s in out)


def test_inject_prm_skipped_for_non_vertical_role():
    onto = FakeOntology({"SK.PRM.000": {"name": "x", "level": 1}})
    out = rs.inject_foundational_prm_if_missing(
        [skill("SK.EVL.001")], "Software Engineer",
        {"technical_background": "non-technical"}, onto)
    assert out == [skill("SK.EVL.001")]


def test_inject_prm_skipped_when_already_present():
    onto = FakeOntology({"SK.PRM.000": {"name": "x", "level": 1}})
    out = rs.inject_foundational_prm_if_missing(
        [skill("SK.PRM.000")], "Learning and Development Specialist",
        {"technical_background": "non-technical"}, onto)
    assert len(out) == 1  # already has a foundational PRM, nothing added


# --- narrative + partition ---

def test_build_ontology_narrative_floors_and_formula():
    onto = FakeOntology({f"s{i}": {} for i in range(40)})
    n = rs.build_ontology_narrative("Senior AI Product Marketing Manager", 5, onto)
    assert n["rubric"]["max_score"] == 42
    floor_names = {f["name"] for f in n["applied_floors"]}
    assert "Role-essence floor" in floor_names and "Domain-skill mandate" in floor_names


def test_maintain_develop_partition():
    skills = [skill("SK.A", required_level=3), skill("SK.B", required_level=4)]
    out = rs.maintain_develop_partition(skills, {"SK.A": 3, "SK.B": 1})
    assert [s["skill_id"] for s in out["maintain"]] == ["SK.A"]   # gap 0
    assert out["develop"][0]["skill_id"] == "SK.B" and out["develop"][0]["gap"] == 3


def test_maintain_develop_unassessed_defaults_to_develop():  # boundary
    out = rs.maintain_develop_partition([skill("SK.A", required_level=2)], {})
    assert out["develop"][0]["skill_id"] == "SK.A" and out["develop"][0]["current_level"] == 0
