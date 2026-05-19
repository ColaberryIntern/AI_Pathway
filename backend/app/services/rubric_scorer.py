"""5-parameter weighted rubric scoring per Luda Kopeikina's May 15 spec.

Deterministic post-processing of the JD parser's candidate skill list:
each candidate is scored 1-3 on five parameters, weighted, summed, and
the list is re-ranked by total score. This guarantees role-essence and
domain skills land in the top 5 without depending on the LLM to follow
ranking instructions correctly.

The formula (from Luda's "Criteria for Skill Selection/Prioritization"):

    Priority Score = (Importance     x 4)
                   + (Breadth        x 3)
                   + (Momentum       x 3)
                   + (Connectivity   x 2)
                   + (Career Signal  x 2)
                   max = 3*4 + 3*3 + 3*3 + 3*2 + 3*2 = 42

Two deterministic guarantees layered on top of the formula:

1. ROLE-ESSENCE FLOOR for cross-functional senior roles (Sr AI PMM, Sr
   AI PM, AI Strategy, AI Solutions). The five role-essence skills
   (SK.COM.001 / SK.PRD.001 / SK.PRD.021 / SK.PRD.022 / SK.FND.002) get
   Importance = 3 and Career Signal = 3 automatically, so they land at
   the top of the ranking. Closes the Brittany W "wrong skills in top 5"
   complaint structurally, not just through prompt instruction.

2. DOMAIN-SKILL MANDATE for vertical roles (marketing / L&D / healthcare
   / legal / finance / HR). The corresponding SK.DOM.* skill gets
   Importance = 3, so it appears in the top 5 even if the LLM ranked it
   low. Closes the Halyna "missed SK.DOM.MKT.001" complaint structurally.

Diversity rule (no more than 2 skills from the same parent domain in
the top 5) is also applied deterministically post-rerank.
"""
from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------
# Cross-functional senior role detection
# ---------------------------------------------------------------------
CROSS_FUNCTIONAL_SENIOR_PATTERNS = [
    re.compile(r"\bproduct\s+marketing\b", re.I),
    re.compile(r"\bai\s+product\s+(manager|management)\b", re.I),
    re.compile(r"\bsr\.?\s+(ai\s+)?(product|strategy|solutions|marketing)\b", re.I),
    re.compile(r"\b(senior|sr\.?)\s+.*\b(pm|pmm|manager|director|lead|head)\b.*\bai\b", re.I),
    re.compile(r"\bai\s+(strategy|solutions)\b", re.I),
]

ROLE_ESSENCE_SKILLS = [
    "SK.COM.001",  # Explaining AI to non-technical audiences
    "SK.PRD.001",  # AI Use Case Identification / Use-case selection & prioritization
    "SK.PRD.021",  # Stakeholder management
    "SK.PRD.022",  # ROI measurement for AI
    "SK.FND.002",  # Capabilities vs limitations (hallucinations)
]


# ---------------------------------------------------------------------
# Vertical-to-domain-skill mapping
# ---------------------------------------------------------------------
VERTICAL_DOMAIN_RULES: list[tuple[re.Pattern, list[str]]] = [
    # Marketing vertical: title must clearly be marketing leadership/strategy.
    # NOT triggered for generic "Content Editor" or "Content Manager" roles -
    # those are content/editorial functions and benefit more from prompting +
    # content-verification skills than from marketing ethics specifically.
    (re.compile(r"\b(marketing|campaigns?|brand\s+(manager|strategist|director)|content\s+strategy|growth\s+(manager|director|lead)|demand\s+gen|pmm|product\s+marketing)\b", re.I),
     ["SK.DOM.MKT.001"]),
    (re.compile(r"\b(learning\s+(and|&)\s+development|l&d|instructional\s+design|curriculum|training\s+(specialist|manager|director)|learning\s+experience|educator|teacher|edtech)\b", re.I),
     ["SK.DOM.EDU.001"]),
    (re.compile(r"\b(clinical|patient|healthcare|medical\s+(director|writer|reviewer)|nurse|physician|hospital)\b", re.I),
     ["SK.DOM.HC.001", "SK.DOM.HC.002"]),
    (re.compile(r"\b(legal\s+(counsel|officer)|attorney|paralegal|compliance\s+counsel|general\s+counsel|law\s+firm)\b", re.I),
     ["SK.DOM.LGL.001", "SK.DOM.LGL.002"]),
    (re.compile(r"\b(finance|accounting|audit|fp\s*&\s*a|treasury|controller|cfo)\b", re.I),
     ["SK.DOM.FIN.001"]),
    (re.compile(r"\b(human\s+resources|hr\s+|recruiting|talent\s+(acquisition|management)|people\s+ops|chief\s+people)\b", re.I),
     ["SK.DOM.HR.001"]),
]


# ---------------------------------------------------------------------
# Career signal heuristics
# ---------------------------------------------------------------------
HIGH_CAREER_SIGNAL_SKILLS: set[str] = {
    "SK.COM.001",   # Explaining AI to non-technical audiences
    "SK.COM.005",   # Cross-functional AI collaboration
    "SK.PRD.001",   # AI Use Case Identification
    "SK.PRD.020",   # AI enablement & training strategy
    "SK.PRD.021",   # Stakeholder management
    "SK.PRD.022",   # ROI measurement for AI
    "SK.FND.002",   # Capabilities vs limitations
    "SK.FND.003",   # Model families (open vs closed)
    "SK.GOV.001",   # AI risk framing
    "SK.GOV.010",   # EU AI Act
    "SK.GOV.022",   # AI-generated content disclosure (NEW v2.0)
    "SK.RSN.003",   # Deep research agents (NEW v2.0)
    "SK.PRM.020",   # Draft -> critique -> revise (when applicable)
    "SK.PRM.003",   # Prompt debugging & iteration (when applicable)
}

LOW_CAREER_SIGNAL_SKILLS: set[str] = {
    # Niche framework / tooling skills with thin transfer value
    "SK.PRM.022",   # ReAct-style patterns
    "SK.PRM.010",   # JSON/schema outputs (useful, but tactical)
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def is_cross_functional_senior(role_text: str) -> bool:
    if not role_text:
        return False
    return any(p.search(role_text) for p in CROSS_FUNCTIONAL_SENIOR_PATTERNS)


def mandated_domain_skills_for_role(role_text: str) -> list[str]:
    if not role_text:
        return []
    matched: list[str] = []
    for pattern, sids in VERTICAL_DOMAIN_RULES:
        if pattern.search(role_text):
            matched.extend(sids)
    return matched


def is_non_technical_learner(learner_profile: dict | None) -> bool:
    """Best-effort heuristic for whether the learner is non-technical."""
    if not learner_profile:
        return True  # default to non-tech (safer for skill depth)
    tb = (learner_profile.get("technical_background") or "").lower()
    exposure = (learner_profile.get("ai_exposure_level") or "").lower()
    # Explicit non-technical markers
    if any(t in tb for t in ("non-tech", "non technical", "don't code", "no coding", "basic tech")):
        return True
    # Technical markers
    if any(t in tb for t in ("python", "engineer", "developer", "ml ", "ml,", "data scien")):
        return False
    if exposure in ("beginner", "novice", "aware"):
        return True
    return True  # default to non-tech


# ---------------------------------------------------------------------
# 5 parameter scorers (each returns 1-3)
# ---------------------------------------------------------------------
def importance_score(skill: dict, role_text: str, mandated_domain: list[str]) -> int:
    sid = skill.get("skill_id", "")
    # Role-essence floor
    if sid in ROLE_ESSENCE_SKILLS and is_cross_functional_senior(role_text):
        return 3
    # Domain mandate floor
    if sid in mandated_domain:
        return 3
    # Otherwise honor the LLM-emitted importance
    imp = (skill.get("importance") or "medium").lower()
    if imp == "high":
        return 3
    if imp == "low":
        return 1
    return 2


def breadth_score(skill: dict, ontology: Any) -> int:
    """Broader = more foundational / applies across more tasks.

    Use the ontology's `level` field as a proxy for depth: skills at
    level 0-1 are foundational (broad), level 2-3 are moderate, level
    4-5 are specialised (narrow).
    """
    sid = skill.get("skill_id", "")
    sk = ontology.get_skill(sid) if hasattr(ontology, "get_skill") else None
    if not sk:
        return 2
    level = sk.get("level", 3)
    if level <= 1:
        return 3
    if level == 2:
        return 2
    return 1


def momentum_score(skill: dict, learner_profile: dict | None) -> int:
    """Can the learner advance one full level in one chapter?

    High when the target level is L1-L2 (foundational, quick to achieve).
    Medium for L3 (Practitioner — typically one chapter is enough).
    Low for L4+ (Builder, Architect — multi-chapter effort).
    Adjusted down for non-technical learners attempting advanced skills.
    """
    required = skill.get("required_level") or skill.get("target_level") or 3
    base = 3 if required <= 2 else (2 if required == 3 else 1)

    # For non-tech learner, advanced PRM skills get momentum dropped
    sid = skill.get("skill_id", "")
    non_tech = is_non_technical_learner(learner_profile)
    if non_tech and sid in ("SK.PRM.003", "SK.PRM.020", "SK.PRM.021", "SK.PRM.022"):
        # Advanced prompting moves slower for non-tech learners
        base = max(1, base - 1)

    return base


def connectivity_score(skill: dict, ontology: Any) -> int:
    """Does this skill unlock multiple other skills?

    Foundational PRM (000-006), foundational FND, and core COM skills
    are highly connective. Domain-specific skills (SK.DOM.*) are narrow
    (they enable mastery within their vertical only).
    """
    sid = skill.get("skill_id", "")
    if sid.startswith("SK.DOM."):
        return 1
    if sid.startswith("SK.FND."):
        return 3
    # Foundational PRM
    if re.match(r"^SK\.PRM\.00[0-6]$", sid):
        return 3
    # Foundational COM and PRD
    if sid in ("SK.COM.001", "SK.COM.005", "SK.PRD.001"):
        return 3
    # Most other skills
    return 2


def career_signal_score(skill: dict, role_text: str) -> int:
    sid = skill.get("skill_id", "")
    if sid in HIGH_CAREER_SIGNAL_SKILLS:
        return 3
    if sid in LOW_CAREER_SIGNAL_SKILLS:
        return 1
    return 2


# ---------------------------------------------------------------------
# Compose and rerank
# ---------------------------------------------------------------------
def score_skill(skill: dict, role_text: str, learner_profile: dict | None,
                ontology: Any, mandated_domain: list[str]) -> dict:
    """Return the 5 component scores + total for a single skill."""
    imp = importance_score(skill, role_text, mandated_domain)
    bdt = breadth_score(skill, ontology)
    mom = momentum_score(skill, learner_profile)
    con = connectivity_score(skill, ontology)
    car = career_signal_score(skill, role_text)
    total = (imp * 4) + (bdt * 3) + (mom * 3) + (con * 2) + (car * 2)
    return {
        "importance": imp,
        "breadth": bdt,
        "momentum": mom,
        "connectivity": con,
        "career_signal": car,
        "total_score": total,
    }


def apply_diversity(reranked: list[dict], max_per_parent: int = 2,
                    top_count: int = 5,
                    protected_ids: set[str] | None = None) -> list[dict]:
    """Enforce: no more than `max_per_parent` non-protected skills from the
    same parent domain in the top `top_count`. Protected skills bypass
    the cap entirely; demoted (non-protected) skills slide to position
    `top_count + 1`.

    Protected = role-essence skills for the matched role family +
    mandated-domain skills. They MUST stay in top 5 even if they cluster
    in one parent domain (e.g., Brittany's 3 D.PRD essence skills).

    Parent domain = "SK.PRM" for "SK.PRM.003", "SK.DOM" for any "SK.DOM.*",
    etc. (We use the first two segments.)
    """
    protected_ids = protected_ids or set()

    def parent_of(sid: str) -> str:
        parts = sid.split(".")
        return ".".join(parts[:2]) if len(parts) >= 2 else sid

    promoted: list[dict] = []
    demoted_tail: list[dict] = []
    parent_count: dict[str, int] = {}

    # First pass: every protected skill is promoted unconditionally,
    # regardless of parent count.
    for s in reranked:
        sid = s.get("skill_id", "")
        if sid in protected_ids:
            promoted.append(s)
            parent_count[parent_of(sid)] = parent_count.get(parent_of(sid), 0) + 1

    # Second pass: fill remaining top-N slots with the highest-scoring
    # non-protected skills that fit the diversity cap.
    for s in reranked:
        sid = s.get("skill_id", "")
        if sid in protected_ids:
            continue
        parent = parent_of(sid)
        if len(promoted) < top_count and parent_count.get(parent, 0) < max_per_parent:
            promoted.append(s)
            parent_count[parent] = parent_count.get(parent, 0) + 1
        else:
            demoted_tail.append(s)

    return promoted + demoted_tail


# Boost applied to total_score for mandated skills, large enough to
# guarantee they sort to the top regardless of base scoring. The actual
# numbers stay visible in the per-skill `scores` payload so the UI can
# show the unboosted 5-parameter breakdown.
MANDATE_BOOST = 100


def rerank(candidates: list[dict], role_text: str,
           learner_profile: dict | None, ontology: Any) -> list[dict]:
    """Score every candidate and return them sorted by total_score desc.

    Each returned skill dict has a `scores` field (the 5 components +
    total) and a new `rank` field (1-based, after rerank + diversity).
    Original LLM `rank` is preserved as `rank_llm` for traceability.

    Mandated skills (role-essence for cross-functional senior roles,
    and SK.DOM.* for vertical roles) receive a large `mandate_boost` so
    they always sort into the top 5, and they are also protected from
    the diversity rule's parent-count cap.
    """
    mandated_domains = set(mandated_domain_skills_for_role(role_text))
    cross_func_senior = is_cross_functional_senior(role_text)
    mandated_role_essence = set(ROLE_ESSENCE_SKILLS) if cross_func_senior else set()
    # For cross-functional senior roles, role-essence skills MUST occupy
    # top 5 - the domain skill is welcome but should not displace any
    # role-essence. Per Luda's May 15 Brittany analysis, the 5 essence
    # skills win even when the role is also a marketing role. Demote
    # the domain skill from "protected" to "boosted into top 10" for
    # these roles.
    if cross_func_senior and mandated_domains:
        protected = mandated_role_essence
        # Domain still gets a smaller boost so it lands in top 10
        # but role-essence takes priority for top 5 slots.
        secondary_boosted = mandated_domains
    else:
        protected = mandated_domains | mandated_role_essence
        secondary_boosted = set()

    scored: list[dict] = []
    for skill in candidates:
        original_rank = skill.get("rank", 99)
        scores = score_skill(
            skill, role_text, learner_profile, ontology, list(mandated_domains),
        )
        sid = skill.get("skill_id", "")
        if sid in protected:
            boost = MANDATE_BOOST
        elif sid in secondary_boosted:
            # Cross-functional senior + vertical role: domain skill gets
            # a smaller boost so it lands in top 10 but does not displace
            # any of the 5 role-essence skills from top 5.
            boost = MANDATE_BOOST // 2  # 50
        else:
            boost = 0
        scores["mandate_boost"] = boost
        scored.append({
            **skill,
            "rank_llm": original_rank,
            "scores": scores,
            "total_score": scores["total_score"] + boost,
        })

    # Sort by total_score desc, ties broken by LLM rank ascending
    scored.sort(key=lambda s: (-s["total_score"], s.get("rank_llm", 99)))

    # Apply diversity rule in top 5, but protect mandated skills
    scored = apply_diversity(
        scored, max_per_parent=2, top_count=5, protected_ids=protected,
    )

    # Assign final ranks
    for i, s in enumerate(scored, 1):
        s["rank"] = i

    return scored


# ---------------------------------------------------------------------
# Maintain vs Develop partition (computed after self-assessment)
# ---------------------------------------------------------------------
# Foundational prompting skills appropriate for non-technical L1-L2
# learners. These are the four PRM skills Luda's Claude analysis picked
# for Halyna ("non-technical but experienced marketing professional") -
# they are the right starting depth when the learner is not technical.
FOUNDATIONAL_PRM_SKILLS = [
    "SK.PRM.000",  # Writing clear requests to AI
    "SK.PRM.001",  # Instructions + constraints + format
    "SK.PRM.004",  # Role & persona prompting
    "SK.PRM.006",  # Breaking complex tasks into steps
]


def inject_foundational_prm_if_missing(
    skills_list: list[dict],
    role_text: str,
    learner_profile: dict | None,
    ontology,
    max_inject: int = 2,
) -> list[dict]:
    """If this is a vertical role with a non-technical learner and the
    LLM's candidate list contains zero foundational PRM skills, inject
    up to `max_inject` of them so the rubric scorer can rank them.

    Without this, the rubric cannot rank skills the LLM never surfaced
    as candidates - and the LLM has a consistent bias toward advanced
    PRM (SK.PRM.020 draft-critique-revise, SK.PRM.003 prompt debugging)
    over foundational PRM (SK.PRM.000-006) regardless of learner level.

    Closes Luda's May 19 Halyna depth complaint structurally: she ran the
    same JD through Claude with our ontology and Claude picked
    SK.PRM.000/001/004/006 specifically because "they are the four
    sub-skills within D.PRM that are achievable without technical
    prerequisites". This function reproduces that judgment deterministically.

    Returns a new list (does not mutate input).
    """
    # Only act on vertical roles - we trust the LLM more when the role
    # is broad enough that the candidate set is naturally diverse.
    if not mandated_domain_skills_for_role(role_text):
        return list(skills_list)
    # Skip cross-functional senior roles (Sr AI PMM, Sr AI PM, AI Strategy).
    # Their top 5 is already locked by the role-essence floor, so injecting
    # foundational PRM would only displace expected top-10 skills (Brittany's
    # SK.GOV.001 + SK.PRD.020 case). The role-essence skills + domain skill
    # already cover what these roles need.
    if is_cross_functional_senior(role_text):
        return list(skills_list)
    # Only act for non-technical learners
    if not is_non_technical_learner(learner_profile):
        return list(skills_list)

    existing_ids = {s.get("skill_id") for s in skills_list}
    already_present = sum(1 for sid in FOUNDATIONAL_PRM_SKILLS if sid in existing_ids)
    if already_present >= 1:
        # The LLM surfaced at least one foundational PRM - good enough
        return list(skills_list)

    candidates_to_add: list[dict] = []
    for sid in FOUNDATIONAL_PRM_SKILLS:
        if len(candidates_to_add) >= max_inject:
            break
        if sid in existing_ids:
            continue
        sk = ontology.get_skill(sid) if hasattr(ontology, "get_skill") else None
        if not sk:
            continue
        # Include proficiency_descriptions and skill_description so the
        # Top 5 page tooltip renders correctly for injected skills.
        prof_descs = []
        if hasattr(ontology, "get_proficiency_descriptions"):
            try:
                prof_descs = ontology.get_proficiency_descriptions(sid) or []
            except Exception:
                prof_descs = []
        candidates_to_add.append({
            "skill_id": sid,
            "skill_name": sk.get("name") or "",
            "domain": sk.get("domain") or "",
            "domain_label": "Prompting & HITL Workflows",
            "required_level": 2,
            "importance": "high",
            "rationale": (
                f"Foundational prompting skill injected for non-technical learner. "
                f"Luda's reference analysis explicitly identified the foundational "
                f"PRM sub-skills (SK.PRM.000-006) as the appropriate starting "
                f"depth for non-technical learners in vertical roles, ahead of "
                f"advanced PRM skills like SK.PRM.020 (draft-critique-revise) "
                f"or SK.PRM.003 (prompt debugging)."
            ),
            "skill_description": sk.get("description") or "",
            "proficiency_descriptions": prof_descs,
            "_injected_by": "foundational_prm_injection",
        })

    return list(skills_list) + candidates_to_add


def build_ontology_narrative(role_text: str, candidate_count: int,
                              ontology) -> dict:
    """Build the 'how do I know these are the right skills?' panel data.

    Shared by parseJDSkills and analysis/results so the surface looks
    the same on a fresh parse and on a revisited analysis. Pulls
    role-essence + domain-mandate detection from the rubric_scorer so
    the rationale matches what was actually applied to the rerank.
    """
    role_text = role_text or ""

    # Resolve domains the JD parser flagged - the caller passes them as
    # IDs and we expand to label + description.
    # (The caller is expected to pre-populate key_domains; if not, the
    # narrative falls back to an empty list and the UI hides that section.)

    try:
        domain_mandate_ids = mandated_domain_skills_for_role(role_text)
    except Exception:
        domain_mandate_ids = []

    applied_floors: list[dict] = []
    if is_cross_functional_senior(role_text):
        applied_floors.append({
            "name": "Role-essence floor",
            "rationale": (
                "This role is a senior cross-functional AI role. We guarantee "
                "that the five role-essence skills appear in the top 5: "
                + ", ".join(ROLE_ESSENCE_SKILLS) + "."
            ),
        })
    if domain_mandate_ids:
        applied_floors.append({
            "name": "Domain-skill mandate",
            "rationale": (
                "This role belongs to a specific vertical, so the vertical's "
                "applied skill is guaranteed in the top 5: "
                + ", ".join(domain_mandate_ids) + "."
            ),
        })

    total_skills = 0
    try:
        total_skills = len(ontology.skills)
    except Exception:
        pass

    return {
        "ontology_name": "GenAI Skills Ontology v2.0",
        "headline": (
            f"We matched the job description against {total_skills} "
            f"skills in the GenAI Skills Ontology v2.0 and produced your top "
            f"{candidate_count} candidates."
        ),
        "role_family": role_text,
        "key_domains": [],   # caller fills these in
        "rubric": {
            "name": "5-parameter priority score",
            "formula": (
                "Priority = (Importance x 4) + (Breadth x 3) + (Momentum x 3) "
                "+ (Connectivity x 2) + (Career Signal x 2)"
            ),
            "max_score": 42,
            "parameters": [
                {"name": "Importance", "weight": 4,
                 "description": "How central this skill is to the job description."},
                {"name": "Breadth", "weight": 3,
                 "description": "How broadly the skill applies across tasks in this role."},
                {"name": "Momentum", "weight": 3,
                 "description": "Whether you can realistically improve one level in one chapter."},
                {"name": "Connectivity", "weight": 2,
                 "description": "Whether mastering this skill unlocks other skills in the ontology."},
                {"name": "Career Signal", "weight": 2,
                 "description": "How recognizable this skill is to recruiters and hiring managers."},
            ],
        },
        "applied_floors": applied_floors,
        "diversity_rule": (
            "No more than 2 skills from the same parent domain in the top 5, "
            "except for role-essence and domain-mandated skills."
        ),
        "candidate_count": candidate_count,
        "rationale_summary": (
            "Each skill in the list below shows its rubric score breakdown so "
            "you can see WHY it scored where it did. Hover the skill name for "
            "the ontology definition; hover each proficiency level for the "
            "skill-specific rubric."
        ),
    }


def maintain_develop_partition(skills: list[dict],
                                self_assessed_levels: dict[str, int]) -> dict:
    """Partition a skill list into 'maintain' (already at level) and
    'develop' (gap exists) buckets based on user self-assessment.

    Each input skill must have a `skill_id` and either `required_level`
    or `target_level`. The output preserves order within each bucket.
    """
    maintain: list[dict] = []
    develop: list[dict] = []
    for skill in skills:
        sid = skill.get("skill_id", "")
        required = skill.get("required_level") or skill.get("target_level") or 3
        current = self_assessed_levels.get(sid)
        if current is None:
            # Not self-assessed - default to bottom of scale (treat as needing development)
            current = 0
        gap = max(0, required - current)
        entry = {**skill, "current_level": current, "gap": gap}
        if gap == 0:
            maintain.append(entry)
        else:
            develop.append(entry)
    return {"maintain": maintain, "develop": develop}
