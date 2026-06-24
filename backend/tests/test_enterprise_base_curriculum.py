"""Tests for the Enterprise Base Curriculum MVP.

Four mandatory types (happy/failure/boundary/idempotency) on the pure merge
function and the JSON store. No LLM, no DB.
"""
from pathlib import Path

from app.services.enterprise_base_curriculum import (
    EnterpriseBaseCurriculumService,
    merge_base_into_planned,
)

# Fake ontology lookup
_ONT = {
    "SK.BASE1": {"name": "Base One", "domain": "D.FND", "level": 2},
    "SK.BASE2": {"name": "Base Two", "domain": "D.FND", "level": 3},
    "SK.P1": {"name": "Personalized 1", "domain": "D.PRM", "level": 2},
}


def _get_skill(sid):
    return _ONT.get(sid)


def _planned(*ids):
    return [{"skill_id": i, "skill_name": _ONT.get(i, {}).get("name", i),
             "domain": "D.PRM", "skill_level": 2} for i in ids]


# --- merge: happy path --------------------------------------------------------

def test_base_skills_prepended():
    planned = _planned("SK.P1")
    merged = merge_base_into_planned(planned, ["SK.BASE1"], _get_skill, {}, 5)
    assert [m["skill_id"] for m in merged] == ["SK.BASE1", "SK.P1"]
    assert merged[0]["is_base_curriculum"] is True


# --- merge: empty base list is a no-op (MVP default) --------------------------

def test_empty_base_is_noop():
    planned = _planned("SK.P1")
    merged = merge_base_into_planned(planned, [], _get_skill, {}, 5)
    assert merged == planned


# --- merge: failure/boundary --------------------------------------------------

def test_unknown_base_id_skipped():
    planned = _planned("SK.P1")
    merged = merge_base_into_planned(planned, ["SK.NOPE"], _get_skill, {}, 5)
    assert [m["skill_id"] for m in merged] == ["SK.P1"]


def test_base_already_in_planned_not_duplicated():
    planned = _planned("SK.BASE1", "SK.P1")
    merged = merge_base_into_planned(planned, ["SK.BASE1"], _get_skill, {}, 5)
    ids = [m["skill_id"] for m in merged]
    assert ids.count("SK.BASE1") == 1


def test_mastered_base_skill_skipped():
    # learner already at/above the base skill's level -> do not teach it
    planned = _planned("SK.P1")
    merged = merge_base_into_planned(planned, ["SK.BASE1"], _get_skill, {"SK.BASE1": 2}, 5)
    assert [m["skill_id"] for m in merged] == ["SK.P1"]


def test_trim_to_max_chapters():
    planned = _planned("SK.P1")
    merged = merge_base_into_planned(planned, ["SK.BASE1", "SK.BASE2"], _get_skill, {}, 2)
    assert len(merged) == 2
    assert [m["skill_id"] for m in merged] == ["SK.BASE1", "SK.BASE2"]  # base wins slots


def test_duplicate_base_ids_collapsed():
    merged = merge_base_into_planned(_planned("SK.P1"), ["SK.BASE1", "SK.BASE1"],
                                     _get_skill, {}, 5)
    assert [m["skill_id"] for m in merged].count("SK.BASE1") == 1


# --- merge: idempotency -------------------------------------------------------

def test_merge_idempotent():
    planned = _planned("SK.P1")
    a = merge_base_into_planned(planned, ["SK.BASE1", "SK.BASE2"], _get_skill, {}, 5)
    b = merge_base_into_planned(planned, ["SK.BASE1", "SK.BASE2"], _get_skill, {}, 5)
    assert [m["skill_id"] for m in a] == [m["skill_id"] for m in b]


# --- store: roundtrip / dedupe / default / idempotency ------------------------

def test_store_default_empty(tmp_path):
    svc = EnterpriseBaseCurriculumService(tmp_path / "ebc.json")
    assert svc.get_skill_ids() == []
    assert svc.get()["skill_ids"] == []


def test_store_update_roundtrip(tmp_path):
    p = tmp_path / "ebc.json"
    svc = EnterpriseBaseCurriculumService(p)
    svc.update(["SK.BASE1", "SK.BASE2"], "Core AI", "2026-06-23T00:00:00Z")
    assert Path(p).exists()
    again = EnterpriseBaseCurriculumService(p)  # fresh instance reads from disk
    assert again.get_skill_ids() == ["SK.BASE1", "SK.BASE2"]
    assert again.get()["label"] == "Core AI"


def test_store_dedupes_preserving_order(tmp_path):
    svc = EnterpriseBaseCurriculumService(tmp_path / "ebc.json")
    saved = svc.update(["SK.BASE1", "SK.BASE2", "SK.BASE1"])
    assert saved["skill_ids"] == ["SK.BASE1", "SK.BASE2"]


def test_store_update_idempotent(tmp_path):
    p = tmp_path / "ebc.json"
    svc = EnterpriseBaseCurriculumService(p)
    first = svc.update(["SK.BASE1"], "L", "2026-06-23T00:00:00Z")
    second = svc.update(["SK.BASE1"], "L", "2026-06-23T00:00:00Z")
    assert first == second
