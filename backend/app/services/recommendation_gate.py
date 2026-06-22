"""Recommendation gate with regeneration fallback (Trust Before Intelligence -
Governance/Orchestration layer).

Wraps the ensembled judge (evaluate_recommendation_stable) with a bounded
regeneration loop so the gate can HARD-gate without ever leaving the learner
empty-handed:

  1. Judge the current top-N recommendation (ensemble: K samples, median-aggregated).
  2. If the verdict is not REJECT, accept it (ACCEPT, or ACCEPT_WITH_REVIEW flagged
     for a human).
  3. If REJECT, regenerate: drop the judge-flagged weak skills (majority fit_level
     not role_specific) and pull in the next-ranked candidates from the pool the
     recommender already produced - no expensive re-run of the orchestrator.
  4. Re-judge. Repeat up to max_attempts.
  5. If still REJECT after the budget is spent, DEGRADE GRACEFULLY: return the
     highest-composite attempt, flagged needs_human_review=True. The learner always
     gets a recommendation; a never-passing one is surfaced for review, never dropped.

Failure-First Design:
  - Failure modes: judge error (propagated by caller as non-blocking in shadow,
    caught in enforce), empty candidate pool, no replacements left, no weak skills
    flagged, regeneration that cannot change the set.
  - Retry strategy: bounded by max_attempts (no unbounded loop); each retry makes a
    strictly different candidate set or stops.
  - Recovery path: graceful degradation to the best attempt + human-review flag.
  - User-visible behavior: always a recommendation; needs_human_review drives a UI
    badge / review queue.

Contract:
    gated_recommendation(jd_text, li_text, candidate_pool, *, k=None,
                         max_attempts=3, top_n=5) -> GateOutcome
"""
from __future__ import annotations

import logging
from typing import Awaitable, Callable, TypedDict

from app.services.recommendation_judge import evaluate_recommendation_stable, gate_decision

logger = logging.getLogger(__name__)

# Indirection so tests can inject a fake judge without monkeypatching the import.
JudgeFn = Callable[..., Awaitable[dict]]


class GateOutcome(TypedDict):
    skills: list[dict]            # the final recommended skill dicts
    decision: dict               # gate_decision() of the final/best attempt
    attempts: list[dict]         # trail: [{attempt, skill_ids, verdict, composite}]
    regenerated: bool            # True if more than one attempt was made
    needs_human_review: bool     # True unless the final verdict is a clean ACCEPT
    exhausted: bool              # True if the attempt budget was spent without ACCEPT


def _ids(skills: list[dict]) -> list[str]:
    return [s.get("skill_id") for s in skills]


def _regenerate(current: list[dict], pool: list[dict], used: set,
                weak_ids: set) -> list[dict] | None:
    """Build a strictly-different next candidate set by replacing weak skills with
    the next unused pool candidates. Returns None if no change is possible."""
    replacements = [s for s in pool if s.get("skill_id") not in used]
    if not replacements:
        return None
    ri = 0
    new: list[dict] = []
    for s in current:
        if s.get("skill_id") in weak_ids and ri < len(replacements):
            rep = replacements[ri]
            ri += 1
            used.add(rep.get("skill_id"))
            new.append(rep)
        else:
            new.append(s)
    # Nothing was flagged weak (or none matched): swap the lowest-ranked skill so
    # the loop still makes progress instead of re-judging the identical set.
    if ri == 0:
        rep = replacements[0]
        used.add(rep.get("skill_id"))
        new = current[:-1] + [rep] if current else [rep]
    if _ids(new) == _ids(current):
        return None
    return new


async def gated_recommendation(jd_text: str, li_text: str, candidate_pool: list[dict],
                               *, k: int | None = None, max_attempts: int = 3,
                               top_n: int = 5,
                               judge_fn: JudgeFn | None = None) -> GateOutcome:
    """Judge -> regenerate -> re-judge with bounded retries and graceful degradation."""
    judge = judge_fn or evaluate_recommendation_stable
    pool = [s for s in (candidate_pool or []) if s.get("skill_id")]
    if not pool:
        return GateOutcome(skills=[], decision={"verdict": "REJECT", "action": "regenerate",
                                                "pass": False, "composite": 0.0,
                                                "gate_failures": ["empty_pool"]},
                           attempts=[], regenerated=False, needs_human_review=True,
                           exhausted=True)

    current = pool[:top_n]
    used = set(_ids(current))
    attempts: list[dict] = []
    best: tuple[float, list[dict], dict] | None = None  # (composite, skills, result)

    for attempt in range(1, max(1, max_attempts) + 1):
        result = await judge(jd_text=jd_text, li_text=li_text, skills=current, k=k)
        decision = gate_decision(result)
        attempts.append({"attempt": attempt, "skill_ids": _ids(current),
                         "verdict": decision["verdict"], "composite": decision["composite"]})
        if best is None or decision["composite"] > best[0]:
            best = (decision["composite"], list(current), result)

        if decision["verdict"] != "REJECT":
            return GateOutcome(
                skills=current, decision=decision, attempts=attempts,
                regenerated=attempt > 1,
                needs_human_review=decision["verdict"] != "ACCEPT",
                exhausted=False,
            )

        weak = set(result.get("weak_skill_ids") or [])
        nxt = _regenerate(current, pool, used, weak)
        if nxt is None:
            logger.info("Gate regeneration exhausted candidate pool at attempt %d", attempt)
            break
        current = nxt

    # Budget spent without an ACCEPT/REVIEW -> degrade to the best attempt.
    _composite, best_skills, best_result = best  # best is set after >=1 attempt
    return GateOutcome(
        skills=best_skills, decision=gate_decision(best_result), attempts=attempts,
        regenerated=len(attempts) > 1, needs_human_review=True, exhausted=True,
    )
