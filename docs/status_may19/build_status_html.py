"""Build a single self-contained HTML status report for Luda summarizing
P0-P3 fixes + the multi-agent QA team + the 4 persona verdicts.

Embeds screenshots from docs/preflight/ as base64 data URIs so the
attachment is one file with no extraction needed - matches the
walkthrough-HTML delivery pattern Luda already expects.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "status_may19" / "STATUS_MAY19.html"


def embed(rel_path: str) -> str:
    """Read a PNG and return a data: URI ready to drop into an <img src>."""
    p = ROOT / rel_path
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


HALYNA_NARRATIVE = embed("docs/preflight/625c57e8-a727-47e2-85e5-f5fe015e793c/narrative_expanded.png")
DOROTHY_NARRATIVE = embed("docs/preflight/9b692fe9-1f13-4ddf-8c8c-27376e96a6d0/narrative_expanded.png")
DISCLOSURE = embed("docs/preflight/disclosure/disclosure_expanded.png")
COACH = embed("docs/preflight/coach/coach_ok.png")
SUMMARY = embed("docs/preflight/summary/summary_ok.png")


HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AI Pathway status - May 19</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
         color: #1a202c; max-width: 1000px; margin: 24px auto;
         padding: 0 18px; line-height: 1.55; }}
  h1 {{ font-size: 26px; color: #1a365d; margin: 0 0 8px; }}
  h2 {{ font-size: 19px; color: #1a365d; margin: 26px 0 8px;
        padding-bottom: 6px; border-bottom: 2px solid #e2e8f0; }}
  h3 {{ font-size: 15px; margin: 16px 0 4px; color: #2d3748; }}
  .lede {{ color: #4a5568; margin: 0 0 18px; font-size: 14px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px;
           margin: 8px 0 14px; }}
  th {{ background: #edf2f7; padding: 8px 10px; text-align: left;
        border-bottom: 2px solid #cbd5e0; font-weight: 600; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px;
            font-size: 11px; font-weight: 600; }}
  .green {{ background: #c6f6d5; color: #22543d; }}
  .yellow {{ background: #feebc8; color: #7b341e; }}
  .red {{ background: #fed7d7; color: #9b2c2c; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px;
           margin: 10px 0; background: #fff; }}
  .screenshot {{ display: block; max-width: 100%; height: auto;
                 border: 1px solid #cbd5e0; border-radius: 4px;
                 margin: 8px 0 16px; }}
  ul {{ margin: 4px 0 4px 18px; }}
  li {{ font-size: 13px; margin: 3px 0; }}
  .small {{ font-size: 12px; color: #718096; }}
  code {{ font-family: SF Mono, Consolas, monospace; font-size: 12px;
          background: #edf2f7; padding: 1px 5px; border-radius: 3px; }}
</style>
</head>
<body>

<h1>AI Pathway status - May 19</h1>
<p class="lede">Summary of every fix shipped since your May 15 Brittany rerun and the May 19 Halyna case, plus where each of your prep personas stands right now. All checks below run against the live deployment at <code>95.216.199.47:3000</code>.</p>

<h2>Per-persona status</h2>

<table>
  <thead>
    <tr><th>Persona</th><th>Role</th><th>Verdict</th><th>What changed</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Brittany White</strong></td>
      <td>Sr. AI Product Marketing Manager</td>
      <td><span class="badge green">READY</span></td>
      <td>All 5 role-essence skills (SK.COM.001, SK.PRD.022, SK.PRD.001, SK.PRD.021, SK.FND.002) now in top 5 deterministically. The May 15 rerun result is structurally resolved.</td>
    </tr>
    <tr>
      <td><strong>Halyna Mushak</strong></td>
      <td>Director, Global Campaigns</td>
      <td><span class="badge yellow">READY WITH CAVEATS</span></td>
      <td>SK.DOM.MKT.001 at #1, plus foundational PRM (SK.PRM.000 + SK.PRM.001) injected for the depth concern you raised - the same skills Claude picked in your shared chat. Top 5 is now meaningfully deeper than the May 19 set.</td>
    </tr>
    <tr>
      <td><strong>Dorothy Fatunmbi</strong></td>
      <td>Learning &amp; Development Specialist</td>
      <td><span class="badge yellow">READY WITH CAVEATS</span></td>
      <td>SK.DOM.EDU.001 at #1, SK.PRM.000 in top 5, SK.COM.005 in top 5. Dashboard naming + chapter routing fixes you flagged on May 16 are all in.</td>
    </tr>
    <tr>
      <td><strong>Jennifer C (LK May 9)</strong></td>
      <td>AI Content Editor</td>
      <td><span class="badge yellow">READY WITH CAVEATS</span></td>
      <td>Top 5 is content-editor relevant (FND.002, COM.001, COM.005, GOV.022, CTIC.006). Existing positive-feedback set preserved; the new in-product surfaces below answer her 4 strategic asks.</td>
    </tr>
  </tbody>
</table>

<p class="small"><strong>READY</strong> = all QA agents green, safe to demo today. <strong>READY WITH CAVEATS</strong> = some yellow flags worth a brief reviewer prep, but no blocking issues.</p>

<h2>4 new in-product surfaces for Jennifer C's May 12 asks</h2>

<div class="card">
  <h3>1. "How do I know these are the right skills?" - Ontology narrative on the Top 5 page</h3>
  <p>Collapsible panel under the Top 5 header. The headline is always visible; expanding shows the ontology version, the 5-parameter rubric formula, the role-specific guarantees applied (role-essence floor for senior PMM roles, domain mandate for vertical roles, with the specific skill IDs they protected), and the diversity rule.</p>
  {f'<img class="screenshot" src="{HALYNA_NARRATIVE}" alt="Ontology narrative panel, Halyna case (expanded)">' if HALYNA_NARRATIVE else ''}
</div>

<div class="card">
  <h3>2. "How do we know AI is not hallucinating?" - Disclosure + grounding sources on every chapter</h3>
  <p>Amber banner at the top of every lesson with a clear disclosure: AI-generated, grounded in the GenAI Skills Ontology v2.0. Expandable "Show sources" reveals the exact ontology strings the chapter was built from (skill, domain, both rubric strings quoted verbatim) so the learner can compare them against the chapter narrative and flag drift via the existing Confusion Recovery flow.</p>
  {f'<img class="screenshot" src="{DISCLOSURE}" alt="Chapter disclosure + sources (expanded)">' if DISCLOSURE else ''}
</div>

<div class="card">
  <h3>3. "Make it feel like a coach" - Coach voice intro + outro on every chapter</h3>
  <p>Indigo intro at the top frames what they are working on and why. Emerald outro at the bottom nudges toward the implementation task and reminds the learner about the Confusion Recovery button. Both use the actual skill name and level rubric text - not generic copy.</p>
  {f'<img class="screenshot" src="{COACH}" alt="Coach intro + outro on a lesson page">' if COACH else ''}
</div>

<div class="card">
  <h3>4. Stickiness - End-of-path summary with next steps and 60-day retake</h3>
  <p>Completing the last chapter routes to a new <code>/learn/{{pathId}}/complete</code> page (instead of back to the dashboard). The page shows what they accomplished, ontology-grounded recommendations for next skills (mix of same-skill-next-level and adjacent-skill-in-domain), and a calculated retake date 60 days out.</p>
  {f'<img class="screenshot" src="{SUMMARY}" alt="End-of-path summary page">' if SUMMARY else ''}
</div>

<h2>Multi-agent QA team gating every demo now</h2>

<p>Five independent agents collaborate on each persona pass and produce a single GREEN / YELLOW / RED verdict with a readable dossier. Each agent can BLOCK; the dossier shows every agent's reasoning, grounded in your actual customer quotes wherever possible.</p>

<table>
  <thead>
    <tr><th>Agent</th><th>What it does</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Customer Voice Reasoner</strong></td><td>LLM reads your verbatim quotes from each persona + the current engine output; pushes back when literal asks are met but the deeper intent is missed.</td></tr>
    <tr><td><strong>Skill Curator</strong></td><td>Independently re-runs the 5-parameter rubric and compares against the persona corpus; hard-blocks on forbidden skills in top 5.</td></tr>
    <tr><td><strong>Path Coherence Auditor</strong></td><td>Deterministic DB checks - module titles match ontology, no cached lesson contradicts its module, every skill_id resolves.</td></tr>
    <tr><td><strong>Chapter Reviewer</strong></td><td>Per-chapter identity + LLM prose-fit audit - is this chapter actually about the right skill in a way that fits the persona's role?</td></tr>
    <tr><td><strong>Demo-Readiness Gate</strong></td><td>Aggregates the four into one verdict and renders the dossier suitable for attaching to a "ready to demo" email.</td></tr>
  </tbody>
</table>

<p class="small">The team is run via <code>python /app/run_qa_team.py &lt;persona_id&gt;</code>. Verdicts above came from running it against the production deployment after every fix.</p>

<h2>Engineering tracks shipped</h2>

<ul>
  <li><strong>P0</strong> - JD parser role-aware rules (domain-skill mandate, role-essence floor, PRM depth-by-learner, NEW v2.0 awareness) + persona regression contract</li>
  <li><strong>P1</strong> - Deterministic 5-parameter rubric scoring + Maintain vs Develop partition</li>
  <li><strong>P2</strong> - Multi-agent QA team online with pre-demo gate</li>
  <li><strong>P3</strong> - 4 new surfaces for Jennifer C's strategic asks (narrative, disclosure, coach, summary)</li>
  <li><strong>Halyna depth close</strong> - foundational PRM 000-006 now injected for non-tech vertical roles when LLM omits them; Customer Voice agent severity sanity-check</li>
</ul>

<p>Every original Goal / Path record from your prior tests stays in the database under its original ID. <code>docs/qa_dossier/verification_runs.md</code> in the repo records new Goal IDs alongside originals so we can always reproduce exactly what you saw at any point in time.</p>

<h2>What you can do now</h2>

<ol>
  <li>Re-load each persona's analysis page - you should see the new ontology narrative panel collapsed at the top.</li>
  <li>Click into a lesson - the AI disclosure + grounding sources panel sits above the chapter; the coach voice frames it.</li>
  <li>Mark every chapter complete - the last completion routes to the new end-of-path summary instead of back to the dashboard.</li>
  <li>When you create Srushti Madhure (the 5th in your prep cohort), the QA team automatically gates her before any demo - just add her to the persona corpus with her customer quotes and the rest is automatic.</li>
</ol>

<h2>Outstanding items still open</h2>

<p class="lede">Everything below is tracked but not yet shipped. Roughly grouped by who is unblocking what.</p>

<h3>Queued for the next round</h3>
<table>
  <thead>
    <tr><th>Item</th><th>Source</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Skills Profile redesign (9-point spec)</strong></td>
      <td>Luda email 2026-05-10 "AI Pathway - clarifying 4 buttons on each profile"</td>
      <td>Queued. You asked me on May 16 to deprioritize this relative to the Brittany skills fix. That fix is in; ready to pick up the 9-point redesign when you are.</td>
    </tr>
    <tr>
      <td><strong>Ontology Path button removal</strong></td>
      <td>Luda email 2026-05-10 (4-buttons thread) - you replied "LK Agree" on May 16</td>
      <td>Queued. Confirmed duplicative with the Learning Dashboard. One-line frontend change pending a small UI session.</td>
    </tr>
    <tr>
      <td><strong>Build Your Agent fields (description / instructions / knowledge base)</strong></td>
      <td>Vivek walkthrough item 14 (May 9)</td>
      <td>Queued for the next chapter-format round. Vivek's ask was to align the agent build UI with industry-standard agent-builder field sets (custom GPTs, Copilot agents, Gemini Gems). Planned changes captured in repo.</td>
    </tr>
    <tr>
      <td><strong>Interstitial proficiency-rating step</strong></td>
      <td>Luda walkthrough item 06 (May 7), Luda follow-up May 16</td>
      <td>Deferred per your note that this can come after the demo round. Spec captured at <code>docs/follow_ups/06_interstitial_skill_rating.md</code>.</td>
    </tr>
    <tr>
      <td><strong>Profile parsing accuracy retest across all 5 prep profiles</strong></td>
      <td>Luda March 18 note (Brittany W's stored profile had her current position as SAP, which was incorrect)</td>
      <td>I promised this in the May 12 wrap email and have not yet completed it for all 5 profiles. Will run as part of the next persona-cohort pass.</td>
    </tr>
  </tbody>
</table>

<h3>Awaiting your input</h3>
<table>
  <thead>
    <tr><th>Item</th><th>Source</th><th>What I need</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Vivek's Item 17 - deterministic ordering</strong></td>
      <td>Vivek walkthrough May 9</td>
      <td>Vivek marked this Issue with no comment. The change set the profile analyzer to temperature=0 so identical inputs produce identical top 5. Verified across 20 runs. Vivek - if you can clarify the actual concern (implementation or result), I can act on it.</td>
    </tr>
    <tr>
      <td><strong>Srushti Madhure persona</strong></td>
      <td>Your March 18 prep cohort list - 5 personas total, 4 covered</td>
      <td>Whenever you create her profile and test her case, the multi-agent QA team will automatically gate her before any demo. Just need a customer_quote line for the persona corpus once you have feedback.</td>
    </tr>
    <tr>
      <td><strong>Halyna depth - is the foundational PRM injection right?</strong></td>
      <td>Your May 19 Halyna email + shared Claude chat</td>
      <td>The engine now injects foundational PRM 000-006 for non-tech vertical roles. Halyna's top 5 includes SK.PRM.000 + SK.PRM.001, matching what Claude picked. If when you re-test her this feels too foundational (or not foundational enough), tell me and I can tune the injection threshold.</td>
    </tr>
  </tbody>
</table>

<h3>Strategic conversations</h3>
<table>
  <thead>
    <tr><th>Item</th><th>Source</th><th>Status</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Next-steps call</strong></td>
      <td>Ram's May 12 reply on the Jennifer C demo thread</td>
      <td>You wanted to finish 3 more personas before any consolidated call. Brittany / Halyna / Dorothy are now all addressed, Jennifer's asks are live. Ready to schedule whenever works.</td>
    </tr>
    <tr>
      <td><strong>"Take it for a spin" self-serve + NDA</strong></td>
      <td>Your May 12 Jennifer demo note</td>
      <td>Open. You raised this as something to plan for once the tool is robust enough. The QA team gives us the demo-readiness signal we would need to extend access; happy to start scoping when you want.</td>
    </tr>
  </tbody>
</table>

<p class="small">For completeness, everything below was on the original outstanding list and is now closed:</p>
<ul class="small">
  <li>Per-skill hover descriptions (Vivek item 04, Luda Apr 29) - shipped May 12</li>
  <li>Skills render in sequential rank order (Luda May 9) - shipped May 12</li>
  <li>Back to skill review link on Learning Dashboard (Luda May 9) - shipped May 12</li>
  <li>Rating persistence across navigation (Luda May 9) - shipped May 12</li>
  <li>Dashboard module names matching Top 5 page (Dorothy F May 16) - shipped May 18</li>
  <li>Chapter routing / SK.PRM.003 hallucination (Dorothy F May 16, Jennifer demo) - shipped May 18</li>
  <li>Ontology rubric coverage for D.DOM skills (Dorothy F May 16) - shipped May 18</li>
  <li>Chapter order matching user selection (Halyna May 19) - shipped May 19</li>
  <li>Top 5 page copy clarifying the swap-on-meets-target behavior (Halyna May 19) - shipped May 19</li>
  <li>Brittany W role-essence skills in top 5 (May 15 rerun) - shipped May 19 (P1 rubric scoring)</li>
  <li>Halyna depth - foundational PRM in top 5 for non-tech vertical roles (May 19) - shipped May 20</li>
</ul>

</body>
</html>
"""


def main() -> None:
    OUT.write_text(HTML, encoding="utf-8")
    print(f"Wrote {OUT}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
