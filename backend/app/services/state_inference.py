"""State-A inference — expand a sparse current-skill profile.

When a learner's state_a only lists a handful of explicitly known
skills, downstream gap computation sees most target skills at
level 0 ("Unaware").  This inflates deltas uniformly and washes
out meaningful priority differences.

``expand_state_a`` addresses this by inferring prerequisite levels:
if a learner demonstrates level 3 in SK.PRM.003, they almost
certainly have at least level 2 in SK.PRM.001 (its prerequisite).
This makes the profile denser without overwriting any explicit
assessments.

Confidence weighting
--------------------
State_a values may be plain ``int`` levels **or** dicts with a
``confidence`` multiplier and an optional ``last_validated_at``
timestamp::

    {
        "SK.PRM.003": 3,                              # plain int
        "SK.FND.001": {"level": 2, "confidence": 0.7} # weighted
        "SK.PRQ.010": {                                # weighted + decay
            "level": 3,
            "confidence": 0.9,
            "last_validated_at": "2025-08-15T00:00:00"
        }
    }

When confidence is present, the effective level used for gap
computation is ``floor(level * effective_confidence)``.

Time-based decay
----------------
When ``last_validated_at`` is present (ISO 8601 timestamp), a
decay factor is computed::

    months_since = (now - last_validated_at) / 30 days
    decay_factor = max(0.4, 1.0 - 0.05 * months_since)
    effective_confidence = confidence * decay_factor

The 0.4 floor on decay_factor prevents knowledge collapse — even
after years without re-validation, a skill's effective confidence
can never drop below 40% of its original confidence.

Rules
-----
1. Normalize mixed input to ``{skill_id: effective_level}``.
2. Walk every skill already in state_a.
3. For each of its ontology prerequisites, if the prerequisite is
   **not** already in state_a, infer a level.
4. Inferred level = ``max(1, effective_level - 1)``.
5. Never exceed the ontology tier for the prerequisite skill.
6. Never overwrite an explicitly defined level.
7. Apply transitively — a newly inferred skill can itself
   trigger inference for *its* prerequisites, up to a bounded
   depth to prevent runaway chains.

All logic is deterministic; no LLM calls.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

_MAX_INFERENCE_DEPTH = 5  # Guard against circular/deep chains.
_DECAY_RATE = 0.05        # 5% per month
_DECAY_FLOOR = 0.4        # Minimum decay factor (never below 40%)
_DAYS_PER_MONTH = 30.0


def _compute_decay_factor(
    last_validated_at: str,
    now: datetime | None = None,
) -> float:
    """Compute time-based decay factor from an ISO 8601 timestamp.

    Parameters
    ----------
    last_validated_at : str
        ISO 8601 timestamp of the last validation/assessment.
    now : datetime | None
        Override for the current time (for testing).  Defaults to
        ``datetime.now(timezone.utc)``.

    Returns
    -------
    float
        Decay factor in [_DECAY_FLOOR, 1.0].
    """
    if now is None:
        now = datetime.now(timezone.utc)

    try:
        validated = datetime.fromisoformat(last_validated_at)
        # Ensure timezone-aware comparison.
        if validated.tzinfo is None:
            validated = validated.replace(tzinfo=timezone.utc)
        delta_days = max(0.0, (now - validated).total_seconds() / 86400)
    except (ValueError, TypeError):
        return 1.0  # Unparseable timestamp — no decay.

    months_since = delta_days / _DAYS_PER_MONTH
    return max(_DECAY_FLOOR, 1.0 - _DECAY_RATE * months_since)


def _normalize_state_a(
    state_a: dict[str, int | dict],
    now: datetime | None = None,
) -> tuple[dict[str, int], bool, bool, float | None]:
    """Convert mixed int/dict state_a to flat ``{sid: effective_level}``.

    Parameters
    ----------
    state_a : dict[str, int | dict]
        Each value is either a plain ``int`` proficiency level, or a
        dict with keys:

        - ``level`` (int) — proficiency level (required if dict)
        - ``confidence`` (float, optional) — source confidence in
          (0.0, 1.0], default 1.0
        - ``last_validated_at`` (str, optional) — ISO 8601 timestamp
          of the last assessment/validation

    now : datetime | None
        Override for the current time (for testing).

    Returns
    -------
    (normalized, confidence_weighted, decay_applied, avg_decay_factor)
        *normalized* maps ``skill_id → effective_level``.
        *confidence_weighted* is True if any entry had a confidence.
        *decay_applied* is True if any entry had a last_validated_at.
        *avg_decay_factor* is the mean decay factor across decayed
        entries (None if no decay was applied).
    """
    normalized: dict[str, int] = {}
    confidence_weighted = False
    decay_applied = False
    decay_factors: list[float] = []

    for sid, value in state_a.items():
        if isinstance(value, dict):
            level = value.get("level", 0)
            confidence = value.get("confidence", 1.0)
            confidence = max(0.0, min(1.0, confidence))

            last_validated = value.get("last_validated_at")
            if last_validated is not None:
                decay_factor = _compute_decay_factor(last_validated, now)
                decay_applied = True
                decay_factors.append(decay_factor)
                effective_confidence = confidence * decay_factor
            else:
                effective_confidence = confidence

            effective_confidence = max(0.0, min(1.0, effective_confidence))
            normalized[sid] = math.floor(level * effective_confidence)
            confidence_weighted = True
        else:
            normalized[sid] = int(value)

    avg_decay_factor: float | None = None
    if decay_factors:
        avg_decay_factor = round(sum(decay_factors) / len(decay_factors), 3)

    return normalized, confidence_weighted, decay_applied, avg_decay_factor


def expand_state_a(
    state_a: dict[str, int | dict],
    ontology_service: Any,
    now: datetime | None = None,
) -> tuple[dict[str, int], int, bool, bool, float | None]:
    """Return an expanded copy of *state_a* with inferred prerequisites.

    Parameters
    ----------
    state_a : dict[str, int | dict]
        Learner's current profile.  Values may be plain ``int`` levels
        or dicts with ``level``, ``confidence``, and/or
        ``last_validated_at`` keys::

            {
                "SK.PRM.003": 3,
                "SK.FND.001": {"level": 2, "confidence": 0.7},
                "SK.PRQ.010": {
                    "level": 3,
                    "confidence": 0.9,
                    "last_validated_at": "2025-08-15T00:00:00",
                },
            }

    ontology_service : OntologyService
        Used to look up skill prerequisites and ontology tiers.
    now : datetime | None
        Override for the current time (for testing decay).

    Returns
    -------
    (expanded, inferred_count, confidence_weighted, decay_applied,
     avg_decay_factor)
        *expanded* maps ``skill_id → int`` (effective level).
        *inferred_count* is the number of skills added by inference.
        *confidence_weighted* is True if any entry had a confidence.
        *decay_applied* is True if any entry had a last_validated_at.
        *avg_decay_factor* is the mean decay factor (None if no decay).
    """
    # Step 1: Normalize mixed input to flat int levels.
    effective_a, confidence_weighted, decay_applied, avg_decay_factor = (
        _normalize_state_a(state_a, now)
    )

    # Work on a copy so the caller's dict is untouched.
    expanded: dict[str, int] = dict(effective_a)
    explicit_keys: frozenset[str] = frozenset(effective_a.keys())

    # BFS queue: (skill_id, level_of_parent_that_triggered_inference)
    queue: list[tuple[str, int]] = [
        (sid, level) for sid, level in effective_a.items()
    ]
    visited: set[str] = set(effective_a.keys())
    depth_map: dict[str, int] = {sid: 0 for sid in effective_a}

    while queue:
        current_sid, parent_level = queue.pop(0)
        current_depth = depth_map.get(current_sid, 0)

        if current_depth >= _MAX_INFERENCE_DEPTH:
            continue

        skill = ontology_service.get_skill(current_sid)
        if not skill:
            continue

        prereq_ids = skill.get("prerequisites", [])
        for prereq_id in prereq_ids:
            # Never overwrite an explicitly defined level.
            if prereq_id in explicit_keys:
                continue

            prereq_skill = ontology_service.get_skill(prereq_id)
            if not prereq_skill:
                continue

            # Inferred level: one below the skill that implied it,
            # but at least 1 (Aware) and at most the ontology tier.
            inferred_level = max(1, parent_level - 1)
            ontology_tier = prereq_skill["level"]
            inferred_level = min(inferred_level, ontology_tier)

            # If already inferred, keep the higher estimate.
            if prereq_id in expanded:
                if expanded[prereq_id] >= inferred_level:
                    continue
            expanded[prereq_id] = inferred_level

            # Continue inference from this newly inferred skill.
            if prereq_id not in visited:
                visited.add(prereq_id)
                depth_map[prereq_id] = current_depth + 1
                queue.append((prereq_id, inferred_level))

    inferred_count = len(expanded) - len(effective_a)
    return (
        expanded,
        inferred_count,
        confidence_weighted,
        decay_applied,
        avg_decay_factor,
    )
