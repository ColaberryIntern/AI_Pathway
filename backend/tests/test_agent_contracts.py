"""Tests for the agent boundary contracts (Contract Enforcement Layer).

The contracts are importable + asserted here. Covers happy, failure (malformed
declared fields rejected), boundary (defaults), and idempotency, plus the
non-breaking property that unknown keys pass through.
"""
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.agents.contracts import (  # noqa: E402
    OrchestratorInput, ContentCuratorInput, ContentCuratorOutput, ChapterResources,
)


# --- OrchestratorInput ---

def test_orchestrator_happy():
    m = OrchestratorInput.model_validate({
        "profile": {"name": "X"}, "jd_text": "jd", "target_role": "Engineer",
        "skip_assessment": False, "self_assessed_skills": {"SK.A": 3},
        "selected_skill_ids": ["SK.A"], "include_resources": False})
    assert m.profile == {"name": "X"} and m.skip_assessment is False
    assert m.selected_skill_ids == ["SK.A"]


def test_orchestrator_boundary_defaults():
    m = OrchestratorInput.model_validate({})
    assert m.profile == {} and m.jd_text == "" and m.target_role == ""
    assert m.skip_assessment is True and m.include_resources is True
    assert m.self_assessed_skills is None and m.selected_skill_ids is None


def test_orchestrator_extra_keys_pass_through():
    dumped = OrchestratorInput.model_validate({"profile": {}, "custom_flag": "v"}).model_dump()
    assert dumped["custom_flag"] == "v"  # non-breaking: unknown keys preserved


def test_orchestrator_rejects_malformed_fields():
    with pytest.raises(ValidationError):
        OrchestratorInput.model_validate({"profile": 123})           # not an object
    with pytest.raises(ValidationError):
        OrchestratorInput.model_validate({"selected_skill_ids": "SK.A"})  # not a list
    with pytest.raises(ValidationError):
        OrchestratorInput.model_validate({"jd_text": 123})           # not a string


def test_orchestrator_idempotent_dump():
    payload = {"profile": {"a": 1}, "jd_text": "x", "extra": "k"}
    a = OrchestratorInput.model_validate(payload).model_dump()
    b = OrchestratorInput.model_validate(payload).model_dump()
    assert a == b


# --- ContentCuratorInput ---

def test_curator_input_happy_and_defaults():
    m = ContentCuratorInput.model_validate({"chapters": [{"skill_id": "SK.A"}], "industry": "Tech"})
    assert m.chapters[0]["skill_id"] == "SK.A" and m.industry == "Tech"
    empty = ContentCuratorInput.model_validate({})
    assert empty.chapters == [] and empty.industry == ""


def test_curator_input_rejects_bad_chapters():
    with pytest.raises(ValidationError):
        ContentCuratorInput.model_validate({"chapters": "not-a-list"})


# --- ContentCuratorOutput ---

def test_curator_output_validates_real_shape():
    result = {"chapter_resources": [
        {"chapter_number": 1, "skill_id": "SK.A",
         "resources": [{"title": "t", "url": "u", "type": "video"}]}],
        "duration_ms": 42}
    out = ContentCuratorOutput.model_validate(result).model_dump()
    assert out["duration_ms"] == 42
    assert out["chapter_resources"][0]["skill_id"] == "SK.A"
    assert out["chapter_resources"][0]["resources"][0]["title"] == "t"


def test_chapter_resources_boundary_defaults():
    cr = ChapterResources.model_validate({})
    assert cr.chapter_number is None and cr.skill_id is None and cr.resources == []


def test_curator_output_rejects_bad_resources_type():
    with pytest.raises(ValidationError):
        ContentCuratorOutput.model_validate({"chapter_resources": [{"resources": "nope"}]})
