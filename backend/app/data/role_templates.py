"""Role-based target skill templates.

Each role template maps ``skill_id → required_level`` representing
what a professional in that role **actually needs**, as opposed to
the ontology's inherent complexity tier for the skill.

Why this matters
----------------
Without role templates, state_b is built as::

    state_b[sid] = ontology.get_skill(sid)["level"]

This conflates "how complex a skill *is*" with "how deeply this role
*needs* it."  For example, SK.EVL.011 (Quality dashboards) is an
ontology tier-4 (Builder) skill, but an AI Product Manager only needs
to *read* dashboards — tier 2 (User) is sufficient.  Using the raw
ontology tier inflates deltas for non-technical roles and makes paths
harder than they need to be.

Template design principles
--------------------------
- **Keep**: skill stays at ontology tier when the role needs full
  mastery (e.g., PRD skills for a PM, OPS skills for an MLE).
- **Reduce**: skill is set below ontology tier when the role needs
  awareness or user-level proficiency, not builder/architect depth.
- **Raise**: skill is set above ontology tier when the role demands
  deeper proficiency than a generic curriculum would assume (e.g.,
  Python for a Data Scientist is tier 2 in the ontology but the
  role needs tier 3).

Usage
-----
::

    from app.data.role_templates import build_state_b

    state_b, source = build_state_b(
        skill_ids=["SK.EVL.001", "SK.EVL.011"],
        target_role="AI Product Manager",
        ontology_service=ont,
    )
    # source == "role_template"
"""

from __future__ import annotations

from typing import Any

# ======================================================================
# Role templates — skill_id → required proficiency level (0-5)
#
# Proficiency scale reminder:
#   0 = Unaware, 1 = Aware, 2 = User, 3 = Practitioner,
#   4 = Builder, 5 = Architect
# ======================================================================

ROLE_TEMPLATES: dict[str, dict[str, int]] = {

    # ------------------------------------------------------------------
    # AI Product Manager
    # ------------------------------------------------------------------
    # Needs to scope, evaluate, and govern AI features — not build them.
    # Core competency is in PRD (product design) and GOV (governance).
    # Technical depth is intentionally capped at User/Practitioner.
    "AI Product Manager": {
        # D.FND — foundational knowledge (keep at ontology tier)
        "SK.FND.001": 1,   # LLM fundamentals — Aware
        "SK.FND.002": 1,   # Capabilities vs limitations — Aware
        "SK.FND.003": 2,   # Model families — User
        "SK.FND.020": 1,   # Privacy basics — Aware
        "SK.FND.021": 1,   # IP/copyright — Aware
        "SK.FND.022": 1,   # Bias & fairness — Aware

        # D.PRD — product design (core of role, keep at tier)
        "SK.PRD.002": 3,   # Workflow mapping — Practitioner
        "SK.PRD.010": 3,   # Explainability UX — Practitioner
        "SK.PRD.011": 3,   # Feedback loop design — Practitioner

        # D.PRM — prompting (understand, don't master)
        "SK.PRM.001": 2,   # Instructions + constraints — User
        "SK.PRM.003": 2,   # Prompt debugging — User (reduced from ont 3)
        "SK.PRM.010": 2,   # JSON/schema outputs — User (reduced from ont 3)

        # D.EVL — evaluation (interpret, don't build)
        "SK.EVL.001": 2,   # Eval types — User
        "SK.EVL.011": 2,   # Quality dashboards — User (reduced from ont 4)
        "SK.EVL.021": 2,   # Release gates — User (reduced from ont 4)

        # D.GOV — governance (core of role, keep at tier)
        "SK.GOV.002": 3,   # Policy to controls — Practitioner
        "SK.GOV.020": 2,   # PII/PHI handling — User
        "SK.GOV.021": 3,   # Data minimization — Practitioner
    },

    # ------------------------------------------------------------------
    # Healthcare Data Scientist
    # ------------------------------------------------------------------
    # Needs analytical depth, model evaluation, and domain-specific
    # clinical knowledge.  Infrastructure/backend skills are secondary.
    "Healthcare Data Scientist": {
        # D.PRQ — prerequisites (Python/data are core tools)
        "SK.PRQ.010": 3,   # Python basics — Practitioner (raised from ont 2)
        "SK.PRQ.011": 3,   # Pandas/NumPy — Practitioner (raised from ont 2)
        "SK.PRQ.022": 2,   # Backend services — User (reduced from ont 3)

        # D.FND — foundational (keep at tier)
        "SK.FND.001": 1,   # LLM fundamentals — Aware
        "SK.FND.002": 1,   # Capabilities vs limitations — Aware
        "SK.FND.012": 2,   # Embeddings — User
        "SK.FND.020": 1,   # Privacy basics — Aware

        # D.EVL — evaluation (use dashboards, don't architect them)
        "SK.EVL.001": 2,   # Eval types — User
        "SK.EVL.010": 3,   # Tracing & observability — Practitioner
        "SK.EVL.011": 3,   # Quality dashboards — Practitioner (reduced from ont 4)
        "SK.EVL.021": 2,   # Release gates — User (reduced from ont 4)

        # D.GOV — governance (PHI handling is critical in healthcare)
        "SK.GOV.020": 3,   # PII/PHI handling — Practitioner (raised from ont 2)
        "SK.GOV.021": 3,   # Data minimization — Practitioner

        # D.DOM — domain expertise (core differentiator, keep at tier)
        "SK.DOM.HC.001": 3,   # Clinical risk awareness — Practitioner
        "SK.DOM.HC.002": 3,   # Evidence synthesis — Practitioner
    },

    # ------------------------------------------------------------------
    # Machine Learning Engineer
    # ------------------------------------------------------------------
    # Deeply technical role.  Most skills stay at or near ontology tier.
    # Python/data handling raised because they are daily tools.
    "Machine Learning Engineer": {
        # D.PRQ — prerequisites (Python is daily driver)
        "SK.PRQ.010": 3,   # Python basics — Practitioner (raised from ont 2)
        "SK.PRQ.011": 3,   # Pandas/NumPy — Practitioner (raised from ont 2)
        "SK.PRQ.030": 2,   # Cloud primitives — User
        "SK.PRQ.031": 3,   # Secrets management — Practitioner
        "SK.PRQ.032": 3,   # CI/CD concepts — Practitioner

        # D.EVL — evaluation (build & interpret)
        "SK.EVL.001": 2,   # Eval types — User
        "SK.EVL.010": 3,   # Tracing & observability — Practitioner
        "SK.EVL.011": 3,   # Quality dashboards — Practitioner (reduced from ont 4)
        "SK.EVL.020": 3,   # Prompt unit tests — Practitioner

        # D.OPS — operations (core of role, keep at tier)
        "SK.OPS.001": 3,   # Latency drivers — Practitioner
        "SK.OPS.002": 3,   # Cost modeling — Practitioner
        "SK.OPS.010": 4,   # Caching/batching/streaming — Builder
        "SK.OPS.022": 3,   # Versioning prompts/models — Practitioner

        # D.RAG — retrieval-augmented generation (keep at tier)
        "SK.RAG.000": 1,   # What is RAG — Aware
        "SK.RAG.001": 3,   # Query rewriting — Practitioner
        "SK.RAG.002": 3,   # Chunking strategies — Practitioner
        "SK.RAG.003": 3,   # Hybrid retrieval — Practitioner

        # D.AGT — agents (keep at tier)
        "SK.AGT.000": 1,   # What are AI agents — Aware
        "SK.AGT.001": 3,   # Tool definitions — Practitioner
        "SK.AGT.002": 3,   # Error handling & retries — Practitioner
        "SK.AGT.003": 3,   # State & memory management — Practitioner
    },
}


def build_state_b(
    skill_ids: list[str],
    target_role: str,
    ontology_service: Any,
) -> tuple[dict[str, int], str]:
    """Build a state_b dict for the given skills and role.

    Parameters
    ----------
    skill_ids : list[str]
        Skill IDs that should appear in state_b.
    target_role : str
        The learner's target role (e.g., ``"AI Product Manager"``).
    ontology_service : OntologyService
        Used to look up fallback levels from the ontology.

    Returns
    -------
    (state_b, source) : tuple[dict[str, int], str]
        *state_b* maps ``skill_id → required_level``.
        *source* is ``"role_template"`` when a matching template was
        used, or ``"ontology_fallback"`` when the ontology tier was
        used (either because no template exists for the role, or
        because a specific skill is not in the template).

    Notes
    -----
    The function applies **per-skill** fallback: if a role template
    exists but does not list a specific skill, the ontology tier is
    used for that skill only.  The ``source`` flag reflects the
    *primary* method — ``"role_template"`` if the template was
    consulted at all, ``"ontology_fallback"`` only when no template
    exists for the role.
    """
    template = ROLE_TEMPLATES.get(target_role)

    if template is None:
        # No template for this role — pure ontology fallback.
        state_b: dict[str, int] = {}
        for sid in skill_ids:
            skill = ontology_service.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
        return state_b, "ontology_fallback"

    # Template exists — prefer template level, fall back per-skill.
    state_b = {}
    for sid in skill_ids:
        if sid in template:
            state_b[sid] = template[sid]
        else:
            skill = ontology_service.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
    return state_b, "role_template"
