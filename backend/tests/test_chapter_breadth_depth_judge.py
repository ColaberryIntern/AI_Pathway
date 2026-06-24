"""Tests for the Chapter Breadth + Depth judge deterministic core.

Covers the four mandatory test types (CLAUDE.md Test Strategy Framework):
happy path, failure path, boundary cases, idempotency. The deterministic core
(compose_score / structural_findings / findings_for_chapter) needs no LLM, so
these are fast pure-function tests.
"""
from app.qa_agents.chapter_breadth_depth_judge import (
    ALL_CRITERIA,
    ChapterScore,
    compose_score,
    findings_for_chapter,
    structural_findings,
)
from app.qa_agents.verdict import Severity


def _full_chapter(narrative_words: int = 80, n_cards: int = 4) -> dict:
    return {
        "meta": {"chapter_title": "X", "current_level": 1, "target_level": 3},
        "scenario": {"narrative": " ".join(["word"] * narrative_words),
                     "why_it_matters": "it matters"},
        "concepts": {"cards": [{"headline": f"c{i}", "body": "b" * 200}
                               for i in range(n_cards)]},
        "example_1": {"original_prompt": {}, "iterated_prompt": {}},
        "example_2": {"comparison": {"variants": [{"id": "A"}, {"id": "B"}]}},
        "agent_build": {"system_prompt_template": "p" * 200},
        "implementation_task": {"title": "t"},
    }


def _scores(value: int) -> dict:
    return {c: value for c in ALL_CRITERIA}


# --- HAPPY PATH ---------------------------------------------------------------

def test_all_fives_full_chapter_is_green():
    score = compose_score(_full_chapter(), _scores(5), chapter_number=1, skill_id="SK.X")
    assert score.color == "green"
    assert score.overall == 1.0
    assert score.breadth == 1.0 and score.depth == 1.0
    assert findings_for_chapter(score) == []


def test_solid_fours_is_green():
    score = compose_score(_full_chapter(), _scores(4), chapter_number=1, skill_id="SK.X")
    # norm(4) = 0.75 -> overall 0.75 >= 0.70, both dims >= 0.60
    assert score.color == "green"


# --- FAILURE PATH -------------------------------------------------------------

def test_all_ones_is_red():
    score = compose_score(_full_chapter(), _scores(1), chapter_number=2, skill_id="SK.Y")
    assert score.color == "red"
    assert score.overall == 0.0
    fs = findings_for_chapter(score)
    assert any(f.severity == Severity.ERROR for f in fs)


def test_missing_scenario_forces_red_even_with_perfect_scores():
    ch = _full_chapter()
    del ch["scenario"]
    score = compose_score(ch, _scores(5), chapter_number=3, skill_id="SK.Z")
    assert score.color == "red"  # critical structural floor overrides
    fs = findings_for_chapter(score)
    assert any(f.severity == Severity.ERROR and "scenario" in f.summary for f in fs)


def test_missing_concepts_forces_red():
    ch = _full_chapter()
    del ch["concepts"]
    score = compose_score(ch, _scores(5), chapter_number=4, skill_id="SK.Z")
    assert score.color == "red"


def test_empty_chapter_does_not_crash():
    score = compose_score({}, {}, chapter_number=0, skill_id="")
    assert score.color == "red"
    assert isinstance(findings_for_chapter(score), list)


# --- BOUNDARY CASES -----------------------------------------------------------

def test_straight_threes_fall_below_yellow_floor():
    # norm(3) = 0.5 -> overall 0.5 < 0.55 (OVERALL_YELLOW) -> red
    score = compose_score(_full_chapter(), _scores(3), chapter_number=1, skill_id="SK.X")
    assert score.overall == 0.5
    assert score.color == "red"


def test_yellow_band_accept_with_review():
    # Push overall into [0.55, 0.70): mostly 4s but weak breadth
    mixed = _scores(4)
    mixed["concept_coverage"] = 2  # drags breadth below GREEN gate
    score = compose_score(_full_chapter(), mixed, chapter_number=1, skill_id="SK.X")
    assert 0.55 <= score.overall < 0.70 or score.color == "yellow"
    assert score.color == "yellow"
    fs = findings_for_chapter(score)
    assert all(f.severity != Severity.ERROR for f in fs)


def test_thin_narrative_caps_green_to_yellow():
    ch = _full_chapter(narrative_words=10)  # below MIN_NARRATIVE_WORDS
    score = compose_score(ch, _scores(5), chapter_number=1, skill_id="SK.X")
    assert score.color == "yellow"
    assert any("thin" in v for v in score.structural_violations)


def test_narrow_cards_flagged():
    ch = _full_chapter(n_cards=2)  # below MIN_CONCEPT_CARDS
    score = compose_score(ch, _scores(5), chapter_number=1, skill_id="SK.X")
    assert score.color == "yellow"
    assert any("narrow" in v for v in score.structural_violations)


def test_out_of_range_scores_are_clamped():
    score = compose_score(_full_chapter(), _scores(99), chapter_number=1, skill_id="SK.X")
    assert score.overall == 1.0  # clamped to 5
    score_low = compose_score(_full_chapter(), _scores(-5), chapter_number=1, skill_id="SK.X")
    assert score_low.overall == 0.0  # clamped to 1


def test_missing_criteria_default_to_failing():
    # Only one criterion provided; the rest default to 1 (failing anchor)
    score = compose_score(_full_chapter(), {"concept_coverage": 5},
                          chapter_number=1, skill_id="SK.X")
    assert score.color == "red"
    assert score.criterion_scores["worked_example_rigor"] == 1


# --- IDEMPOTENCY --------------------------------------------------------------

def test_compose_score_idempotent():
    ch = _full_chapter()
    runs = [compose_score(ch, _scores(4), chapter_number=1, skill_id="SK.X")
            for _ in range(5)]
    first = runs[0]
    for r in runs:
        assert (r.breadth, r.depth, r.overall, r.color) == (
            first.breadth, first.depth, first.overall, first.color)


def test_structural_findings_idempotent():
    ch = _full_chapter(narrative_words=5, n_cards=1)
    runs = [structural_findings(ch) for _ in range(5)]
    assert all(r == runs[0] for r in runs)


def test_findings_idempotent():
    score = compose_score(_full_chapter(), _scores(2), chapter_number=1, skill_id="SK.X")
    runs = [[(f.severity, f.summary) for f in findings_for_chapter(score)]
            for _ in range(5)]
    assert all(r == runs[0] for r in runs)
