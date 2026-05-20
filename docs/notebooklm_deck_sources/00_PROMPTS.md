# NotebookLM slide deck prompt

NotebookLM's "Customize Slide Deck" dialog takes a **single description-style prompt**, not a slide-by-slide outline. The model decides the slide structure based on the prompt and the uploaded sources. The prompt below is written for that field.

## Pick these settings in the dialog

- **Format**: Detailed Deck (the deck has to read on its own when Luda forwards it to an enterprise prospect, so we want full text, not just talking points)
- **Length**: Default
- **Language**: English

## Paste this into the "Describe the slide deck you want to create" field

```
Create a comprehensive deck explaining the AI Pathway multi-agent QA
system. The audience is an enterprise buyer, CTO, or VP of Learning at
a Fortune 1000 company who has seen ten AI tools this quarter, is
skeptical, time-poor, and looking for one reason to disqualify us. Win
them on rigor and traceability, not on hype. The deck must answer four
buyer questions in the first ninety seconds: why does this exist, what
does each agent do, how do you assure quality specifically, and show
me proof it works.

Core content the deck must cover, drawing from the uploaded source files:

The problem we solved. Across five customer testing rounds with Luda
Kopeikina (a real product reviewer whose emails are in the persona
corpus file), every issue surfaced AFTER she found it. The pattern was
reactive. A real reviewer was always the one catching drift first. That
does not scale to multiple personas, external pilots, or enterprise
buyers who expect us to know our own product is right before showing it
to them.

The answer. Five independent QA agents that gate every customer-facing
demo. Three are pure Python (no language model in the loop); two use
an LLM only for prose-fit judgment. Each agent reads a different input
(customer quotes, engine skill-set output, the database, chapter prose,
or the aggregator), so they cannot agree on the same observation by
accident because they are not looking at the same data.

Each agent in detail, with what it reads, what it does, what it blocks,
and what it cannot do:

  Customer Voice Reasoner reads the persona's verbatim customer
  feedback (the customer_quote field in the persona corpus) and judges
  whether the engine output addresses what the customer actually wants,
  not just the literal request. Pushes back when intent is missed.

  Skill Curator independently re-runs Luda's five-parameter weighted
  rubric: Priority equals (Importance times four) plus (Breadth times
  three) plus (Momentum times three) plus (Connectivity times two) plus
  (Career Signal times two), maximum forty-two. Blocks if forbidden
  skills appear in the top five or expected skills are missing.

  Path Coherence Auditor runs deterministic database invariants:
  chapter skill IDs resolve in the ontology, module titles match the
  Top Five Skills page, cached lesson content matches its parent
  module's skill ID, chapter numbering is contiguous. Pure Python; runs
  in under a second.

  Chapter Reviewer reads the actual generated chapter content. Identity
  check (does the chapter actually teach the right skill?) plus a prose
  fit check using an LLM (does a marketing chapter mention campaigns,
  not generic documents?). Catches hallucinated content.

  Demo Readiness Gate aggregates the four upstream verdicts into one
  GREEN slash YELLOW slash RED signal and renders the readable Markdown
  dossier that gets attached to a "ready to demo" decision.

How quality is assured. Independence by input differentiation. Determinism
wherever possible (three of five agents are pure Python and compute facts,
not opinions). Customer-quote grounding (every Customer Voice finding cites
Luda's verbatim words from her emails; the persona corpus pins those quotes
in the repo so they cannot drift). Auditability (every run produces a
Markdown dossier with per-agent reasoning, the customer quote that grounded
each finding, and the proposed fix). Pre-demo gate (nothing ships to a
customer until the Demo Readiness Gate returns GREEN or YELLOW with
documented caveats; RED blocks until the underlying finding is fixed or
an override is logged in the dossier). The human (Ali) makes the final
override call; we have never overridden a RED to date.

The concrete proof point. On May 19, Luda emailed about her Halyna Mushak
test and said the engine "pulled rather rudimentary skills" for a
non-technical marketing director. Her exact words went into the persona
corpus as a customer_quote. The next day the Customer Voice agent
independently flagged the same depth concern when reading the corpus
quote against fresh engine output. We shipped a foundational prompting
skill injection that day. When Luda re-tested, the depth concern was
resolved. The team caught the next-level issue before the customer had
to surface it again. The Halyna dossier in the uploaded source files
shows the per-agent reasoning, the customer quote, and the proposed fix
verbatim.

The buyer takeaway, delivered on the final slide: every customer-facing
demo passes a documented pre-demo gate; every finding cites the customer's
own words or the literal source; every override is logged in the same
file as the verdict, so audit is the default; the system is repeatable
for any new persona we onboard.

Voice and style rules, non-negotiable:

  Never use em dashes anywhere in the deck. Use hyphens with spaces
  ( - ) or periods.

  Specific over generic. "The agent re-runs Luda Kopeikina's
  five-parameter rubric" is correct; "the agent re-evaluates the
  skills" is wrong.

  Receipts on every claim. Cite the dossier file, the corpus entry, or
  the code module in speaker notes when the slide makes a specific
  factual claim.

  No hedging language. Replace "may", "could", "potentially" with
  concrete statements grounded in the source files.

  No buzzwords. Do not use "revolutionary", "cutting-edge", "next-gen",
  "AI-powered", or similar marketing language.

  Frame failures as discovered, not hidden. The Halyna case is a
  feature, not an apology.

Visual and structural rules:

  One idea per slide. If a slide has two ideas, split it.

  Title is a complete sentence claim, not a label. "Why a QA team" is
  weak; "The pattern was reactive across five customer rounds" is
  strong.

  Charts and diagrams over bullet walls. If a slide has more than six
  lines of body text, replace half of it with a diagram description.

  Define jargon on first use. The first slide that mentions "rubric",
  "persona corpus", or "dossier" must define the term in one line.

  Speaker notes carry depth. The visible slide is the headline; the
  speaker notes are where the receipts and the nuance live, so the
  deck reads tight on screen and rich in person.

  Match the in-product color cues where they help: GREEN, YELLOW, RED
  for verdict states; indigo, amber, emerald, navy for the four
  in-product surfaces (ontology narrative, chapter disclosure, coach
  voice, end-of-path summary) when those are referenced.

Do not include:

  A roadmap slide or future promises beyond what is shipped today.

  Anything about LLM internals, model selection, or vendor choice.

  Internal commit IDs, GitHub URLs, or engineer names in the visible
  slide content. Those belong in speaker notes only if at all.

End with a single buyer-question takeaway slide that answers "how do
you know your AI is right?" with the auditable-by-default story.
```

## If the first draft is off

NotebookLM gives you a "Customize" loop. If something is wrong, paste a follow-up like one of these into the same dialog:

- **Too short or too thin** - "Expand the section explaining each agent; give each agent its own slide with what it reads, what it does, what it blocks, and what it cannot do."
- **Buzzword creep** - "Remove every instance of 'revolutionary', 'cutting-edge', 'next-gen', or similar marketing language; replace with specific factual claims grounded in the source files."
- **Em dashes appeared** - "Replace every em dash with a hyphen surrounded by spaces, or a period."
- **Too generic** - "Make each claim more specific by citing the file or quote it draws from."
- **Wrong audience tone** - "Tighten the voice for an enterprise CTO who has ninety seconds; cut every sentence that does not earn its space."
- **Want a different structure** - "Reorganize around the four buyer questions: why this exists, what each agent does, how quality is assured, and the proof point."

The uploaded source files give NotebookLM enough citations that you can ask it to re-ground any slide in a specific dossier or corpus entry.
