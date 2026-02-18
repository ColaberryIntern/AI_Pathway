"""Skill Gap Engine — Phase 3.1

Computes the delta between a learner's current skill levels (State A)
and a target skill profile (State B), returning a prioritised list of
gaps that need to be closed.

Every skill ID is validated against the canonical ontology so that
downstream consumers never receive phantom entries.

Scoring formula
---------------
::

    priority_score = (3 × delta)
                   + (2 × role_relevance)
                   - (0.5 × skill_level)

- **delta** (weight 3) — the proficiency distance is the strongest
  signal; larger gaps need attention first.
- **role_relevance** (weight 2) — binary flag (1 when the skill's
  domain is in the target role's focus domains, else 0).  This pulls
  persona-relevant skills above generic ones.
- **skill_level** (weight −0.5) — mild penalty for very advanced
  skills so that foundational gaps are addressed before architect-tier
  ones when deltas are equal.
"""

from __future__ import annotations

from typing import Any

from app.services.ontology import OntologyService, get_ontology_service


class SkillGapEngine:
    """Calculate and rank skill gaps between current and target profiles.

    Parameters
    ----------
    ontology_service : OntologyService | None
        Injected ontology service.  When *None* the cached singleton
        returned by ``get_ontology_service()`` is used.
    """

    def __init__(self, ontology_service: OntologyService | None = None) -> None:
        self._ontology = ontology_service or get_ontology_service()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_gap(
        self,
        state_a: dict[str, int],
        state_b: dict[str, int],
        role_context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return a sorted list of skill gaps where delta > 0.

        Parameters
        ----------
        state_a : dict[str, int]
            Learner's current profile — ``{skill_id: current_level}``.
            Skills present in *state_b* but absent here default to 0,
            but two floors apply:

            * **Professional floor** — if the learner has *any* skill
              at level 2+, unknown skills start at 1 (Aware).
            * **Skill-level floor** — experienced professionals (L3+
              anywhere) start at 2 (User) for intermediate+ skills
              (ontology level 3+), giving mixed starting levels.
            * **Domain floor** — if the learner knows any skill in a
              domain, other skills in that domain start at
              ``max(1, domain_max − 1)``.
        state_b : dict[str, int]
            Target/required profile — ``{skill_id: required_level}``.
        role_context : dict | None
            Optional role hint used for relevance scoring::

                {
                    "target_role":    str,          # e.g. "AI Product Manager"
                    "target_domains": list[str],    # e.g. ["D.PRD", "D.EVL"]
                }

            When *None*, role_relevance is 0 for every skill (pure
            delta-based ranking, backward compatible).

        Returns
        -------
        list[dict]
            Each entry contains::

                {
                    "skill_id":        str,
                    "skill_name":      str,
                    "domain":          str,
                    "current_level":   int,
                    "required_level":  int,
                    "delta":           int,
                    "skill_level":     int,
                    "prerequisites":   list[str],
                    "role_relevance":  int,          # 1 or 0
                    "priority_score":  float,
                }

            Sorted by *priority_score* descending.  Ties are broken by
            *skill_id* ascending for deterministic output.

        Raises
        ------
        ValueError
            If any skill ID in *state_a* or *state_b* is not found in the
            ontology.
        """
        self._validate_skill_ids(state_a, label="state_a")
        self._validate_skill_ids(state_b, label="state_b")

        target_domains: set[str] = set()
        if role_context:
            target_domains = set(role_context.get("target_domains") or [])

        # Professional floor: any working professional (L2+ in anything)
        # is at least Aware (L1) of all skills.  Prevents L0 display.
        max_skill = max(state_a.values()) if state_a else 0
        professional_floor = 1 if max_skill >= 2 else 0

        # Domain floor: if a learner has ANY skill in a domain, other
        # skills in that domain start at max(1, domain_max - 1).
        # A data analyst with SQL at L3 (D.PRQ) starts other D.PRQ
        # skills at L2 — she can "apply with help" in her own domain.
        domain_max: dict[str, int] = {}
        for sid, level in state_a.items():
            skill_info = self._ontology.get_skill(sid)
            if skill_info:
                d = skill_info["domain"]
                domain_max[d] = max(domain_max.get(d, 0), level)

        gaps: list[dict[str, Any]] = []

        for skill_id, required_level in state_b.items():
            skill = self._ontology.get_skill(skill_id)
            # skill is guaranteed non-None after validation

            # Domain floor: known domains get a boost
            dm = domain_max.get(skill["domain"], 0)
            domain_floor = max(1, dm - 1) if dm > 0 else 0

            # Skill-level floor: experienced professionals (L3+
            # anywhere) start at L2 for intermediate+ skills
            # (ontology level 3+).  A 6-year analyst isn't just
            # "aware" of A/B testing — she's worked adjacent to it.
            # But for foundational skills (level 1-2) she's just L1.
            if max_skill >= 3 and skill["level"] >= 3:
                skill_floor = 2
            else:
                skill_floor = professional_floor

            current_level = max(
                state_a.get(skill_id, 0), domain_floor, skill_floor
            )
            delta = required_level - current_level

            if delta <= 0:
                continue

            role_relevance = 1 if skill["domain"] in target_domains else 0

            priority_score = (
                (3 * delta)
                + (2 * role_relevance)
                - (0.5 * skill["level"])
            )

            gaps.append(
                {
                    "skill_id": skill_id,
                    "skill_name": skill["name"],
                    "domain": skill["domain"],
                    "current_level": current_level,
                    "required_level": required_level,
                    "delta": delta,
                    "skill_level": skill["level"],
                    "prerequisites": skill.get("prerequisites", []),
                    "role_relevance": role_relevance,
                    "priority_score": priority_score,
                }
            )

        gaps.sort(
            key=lambda g: (g["priority_score"], g["skill_id"]),
            reverse=True,
        )

        return gaps

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _validate_skill_ids(
        self,
        profile: dict[str, int],
        *,
        label: str,
    ) -> None:
        """Raise ``ValueError`` listing every unknown skill ID in *profile*."""
        unknown = [
            sid for sid in profile if self._ontology.get_skill(sid) is None
        ]
        if unknown:
            raise ValueError(
                f"Unknown skill ID(s) in {label}: {', '.join(unknown)}"
            )
