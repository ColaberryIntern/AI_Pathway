"""Tests for the shadow-verdict summary parser (pure summarize())."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from shadow_verdict_summary import summarize  # noqa: E402

_LINES = [
    'INFO Judge gate verdict (shadow): verdict=ACCEPT regenerated=False needs_review=False exhausted=False attempts=[...]',
    'INFO Judge gate verdict (shadow): verdict=ACCEPT_WITH_REVIEW regenerated=True needs_review=True exhausted=False attempts=[...]',
    'INFO Judge gate verdict (shadow): verdict=REJECT regenerated=True needs_review=True exhausted=True attempts=[...]',
    'INFO some unrelated log line that should be ignored',
    '{"event": "http_request", "status": "success"}',
]


def test_happy_counts_and_rates():
    s = summarize(_LINES)
    assert s["total"] == 3
    assert s["verdicts"] == {"ACCEPT": 1, "ACCEPT_WITH_REVIEW": 1, "REJECT": 1}
    assert s["accept_rate"] == round(1 / 3, 4)
    assert s["needs_review_rate"] == round(2 / 3, 4)
    assert s["regenerated_count"] == 2
    assert s["exhausted_count"] == 1


def test_boundary_empty_input():
    s = summarize([])
    assert s["total"] == 0 and s["verdicts"] == {} and s["accept_rate"] == 0.0


def test_failure_ignores_malformed_lines():
    s = summarize(["Judge gate verdict (shadow): no verdict token here",
                   "totally unrelated"])
    assert s["total"] == 0  # marker without a parseable verdict is skipped


def test_idempotent():
    assert summarize(_LINES) == summarize(_LINES)
