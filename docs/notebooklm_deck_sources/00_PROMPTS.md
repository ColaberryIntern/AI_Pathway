# NotebookLM prompts: AI Pathway QA System enterprise deck

Two prompts to paste into NotebookLM. Upload these source files alongside them so the model has the receipts:

- `docs/qa_dossier/halyna_mushak.md` (sample real dossier)
- `docs/qa_dossier/verification_runs.md` (audit-trail ledger)
- `backend/scripts/persona_corpus.py` (the customer-quote-grounded test corpus)
- `backend/app/qa_agents/` (any of the five agent modules - they self-document)
- This email thread or just paste the body of the May 20 reply to Ram

---

## 1. System prompt (paste into NotebookLM as Custom Instructions)

```
You are drafting an enterprise sales-ready PowerPoint deck explaining a
multi-agent QA system that gates customer-facing demos of an AI learning-
path tool. The deck must answer the four questions an enterprise buyer
or CTO will ask in the first 90 seconds of seeing this:

  1. Why does this exist?
  2. What does each agent do?
  3. How do you assure quality, specifically?
  4. Show me proof it works.

Audience: enterprise buyer, CTO, VP of Learning, or chief AI officer at a
Fortune 1000 company. They have seen ten AI tools this quarter. They are
skeptical, time-poor, and looking for one reason to disqualify us. Win
them on rigor and traceability, not hype.

Voice rules - non-negotiable:
  - Never use em dashes. Use hyphens (- with spaces) or periods.
  - Specific over generic. "The agent re-runs Luda Kopeikina's
    5-parameter rubric" beats "the agent re-evaluates the skills."
  - Receipts. Every claim should map to a named artifact in the source
    files (a dossier line, a corpus entry, a code module). When in
    doubt, name the file.
  - No hedging. Replace "may," "could," "potentially" with concrete
    statements grounded in the source files.
  - Frame failures as discovered, not hidden. The Halyna case is a
    feature, not a bug - the system caught the depth issue before the
    customer re-tested.

Visual rules:
  - One idea per slide. If a slide has two ideas, split it.
  - Title is a statement, not a label. "Why a QA team" weak; "The
    pattern was reactive across five customer rounds" strong.
  - Each slide has a single hero claim (top) and at most three
    supporting points (middle), plus one piece of evidence (bottom).
  - Use the existing color cues from the source files where they help:
    GREEN / YELLOW / RED for verdict states; agent-pair colors only if
    they reinforce the distinction.
  - Charts and diagrams over bullet walls. If a slide has more than
    six lines of body text, replace half of it with a diagram.
  - End every slide with a "so what" line if it does not have one.

Structural rules:
  - Cite the source. When a slide makes a specific claim ("the team
    caught the Halyna depth issue before the customer re-tested"),
    include a small footer line referencing the dossier or commit.
  - Define jargon on first use. The first slide that uses "rubric" or
    "persona corpus" or "dossier" must define it in one line.
  - Speaker notes on every slide. The visible content is the headline;
    the speaker notes carry the depth so the deck reads tight on
    screen and rich in person.
  - No agent is described in less than one full slide. Each of the
    five agents gets its own slide with: what it reads, what it does,
    what it blocks, what it cannot do.

Do not include:
  - Generic AI buzzwords ("revolutionary," "cutting-edge," "next-gen")
  - Roadmap slides or future promises beyond what is shipped today
  - Anything about LLM internals or model selection
  - Internal team names or commit IDs in the visible slide content
    (keep those in speaker notes only)
```

---

## 2. Slide deck prompt (paste this as the main NotebookLM prompt after the system instructions)

```
Generate a 12-slide PowerPoint-ready outline for the AI Pathway QA
System enterprise deck. Use the uploaded source files as your evidence
base. Every slide must include: slide title (a complete sentence claim),
body content (visible on slide), speaker notes (depth for the presenter),
and source citation (which uploaded file the content draws from).

Slide 1 - cover
  Title: Building reliability into AI-generated learning paths
  Subtitle: How the AI Pathway QA team gates every customer demo
  Speaker notes: Set the stakes - personalized skill matching is the
  core value proposition. If we cannot do it reliably, there is no
  product. The deck shows how a five-agent QA team makes reliability
  structural, not aspirational.

Slide 2 - the problem
  Title: Five customer rounds, one pattern - the customer found every
         issue first
  Body: Brief timeline (May 7 to May 19) showing customer-discovered
  issues per round. Headline: 100 percent of issues surfaced by the
  customer before our QA caught them. That does not scale to multiple
  personas or external pilots.
  Speaker notes: Specifically name the customer rounds (Luda's Apr 28
  test, the May 7 walkthrough, the May 9 follow-up, the May 15 Brittany
  rerun, the May 19 Halyna case). For each round, name one specific
  bug she found. Then make the structural point: reactive bug-finding
  by customers is a sales-cycle killer.
  Source: persona_corpus.py customer_quote fields

Slide 3 - the answer
  Title: Five agents, one verdict, every persona before every demo
  Body: Diagram of the five agents with arrows into a single Demo
  Readiness Gate verdict (GREEN / YELLOW / RED). Tagline: same checks
  the customer would run, before the customer has to run them.
  Speaker notes: The team is independent agents with different
  responsibilities. Three are deterministic (no LLM), two use an LLM
  for prose-fit judgment. They produce a single readable verdict per
  persona with reasoning grounded in the customer's own words.
  Source: backend/app/qa_agents/ directory layout

Slide 4 - Customer Voice agent
  Title: Customer Voice reads the customer's own words, not ours
  Body: What it reads (verbatim customer quotes from emails); what it
  does (compares engine output to customer intent); what it blocks
  (any finding where intent is missed); what it cannot do (judge
  database state or chapter prose, which the other agents own).
  Speaker notes: Show the persona_corpus.py customer_quote line for
  Halyna, then point to the dossier line where Customer Voice cited
  the same quote when it flagged the depth concern. The agent is not
  asked to imagine what the customer would want; it is asked to
  compare against quoted customer feedback.
  Source: persona_corpus.py Halyna entry + halyna_mushak.md dossier

Slide 5 - Skill Curator agent
  Title: Skill Curator runs the customer's rubric independently
  Body: Re-runs the 5-parameter weighted rubric scoring (Importance,
  Breadth, Momentum, Connectivity, Career Signal). Blocks if forbidden
  skills appear in the top 5 or expected skills are missing. Pure
  Python; no model temperature affects what it computes.
  Speaker notes: This is the customer's rubric, not ours. Luda
  Kopeikina authored the 5-parameter scoring spec; the agent applies
  it to engine output and compares against persona_corpus assertions.
  Walk through the Halyna case: the corpus says "marketing role must
  include SK.DOM.MKT.001 in top 5"; the engine produces a top 5; the
  agent confirms or blocks.
  Source: backend/app/services/rubric_scorer.py + persona_corpus.py

Slide 6 - Path Coherence Auditor
  Title: Path Coherence proves the database state is consistent
  Body: Every chapter's skill ID resolves in the ontology; dashboard
  module names match the Top 5 page; cached chapter content matches
  its parent module; chapter numbering is contiguous. Pure deterministic
  database checks; runs in under one second.
  Speaker notes: This is the agent that catches the structural-drift
  class of bug - the kind that surfaced as "the dashboard shows
  different skill names than the Top 5 page" on May 16. Catches it
  before the customer opens the dashboard.
  Source: backend/app/qa_agents/path_coherence.py

Slide 7 - Chapter Reviewer
  Title: Chapter Reviewer reads the actual generated content
  Body: For every cached chapter, verifies the chapter identity (does
  it actually teach the right skill?) and the prose fit (does a
  marketing chapter mention campaigns, not generic documents?). Catches
  the LLM-hallucinated-the-wrong-skill class of bug.
  Speaker notes: Reference the May 18 SK.PRM.003 hallucination where
  the LLM emitted prompt-debugging content for every skill regardless
  of input. Chapter Reviewer catches this by reading meta.skill_id and
  cross-checking against the module's required skill. Hallucination
  detection is grounded in literal text comparison, not vibe.
  Source: backend/app/qa_agents/chapter_reviewer.py

Slide 8 - Demo Readiness Gate
  Title: One verdict that ships or blocks the demo
  Body: Aggregates the four upstream verdicts. Any RED blocks. Any
  YELLOW (no RED) ships with documented caveats. All GREEN ships
  clean. Renders a Markdown dossier with the per-agent reasoning,
  customer quotes that grounded each finding, and proposed fixes.
  Speaker notes: The gate is pure aggregation logic. It does not
  reason; it accumulates. The dossier is what gets attached to a
  "ready to demo" decision. Show the bottom of the halyna_mushak.md
  dossier as a real example of what a buyer would see.
  Source: backend/app/qa_agents/demo_gate.py + halyna_mushak.md

Slide 9 - The independence safeguard
  Title: Agents read different inputs, so they cannot agree by
         accident
  Body: A 2x2 diagram showing each agent and its input source.
  Customer Voice reads customer quotes. Skill Curator reads engine
  skill output. Path Coherence reads the database. Chapter Reviewer
  reads chapter prose. They cannot converge on the same opinion
  because they are not looking at the same data.
  Speaker notes: Address the "echo chamber" concern directly. The
  agents are designed to disagree where the underlying data
  disagrees, and agree only where the data agrees. Cite the May 19
  Halyna pass where the deterministic Skill Curator and the LLM-based
  Customer Voice independently arrived at the same finding from
  different starting points - that is signal, not slop.
  Source: backend/app/qa_agents/orchestrator.py + dossier

Slide 10 - The determinism safeguard
  Title: Three of five agents do not use a language model at all
  Body: Path Coherence, Skill Curator's rubric math, and the Demo
  Readiness Gate are pure Python. They compute facts. There is no
  model temperature affecting whether the database has the right
  state or whether a forbidden skill is in the top 5. Two of five
  use an LLM for prose-fit judgment only; both ground every finding
  in literal text from the source.
  Speaker notes: Cost is bounded by determinism. Auditability is
  bounded by determinism. The LLM is used only where reading prose
  is the actual job; everywhere else, the answer is computed, not
  reasoned.
  Source: persona_corpus.py + sweep_integrity.py + rubric_scorer.py

Slide 11 - Proof point
  Title: The May 19 Halyna depth concern was caught by the team
         before the customer re-tested
  Body: Timeline. Day 1: customer flags depth concern in email. Day
  1+: persona_corpus updated with customer_quote. Day 2: Customer
  Voice agent flags the same depth concern reading the corpus quote.
  Day 2+: foundational PRM injection shipped. Day 3: customer
  re-tests with the new engine, sees fix.
  Speaker notes: This is the entire promise of the system in one
  case. The team did not prevent the original bug, but it caught the
  next-level concern (depth, not just domain skill) before the
  customer re-flagged it. That is the cycle we want: customer finds
  Type A bug, team catches Type B before customer does, customer
  finds Type C, team learns and catches Type D, and so on. Over
  time, customer findings shift from "the basics are broken" to
  "here is a nuance worth discussing."
  Source: halyna_mushak.md dossier + verification_runs.md ledger

Slide 12 - what this gives you
  Title: A defensible, auditable answer to "how do you know your AI
         is right?"
  Body: Three bullets - (1) every customer-facing demo passes a
  documented pre-demo gate, (2) every finding cites the customer's
  own words or the literal source, (3) every override is logged in
  the same file as the verdict so audit is the default. Close with:
  this is repeatable for any new persona we onboard.
  Speaker notes: Land the deck on the buyer's actual question. The
  buyer wants to know: when something goes wrong, can you tell me
  why and show me what you did about it? Yes. Here is the file.
  Source: docs/qa_dossier/ directory

Format each slide as:
  ### Slide N - <title sentence>
  **Body:** <visible content>
  **Speaker notes:** <depth>
  **Source:** <citation>

After the 12 slides, append a final section titled "Deck production
notes" listing: recommended slide layout (title at top, hero claim,
diagram or evidence, speaker notes hidden), color palette suggestions
(navy / indigo / amber / emerald to match the in-product surfaces),
and a one-line list of what the presenter should rehearse before
showing this to a real buyer.
```

---

## Suggested NotebookLM workflow

1. Create a new Notebook.
2. Upload sources: the QA agent files, the dossier, the verification log, the persona corpus, and this email's content. (Do not upload internal slack threads or anything containing customer PII beyond what was in the public email.)
3. Paste the system prompt into Custom Instructions.
4. Paste the slide deck prompt into the main composer.
5. Generate. Iterate by asking for specific changes ("rewrite slide 3 with a simpler diagram description," "tighten the speaker notes on slide 11 to under 80 words," etc.).
6. Once the markdown outline is good, paste into your preferred deck tool (PowerPoint via Pages > Outline import, or Google Slides via Slidesgo style outline-to-slides) and apply the visual identity.

The point of doing it through NotebookLM rather than asking the model raw: NotebookLM grounds each slide in the uploaded source files, so the citations remain real. That matches the integrity story you are selling.
