"""Deterministic Learning Path Generator — Phase 3.3

Produces a fixed-length, prerequisite-ordered learning path from a
skill-gap analysis.  Every run with the same inputs yields the same
output — no randomness, no LLM calls.

Key design rules
----------------
1. **Mandatory category coverage** — every path must include at least
   one skill from each of four categories: Foundation (D.FND),
   Applied AI (RAG/Agents/Prompting/etc.), Evaluation (D.EVL), and
   Safety (D.SEC or D.GOV).  Phase 0.5 ensures state_b has gaps in
   each category; Phase 4 post-processes the final chapter list,
   swapping in self-contained skills from missing categories.
2. **Two-phase selection** — Phase 1 picks the top-5 primary skills
   from the ranked gap list.  Phase 2 resolves prerequisites with
   back-pressure.
3. **Domain diversity** — no more than ``MAX_DOMAIN_CHAPTERS`` chapters
   from the same domain.
4. **Prerequisite ordering** — prerequisites appear before the skills
   that depend on them.  Only immediate (depth-1) prerequisites are
   resolved; transitive prerequisites are deferred to future path
   generations.
5. **+1 progression** — each chapter advances the learner exactly one
   proficiency level, regardless of how large the total gap is.
"""

from __future__ import annotations

from typing import Any

from app.services.gap_engine import SkillGapEngine
from app.services.ontology import OntologyService, get_ontology_service
from app.services.state_inference import expand_state_a

MAX_CHAPTERS = 5
MAX_DOMAIN_CHAPTERS = 2

# Every learning path must include at least one skill from each
# mandatory category.  Categories are checked in order; the first
# domain in each category that yields a usable gap is used.
MANDATORY_CATEGORIES: list[dict[str, Any]] = [
    {"name": "foundation",  "domains": ["D.FND"]},
    {"name": "applied_ai",  "domains": ["D.PRM", "D.RAG", "D.AGT", "D.MOD", "D.MUL", "D.OPS", "D.TOOL"]},
    {"name": "evaluation",  "domains": ["D.EVL"]},
    {"name": "safety",      "domains": ["D.SEC", "D.GOV"]},
]


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

        # ==============================================================
        # Phase 0.5 — Ensure mandatory domains in state_b
        # ==============================================================
        # If state_b has no skills from a mandatory category, inject
        # the lowest-level skill (L2+) so the gap engine produces at
        # least one gap for that category.
        state_b = dict(state_b)  # don't mutate caller's dict
        self._ensure_mandatory_in_state_b(state_b)

        gaps = self._gap_engine.compute_gap(expanded_a, state_b, role_context)

        # ==============================================================
        # Phase 1 — Select primary candidates
        # ==============================================================
        primary_candidates: list[dict[str, Any]] = gaps[:MAX_CHAPTERS]

        # ==============================================================
        # Phase 2 — Prerequisite resolution with back-pressure
        # ==============================================================
        planned: list[dict[str, Any]] = self._resolve_with_backpressure(
            primary_candidates, expanded_a,
        )

        # ==============================================================
        # Phase 3 — Domain diversity enforcement
        # ==============================================================
        planned = self._enforce_domain_diversity(planned, gaps, expanded_a)

        # ==============================================================
        # Build chapter list — prereqs before their dependents
        # ==============================================================
        chapters = self._build_ordered_chapters(planned, expanded_a)

        # ==============================================================
        # Phase 4 — Mandatory category enforcement (post-processing)
        # ==============================================================
        # After a valid chapter plan is built, swap in skills from
        # missing mandatory categories.  This operates on the final
        # chapter list rather than the candidate list, avoiding the
        # cascading back-pressure problem.
        chapters = self._post_enforce_mandatory(chapters, gaps, expanded_a)

        return {
            "total_chapters": len(chapters),
            "chapters": chapters,
            "inferred_skill_count": inferred_count,
            "confidence_weighted": confidence_weighted,
            "decay_applied": decay_applied,
            "avg_decay_factor": avg_decay_factor,
        }

    # ------------------------------------------------------------------
    # Mandatory category helpers
    # ------------------------------------------------------------------

    def _ensure_mandatory_in_state_b(
        self,
        state_b: dict[str, int],
    ) -> None:
        """Inject one skill per missing mandatory category into *state_b*.

        For each mandatory category that has zero representation in
        *state_b*, pick the lowest-level skill (level >= 2) from the
        first domain in that category.  Level 2+ guarantees a positive
        delta after the gap engine's professional floor (L1).

        Mutates *state_b* in place.
        """
        state_b_domains = set()
        for sid in state_b:
            skill = self._ontology.get_skill(sid)
            if skill:
                state_b_domains.add(skill["domain"])

        for cat in MANDATORY_CATEGORIES:
            if state_b_domains & set(cat["domains"]):
                continue  # category already represented

            # Find the lowest-level L2+ skill with fewest prerequisites
            # from the first viable domain.
            for domain_id in cat["domains"]:
                domain_skills = [
                    s for s in self._ontology.get_skills_by_domain(domain_id)
                    if s["level"] >= 2 and s["id"] not in state_b
                ]
                # Prefer: fewest prereqs, then lowest level, then stable ID
                domain_skills.sort(key=lambda s: (
                    len(s.get("prerequisites", [])),
                    s["level"],
                    s["id"],
                ))
                if domain_skills:
                    best = domain_skills[0]
                    state_b[best["id"]] = best["level"]
                    state_b_domains.add(domain_id)
                    break

    def _post_enforce_mandatory(
        self,
        chapters: list[dict[str, Any]],
        all_gaps: list[dict[str, Any]],
        state_a: dict[str, int],
    ) -> list[dict[str, Any]]:
        """Swap chapters to ensure mandatory category coverage.

        Operates on the final chapter list (after topological sort)
        rather than the candidate list, avoiding cascading back-pressure.
        For each missing mandatory category, the lowest-value chapter
        from a non-mandatory (or already-covered) domain is replaced
        with a single-chapter skill from the missing category.

        The replacement skill is chosen to be self-contained: it must
        not require unmet prerequisites, so that a 1-for-1 swap keeps
        the chapter count at exactly ``MAX_CHAPTERS``.
        """
        if not chapters:
            return chapters

        chapters = list(chapters)
        chapter_domains = [
            self._ontology.get_skill(
                ch.get("primary_skill_id", "")
            )
            for ch in chapters
        ]

        for cat in MANDATORY_CATEGORIES:
            cat_domains = set(cat["domains"])

            # Check if any chapter covers this category
            covered = any(
                s is not None and s["domain"] in cat_domains
                for s in chapter_domains
            )
            if covered:
                continue

            # Find a replacement skill: must be from this category,
            # must have all prereqs already met (self-contained swap).
            replacement_skill = None
            for gap in all_gaps:
                if gap["domain"] not in cat_domains:
                    continue
                sid = gap["skill_id"]
                # Already in the chapter list?
                if any(
                    ch.get("primary_skill_id") == sid for ch in chapters
                ):
                    continue
                # Check all prereqs are met
                prereqs_met = True
                for prereq_id in gap["prerequisites"]:
                    prereq_skill = self._ontology.get_skill(prereq_id)
                    if prereq_skill is None:
                        continue
                    current = state_a.get(prereq_id, 0)
                    # Also count as met if it's already a chapter
                    if any(
                        ch.get("primary_skill_id") == prereq_id
                        for ch in chapters
                    ):
                        continue
                    if current < prereq_skill["level"]:
                        prereqs_met = False
                        break
                if prereqs_met:
                    replacement_skill = gap
                    break

            if replacement_skill is None:
                # Fallback: pick the cheapest gap (fewest prereqs)
                for gap in all_gaps:
                    if gap["domain"] not in cat_domains:
                        continue
                    if any(
                        ch.get("primary_skill_id") == gap["skill_id"]
                        for ch in chapters
                    ):
                        continue
                    replacement_skill = gap
                    break

            if replacement_skill is None:
                continue  # no gap at all — graceful skip

            # Find the chapter to replace: lowest-priority chapter
            # from a domain that either (a) isn't mandatory, or
            # (b) has multiple chapters so removing one still leaves
            # coverage.
            swap_idx = self._find_swap_target(chapters, chapter_domains)
            if swap_idx is None:
                continue

            # Build replacement chapter
            skill = self._ontology.get_skill(replacement_skill["skill_id"])
            if skill is None:
                continue

            new_chapter = self._build_chapter(
                chapter_number=chapters[swap_idx]["chapter_number"],
                skill=skill,
                current_level=replacement_skill["current_level"],
            )
            chapters[swap_idx] = new_chapter
            chapter_domains[swap_idx] = skill

        # Re-number chapters sequentially
        for i, ch in enumerate(chapters, start=1):
            ch["chapter_number"] = i

        return chapters

    def _find_swap_target(
        self,
        chapters: list[dict[str, Any]],
        chapter_domains: list[dict[str, Any] | None],
    ) -> int | None:
        """Find the best chapter to replace for mandatory coverage.

        Prefers chapters from domains that have multiple chapters
        (so removing one doesn't lose domain coverage).  Falls back
        to the last chapter.  Never swaps the only representative
        of a mandatory category.
        """
        # Count chapters per domain
        domain_chapter_counts: dict[str, int] = {}
        for skill in chapter_domains:
            if skill:
                d = skill["domain"]
                domain_chapter_counts[d] = domain_chapter_counts.get(d, 0) + 1

        # Identify which chapters are the sole mandatory representative
        mandatory_sole: set[int] = set()
        for cat in MANDATORY_CATEGORIES:
            cat_domains = set(cat["domains"])
            cat_indices = [
                i for i, s in enumerate(chapter_domains)
                if s and s["domain"] in cat_domains
            ]
            if len(cat_indices) == 1:
                mandatory_sole.add(cat_indices[0])

        # Prefer swapping a chapter from a domain with 2+ chapters,
        # scanning from the end (lowest priority / last in topo order).
        best_idx = None
        for idx in reversed(range(len(chapters))):
            if idx in mandatory_sole:
                continue
            skill = chapter_domains[idx]
            if skill and domain_chapter_counts.get(skill["domain"], 0) >= 2:
                return idx
            if best_idx is None:
                best_idx = idx  # first non-mandatory-sole from the end

        return best_idx

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
