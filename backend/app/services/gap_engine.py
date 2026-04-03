"""Skill Gap Engine — Phase 3.2

Computes the delta between a learner's current skill levels (State A)
and a target skill profile (State B), returning a prioritised list of
gaps that need to be closed.

Every skill ID is validated against the canonical ontology so that
downstream consumers never receive phantom entries.

Scoring formula
---------------
::

    priority_score = (3 × delta)
                   + (3 × criticality)
                   + (2 × role_relevance)
                   - (0.5 × skill_level)

- **delta** (weight 3) — the proficiency distance; larger gaps need
  attention first.
- **criticality** (weight 3) — from the JD parser's importance rating:
  high=3, medium=1, low=0.  Ensures "must have" skills outrank
  "nice to have" skills even when deltas are equal.
- **role_relevance** (weight 2) — graduated: 2 for primary domains
  (from role_analysis.key_domains), 1 for broader target domains,
  0 otherwise.
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
        skill_importance: dict[str, str] | None = None,
        skill_rank: dict[str, int] | None = None,
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
                    "target_role":    str,
                    "target_domains": list[str],
                    "primary_domains": list[str],   # from role_analysis.key_domains
                }

            When *None*, role_relevance is 0 for every skill (pure
            delta-based ranking, backward compatible).
        skill_importance : dict[str, str] | None
            Optional mapping of ``{skill_id: "high"|"medium"|"low"}``
            from the JD parser's importance ratings.  Used to compute
            a criticality score so that "must have" skills outrank
            "nice to have" skills even when deltas are equal.

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
                    "role_relevance":  int,          # 0, 1, or 2
                    "criticality":     int,          # 0, 1, or 3
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
        primary_domains: set[str] = set()
        if role_context:
            target_domains = set(role_context.get("target_domains") or [])
            primary_domains = set(role_context.get("primary_domains") or [])

        _IMPORTANCE_TO_CRITICALITY = {"critical": 5, "high": 3, "medium": 1, "low": 0}

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

            # Graduated role relevance: primary domains (from
            # role_analysis.key_domains) score 2, broader target
            # domains score 1, everything else 0.
            if skill["domain"] in primary_domains:
                role_relevance = 2
            elif skill["domain"] in target_domains:
                role_relevance = 1
            else:
                role_relevance = 0

            # ── 5-Factor Rubric Scoring (matches Luda's prioritization rubric) ──
            # Each factor scored 1-3, then weighted:
            # Priority = (Importance x 4) + (Breadth x 3) + (Momentum x 3) + (Connectivity x 2) + (Career Signal x 2)

            # 1. IMPORTANCE (x4): How critical for the target role?
            #    Based on JD parser's importance rating
            imp_rating = (skill_importance or {}).get(skill_id, "medium")
            importance_score = {"critical": 3, "high": 3, "medium": 2, "low": 1}.get(imp_rating, 2)

            # 2. BREADTH (x3): How many scenarios does this skill apply to?
            #    Foundation/prompting skills are broad (used daily), niche skills are narrow
            domain = skill["domain"]
            breadth_score = 3 if domain in ("D.PRM", "D.FND", "D.CTIC") else (2 if domain in ("D.EVL", "D.GOV", "D.COM") else 1)

            # 3. MOMENTUM (x3): How quickly can THIS LEARNER realistically improve?
            #    High = learner has transferable skills from their background to build on
            #    Low = starting from scratch, long ramp-up needed
            #    This is about the LEARNER's existing foundation, not the gap size
            if current_level >= 2:
                momentum_score = 3  # Strong existing foundation
            elif domain_floor >= 2:
                momentum_score = 3  # Strong in this domain already
            elif current_level == 1 or domain_floor >= 1:
                momentum_score = 2  # Some related experience
            else:
                momentum_score = 1  # Starting from scratch

            # 4. CONNECTIVITY (x2): How much does this skill enable other skills?
            #    Count dependents in the ontology
            dependents = self._ontology.get_skill_dependents(skill_id)
            connectivity_score = 3 if len(dependents) >= 3 else (2 if len(dependents) >= 1 else 1)

            # 5. CAREER SIGNAL (x2): How visible is this skill to hiring managers?
            #    Explicitly mentioned in JD (high importance) = high signal
            career_score = 3 if imp_rating in ("critical", "high") else (2 if imp_rating == "medium" else 1)
            # Skills in primary domains get a boost
            if skill["domain"] in primary_domains:
                career_score = min(3, career_score + 1)

            # Compute total rubric score
            priority_score = (
                (importance_score * 4)
                + (breadth_score * 3)
                + (momentum_score * 3)
                + (connectivity_score * 2)
                + (career_score * 2)
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
                    "rubric_scores": {
                        "importance": importance_score,
                        "breadth": breadth_score,
                        "momentum": momentum_score,
                        "connectivity": connectivity_score,
                        "career_signal": career_score,
                    },
                }
            )

        # Sort by: (1) JD parser rank (lower = higher priority), then
        # (2) rubric priority_score as tiebreaker
        # skill_rank maps skill_id -> rank (1 = most important)
        max_rank = len(state_b) + 1
        gaps.sort(
            key=lambda g: (
                -(skill_rank or {}).get(g["skill_id"], max_rank),  # negative rank so rank 1 sorts first
                g["priority_score"],
            ),
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
