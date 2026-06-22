"""Shadow-gate verdict summary (Trust Before Intelligence - Permitted / enforce prep).

Rolls up the judge gate's shadow-mode verdicts from the backend logs so the
enforce-flip decision is data-driven. The gate logs one line per live analysis:
  "Judge gate verdict (shadow): verdict=... regenerated=... needs_review=... exhausted=..."

Usage (pipe the logs in):
  ssh root@PROD "cd /opt/ai-pathway && docker compose logs --since 168h backend" \
    | py -3.12 backend/scripts/shadow_verdict_summary.py
or locally:  docker compose logs backend | py -3.12 backend/scripts/shadow_verdict_summary.py

Read-only. summarize() is pure + unit-tested.
"""
import re
import sys
from collections import Counter

_MARKER = "Judge gate verdict (shadow)"
_VERDICT = re.compile(r"verdict=(\w+)")
_FLAG = {f: re.compile(rf"{f}=(True|False)") for f in ("regenerated", "needs_review", "exhausted")}


def summarize(lines) -> dict:
    """Aggregate shadow verdict log lines into counts + rates."""
    verdicts: Counter = Counter()
    flags = {f: 0 for f in _FLAG}
    total = 0
    for line in lines:
        if _MARKER not in line:
            continue
        m = _VERDICT.search(line)
        if not m:
            continue
        total += 1
        verdicts[m.group(1)] += 1
        for f, rx in _FLAG.items():
            fm = rx.search(line)
            if fm and fm.group(1) == "True":
                flags[f] += 1

    def rate(n):
        return round(n / total, 4) if total else 0.0

    return {
        "total": total,
        "verdicts": dict(verdicts),
        "accept_rate": rate(verdicts.get("ACCEPT", 0)),
        "review_rate": rate(verdicts.get("ACCEPT_WITH_REVIEW", 0)),
        "reject_rate": rate(verdicts.get("REJECT", 0)),
        "needs_review_rate": rate(flags["needs_review"]),
        "regenerated_count": flags["regenerated"],
        "exhausted_count": flags["exhausted"],
    }


def _print(s: dict) -> None:
    print("=== Shadow gate verdict summary ===")
    if not s["total"]:
        print("No shadow verdicts found in the input (no live analysis traffic yet, "
              "or the gate is off). Pipe in more log history with a wider --since.")
        return
    print(f"total verdicts: {s['total']}")
    print(f"  ACCEPT             {s['verdicts'].get('ACCEPT', 0):>4}  ({s['accept_rate']:.0%})")
    print(f"  ACCEPT_WITH_REVIEW {s['verdicts'].get('ACCEPT_WITH_REVIEW', 0):>4}  ({s['review_rate']:.0%})")
    print(f"  REJECT             {s['verdicts'].get('REJECT', 0):>4}  ({s['reject_rate']:.0%})")
    print(f"needs_human_review: {s['needs_review_rate']:.0%} | regenerated: "
          f"{s['regenerated_count']} | exhausted: {s['exhausted_count']}")
    print("\nEnforce-readiness read: a low + stable needs_review rate over a meaningful "
          "sample means flipping enforce will rarely surprise a learner. A high reject/"
          "exhausted rate means fix the recommender (upstream) before enforcing.")


if __name__ == "__main__":
    _print(summarize(sys.stdin))
