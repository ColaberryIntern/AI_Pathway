"""Deterministic Learning Path Generator — Phase 3.2

Produces a fixed-length, prerequisite-ordered learning path from a
skill-gap analysis.  Every run with the same inputs yields the same
output — no randomness, no LLM calls.

Key design rules
----------------
1. **Two-phase selection** — Phase 1 picks the top-5 primary skills
   from the ranked gap list.  Phase 2 resolves their prerequisites.
   When a prerequisite would push the total beyond ``MAX_CHAPTERS``,
   the *lowest-priority primary skill* is dropped — not the
   prerequisite.  This guarantees that high-priority skills always
   have their foundations in place.
2. **Domain diversity** — no more than ``MAX_DOMAIN_CHAPTERS`` chapters
   from the same domain.  When a domain is over-represented, the
   lowest-priority primary in that domain is replaced with the
   next-highest-ranked gap skill from a different domain, and
   prerequisite validation is re-run.
3. **Prerequisite ordering** — prerequisites appear before the skills
   that depend on them.  Only immediate (depth-1) prerequisites are
   resolved; transitive prerequisites are deferred to future path
   generations.
4. **+1 progression** — each chapter advances the learner exactly one
   proficiency level, regardless of how large the total gap is.
"""

from __future__ import annotations

from typing import Any

from app.services.gap_engine import SkillGapEngine
from app.services.ontology import OntologyService, get_ontology_service
from app.services.state_inference import expand_state_a

MAX_CHAPTERS = 5
MAX_DOMAIN_CHAPTERS = 2


class LearningPathGenerator:
    """Build a deterministic, prerequisite-aware learning path.

    Parameters
    ----------
    ontology_service : OntologyService | None
        Shared ontology instance.  Defaults to the cached singleton.
    """

    def __init__(self, ontology_service: OntologyService | None = None) -> None:
        self._ontology = ontology_service or get_ontology_service()
        self._gap_engine = SkillGapEngine(ontology_service=self._ontology)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_path(
        self,
        state_a: dict[str, int],
        state_b: dict[str, int],
        role_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a learning path of up to 5 chapters.

        Uses a two-phase algorithm:

        * **Phase 1** — select the top ``MAX_CHAPTERS`` primary skills
          from the gap engine's ranked output.
        * **Phase 2** — for each primary skill (highest priority first),
          collect missing prerequisites.  If the combined total exceeds
          ``MAX_CHAPTERS``, drop the lowest-priority primary skill from
          the *end* of the candidate list.  Repeat until the plan fits.
          Finally, build the chapter list with prerequisites placed
          immediately before their dependent skill.

        Parameters
        ----------
        state_a : dict[str, int]
            Learner's current profile — ``{skill_id: current_level}``.
            Missing skills are assumed to be level 0 (Unaware).
        state_b : dict[str, int]
            Target/required profile — ``{skill_id: required_level}``.
        role_context : dict | None
            Passed through to ``SkillGapEngine.compute_gap()`` for
            role-aware prioritisation.

        Returns
        -------
        dict
            ::

                {
                    "total_chapters": int,        # <= 5
                    "chapters": [
                        {
                            "chapter_number":     int,
                            "primary_skill_id":   str,
                            "primary_skill_name": str,
                            "current_level":      int,
                            "target_level":       int,   # current + 1
                            "objectives":         [],
                            "project_placeholder": {},
                        },
                        ...
                    ]
                }

        Raises
        ------
        ValueError
            Propagated from ``SkillGapEngine`` when skill IDs are
            unknown.
        """
        # ==============================================================
        # Phase 0 — Expand state_a with inferred prerequisites
        # ==============================================================
        (
            expanded_a,
            inferred_count,
            confidence_weighted,
            decay_applied,
            avg_decay_factor,
        ) = expand_state_a(state_a, self._ontology)

        gaps = self._gap_engine.compute_gap(expanded_a, state_b, role_context)

        # ==============================================================
        # Phase 1 — Select primary candidates
        # ==============================================================
        primary_candidates: list[dict[str, Any]] = gaps[:MAX_CHAPTERS]

        # ==============================================================
        # Phase 2 — Prerequisite resolution with back-pressure
        # ==============================================================
        # For each candidate, determine which direct prerequisites the
        # learner still needs.  If adding those prereqs pushes the
        # total count past MAX_CHAPTERS, drop the lowest-priority
        # candidate (the last one in the list) and retry.

        planned: list[dict[str, Any]] = self._resolve_with_backpressure(
            primary_candidates, state_a,
        )

        # ==============================================================
        # Phase 3 — Domain diversity enforcement
        # ==============================================================
        # No more than MAX_DOMAIN_CHAPTERS chapters from the same domain.
        # Over-represented domains trigger a swap: drop the lowest-
        # priority primary in that domain, pull in the next-best gap
        # skill from a different domain, then re-run back-pressure.

        planned = self._enforce_domain_diversity(planned, gaps, state_a)

        # ==============================================================
        # Build chapter list — prereqs before their dependents
        # ==============================================================
        chapters = self._build_ordered_chapters(planned, state_a)

        return {
            "total_chapters": len(chapters),
            "chapters": chapters,
            "inferred_skill_count": inferred_count,
            "confidence_weighted": confidence_weighted,
            "decay_applied": decay_applied,
            "avg_decay_factor": avg_decay_factor,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_with_backpressure(
        self,
        candidates: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> list[dict[str, Any]]:
        """Trim candidates until primaries + prerequisites fit in MAX_CHAPTERS.

        Returns a list of gap dicts (the surviving primary candidates)
        in their original priority order.
        """
        remaining = list(candidates)

        while remaining:
            total_slots = self._count_slots(remaining, state_a)
            if total_slots <= MAX_CHAPTERS:
                break
            # Drop the lowest-priority candidate (last in list)
            remaining.pop()

        return remaining

    def _count_slots(
        self,
        candidates: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> int:
        """Count total chapters needed: primaries + unique prerequisites."""
        seen: set[str] = set()
        count = 0

        for gap in candidates:
            # Count prerequisite slots
            for prereq_id in gap["prerequisites"]:
                if prereq_id in seen:
                    continue
                prereq_skill = self._ontology.get_skill(prereq_id)
                if prereq_skill is None:
                    continue
                current = state_a.get(prereq_id, 0)
                if current < prereq_skill["level"]:
                    seen.add(prereq_id)
                    count += 1

            # Count the primary skill slot
            if gap["skill_id"] not in seen:
                seen.add(gap["skill_id"])
                count += 1

        return count

    # ------------------------------------------------------------------
    # Domain diversity
    # ------------------------------------------------------------------

    def _enforce_domain_diversity(
        self,
        planned: list[dict[str, Any]],
        all_gaps: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> list[dict[str, Any]]:
        """Swap out over-represented domain skills for alternatives.

        Iteratively checks whether any single domain contributes more
        than ``MAX_DOMAIN_CHAPTERS`` chapters (counting both primaries
        and their unmet prerequisites).  When a violation is found:

        1. The lowest-priority primary in the offending domain is removed.
        2. The next-highest-ranked gap skill from a *different* domain
           that actually fits within ``MAX_CHAPTERS`` is inserted.
        3. The candidate list is re-sorted and back-pressure is re-run.

        After all domain violations are resolved, a backfill pass adds
        more primaries (from any non-saturated domain) if capacity
        remains.
        """
        rejected: set[str] = set()

        for _ in range(MAX_CHAPTERS * 3):  # safety bound
            domain_counts = self._count_chapter_domains(planned, state_a)

            # Find the most over-represented domain
            over_domain: str | None = None
            max_over = MAX_DOMAIN_CHAPTERS
            for domain, count in sorted(domain_counts.items()):
                if count > max_over:
                    over_domain = domain
                    max_over = count
            if over_domain is None:
                break  # all domains within limit

            # Find lowest-priority primary to drop
            drop_idx = self._find_domain_drop(
                planned, over_domain, state_a,
            )
            if drop_idx is None:
                break  # cannot reduce further

            dropped = planned.pop(drop_idx)
            rejected.add(dropped["skill_id"])

            # Find replacement: must be from a different domain AND
            # must fit within MAX_CHAPTERS when combined with existing
            # planned candidates.
            planned_ids = {g["skill_id"] for g in planned}
            for gap in all_gaps:
                sid = gap["skill_id"]
                if sid in planned_ids or sid in rejected:
                    continue
                skill = self._ontology.get_skill(sid)
                if skill is None:
                    continue
                if skill["domain"] == over_domain:
                    continue  # same domain — skip
                # Fitness check: would this candidate fit?
                test = list(planned) + [gap]
                if self._count_slots(test, state_a) > MAX_CHAPTERS:
                    continue  # too heavy — try next
                planned.append(gap)
                break

            # Re-sort by priority_score desc, skill_id asc (deterministic)
            planned.sort(
                key=lambda g: (-g["priority_score"], g["skill_id"]),
            )
            # Re-run back-pressure with the updated set
            planned = self._resolve_with_backpressure(planned, state_a)

        # Backfill: if capacity remains, add more primaries from any
        # non-saturated domain.
        planned = self._backfill(planned, all_gaps, state_a, rejected)

        return planned

    def _backfill(
        self,
        planned: list[dict[str, Any]],
        all_gaps: list[dict[str, Any]],
        state_a: dict[str, int],
        rejected: set[str],
    ) -> list[dict[str, Any]]:
        """Fill unused capacity with the next eligible gap skills."""
        for gap in all_gaps:
            if self._count_slots(planned, state_a) >= MAX_CHAPTERS:
                break
            sid = gap["skill_id"]
            planned_ids = {g["skill_id"] for g in planned}
            if sid in planned_ids or sid in rejected:
                continue
            skill = self._ontology.get_skill(sid)
            if skill is None:
                continue
            # Respect domain cap
            domain_counts = self._count_chapter_domains(planned, state_a)
            if domain_counts.get(skill["domain"], 0) >= MAX_DOMAIN_CHAPTERS:
                continue
            # Fitness check
            test = list(planned) + [gap]
            if self._count_slots(test, state_a) > MAX_CHAPTERS:
                continue
            planned.append(gap)

        planned.sort(
            key=lambda g: (-g["priority_score"], g["skill_id"]),
        )
        return self._resolve_with_backpressure(planned, state_a)

    def _count_chapter_domains(
        self,
        planned: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> dict[str, int]:
        """Count how many chapters each domain would contribute.

        Expands primaries + their unmet direct prerequisites, then
        tallies by domain.
        """
        domain_counts: dict[str, int] = {}
        seen: set[str] = set()

        for gap in planned:
            sid = gap["skill_id"]
            if sid not in seen:
                skill = self._ontology.get_skill(sid)
                if skill:
                    d = skill["domain"]
                    domain_counts[d] = domain_counts.get(d, 0) + 1
                    seen.add(sid)

            for prereq_id in gap["prerequisites"]:
                if prereq_id in seen:
                    continue
                prereq_skill = self._ontology.get_skill(prereq_id)
                if prereq_skill is None:
                    continue
                current = state_a.get(prereq_id, 0)
                if current < prereq_skill["level"]:
                    d = prereq_skill["domain"]
                    domain_counts[d] = domain_counts.get(d, 0) + 1
                    seen.add(prereq_id)

        return domain_counts

    def _find_domain_drop(
        self,
        planned: list[dict[str, Any]],
        over_domain: str,
        state_a: dict[str, int],
    ) -> int | None:
        """Find the lowest-priority primary in *over_domain*.

        First looks for a primary whose own domain matches.  Falls back
        to a primary whose *prerequisites* are in the domain (the
        primary is the reason those prereq chapters exist).

        Returns the index into *planned*, or None.
        """
        # Pass 1: primary skill directly in the domain
        for idx in reversed(range(len(planned))):
            skill = self._ontology.get_skill(planned[idx]["skill_id"])
            if skill and skill["domain"] == over_domain:
                return idx

        # Pass 2: primary whose unmet prereqs are in the domain
        for idx in reversed(range(len(planned))):
            for prereq_id in planned[idx]["prerequisites"]:
                prereq_skill = self._ontology.get_skill(prereq_id)
                if prereq_skill is None:
                    continue
                if prereq_skill["domain"] != over_domain:
                    continue
                current = state_a.get(prereq_id, 0)
                if current < prereq_skill["level"]:
                    return idx

        return None

    # ------------------------------------------------------------------
    # Topological ordering
    # ------------------------------------------------------------------

    def _build_ordered_chapters(
        self,
        planned: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> list[dict[str, Any]]:
        """Build the final chapter list via topological sort.

        Collects all skills to schedule (primaries + their unmet
        prerequisites), builds a dependency graph among them, then
        emits chapters in topological order so that every prerequisite
        appears before the skills that depend on it.  Ties within the
        same topological layer are broken by the original gap-engine
        priority (position in ``planned``).
        """
        # Professional floor for prerequisites: L1 minimum for any
        # working professional (L2+ in anything).  Primary skills
        # already carry the gap engine's per-skill floor in their
        # current_level field.
        professional_floor = (
            1 if any(v >= 2 for v in state_a.values()) else 0
        )

        # -- Step 1: collect every skill that will become a chapter --------
        #    skill_id -> {"skill": dict, "current_level": int}
        to_schedule: dict[str, dict[str, Any]] = {}
        # Edges: skill_id -> set of skill_ids it depends on (within the set)
        depends_on: dict[str, set[str]] = {}

        for gap in planned:
            sid = gap["skill_id"]
            if sid not in to_schedule:
                to_schedule[sid] = {
                    "skill": self._ontology.get_skill(sid),
                    "current_level": gap["current_level"],
                }
                depends_on.setdefault(sid, set())

            for prereq_id in gap["prerequisites"]:
                prereq_skill = self._ontology.get_skill(prereq_id)
                if prereq_skill is None:
                    continue
                current = max(state_a.get(prereq_id, 0), professional_floor)
                if current >= prereq_skill["level"]:
                    continue  # learner already meets this prereq
                if prereq_id not in to_schedule:
                    to_schedule[prereq_id] = {
                        "skill": prereq_skill,
                        "current_level": current,
                    }
                    depends_on.setdefault(prereq_id, set())
                # Record the dependency edge
                depends_on.setdefault(sid, set()).add(prereq_id)

        # Also record cross-prerequisite edges: if a prerequisite skill
        # itself has prerequisites that are also in to_schedule, those
        # must come first.
        for sid in list(to_schedule):
            skill_data = to_schedule[sid]["skill"]
            if skill_data is None:
                continue
            for prereq_id in skill_data.get("prerequisites", []):
                if prereq_id in to_schedule and prereq_id != sid:
                    depends_on.setdefault(sid, set()).add(prereq_id)

        # -- Step 2: Kahn's algorithm (topological sort) ------------------
        # Build priority lookup: lower index = higher priority
        priority_lookup: dict[str, int] = {}
        for idx, gap in enumerate(planned):
            priority_lookup.setdefault(gap["skill_id"], idx)
        # Prerequisites not in planned get a priority after all primaries
        next_priority = len(planned)
        for sid in to_schedule:
            if sid not in priority_lookup:
                priority_lookup[sid] = next_priority
                next_priority += 1

        in_degree: dict[str, int] = {sid: 0 for sid in to_schedule}
        for sid, deps in depends_on.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[sid] = in_degree.get(sid, 0) + 1

        # Seed with zero in-degree nodes, sorted by priority
        queue: list[str] = sorted(
            [sid for sid, deg in in_degree.items() if deg == 0],
            key=lambda s: priority_lookup.get(s, 999),
        )

        ordered: list[str] = []
        while queue:
            node = queue.pop(0)
            ordered.append(node)
            # Decrease in-degree for dependents
            for sid, deps in depends_on.items():
                if node in deps:
                    in_degree[sid] -= 1
                    if in_degree[sid] == 0:
                        # Insert in priority order
                        queue.append(sid)
                        queue.sort(key=lambda s: priority_lookup.get(s, 999))

        # -- Step 3: build chapter dicts ----------------------------------
        chapters: list[dict[str, Any]] = []
        for seq, sid in enumerate(ordered, start=1):
            entry = to_schedule[sid]
            chapters.append(self._build_chapter(
                chapter_number=seq,
                skill=entry["skill"],
                current_level=entry["current_level"],
            ))

        return chapters

    @staticmethod
    def _build_chapter(
        *,
        chapter_number: int,
        skill: dict[str, Any],
        current_level: int,
    ) -> dict[str, Any]:
        """Create a single chapter dict with the +1 progression rule.

        The target level is always ``current_level + 1``, capping the
        learner's advancement to a single step per chapter.  Larger
        gaps are closed across multiple path generations.
        """
        return {
            "chapter_number": chapter_number,
            "primary_skill_id": skill["id"],
            "primary_skill_name": skill["name"],
            "current_level": current_level,
            "target_level": current_level + 1,
            "objectives": [],
            "project_placeholder": {},
        }
