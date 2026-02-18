"""Path Quality Evaluator — rule-based educational quality scoring.

Scores enriched learning paths on objective clarity, Bloom's taxonomy
progression, project specificity, cross-chapter consistency, and domain
balance.  All heuristics are deterministic — no LLM calls.

Scoring scale
-------------
Each metric produces a value on 0-5:

    0  — missing / completely invalid
    1  — present but severely deficient
    2  — below expectations
    3  — meets minimum expectations
    4  — good quality
    5  — excellent quality

The ``overall_score`` is the weighted mean of all chapter and path
scores.  ``weakness_flags`` lists human-readable strings that identify
specific improvement opportunities.
"""

from __future__ import annotations

import re
from typing import Any

# ======================================================================
# Bloom's taxonomy verb tiers (case-insensitive first word of objective)
# ======================================================================
# Tier 1 = Remember, Tier 6 = Create.  Each verb maps to a numeric tier.

_BLOOM_VERBS: dict[str, int] = {}

_BLOOM_TIERS: list[tuple[int, list[str]]] = [
    (1, [
        "list", "define", "identify", "name", "recall",
        "recognize", "state", "label", "match", "memorize",
    ]),
    (2, [
        "describe", "explain", "summarize", "classify", "discuss",
        "interpret", "paraphrase", "predict", "translate", "illustrate",
    ]),
    (3, [
        "apply", "implement", "use", "demonstrate", "execute",
        "solve", "calculate", "operate", "practice", "compute",
    ]),
    (4, [
        "analyze", "compare", "contrast", "differentiate", "examine",
        "investigate", "distinguish", "organize", "deconstruct",
        "categorize",
    ]),
    (5, [
        "evaluate", "assess", "justify", "critique", "judge",
        "recommend", "defend", "prioritize", "rank", "validate",
    ]),
    (6, [
        "design", "create", "develop", "construct", "propose",
        "formulate", "build", "compose", "invent", "synthesize",
    ]),
]

for _tier, _verbs in _BLOOM_TIERS:
    for _v in _verbs:
        _BLOOM_VERBS[_v] = _tier

# Weights for the overall score
_WEIGHT_OBJECTIVE_CLARITY = 2.0
_WEIGHT_BLOOM_PROGRESSION = 1.5
_WEIGHT_PROJECT_SPECIFICITY = 2.0
_WEIGHT_PROGRESSION_CONSISTENCY = 1.5
_WEIGHT_DOMAIN_BALANCE = 1.0


class PathQualityEvaluator:
    """Score an enriched learning path using rule-based heuristics.

    Usage::

        evaluator = PathQualityEvaluator()
        report = evaluator.evaluate(enriched_path)
    """

    def evaluate(self, path: dict[str, Any]) -> dict[str, Any]:
        """Score the enriched path and return a quality report.

        Parameters
        ----------
        path : dict
            The enriched learning-path dict as returned by
            ``PathGeneratorAgent.execute()``.  Expected shape::

                {
                    "chapters": [
                        {
                            "chapter_number": int,
                            "skill_id": str,
                            "learning_objectives": [str, ...],
                            "applied_project": {
                                "project_title": str,
                                "project_description": str,
                                "deliverable": str,
                                "estimated_time_minutes": int,
                            },
                            ...
                        },
                        ...
                    ]
                }

        Returns
        -------
        dict
            ::

                {
                    "chapter_scores": [
                        {
                            "chapter_number": int,
                            "objective_clarity_score": float,
                            "bloom_progression_score": float,
                            "project_specificity_score": float,
                            "chapter_average": float,
                        },
                        ...
                    ],
                    "progression_consistency_score": float,
                    "domain_balance_score": float,
                    "overall_score": float,
                    "weakness_flags": [str, ...],
                }
        """
        chapters = path.get("chapters", [])
        if not chapters:
            return {
                "chapter_scores": [],
                "progression_consistency_score": 0.0,
                "domain_balance_score": 0.0,
                "overall_score": 0.0,
                "weakness_flags": ["Path contains no chapters."],
            }

        weakness_flags: list[str] = []
        chapter_scores: list[dict[str, Any]] = []
        bloom_tiers_per_chapter: list[float] = []

        for idx, chapter in enumerate(chapters):
            ch_num = chapter.get("chapter_number", idx + 1)
            ch_label = f"Chapter {ch_num}"
            n_chapters = len(chapters)

            obj_score, obj_flags = self._score_objective_clarity(
                chapter, ch_label,
            )
            bloom_score, avg_tier, bloom_flags = self._score_bloom_progression(
                chapter, idx, n_chapters, ch_label,
            )
            proj_score, proj_flags = self._score_project_specificity(
                chapter, ch_label,
            )

            bloom_tiers_per_chapter.append(avg_tier)
            weakness_flags.extend(obj_flags)
            weakness_flags.extend(bloom_flags)
            weakness_flags.extend(proj_flags)

            ch_avg = round(
                (obj_score + bloom_score + proj_score) / 3, 2,
            )

            chapter_scores.append({
                "chapter_number": ch_num,
                "objective_clarity_score": obj_score,
                "bloom_progression_score": bloom_score,
                "project_specificity_score": proj_score,
                "chapter_average": ch_avg,
            })

        prog_score, prog_flags = self._score_progression_consistency(
            bloom_tiers_per_chapter, chapters,
        )
        weakness_flags.extend(prog_flags)

        domain_score, domain_flags = self._score_domain_balance(chapters)
        weakness_flags.extend(domain_flags)

        # Weighted overall score
        chapter_avg_sum = sum(cs["chapter_average"] for cs in chapter_scores)
        chapter_avg_mean = chapter_avg_sum / len(chapter_scores)

        total_weight = (
            _WEIGHT_OBJECTIVE_CLARITY
            + _WEIGHT_BLOOM_PROGRESSION
            + _WEIGHT_PROJECT_SPECIFICITY
            + _WEIGHT_PROGRESSION_CONSISTENCY
            + _WEIGHT_DOMAIN_BALANCE
        )

        # Per-chapter metric averages
        avg_obj = (
            sum(cs["objective_clarity_score"] for cs in chapter_scores)
            / len(chapter_scores)
        )
        avg_bloom = (
            sum(cs["bloom_progression_score"] for cs in chapter_scores)
            / len(chapter_scores)
        )
        avg_proj = (
            sum(cs["project_specificity_score"] for cs in chapter_scores)
            / len(chapter_scores)
        )

        overall = round(
            (
                _WEIGHT_OBJECTIVE_CLARITY * avg_obj
                + _WEIGHT_BLOOM_PROGRESSION * avg_bloom
                + _WEIGHT_PROJECT_SPECIFICITY * avg_proj
                + _WEIGHT_PROGRESSION_CONSISTENCY * prog_score
                + _WEIGHT_DOMAIN_BALANCE * domain_score
            )
            / total_weight,
            2,
        )

        return {
            "chapter_scores": chapter_scores,
            "progression_consistency_score": prog_score,
            "domain_balance_score": domain_score,
            "overall_score": overall,
            "weakness_flags": weakness_flags,
        }

    # ------------------------------------------------------------------
    # Per-chapter scorers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_objective_clarity(
        chapter: dict[str, Any],
        ch_label: str,
    ) -> tuple[float, list[str]]:
        """Score learning objectives on count, verb presence, and specificity.

        Rubric:
            +1   — objectives list exists and is non-empty
            +1   — count in 3-5 range
            +1   — majority (>= 50%) start with a recognised Bloom's verb
            +1   — average word count per objective >= 6 (specific enough)
            +1   — no duplicate objectives
        """
        flags: list[str] = []
        objectives = chapter.get("learning_objectives")

        if not objectives or not isinstance(objectives, list):
            flags.append(f"{ch_label}: objectives missing or empty.")
            return 0.0, flags

        score = 1.0  # exists

        # Count in range
        if 3 <= len(objectives) <= 5:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: {len(objectives)} objectives "
                f"(expected 3-5)."
            )

        # Bloom's verb coverage
        verb_hits = 0
        for obj in objectives:
            first_word = obj.strip().split()[0].lower().rstrip(".,;:")
            if first_word in _BLOOM_VERBS:
                verb_hits += 1
        verb_ratio = verb_hits / len(objectives)
        if verb_ratio >= 0.5:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: only {verb_hits}/{len(objectives)} "
                f"objectives start with a Bloom's verb."
            )

        # Specificity — average word count
        avg_words = sum(len(obj.split()) for obj in objectives) / len(objectives)
        if avg_words >= 6:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: objectives too brief "
                f"(avg {avg_words:.0f} words, need >= 6)."
            )

        # Uniqueness
        normalised = [re.sub(r"\s+", " ", o.strip().lower()) for o in objectives]
        if len(set(normalised)) == len(normalised):
            score += 1.0
        else:
            flags.append(f"{ch_label}: duplicate objectives detected.")

        return round(score, 2), flags

    @staticmethod
    def _score_bloom_progression(
        chapter: dict[str, Any],
        chapter_idx: int,
        total_chapters: int,
        ch_label: str,
    ) -> tuple[float, float, list[str]]:
        """Score whether objective verbs match expected Bloom's tier.

        For chapter at position *chapter_idx* (0-based) in a path of
        *total_chapters*, the expected tier is linearly interpolated:

            expected_tier = 1 + 5 * (chapter_idx / max(total_chapters - 1, 1))

        Scoring:
            5  — average tier within +/-0.5 of expected
            4  — within +/-1.0
            3  — within +/-1.5
            2  — within +/-2.0
            1  — present but further off
            0  — no verbs detected

        Returns (score, average_tier, flags).
        """
        flags: list[str] = []
        objectives = chapter.get("learning_objectives")
        if not objectives or not isinstance(objectives, list):
            return 0.0, 0.0, []

        tiers: list[int] = []
        for obj in objectives:
            first_word = obj.strip().split()[0].lower().rstrip(".,;:")
            tier = _BLOOM_VERBS.get(first_word)
            if tier is not None:
                tiers.append(tier)

        if not tiers:
            flags.append(
                f"{ch_label}: no recognised Bloom's verbs in objectives."
            )
            return 0.0, 0.0, flags

        avg_tier = sum(tiers) / len(tiers)

        # Expected tier for this chapter position
        denom = max(total_chapters - 1, 1)
        expected_tier = 1.0 + 5.0 * (chapter_idx / denom)

        distance = abs(avg_tier - expected_tier)

        if distance <= 0.5:
            score = 5.0
        elif distance <= 1.0:
            score = 4.0
        elif distance <= 1.5:
            score = 3.0
        elif distance <= 2.0:
            score = 2.0
        else:
            score = 1.0
            flags.append(
                f"{ch_label}: Bloom's tier avg {avg_tier:.1f} far from "
                f"expected {expected_tier:.1f}."
            )

        return score, avg_tier, flags

    @staticmethod
    def _score_project_specificity(
        chapter: dict[str, Any],
        ch_label: str,
    ) -> tuple[float, list[str]]:
        """Score the applied project on completeness and detail.

        Rubric:
            +1   — applied_project dict exists
            +1   — project_title is non-empty
            +1   — project_description >= 20 words
            +1   — deliverable is specific (>= 3 words)
            +1   — estimated_time_minutes is a positive number
        """
        flags: list[str] = []
        project = chapter.get("applied_project")

        if not project or not isinstance(project, dict):
            flags.append(f"{ch_label}: applied_project missing.")
            return 0.0, flags

        score = 1.0  # exists

        # Title
        title = project.get("project_title", "")
        if title and title.lower() not in ("pending enrichment", "tbd", "n/a"):
            score += 1.0
        else:
            flags.append(f"{ch_label}: project title is missing or placeholder.")

        # Description depth
        desc = project.get("project_description", "")
        desc_words = len(desc.split()) if desc else 0
        if desc_words >= 20:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: project description too brief "
                f"({desc_words} words, need >= 20)."
            )

        # Deliverable specificity
        deliverable = project.get("deliverable", "")
        deliv_words = len(deliverable.split()) if deliverable else 0
        if deliv_words >= 3:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: project deliverable too vague "
                f"({deliv_words} words, need >= 3)."
            )

        # Time estimate
        time_mins = project.get("estimated_time_minutes")
        if isinstance(time_mins, (int, float)) and time_mins > 0:
            score += 1.0
        else:
            flags.append(
                f"{ch_label}: project estimated_time_minutes "
                f"missing or invalid."
            )

        return round(score, 2), flags

    # ------------------------------------------------------------------
    # Path-level scorers
    # ------------------------------------------------------------------

    @staticmethod
    def _score_progression_consistency(
        bloom_tiers: list[float],
        chapters: list[dict[str, Any]],
    ) -> tuple[float, list[str]]:
        """Score whether Bloom's tiers increase across chapters.

        Rubric:
            5  — strictly non-decreasing
            4  — at most 1 regression
            3  — at most 2 regressions
            2  — more regressions but overall trend is upward
            1  — flat or downward trend
            0  — no data
        """
        flags: list[str] = []

        # Filter out zero entries (chapters with no bloom data)
        valid = [(i, t) for i, t in enumerate(bloom_tiers) if t > 0]
        if len(valid) < 2:
            return 3.0, []  # not enough data to judge

        regressions = 0
        for k in range(1, len(valid)):
            prev_idx, prev_tier = valid[k - 1]
            curr_idx, curr_tier = valid[k]
            if curr_tier < prev_tier - 0.25:  # small tolerance
                regressions += 1
                flags.append(
                    f"Chapter {chapters[curr_idx].get('chapter_number', curr_idx + 1)}: "
                    f"Bloom's tier {curr_tier:.1f} regresses from "
                    f"Chapter {chapters[prev_idx].get('chapter_number', prev_idx + 1)}'s "
                    f"{prev_tier:.1f}."
                )

        # Overall trend
        first_tier = valid[0][1]
        last_tier = valid[-1][1]
        upward = last_tier >= first_tier

        if regressions == 0:
            score = 5.0
        elif regressions == 1:
            score = 4.0
        elif regressions == 2:
            score = 3.0
        elif upward:
            score = 2.0
        else:
            score = 1.0

        return score, flags

    @staticmethod
    def _score_domain_balance(
        chapters: list[dict[str, Any]],
    ) -> tuple[float, list[str]]:
        """Score domain diversity across chapters.

        Rubric:
            5  — 4+ unique domains
            4  — 3 unique domains
            3  — 2 unique domains, neither exceeds 60%
            2  — 2 unique domains, one exceeds 60%
            1  — single domain
            0  — no domain data
        """
        flags: list[str] = []

        domains: list[str] = []
        for ch in chapters:
            # skill_id format: SK.<DOMAIN>.<NUM> — extract domain
            skill_id = ch.get("skill_id", "")
            parts = skill_id.split(".")
            if len(parts) >= 2:
                domains.append(f"D.{parts[1]}")
            else:
                domains.append("unknown")

        unique = set(domains)
        n_unique = len(unique)

        if n_unique == 0:
            return 0.0, ["No domain data in chapters."]

        if n_unique >= 4:
            score = 5.0
        elif n_unique == 3:
            score = 4.0
        elif n_unique == 2:
            # Check concentration
            from collections import Counter
            counts = Counter(domains)
            max_share = max(counts.values()) / len(domains)
            if max_share <= 0.6:
                score = 3.0
            else:
                score = 2.0
                dominant = counts.most_common(1)[0]
                flags.append(
                    f"Domain {dominant[0]} dominates with "
                    f"{dominant[1]}/{len(domains)} chapters "
                    f"({max_share:.0%})."
                )
        else:
            score = 1.0
            flags.append(
                f"All chapters are in a single domain ({domains[0]})."
            )

        return score, flags
