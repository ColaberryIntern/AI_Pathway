# Persona corpus (regression contract)

_Every persona Luda has shared, with verbatim customer_quote, expected_top5_includes, forbidden_in_top5, and rationale. The Customer Voice agent grounds every finding against the customer_quote field._

Source file in the repo: `03/persona_corpus.py` (numeric prefix added for NotebookLM upload order).

```python
"""Test corpus of every persona Luda has shared.

Each entry codifies the expected behaviour of the skill-selection engine
for that persona. The corpus is the regression contract: every engine
change runs against every persona and any drift from the expected set
blocks the change (or requires explicit override + customer sign-off).

Entries are organized so the multi-agent QA team can reason about them:
  - id:               stable identifier for screenshots and logs
  - profile_id:       production profile UUID (None if not yet created)
  - role:             target role text the JD parser sees
  - source:           where the expected behaviour came from (email date + sender)
  - expected_top5_includes:   skill IDs that MUST appear in the top 5
  - expected_top10_includes:  skill IDs that MUST appear in the top 10
  - forbidden_in_top5:        skill IDs that MUST NOT appear in the top 5
  - rationale:        short note explaining why these expectations exist
  - customer_quote:   verbatim line from the originating email so the
                      Customer Voice Reasoner agent can ground its
                      reasoning in actual customer language

Used by:
  - backend/scripts/verify_profile_e2e.py  (preflight gate per persona)
  - the future multi-agent QA team's Regression Guardian agent

When Luda shares a new persona, add a new entry here BEFORE shipping any
engine change for that persona.
"""
from __future__ import annotations

PERSONAS: list[dict] = [
    {
        "id": "brittany_white",
        "profile_id": "4d1a84b9-16b8-4a35-9880-c04b555db51e",
        "role": "Sr. AI Product Marketing Manager",
        "vertical": None,  # cross-functional senior role, not a vertical
        "learner_technical_background": "non-technical with strong AI tool fluency",
        "source": "Luda email 2026-05-15 'Rerun of Brittany White case' + March 18 manual Claude analysis",
        "expected_top5_includes": [
            "SK.COM.001",  # Explaining AI to non-technical audiences - #1 for AI PMM
            "SK.PRD.022",  # ROI Measurement for AI - enterprise sales requirement
            "SK.PRD.001",  # AI Use Case Identification - core PMM raw material
            "SK.PRD.021",  # Stakeholder Management - senior cross-functional role
            "SK.FND.002",  # Capabilities vs Limitations - credibility skill
        ],
        "expected_top10_includes": [
            "SK.GOV.001",  # AI risk framing / governance for regulated industries
            "SK.PRD.020",  # AI Enablement & Training Strategy
            "SK.LRN.001",  # Keeping Up with AI Developments
        ],
        "forbidden_in_top5": [
            "SK.PRM.003",   # Prompt debugging - too tactical for a Sr PMM
            "SK.PRM.020",   # Draft-critique-revise - learner skill, not role-essence
        ],
        "expected_develop_count": 2,  # Luda's manual analysis: only 2 real gaps
        "expected_develop_ids": ["SK.GOV.001", "SK.FND.002"],
        "rationale": "Cross-functional senior AI marketing role. Role-essence is "
                     "communication + product + governance, not prompting tooling. "
                     "Brittany is well-matched already; only 2 real gaps.",
        "customer_quote": "At the end of the day, there are only 2 skills that are "
                          "relevant for her to prep for this role. In essence, she is "
                          "close to being a good fit for this role.",
    },
    {
        "id": "jennifer_c_lk_may9",
        "profile_id": "a2e05583-52fb-407e-adea-821a2522e9a7",
        "role": "AI Content Editor",
        "vertical": None,
        "learner_technical_background": "content / editorial",
        "source": "Luda email 2026-05-12 'AI Pathway Demo with Jennifer C'",
        # Jennifer got positive feedback from Luda - no specific top5
        # complaints. The corpus only asserts top10 expectations because
        # any reasonable content-editor-relevant set in top 5 is fine.
        "expected_top5_includes": [],
        "expected_top10_includes": [
            "SK.PRM.003",   # Prompt debugging - core content editor skill
            "SK.CTIC.006",  # Recognizing AI-generated content
            "SK.CTIC.004",  # Understanding bias in content
            "SK.GOV.022",   # AI-generated content disclosure - new, content-facing
        ],
        "forbidden_in_top5": [],
        "expected_develop_count": None,  # not specified in customer feedback
        "rationale": "Content-editor role; prompting + content-criticality skills "
                     "are appropriate. Jennifer got positive feedback so the existing "
                     "selection works. Top 5 should be content-editor-relevant; "
                     "no single-skill must in top 5.",
        "customer_quote": "I demoed the tool to Jennifer C today. Positive feedback!",
    },
    {
        "id": "dorothy_fatunmbi",
        "profile_id": "9b692fe9-1f13-4ddf-8c8c-27376e96a6d0",
        "role": "Learning and Development Specialist",
        "vertical": "L&D",
        "learner_technical_background": "L&D / instructional design, non-technical",
        "source": "Luda email 2026-05-16 'Dorothy F walkthrough feedback'",
        "expected_top5_includes": [
            "SK.DOM.EDU.001",  # Education: Learning design with AI - mandatory domain skill
            "SK.COM.005",      # Cross-functional AI collaboration
            "SK.COM.003",      # Facilitating AI workshops
        ],
        "expected_top10_includes": [
            "SK.PRM.000",  # Foundational PRM for non-tech L&D
        ],
        "forbidden_in_top5": [
            "SK.PRM.020",  # Advanced PRM not appropriate for L0-L2 L&D specialist
        ],
        "expected_develop_count": None,
        "rationale": "L&D vertical role. Domain skill (SK.DOM.EDU.001) is mandatory. "
                     "Luda confirmed the existing selection 'made sense' for Dorothy, "
                     "so this is a positive-control case to make sure we do not regress.",
        "customer_quote": "Good news - the skills generated by the tool made sense!",
    },
    {
        "id": "halyna_mushak",
        "profile_id": "625c57e8-a727-47e2-85e5-f5fe015e793c",
        "role": "Director, Global Campaigns",
        "vertical": "marketing",
        "learner_technical_background": "non-technical marketing leader, 13 years experience",
        "source": "Luda email 2026-05-19 'Halyna Mushak use case' + Luda's Claude chat",
        "expected_top5_includes": [
            "SK.DOM.MKT.001",  # Marketing: Content generation ethics - mandatory domain skill
            "SK.COM.005",      # Cross-functional AI collaboration
        ],
        "expected_top10_includes": [
            "SK.PRM.000",   # Foundational PRM for non-tech learner
            "SK.PRM.001",   # Foundational PRM
            "SK.COM.004",   # Managing AI expectations - senior cross-functional
            "SK.RSN.003",   # Deep research agents - NEW v2.0, marketing-relevant
            "SK.GOV.022",   # AI-generated content disclosure - NEW v2.0, content-facing
            "SK.GOV.010",   # AI regulations landscape (EU AI Act) - global role
        ],
        "forbidden_in_top5": [
            "SK.PRM.020",  # Advanced PRM not appropriate for L1 non-tech learner
            "SK.PRM.003",  # Same
        ],
        "expected_develop_count": None,
        "rationale": "Marketing vertical + non-technical senior role + global scope. "
                     "Domain skill (SK.DOM.MKT.001) mandatory; foundational PRM over "
                     "advanced; NEW v2.0 skills (RSN.003, GOV.022, GOV.010) prefered "
                     "over older generic ones.",
        "customer_quote": "the tool pulled our rather rudimentary set of skills for "
                          "her level. I ran this set by Claude. It recommended a set "
                          "of skills that was more in depth.",
    },
    # Srushti Madhure not yet in the production DB; entry added when she is.
]


def get_persona(persona_id: str) -> dict | None:
    """Look up a persona entry by id."""
    for p in PERSONAS:
        if p["id"] == persona_id:
            return p
    return None


def evaluate_skill_set(persona: dict, actual_top10_skill_ids: list[str]) -> dict:
    """Compare an actual skill-set output against a persona's expectations.

    Returns a structured verdict the Demo-Readiness Gate agent will use:
      {
        "passed": bool,
        "top5_hits": [...],   # IDs from expected_top5_includes that appeared
        "top5_misses": [...], # IDs from expected_top5_includes that did NOT
        "forbidden_hits": [...],  # forbidden IDs that wrongly appeared in top5
        "top10_hits": [...],
        "top10_misses": [...],
      }
    """
    top5 = actual_top10_skill_ids[:5]
    top10 = actual_top10_skill_ids[:10]
    exp5 = persona.get("expected_top5_includes") or []
    exp10 = persona.get("expected_top10_includes") or []
    forb5 = persona.get("forbidden_in_top5") or []

    top5_hits = [s for s in exp5 if s in top5]
    top5_misses = [s for s in exp5 if s not in top5]
    top10_hits = [s for s in exp10 if s in top10]
    top10_misses = [s for s in exp10 if s not in top10]
    forbidden_hits = [s for s in forb5 if s in top5]

    # Pass = all expected_top5 are in top5 AND no forbidden in top5
    passed = (not top5_misses) and (not forbidden_hits)

    return {
        "passed": passed,
        "top5_hits": top5_hits,
        "top5_misses": top5_misses,
        "top10_hits": top10_hits,
        "top10_misses": top10_misses,
        "forbidden_hits": forbidden_hits,
    }


if __name__ == "__main__":
    # Quick listing
    for p in PERSONAS:
        print(f"{p['id']}: {p['role']}  (vertical={p.get('vertical')})")
        print(f"  expected top5: {p['expected_top5_includes']}")
        print(f"  expected top10 also: {p.get('expected_top10_includes') or '[]'}")
        print(f"  forbidden in top5: {p.get('forbidden_in_top5') or '[]'}")
        print(f"  source: {p['source']}")
        print()

```
