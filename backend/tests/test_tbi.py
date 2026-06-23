"""Tests for the TBI status aggregation + dashboard render."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.tbi import build_tbi_status, render_dashboard_html  # noqa: E402


def test_build_status_shape():
    s = build_tbi_status()
    assert s["framework"] == "Trust Before Intelligence"
    inp = s["inpact"]
    assert inp["total"] == 27 and inp["pct"] == 75 and len(inp["dimensions"]) == 6
    assert len(s["layers"]) == 7
    g = s["goals"]
    # live governance signal reflects current config
    assert "gate_mode" in g["governance"] and "judge_model" in g["governance"]
    # live availability signal present (rag may be available or not depending on creds)
    assert "rag" in g["availability"] and "available" in g["availability"]["rag"]
    # recorded GOALS
    assert "tests_passing" in g["solid"] and "result" in g["lexicon"]


def test_dimensions_are_within_scale():  # boundary
    inp = build_tbi_status()["inpact"]
    maxp = inp["max_per"]
    assert all(0 <= d["score"] <= maxp for d in inp["dimensions"])
    assert sum(d["score"] for d in inp["dimensions"]) == inp["total"]


def test_render_html_contains_key_signals():
    html = render_dashboard_html(build_tbi_status())
    assert html.startswith("<!doctype html>")
    assert "Trust Before Intelligence" in html and "75%" in html
    for dim in ("Instant", "Natural", "Permitted", "Adaptive", "Contextual", "Transparent"):
        assert dim in html
    assert "7-layer architecture" in html and "Governance" in html


def test_recorded_signals_idempotent():
    a, b = build_tbi_status(), build_tbi_status()
    assert a["inpact"] == b["inpact"] and a["layers"] == b["layers"]
