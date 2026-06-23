"""Tests for the ontology description-wiring core (pure wire_descriptions)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from wire_skill_descriptions import wire_descriptions  # noqa: E402


def _onto(*ids):
    return {"version": "x", "skills": [{"id": i, "name": i, "rubric_by_level": []} for i in ids]}


# --- happy path ---

def test_wires_matching_descriptions():
    onto = _onto("SK.A", "SK.B")
    out, rep = wire_descriptions(onto, {"SK.A": "desc a", "SK.B": "desc b"})
    assert rep["matched"] == 2 and rep["missing_description"] == [] and rep["orphan_descriptions"] == []
    got = {s["id"]: s.get("description") for s in out["skills"]}
    assert got == {"SK.A": "desc a", "SK.B": "desc b"}


# --- boundary: a skill with no description is reported, not failed ---

def test_missing_description_reported():
    out, rep = wire_descriptions(_onto("SK.A", "SK.B"), {"SK.A": "only a"})
    assert rep["matched"] == 1 and rep["missing_description"] == ["SK.B"]


# --- failure-ish: a description with no matching skill is an orphan, ignored ---

def test_orphan_description_reported_and_ignored():
    out, rep = wire_descriptions(_onto("SK.A"), {"SK.A": "a", "SK.GHOST": "x"})
    assert rep["orphan_descriptions"] == ["SK.GHOST"]
    assert all(s["id"] != "SK.GHOST" for s in out["skills"])  # not added


# --- does not mutate the input ontology ---

def test_input_not_mutated():
    onto = _onto("SK.A")
    wire_descriptions(onto, {"SK.A": "a"})
    assert "description" not in onto["skills"][0]  # original untouched


# --- idempotency ---

def test_idempotent():
    onto = _onto("SK.A", "SK.B")
    descs = {"SK.A": "a", "SK.B": "b"}
    once, _ = wire_descriptions(onto, descs)
    twice, _ = wire_descriptions(once, descs)
    assert once == twice


# --- empty boundary ---

def test_empty_descriptions():
    out, rep = wire_descriptions(_onto("SK.A"), {})
    assert rep["matched"] == 0 and rep["missing_description"] == ["SK.A"]
