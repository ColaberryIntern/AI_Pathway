# CLAUDE.md
**Colaberry Agent Project Rules, QA Model & Operating Contract (Governed Autonomous v2)**

This file defines how Claude (and other AI coding agents) must behave when working in this repository. This project does NOT use Moltbot. Claude Code and other coding agents are used to design, build, validate, and maintain the system, they are not the runtime system itself.

---

# Core Principle

LLMs are probabilistic. Production systems must be deterministic.

Claude's role: reason, plan, orchestrate, validate, and modify instructions/code carefully and audibly. Claude is never the runtime executor of business logic, tests, or workflows.

**Operating bias: proceed by default.** Pause only when a governance boundary is crossed, a strategic constraint is unclear, or an irreversible decision is required. Claude is a senior autonomous engineer, not a junior developer seeking permission for implementation details.

---

# Trust Before Intelligence (MANDATORY for all AI work)

All AI work in this repository MUST apply the **Trust Before Intelligence** framework (the Architecture of Trust) by Ram Katamaraja, Colaberry. Canonical reference: https://github.com/colaberry/trust-before-intelligence-book. This is the governing design philosophy for every agent, judge, pipeline, prompt, model integration, and evaluation we build. It is not optional.

**Core tenet:** earn trust before relying on intelligence. The model's probabilistic output is never trusted on its own; it is wrapped in deterministic verification, governance, and observability. Anything the model would self-report that can be computed deterministically (scores, gates, arithmetic, ID/lookup validation) MUST be computed in code, never asked of the model.

Apply the three pillars:

1. **INPACT (what the AI must provide):** Instant, Natural, Permitted, Adaptive, Contextual, Transparent. The requirements checklist for any AI capability.
2. **7-Layer Architecture (how to build it):** Storage -> Real-Time -> Semantic -> Intelligence -> Governance -> Observability -> Orchestration. Diagnose failures by layer and fix the binding layer, not a random knob.
3. **GOALS (how to measure):** Governance, Observability, Availability, Lexicon, Solid.

**Hard rules:**
- Every new or changed AI feature names which INPACT dimensions it serves and which of the 7 layers it touches, recorded in `PROGRESS.md`.
- Judges and evaluators: the LLM produces only per-item judgments; a deterministic Python step computes composites, gates, and verdicts. Pin the judge model and calibrate it against a golden reference (the Lexicon dimension). Do not let an LLM grade its own arithmetic.
- Diagnose AI failures with the layer model BEFORE changing code: identify the binding layer (often Intelligence, e.g. the model choice) instead of tuning one parameter at a time.
- When assessing or escalating an AI system's production-readiness, score it with INPACT (1-6 per dimension, total / 36 x 100). Below 80/100 is not production-ready.
- A model-class or judge-model change remains a Strategic Decision (escalate) per the Autonomy Model.

This complements the Core Principle above and the Contract, Security, Failure-First, Observability, and Test layers below. Where requirements overlap, apply the stricter one. The AI Pathway judge fix (2026-06-20) is the worked example: `docs/jun19_trust_arch/`.

---

# Architecture & System Layers

**Model:** Agent-First, Deterministic-Execution with Test-First Validation.

| Layer | Role | Location | Notes |
|---|---|---|---|
| 1. Directives | What to do (SOPs) | `/directives` | Human-readable. Define goals, inputs, outputs, edge cases, safety constraints, verification expectations. Living documents. |
| 2. Orchestration | Decision making | Claude | Plans changes, designs tests before logic, updates directives, escalates only for strategic decisions. Never executes business logic directly. |
| 3. Execution | Doing the work | `/execution`, `/services/worker` | Deterministic scripts. Repeatable, testable, auditable, safe to rerun. |
| 4. Verification | Proving it works | `/tests` | Unit, integration, E2E. Tests are first-class citizens, not afterthoughts. |

---

# Folder Responsibilities

Claude must respect these boundaries.

- **`/agents`** - Agent personas and role definitions. Behavioral descriptions only. No executable logic.
- **`/directives`** - SOPs and runbooks. Step-by-step, human-readable. Must define how success is verified.
- **`/execution`** - Deterministic tools and scripts. One script = one clear responsibility. Core logic must be importable and testable. No orchestration logic. No prompts.
- **`/services/worker`** - Long-running or scheduled jobs. Calls scripts from `/execution`. Represents the actual runtime system.
- **`/tests`** - Automated verification layer. Mirrors execution and worker structure. Includes unit, integration, Playwright/browser, API contract, and visual regression tests.
- **`/config`** - Environment wiring (dev vs prod identifiers). No secrets.
- **`/tmp`** - Scratch space. Always safe to delete. Never committed.

No business logic in directives. No orchestration in execution scripts. No execution or testing inside Claude responses.

---

# Contract Enforcement Layer (NEW)

Every module exposes an explicit, typed contract at its boundary. No untyped inputs. No ambiguous outputs. No "we'll figure it out at runtime."

**Required:**

- All inputs and outputs typed via TypeScript types, Zod schemas, or JSON Schema (TS/JS surfaces)
- Python boundaries use Pydantic models or `dataclass` with type hints
- Contracts must be importable, testable, and asserted in tests
- Validation runs at the module boundary, not deep inside the call stack

**Hard rules:**

- A breaking contract change = failing build. Treat it as a compile error, not a warning.
- No `any`, `unknown`, or `dict[str, Any]` returned to callers across module boundaries
- Contract changes require a directive update AND a migration note in `PROGRESS.md`
- Every external boundary (HTTP request, queue message, file load, env var parse) validates against its contract before doing work

If a function's signature isn't enough to write a unit test against, the contract is too loose. Tighten it.

See also: **Security Enforcement Layer** (input validation uses contracts), **Test Strategy Framework** (contracts must be testable).

---

# Modular Composition Rule

Code health is a leading indicator of system health. Enforce structural limits.

| Limit | Target | When to refactor |
|---|---|---|
| File size | ~300 lines | At 400, plan a split. At 500, split before adding more. |
| Function size | ~50 lines | At 75, extract helpers. |
| Function parameters | <= 5 | More -> pass an object/dataclass instead. |
| Cyclomatic complexity | <= 10 per function | Higher -> extract branches into named functions. |

**Composition rules:**

- One responsibility per module. If you describe a module with "and", split it.
- No circular dependencies. The dependency graph must be a DAG. CI should enforce this.
- Extract reusable logic into shared modules. Do not copy-paste across services.
- Public API surface should be small and explicit. Internal helpers stay private.

These limits are guidance, not gospel, but exceeding them requires a one-line justification in `PROGRESS.md` so the decision is auditable.

---

# Production Readiness Principles (12-Factor Adapted)

A pragmatic subset of the 12-factor app methodology, adapted for this repo.

| Principle | Rule |
|---|---|
| Config in environment | Secrets and env-specific values come from env vars or `/config`. Never hardcoded. |
| Stateless execution | Scripts in `/execution` hold no in-memory state across invocations. State lives in the database. |
| Idempotent processes | Re-running a script must not double-write, double-charge, or double-notify. (See Idempotency section.) |
| Logs as event streams | Logs are structured JSON to stdout. No `print()` in production code. (See Observability Framework.) |
| Dev/prod parity | Test environments mirror prod schema, tooling, and dependency versions. No "works on my machine." |
| Explicit dependencies | All dependencies declared in `requirements.txt` / `package.json` with pinned versions. No implicit system installs. |
| Single responsibility scripts | One script = one purpose. If you can't name it in 4 words, split it. |

Violations are reviewable defects, not style preferences.

---

# Idempotency & Replayability (NON-NEGOTIABLE)

Every script and every API endpoint must be safe to run multiple times.

**Required behavior:**

- Same input -> same output
- No duplicate side effects (no double-emails, double-rows, double-charges, double-jobs)
- Failed runs can be re-executed without manual cleanup
- Long-running jobs use idempotency keys (request ID, hash of input, or natural key) to detect re-runs

**Implementation guidance:**

- Database writes use `INSERT ... ON CONFLICT` or upsert patterns where appropriate
- External API calls pass an idempotency key when the API supports one (Stripe, payment, email send, etc.)
- File operations check existence before write OR use atomic rename
- Background jobs check "already done" status before doing work

**Hard rule:** A script that produces different effects on the second run than the first is a production defect, not a quirk. File a fix. Do not work around it.

See also: **Test Strategy Framework** (idempotency is a mandatory test type), **Security Enforcement Layer** (external call retries must be idempotency-aware).

---

# Failure-First Design (NEW)

Every system component must define how it fails before defining how it succeeds.

**Required for every new module / endpoint / script:**

1. **Explicit failure modes** - documented list: timeout, bad input, upstream down, partial write, race condition, quota exceeded, etc.
2. **Retry strategy** - how many retries, with what backoff, and which errors are retryable vs fatal
3. **Recovery path** - what happens after retries are exhausted: alert, dead-letter queue, manual runbook, graceful degradation
4. **User-visible behavior on failure** - error message, status code, fallback UI

**Anti-patterns (forbidden):**

- Silent `try: ... except: pass`
- Bare retries with no backoff
- Errors swallowed and replaced with default values without logging
- "It'll probably work" without a recovery plan

If the failure mode isn't designed, the success mode isn't designed either.

See also: **Observability Framework** (correlation IDs and error_class on every failure), **Build-Break-Harden Loop** (BREAK phase exercises these failure modes).

---

# Security Enforcement Layer

Security is a gate, not a polish step.

**Input validation:**

- Every external input (HTTP body, query string, file upload, env var, CLI arg) is validated at the boundary using the module's contract (see Contract Enforcement Layer)
- Reject malformed input with a clear error. Do not "best effort" parse it.

**Database safety:**

- No string-concatenated SQL. Use parameterized queries or an ORM exclusively.
- No raw user input in shell commands, file paths, or template strings without sanitization

**Secrets:**

- Never committed to the repo. CI must scan for this.
- Loaded from env vars or a secrets manager.
- Never logged, even on error paths.

**External calls (HTTP, DB, queue, file system) must specify all three:**

- **Timeout** - explicit, never unbounded
- **Retry** - with backoff, capped, idempotency-aware (see Idempotency & Replayability)
- **Error handling** - mapped to the module's defined failure modes (see Failure-First Design)

A function that calls `requests.get(url)` with no timeout is a production defect.

---

# Build-Break-Harden Loop (CORE EXECUTION MODEL)

This is how features are developed in this repo. Skipping a phase is skipping the work.

## Phase 1: BUILD

Implement the happy path. Get canonical input -> expected output flow working with tests.

## Phase 2: BREAK

Actively try to break what you just built:

- Send invalid, empty, oversized, malformed input
- Simulate downstream failure (kill the DB, time out the API, return 500)
- Run the script twice in a row (idempotency check)
- Run two instances concurrently (race condition check)
- Pull the network mid-execution

Document every failure mode you find.

## Phase 3: HARDEN

For each failure found in BREAK:

- Add a test that reproduces it
- Add the protection (validation, retry, timeout, idempotency key, error message, fallback)
- Confirm the test now passes

## The rule

**A feature is NOT complete until it has survived BREAK.** Definition of Done explicitly blocks on this. "It works on the happy path" is a starting point, not a finished feature.

---

# Autonomy Model

## Strategic decisions (ESCALATE)

Escalation required when decisions affect:

- Business model, architecture layer structure, cross-module dependency shifts
- Database engine or schema redesign
- External dependency introduction, paid external services
- Compliance or security posture
- Production infrastructure or environment modification
- Non-functional requirement thresholds, cost model shifts
- AI model class changes
- Large refactors (>25% module rewrite)

These are governance boundaries. Autonomy does not override governance.

## Implementation decisions (PROCEED)

Claude must proceed autonomously for:

- Naming, helper structure, internal patterns, default parameter values
- Test structure, refactoring within a module, readability improvements
- Adding missing validations, extending non-breaking interfaces
- Logging structure, minor configuration adjustments
- Small performance improvements, localized bug fixes
- Any reversible change with low blast radius

If the change is reversible AND blast radius is local AND no governance boundary is crossed AND tests validate behavior, then proceed without asking. Escalation is prohibited for implementation-level ambiguity.

## Default resolution strategy

When multiple reasonable paths exist: prefer (1) simplest, (2) deterministic, (3) lowest blast radius, (4) highest testability. Log the assumption and proceed. Do not ask clarifying questions for implementation-level reversible decisions.

## Scope lock

Do not expand scope beyond directives. If scope expansion is detected: log the proposal, continue current scope work, escalate separately for expansion approval. Scope expansion must never block implementation progress.

---

# Confidence, Diagnostic Mode & Stall Detection

## Confidence scoring

Claude internally evaluates: directive clarity, test coverage strength, reversibility, architectural blast radius, compliance/security impact.

| Score | Action |
|---|---|
| > 0.80 | Proceed autonomously |
| 0.65 - 0.80 | Proceed + log assumptions |
| < 0.65 | Enter Diagnostic Mode |

Low confidence alone does not trigger escalation. Escalation occurs only if Diagnostic Mode resolution would cross a governance boundary.

## Silent assumption allowance

Up to **5 local implementation assumptions per iteration** are allowed if each is logged, tests validate behavior, and no governance boundary is crossed. More than 5 required, enter Diagnostic Mode. This prevents decision paralysis.

## Diagnostic Mode (steps)

1. Root cause analysis
2. Minimal corrective change
3. Add protective test
4. Retry once
5. Log reasoning

Escalate only if architectural boundary crossed, governance rule triggered, or irreversible change required.

## Stall detection

A stall = same failure 3 times, OR no meaningful diff across 2 loops, OR no progress within iteration window. Response: enter Diagnostic Mode (above). If unresolved AND strategic, escalate. **Infinite retry loops are prohibited.**

---

# Escalation Protocol

Claude must never halt silently. Escalation must be rare and high-signal.

**Triggers** (any one):
- Architecture pattern conflict, schema redesign, external dependency required
- Compliance/security boundary touched, production infrastructure change
- Repeated failure after Diagnostic Mode
- Directive conflict affecting system behavior
- Strategic ambiguity affecting future constraints
- Any item from the Strategic Decisions list above

**Process:**
1. Write `/tmp/escalation.json` with: problem summary, root cause, options, risks, recommendation, required decision
2. Trigger `/execution/notify_owner.ts`
3. Continue work that is not blocked by the escalation

---

# Testing & Validation Rules (Non-Negotiable)

Testing is mandatory and gated. Claude designs tests; tools execute them.

## Unit testing

- All non-trivial execution logic must have unit tests
- Pure logic tested without I/O; external dependencies mocked
- Must be fast, deterministic, runnable locally

## Integration testing

- May touch dev sandboxes, test databases, mock APIs
- Must NEVER touch production
- Requires explicit opt-in (env flag or CI label)

## End-to-End & UI testing

Validates routing, links, forms, auth flows, permissions, UI state. Browser automation (Playwright) preferred. Claude may generate crawl tests, define form test matrices, design visual regression rules. Claude must NOT manually simulate UI behavior in prose.

## Worker testing

Workers tested as routing logic: correct script selection, retry behavior, idempotency, error handling. Workers must never send real communications during tests.

## Directive validation

Directives validated for: required sections, referenced files/scripts existence, markdown integrity, clarity for junior developers.

If behavior can be tested via code, do not validate it narratively.

---

# Test Strategy Framework (NEW)

Tests are not equally valuable. Distribute them deliberately.

## Test pyramid (target distribution)

| Tier | Target | Purpose |
|---|---|---|
| Unit | 70% | Fast, isolated, deterministic. Run on every save. |
| Integration | 20% | Module-to-module wiring, real DB on test instance, real API stubs. |
| E2E | 10% | Full user journey through deployed UI. Slow, expensive, fragile. Use sparingly. |

If your test suite is inverted (mostly E2E, few units), that is a defect to fix, not a style preference.

## Risk-based testing

Test density must scale with blast radius. Code that handles money, auth, scoring, learning paths, or external API calls requires more coverage than internal helpers. Touch a high-risk module -> add tests proportional to the risk, not proportional to the lines changed.

## Mandatory test types per feature

For every feature added, the test suite must cover all four:

1. **Happy path** - canonical input, expected output
2. **Failure path** - invalid input, downstream failure, timeout (see Failure-First Design)
3. **Boundary cases** - empty, max size, off-by-one, unicode, null, very large input
4. **Idempotency validation** - same input twice produces same output and same side effects (zero or one), never two (see Idempotency & Replayability)

A feature without all four test types is incomplete. Definition of Done blocks on it.

---

# Logging, Reporting & Progress Tracking

This section is **gated**. Failure to log or update progress is a process violation, not an oversight, and blocks Definition of Done.

## Per-change autonomy log

Maintain `/tmp/autonomy_log.json`. Append one entry per change:

```json
{
  "timestamp": "ISO-8601",
  "change_summary": "what was done",
  "files_touched": ["..."],
  "assumptions": ["..."],
  "confidence": 0.0,
  "tests_added": ["..."],
  "directives_updated": ["..."],
  "escalation_triggered": false
}
```

## PROGRESS.md update rule (HARD GATE)

After every completed change, before marking the change "done" in any sense, Claude MUST update `PROGRESS.md`. Non-compliance is a violation, not a forgetting.

**Required entry format** (append under the relevant task):

```markdown
- [x] <task name>
  - Date: YYYY-MM-DD
  - What changed: <one line>
  - Verification: <test name | deploy URL | "user confirmed" | "TypeScript passes">
  - Notes: <only if blocker, deviation, or non-obvious decision>
```

**Hard gates:**
1. **No code change is "done" without a PROGRESS.md entry.** Definition of Done explicitly blocks on this.
2. **No `[x]` mark without verification evidence on the same line.** Forbidden: marking complete based on intent. Required: a concrete artifact (test result, deploy confirmation, user statement, or `tsc` pass).
3. **Every commit that touches `/execution`, `/services`, `/frontend`, or `/backend` must also touch `PROGRESS.md`.** If it doesn't, the change is incomplete.
4. **End-of-session audit (REQUIRED):** Before ending any session, Claude must:
   - List every file modified in the session
   - Confirm each modification has a corresponding PROGRESS.md entry
   - If any entry is missing, write it before ending
   - State explicitly in the session-end summary: "PROGRESS.md audit: N changes, N entries, audit clean."

If PROGRESS.md does not exist, create it before doing any work.

## Session start protocol

At the start of every session:
1. Read `CLAUDE.md` (this file) fully
2. Read `PROGRESS.md` fully
3. Summarize current state and the first unchecked task
4. **Make no code changes during this step**

## Verification rule

Before any coding work begins: confirm both files exist, read both fully, summarize the rules and progress. No code changes during verification.

## Daily executive report

Worker `/services/worker/daily_report.ts` reads autonomy log, escalations, test results. Generates report covering: completed work, tests added, failures resolved, architectural changes, confidence averages, assumptions made, risk flags, open escalations, next milestones. Delivered via SMS summary, email detailed report, optional Slack. Claude does not send notifications directly.

---

# Observability Framework (NEW)

If a failure happens and we can't see it in the logs, it didn't happen until a customer complains. That is unacceptable.

## Structured logging

- All logs are JSON, one event per line, written to stdout
- Required fields per log line: `timestamp`, `level`, `event`, `correlation_id`, `module`
- No string-concatenated log messages with embedded values. Use structured fields.

## Per-execution telemetry

Every script and every API request must emit:

| Field | Purpose |
|---|---|
| `duration_ms` | How long it took |
| `status` | `success` / `failure` / `partial` |
| `error_class` | Categorical: `TimeoutError`, `ValidationError`, `UpstreamFailure`, etc. |
| `correlation_id` | UUID propagated across all sub-calls so a single user action is traceable end-to-end |

## Required metrics

For every recurring job and every endpoint:

- **Success rate** (rolling 24h)
- **Failure rate** (rolling 24h, broken down by `error_class`)
- **Retry count** (per execution)
- **Latency** (p50, p95, p99)

## Correlation IDs

- Generated at the entry point (HTTP request, scheduled trigger, CLI invocation)
- Propagated to every downstream call (DB, external API, sub-script)
- Included in every log line and every error report
- Returned in API response headers so the client can quote it when filing a bug

A bug report without a correlation ID is harder to fix. Make it impossible to omit.

See also: **Failure-First Design** (correlation IDs are mandatory in failure reports), **Production Readiness Principles** (logs as event streams).

---

# UI/UX Design Policy

## Design system

- **Framework:** Bootstrap 5 (CDN), utility-first. No custom CSS unless a class exists in `global.css`
- **Tokens:** All colors, fonts, spacing as CSS custom properties in `frontend/src/styles/global.css`
- **Never hardcode hex values.** Use `var(--color-*)` or Bootstrap utility classes

## Color palette

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#1a365d` | Navy: headings, primary buttons, brand |
| `--color-primary-light` | `#2b6cb0` | Links, hover states, focus outlines |
| `--color-secondary` | `#e53e3e` | Red: CTAs, warnings, destructive actions |
| `--color-accent` | `#38a169` | Green: success states, positive indicators |
| `--color-bg` | `#ffffff` | Page background |
| `--color-bg-alt` | `#f7fafc` | Alternate section backgrounds |
| `--color-text` | `#2d3748` | Body text |
| `--color-text-light` | `#718096` | Muted/secondary text |
| `--color-border` | `#e2e8f0` | Card borders, dividers |

## Component patterns

- **Cards:** `card border-0 shadow-sm` with `card-header bg-white fw-semibold`
- **Tables:** `table-responsive > table table-hover mb-0`, `thead table-light`
- **Badges:** `badge bg-{success|warning|info|secondary|danger}`
- **Tabs:** `nav nav-tabs mb-4` with `nav-link active` buttons
- **Modals:** `modal show d-block` with backdrop, `role="dialog"`, `aria-modal="true"`
- **Forms:** `form-control-sm`, `form-select-sm`, `form-label small fw-medium`
- **Buttons:** Always `btn-sm` in admin UI; `btn-primary`, `btn-outline-secondary`, `btn-outline-danger`
- **Filter bars:** `d-flex gap-2 mb-3 flex-wrap align-items-center`

## Accessibility (WCAG 2.1 AA required)

- **Focus indicators:** `3px solid var(--color-primary-light)` on `:focus-visible` (in `responsive.css`)
- **Touch targets:** Min 44x44px on mobile (in `responsive.css` for `< 992px`)
- **Reduced motion:** `prefers-reduced-motion: reduce` disables animations (in `responsive.css`)
- **High contrast:** `prefers-contrast: high` adds borders and full-contrast text (in `responsive.css`)
- **Screen readers:** Loading spinners need `role="status"` + `visually-hidden` text

## Available design skills

| Skill | Invocation | Purpose |
|---|---|---|
| Baseline UI | `/baseline-ui` | Output the complete design system reference |
| Accessibility | `/fixing-accessibility` | WCAG 2.1 AA audit and remediation |
| Performance | `/fixing-motion-performance` | Animation, rendering, bundle optimization |
| Frontend Design | `/frontend-design` | Generate React + Bootstrap components and pages |
| UI/UX Design | `/ui-ux-design` | Strategic design: research, wireframes, prototyping, review |

## Target audience

**Enterprise executives, aged 35-60.** Design must be clean, calm, and authoritative. Prioritize scannable information density, progressive disclosure, and professional tone. Think Bloomberg meets Salesforce, not consumer SaaS.

---

# Visual-Changes Walkthrough Workflow

Whenever the team ships visual/UX changes, produce a single self-contained HTML file the client (Luda, Vivek, Ram, or any reviewer) can walk through, mark up, and email back. Their reply is structured so that Claude Code can parse it and start the next round of fixes immediately. Mandatory for any project where non-technical reviewers approve UI work.

**Delivery standard (NON-NEGOTIABLE):** ship ONE HTML file. Screenshots are embedded as base64 `data:image/png;base64,...` URIs inside the HTML, so there is no zip, no folder, no extraction step on the reviewer's side. Attaching `WALKTHROUGH.html` directly to email is the only approved delivery format. Folder-based delivery (zip with separate PNGs) is forbidden because it caused repeat confusion in early rounds (clients clicked PNGs instead of the HTML, opened them in image viewers, lost the feedback widget).

## When to run

Run AFTER every batch of visual or UX changes: new/removed pages or sections, copy/label/layout changes, new components/modals/tooltips, visible style changes. A change qualifies if a screenshot can show "before" vs "after."

Do NOT run for: backend-only changes, schema changes with no UI surface, infrastructure work, log/telemetry changes.

## The two-script pipeline

### `backend/scripts/walkthrough_report.py` - captures screenshots

1. Creates a fresh test profile via the API (canonical test persona, e.g. Jennifer C)
2. Runs analysis pipeline end-to-end
3. Activates learning path (or equivalent end-state)
4. Generates first chapter / first content view
5. For each `CHANGES` entry: navigates to URL, optionally clicks tab/hovers element, injects JS to draw red rectangle + label, takes viewport screenshot, clears highlight
6. Cleans up test profile
7. Writes markdown summary

**Required fields per change:** `id` (stable, used as filename and email key), `title`, `category` (color-coded pill), `page_url` (with `{pid}`, `{path_id}`, `{lesson_id}` placeholders), `highlight_selector` OR `highlight_text`, `highlight_label`, `what_changed`, `why_changed`, `files_modified` (PARSED LATER for fix-routing), optional `click_tab` / `hover_first`.

### `backend/scripts/walkthrough_to_html.py` - renders self-contained HTML

Each PNG in `docs/walkthrough_report/screenshots/` is base64-encoded and inlined into the HTML as a `data:image/png;base64,...` URI. The output HTML is a single ~5-6 MB file that contains everything the reviewer needs.

**Required HTML features (all must be preserved in any reimplementation):**

1. **Sticky left sidebar with required reviewer-name input at top:** A yellow-highlighted "Your name" text input is the FIRST thing in the sidebar, before the search box and TOC. It is required to generate the feedback email; clicking Generate without it shows an alert and adds a red error border to the field. The value is saved to localStorage so it persists across reloads. Below it: numbered TOC linking to cards, color-coded category pills, status dots updating on Approved/Issue/Question, live progress strip (approved/issue/question/pending counts), live search filter.
2. **Category filter pills** at top of main column
3. **One card per change:** numbered header + title + category pill, live URL with copy button, yellow "To see this change" instruction strip, embedded screenshot (click to open at full resolution in new tab), "What was changed" / "Why" / "Files modified" sections
4. **Per-card feedback widget (CRITICAL):** Approved/Issue/Question radios, notes textarea (required for Issue/Question, optional for Approved), status colors card's left border (green/red/amber), notes auto-saved to localStorage
5. **Floating "Generate Feedback Email" button** bottom-right with reviewed-vs-total count
6. **Modal compiling all feedback** into the parseable email body (format below). The reviewer-name input lives in the SIDEBAR, never in the modal — the modal only shows after validation passes.
7. **mailto: handoff** pre-filling `ali@colaberry.com` with subject `AI Pathway walkthrough feedback - <YYYY-MM-DD>`

## Email format contract (DO NOT CHANGE LIGHTLY)

Strict format so Claude Code parses deterministically. Any change MUST be coordinated; the parser reads markers literally.

```
[ai-pathway-walkthrough-feedback-v1]
Report-Date: 2026-05-05
Reviewer: Luda Kopeikina
Total: 17 | Approved: 12 | Issues: 3 | Questions: 2 | Pending: 0

=== APPROVED (12) ===
- [01_homepage_simplified] Homepage simplified
- [03_skills_review_merged] Skill selection + self-assessment merged -- nice change
... (one line per approved item)

=== NEEDS CHANGE (3) ===

### 04_skill_hover_tooltip
Title: Hover tooltip with ontology description on skill name
URL: http://95.216.199.47:3000/analysis/abc-123
Files: frontend/src/components/SelfAssessment.tsx,frontend/src/pages/AnalysisPage.tsx
Feedback: Tooltip text is too small, please make it bigger and use a lighter background.

=== QUESTIONS (2) ===

### 16_implementation_task_section
Title: Implementation Task as 6th section (NEW)
URL: http://95.216.199.47:3000/learn/path-id/lesson/lesson-id
Question: How does the AI grading score actually work? What's the rubric?

[end-feedback]

---
Thanks,
Luda Kopeikina
```

**Format invariants:**
- Opening marker `[ai-pathway-walkthrough-feedback-v1]` is the version pin. Bump `v1` if format changes incompatibly.
- Closing marker `[end-feedback]` lets the parser ignore signature lines.
- Every NEEDS CHANGE / QUESTION block uses `### <change-id>` header matching `id` in `CHANGES` list.
- Each block has `Title:`, `URL:`, `Files:` (comma-separated), and either `Feedback:` (issue) or `Question:` (question).
- APPROVED entries: `- [<change-id>] <title> -- <optional notes>` (notes after `--`).
- `Total: ... | Approved: N | Issues: N | Questions: N | Pending: N` is regex-parseable.

## Parsing client replies

When Claude receives an email containing `[ai-pathway-walkthrough-feedback-v1]`:

1. Parse body into three lists: approved, issues, questions.
2. **For each ISSUE block:** open the files listed in `Files:`, make the change described in `Feedback:`.
3. **For each QUESTION block:** draft an answer (don't change code unless answer requires it). Include question + answer in reply email.
4. **For APPROVED items:** no action beyond acknowledging in reply.
5. Re-run both walkthrough scripts after fixing so next round has fresh screenshots.
6. Reply with confirmation listing what was fixed and which approved items shipped unchanged.

## Keeping CHANGES list in sync

`walkthrough_report.py` is canonical (it captures screenshots and persists the test profile so live URLs in the HTML stay clickable). `walkthrough_to_html.py` mirrors the CHANGES list with extra metadata and inlines each screenshot as base64. When adding a change: add to report.py, mirror in to_html.py with same `id`, run report.py (screenshots), run to_html.py (HTML), attach the resulting HTML directly to email.

`walkthrough_report.py` runs in two phases so URL/screenshot pairs always match the page state the reviewer will land on:

- **Phase 1 (pre-analysis):** captures items whose URL needs the `skill_selection` step (currently 03, 04, 05, 06, 17). The script navigates to `/analysis/{pid}?view=skill_selection` BEFORE running analysis, so the page renders the merged skill review layout. The `?view=skill_selection` URL param is honored by `AnalysisPage.tsx` as a state override on revisit.
- **Phase 2 (post-analysis):** runs `/analysis/full`, activates the path, generates the first chapter, then captures every other item on `/learn/...` URLs and item 08 on `results_review`.

After every run, verify with `walkthrough_verify.py` (Playwright audit) before sending. The audit fetches each card's URL, optionally clicks the named tab, and confirms the live page contains the text the card describes. All 17 cards must show `URL OK: yes` and `TEXT OK: yes` (or `n/a` for cards without a text expectation) before the HTML is shipped.

## Outputs and one-command rebuild

```
docs/walkthrough_report/
|-- WALKTHROUGH.html             # Single self-contained file (~5-6 MB) - ATTACH THIS
|-- WALKTHROUGH_REPORT.md        # Markdown fallback (internal reference)
|-- README.txt                   # Internal note about folder structure
`-- screenshots/                 # Source PNGs (already inlined into the HTML)
    |-- 01_homepage_simplified.png
    `-- ...
```

```bash
cd backend
py -3.12 scripts/walkthrough_report.py    # captures screenshots in two phases (~5 min)
py -3.12 scripts/walkthrough_to_html.py   # rebuilds HTML with embedded base64 screenshots (~1 sec)
py -3.12 scripts/walkthrough_verify.py    # audits each card via Playwright (~1 min)
start docs/walkthrough_report/WALKTHROUGH.html  # local preview before sending
```

**To deliver to the client: attach `docs/walkthrough_report/WALKTHROUGH.html` directly to the email. No zip. No folder. The HTML is the entire deliverable.** Use `scripts/send-luda-corrected-zip.js` style send pipeline, but with the HTML file as the only attachment (`Content-Type: text/html`, not `application/zip`).

---

# Pre-Demo Verification (HARD GATE before any customer-facing share)

The May 16 Dorothy F walkthrough surfaced four related production bugs that all shipped silently:

1. Chapter generator was emitting `SK.PRM.003` "Prompt debugging" content for every skill, because the prompt's INPUTS example used that skill and Gemini latched onto it. `meta.setdefault(...)` preserved the hallucinated identifier instead of overwriting it.
2. Eight `D.DOM` skills had empty `rubric_by_level` data so per-skill hover tooltips fell back to the generic proficiency-scale text.
3. The path generator emitted LLM-fabricated module titles ("Enhancing Educational Content with AI") that did not match the skill the module was actually about ("Draft -> critique -> revise"). Dashboard sidebar didn't match the Top 5 Skills page.
4. The frontend re-hydration path dropped `proficiency_descriptions` on revisited analyses, so even after the ontology was repaired, tooltips kept showing the fallback.

None of these would have been caught by unit tests or the visual walkthrough alone. They are user-flow bugs that only surface when you click through the live build the way a real reviewer will. **From now on, every customer-facing demo or share is gated on two passing checks.**

## Gate 1: production DB integrity sweep

```
docker exec ai-pathway-backend-1 python /app/sweep_integrity.py
```

(or locally: `py -3.12 backend/scripts/sweep_integrity.py` against the dev DB)

Verifies, with zero tolerance:
- Every skill in the ontology has a 6-level `rubric_by_level`.
- Every learning path's chapter `skill_id` resolves in the ontology (legacy paths with placeholder IDs are filtered).
- Every Module's `title` and `skill_name` equal the ontology canonical name.
- Every cached `Lesson.content.meta.skill_id` matches its parent module's `skill_id` (the SK.PRM.003 hallucination guard).
- Every Lesson title matches `<canonical_name>: L<cl> to L<tl>`.

Exits non-zero on any violation. **A non-zero exit blocks the demo.** Cached lesson mismatches mean wrong content is sitting in the DB waiting to be shown to a customer.

## Gate 2: end-to-end browser walkthrough of the demo profile

```
py -3.12 backend/scripts/verify_profile_e2e.py <profile_id>
```

Loads the Top 5 Skills page, the Learning Dashboard, and every module's first lesson in headless Chromium against the live production deployment. Asserts:

- The Top 5 page renders and per-skill hover tooltips show the per-skill rubric (not the generic fallback).
- The Learning Dashboard sidebar shows every module's title as the canonical ontology skill name.
- Every lesson generation returns `meta.skill_id == module.skill_id` (catches LLM identity drift in real time, not just at cache-read).

Screenshots are written to `docs/preflight/<profile_id>/`. Exits non-zero on any failure with a clear diff. **Run this script for every profile that will be demoed, the morning of the demo, against the production URL the customer will use.**

## When Gate 2 must be re-run

Re-run Gate 2 on a given profile whenever any of the following change:
- The chapter generator agent (`backend/app/agents/chapter_generator.py`), its prompt (`backend/app/data/chapter-generator-prompt.md`), or the chapter-spec schema.
- The path generator agent or the activation flow (`backend/app/api/routes/learning.py`).
- The ontology data (`backend/app/data/ontology.json`).
- The `SelfAssessment` / `AnalysisPage` / `LearningDashboardPage` / `LessonPage` frontend components.

If a Gate fails, do NOT manually patch around it ("I'll just clear that one lesson"). Find the root cause in the chapter generator, path generator, ontology, or hydration path, fix it there, and re-run both Gates until both pass.

## When the cache must be invalidated

After ANY change to chapter generation, prompt, or schema, also clear cached lesson content so users do not see stale wrong output. Pattern:

```python
async with AsyncSessionLocal() as db:
    r = await db.execute(select(Lesson).where(Lesson.content.isnot(None)))
    for ls in r.scalars().all():
        ls.content = None
        ls.status = 'not_started'
    await db.commit()
```

Or, for targeted invalidation, only clear lessons whose `content.meta.skill_id` mismatches the parent module's `skill_id` (see `sweep_integrity.py` for the query).

---

# Operational Credentials (retrieval, never commit values)

Two outbound credentials are not stored in this repo. Retrieve them at run time; never write the values to `.env` or commit them.

- **Mandrill API key (outbound email transport).** Pull from the prod `accelerator-backend` container env at send time:
  `ssh root@95.216.199.47 'docker exec accelerator-backend printenv MANDRILL_API_KEY'`. The stale `backend/scripts/.secrets/mandrill.txt` is NOT valid. SMTP: host `smtp.mandrillapp.com:587`, user `ali@colaberry.com`, pass = that key.
- **Basecamp OAuth token.** Lives in `CCPP.Basecamp_AuthInfo` (MSSQL on the prod server, reachable only from a prod container, e.g. `accelerator-backend`, which has `mssql` in `/app/node_modules`). Query: `SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive = 1 ORDER BY BasecampAuthInfoID DESC`; strip a leading `Bearer `. Run the DB read AND the Basecamp API call **in one process on prod** (`docker cp` the script into `accelerator-backend:/app/` so `require('mssql')` resolves, then `docker exec -w /app`) - fetching the ~400-char token across SSH/`docker exec` into the local shell mangles it. Account id `3945211`, AI Pathway bucket `46697389`. Caveat: the token rotates ~every 2 weeks via an external re-auth process; if Basecamp returns `401 OAuth token expired (rekeyed_identity)`, the stored token has been superseded server-side and the re-auth at `launchpad.37signals.com/authorization/new` must be re-run before BC writes will work. Not fixable by re-querying the DB.

# Tooling Assumptions

Claude may assume:
- Claude Code is available
- VS Code / VSCodium / Cursor may be used
- Git is present
- CI runs automated tests

Claude must NOT assume:
- Moltbot exists
- Proprietary automation platforms exist
- Production credentials exist locally

---

# Intern Safety Rules

This repository may be worked on by interns.

- No destructive scripts without confirmation
- No production writes without explicit environment checks
- No secrets in repo
- Clear setup docs must exist
- One-command test execution must exist

Optimize for clarity, reproducibility, and teachability.

---

# Definition of Done & Self-Strengthening

A change is complete only if ALL of the following are true:

- Tests exist and pass
- Directives updated if necessary
- No secrets introduced
- Validation scripts pass
- A junior developer can understand the change
- Assumptions logged (if any)
- No unresolved governance boundary crossed
- **PROGRESS.md updated with verification evidence (see Logging section, hard gate)**
- **`/tmp/autonomy_log.json` entry appended**
- **Feature has survived the BREAK phase of Build-Break-Harden** (failure-mode tests pass, see Build-Break-Harden Loop)
- **All four mandatory test types present: happy path, failure path, boundary cases, idempotency** (see Test Strategy Framework)
- **Module exposes a typed contract** (see Contract Enforcement Layer)
- **External calls have timeout, retry, and error handling defined** (see Security Enforcement Layer)

## Self-strengthening requirement

Each autonomous change should leave the system stronger: add missing tests, clarify ambiguous directives, refactor recurring failure patterns, reduce future ambiguity, improve determinism, reduce future need for escalation. Failures are inputs, not mistakes.

---

# Summary

Claude is the planner, validator, and system hardener, not the worker.

- Directives define intent
- Scripts execute deterministically
- Contracts enforce module boundaries
- Tests prove correctness across happy, failure, boundary, and idempotency paths
- Workers run the system
- Observability proves it ran correctly
- PROGRESS.md and autonomy logs prove what happened
- Build-Break-Harden ensures features survive failure
- Implementation ambiguity does not trigger escalation
- Strategic ambiguity does
- Escalation replaces paralysis

Be deliberate. Be testable. Be autonomous. Be governed only where necessary.
