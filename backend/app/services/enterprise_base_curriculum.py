"""Enterprise Base Curriculum (MVP).

Jun 23 weekly sync (item D, the B2B angle): an enterprise wants everyone to know
a BASE set of skills; personalized pathways are then layered on top so every
served path includes those base skills. Luda's MVP framing: "maybe all we need
in MVP is a user interface that we could then change later on."

MVP scope (deliberately small, reversible, no schema migration):
  - ONE global base set (per-tenant is deferred with multi-tenancy, which is
    greenfield). Stored as a JSON file in app/data, written atomically.
  - The default is an EMPTY base list, so `merge_base_into_planned` is a no-op
    and existing path generation is byte-for-byte unchanged until an admin
    actually defines a base curriculum.

The pure `merge_base_into_planned` function (no I/O) is the part wired into the
path generator and is unit-tested in isolation.
"""
from __future__ import annotations

import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable


_DATA_PATH = Path(__file__).parent.parent / "data" / "enterprise_base_curriculum.json"


class EnterpriseBaseCurriculumService:
    """Read/write the global enterprise base curriculum JSON store."""

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = Path(data_path) if data_path else _DATA_PATH

    def _read(self) -> dict:
        if not self.data_path.exists():
            return {"skill_ids": [], "label": "", "updated_at": None}
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("skill_ids", [])
        data.setdefault("label", "")
        data.setdefault("updated_at", None)
        return data

    def get(self) -> dict:
        return self._read()

    def get_skill_ids(self) -> list[str]:
        return list(self._read().get("skill_ids", []))

    def update(self, skill_ids: list[str], label: str = "", updated_at: str | None = None) -> dict:
        """Persist the base curriculum. De-dupes while preserving order.
        Idempotent: writing the same list twice yields the same file.
        Atomic: write to a temp file then os.replace."""
        deduped: list[str] = []
        seen: set[str] = set()
        for sid in skill_ids:
            if sid not in seen:
                seen.add(sid)
                deduped.append(sid)
        payload = {"skill_ids": deduped, "label": label, "updated_at": updated_at}
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.data_path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp, self.data_path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        return payload


@lru_cache
def get_base_curriculum_service() -> EnterpriseBaseCurriculumService:
    return EnterpriseBaseCurriculumService()


def merge_base_into_planned(
    planned: list[dict[str, Any]],
    base_skill_ids: list[str],
    get_skill: Callable[[str], dict | None],
    expanded_a: dict[str, int] | None = None,
    max_chapters: int = 5,
) -> list[dict[str, Any]]:
    """Prepend enterprise base skills to the planned chapter-skill list.

    Pure function (no I/O). Rules:
      - Empty base list -> return `planned` unchanged (the MVP default no-op).
      - Skip base skills already in `planned` (no duplicate chapters).
      - Skip base skills the learner has already mastered
        (current_level >= the skill's level) - no point teaching them.
      - Skip base skill_ids the ontology does not know.
      - Base skills come first (foundation), then the rubric-ranked skills,
        trimmed to `max_chapters`.
    """
    if not base_skill_ids:
        return planned
    expanded_a = expanded_a or {}
    planned_ids = {g.get("skill_id") for g in planned}
    base_dicts: list[dict[str, Any]] = []
    base_ids_added: set[str] = set()
    for sid in base_skill_ids:
        if sid in planned_ids or sid in base_ids_added:
            continue
        sk = get_skill(sid)
        if not sk:
            continue
        skill_level = sk.get("level", 1)
        current = expanded_a.get(sid, 0)
        if current >= skill_level:
            continue
        base_dicts.append({
            "skill_id": sid,
            "skill_name": sk.get("name", sid),
            "domain": sk.get("domain", ""),
            "skill_level": skill_level,
            "prerequisites": sk.get("prerequisites", []),
            "current_level": current,
            "is_base_curriculum": True,
        })
        base_ids_added.add(sid)
    merged = base_dicts + [g for g in planned if g.get("skill_id") not in base_ids_added]
    return merged[:max_chapters]
