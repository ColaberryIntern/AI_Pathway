import { useState } from "react";

// ============================================================
// JENNIFER C. — Chapter: Prompt Debugging & Iteration
// Skill: SK.PRM.003  |  Level 2 → Level 3  |  15 minutes
// 5-section structure: Scenario → Concepts → Example 1 → Example 2 → Build
// ============================================================

const LEARNER = {
  name: "Jennifer C.",
  role: "Freelance Senior Copywriter",
  industry: "Marketing & Creative",
  aiTools: "ChatGPT",
  coding: "No-code",
  targetRole: "AI Content Editor",
};

const SKILL = {
  id: "SK.PRM.003",
  name: "Prompt debugging & iteration",
  domain: "D.PRM — Prompting",
  from: {
    level: 2,
    label: "Literacy",
    rubric: "Knows that prompts can be revised when output is unsatisfactory",
  },
  to: {
    level: 3,
    label: "Practitioner",
    rubric: "Systematically debugs prompts: isolates variables, tests variations, logs results",
  },
};

// Sections
const SECTIONS = [
  { id: 1, title: "Scenario", minutes: 2, icon: "◐" },
  { id: 2, title: "Concepts", minutes: 3, icon: "◉" },
  { id: 3, title: "Example 1", minutes: 3, icon: "▲" },
  { id: 4, title: "Example 2", minutes: 4, icon: "▲▲" },
  { id: 5, title: "Build your agent", minutes: 3, icon: "✦" },
];

// ============================================================
// STYLING — editorial, warm, no AI-slop aesthetic
// Serif display font + clean sans body; warm paper palette
// ============================================================

const C = {
  ink: "#1a1915",
  ink2: "#4a463d",
  ink3: "#8a8578",
  paper: "#faf7f0",
  paper2: "#f3efe4",
  paper3: "#ebe5d3",
  rule: "#d9d1ba",
  accent: "#b8461e",      // editor's red
  accent2: "#c97d1e",     // highlighter amber
  sage: "#5a6b4e",        // calm green for "after"
  sageBg: "#e8ede1",
  clay: "#c9a489",        // warm tan
  ink4: "#2d2a24",
};

const FONT_DISPLAY = "'Fraunces', 'Playfair Display', Georgia, serif";
const FONT_BODY = "'Inter', system-ui, -apple-system, sans-serif";
const FONT_MONO = "'JetBrains Mono', ui-monospace, monospace";

// ============================================================
// APP
// ============================================================

export default function App() {
  const [active, setActive] = useState(1);
  const [completed, setCompleted] = useState(new Set());

  const complete = (n) => {
    setCompleted((prev) => new Set([...prev, n]));
    if (n < 5) setActive(n + 1);
  };

  const pct = (completed.size / 5) * 100;

  return (
    <div style={{ background: C.paper, minHeight: "100vh", fontFamily: FONT_BODY, color: C.ink }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        button { font-family: inherit; cursor: pointer; border: none; }
        .marker { background: linear-gradient(180deg, transparent 55%, ${C.accent2}55 55%); padding: 0 2px; }
        .scribble { position: relative; }
        .scribble::after { content:""; position:absolute; left:-4px; right:-4px; bottom:-3px; height:6px; border-bottom: 2px solid ${C.accent}; border-radius: 50%; opacity:.6; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
        .fade { animation: fadeUp 0.35s ease-out both; }
      `}</style>

      <Header skill={SKILL} learner={LEARNER} pct={pct} />

      <SectionNav sections={SECTIONS} active={active} completed={completed} onJump={setActive} />

      <main style={{ maxWidth: 820, margin: "0 auto", padding: "24px 24px 80px" }}>
        {active === 1 && <Section1 onDone={() => complete(1)} />}
        {active === 2 && <Section2 onDone={() => complete(2)} />}
        {active === 3 && <Section3 onDone={() => complete(3)} />}
        {active === 4 && <Section4 onDone={() => complete(4)} />}
        {active === 5 && <Section5 onDone={() => complete(5)} done={completed.has(5)} />}
      </main>
    </div>
  );
}

// ============================================================
// HEADER — book chapter opener
// ============================================================

function Header({ skill, learner, pct }) {
  return (
    <div style={{ background: C.paper2, borderBottom: `1px solid ${C.rule}` }}>
      <div style={{ maxWidth: 820, margin: "0 auto", padding: "28px 24px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 11, letterSpacing: "0.18em", textTransform: "uppercase", color: C.ink3, marginBottom: 8 }}>
              Chapter · {skill.id} · 15 minutes
            </div>
            <h1 style={{ fontFamily: FONT_DISPLAY, fontWeight: 500, fontSize: 36, lineHeight: 1.1, margin: "0 0 10px", color: C.ink, letterSpacing: "-0.01em" }}>
              Debugging a prompt <em style={{ color: C.accent }}>like an editor</em> debugs a draft
            </h1>
            <div style={{ fontSize: 14, color: C.ink2, fontStyle: "italic", fontFamily: FONT_DISPLAY }}>
              For {learner.name} — from Literacy (L2) to Practitioner (L3)
            </div>
          </div>

          <LevelBadge from={skill.from} to={skill.to} />
        </div>

        <div style={{ marginTop: 18, height: 4, background: C.paper3, borderRadius: 2, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${pct}%`, background: C.accent, transition: "width 0.4s" }} />
        </div>
      </div>
    </div>
  );
}

function LevelBadge({ from, to }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, background: C.paper, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "10px 14px" }}>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 10, letterSpacing: "0.15em", color: C.ink3, textTransform: "uppercase" }}>From</div>
        <div style={{ fontFamily: FONT_DISPLAY, fontSize: 22, fontWeight: 600, color: C.ink2 }}>L{from.level}</div>
        <div style={{ fontSize: 10, color: C.ink3 }}>{from.label}</div>
      </div>
      <div style={{ color: C.accent, fontSize: 18 }}>→</div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 10, letterSpacing: "0.15em", color: C.ink3, textTransform: "uppercase" }}>To</div>
        <div style={{ fontFamily: FONT_DISPLAY, fontSize: 22, fontWeight: 600, color: C.accent }}>L{to.level}</div>
        <div style={{ fontSize: 10, color: C.accent }}>{to.label}</div>
      </div>
    </div>
  );
}

// ============================================================
// SECTION NAV
// ============================================================

function SectionNav({ sections, active, completed, onJump }) {
  return (
    <div style={{ background: C.paper, borderBottom: `1px solid ${C.rule}`, position: "sticky", top: 0, zIndex: 10 }}>
      <div style={{ maxWidth: 820, margin: "0 auto", display: "flex", overflowX: "auto" }}>
        {sections.map((s) => {
          const isActive = active === s.id;
          const isDone = completed.has(s.id);
          return (
            <button
              key={s.id}
              onClick={() => onJump(s.id)}
              style={{
                flex: 1,
                minWidth: 120,
                padding: "14px 12px",
                background: "transparent",
                borderBottom: isActive ? `3px solid ${C.accent}` : `3px solid transparent`,
                color: isActive ? C.ink : C.ink3,
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                whiteSpace: "nowrap",
              }}
            >
              <span style={{ fontSize: 14, color: isDone ? C.sage : (isActive ? C.accent : C.ink3) }}>
                {isDone ? "✓" : s.icon}
              </span>
              <span>{s.title}</span>
              <span style={{ fontSize: 11, color: C.ink3 }}>{s.minutes}m</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ============================================================
// SHARED COMPONENTS
// ============================================================

function SectionHeader({ num, kicker, title, minutes }) {
  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.2em", color: C.accent, textTransform: "uppercase", marginBottom: 10, fontWeight: 600 }}>
        Section {num} · {minutes} min
      </div>
      <div style={{ fontFamily: FONT_DISPLAY, fontStyle: "italic", color: C.ink3, fontSize: 15, marginBottom: 6 }}>
        {kicker}
      </div>
      <h2 style={{ fontFamily: FONT_DISPLAY, fontWeight: 500, fontSize: 30, lineHeight: 1.15, margin: 0, color: C.ink, letterSpacing: "-0.01em" }}>
        {title}
      </h2>
    </div>
  );
}

function NextButton({ onClick, label = "Continue" }) {
  return (
    <div style={{ marginTop: 36, paddingTop: 20, borderTop: `1px solid ${C.rule}`, display: "flex", justifyContent: "flex-end" }}>
      <button
        onClick={onClick}
        style={{
          background: C.accent,
          color: C.paper,
          padding: "12px 24px",
          borderRadius: 6,
          fontSize: 14,
          fontWeight: 500,
          letterSpacing: "0.02em",
        }}
      >
        {label} →
      </button>
    </div>
  );
}

function Prose({ children, size = 16 }) {
  return <p style={{ fontSize: size, lineHeight: 1.65, color: C.ink2, margin: "0 0 14px" }}>{children}</p>;
}

// ============================================================
// SECTION 1 — SCENARIO + OBJECTIVES
// ============================================================

function Section1({ onDone }) {
  return (
    <div className="fade">
      <SectionHeader
        num={1}
        kicker="Where you are. Where you're going."
        title="The client email that keeps missing"
        minutes={2}
      />

      {/* Scenario card */}
      <div style={{ background: C.paper2, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "22px 26px", marginBottom: 28, borderLeft: `4px solid ${C.accent}` }}>
        <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.accent, textTransform: "uppercase", marginBottom: 10, fontWeight: 600 }}>
          The scenario
        </div>
        <p style={{ fontFamily: FONT_DISPLAY, fontSize: 18, lineHeight: 1.55, color: C.ink, margin: 0, fontStyle: "italic" }}>
          A new freelance client — a financial wellness brand — has asked you to use ChatGPT to draft
          a weekly email series. You write a prompt. The output is <span className="marker">close</span>, but the
          tone is off. It sounds generic. You rewrite the prompt, try again. Still off, in a different way.
          After six tries you're not sure what changed — or why any of them worked or didn't.
        </p>
      </div>

      {/* A to B */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: 16, alignItems: "stretch", marginBottom: 28 }}>
        <StateCard
          label="Where you are now"
          level="Level 2 · Literacy"
          quote="When the output isn't right, I rewrite the prompt and hope it gets better."
          color={C.ink3}
          bg={C.paper2}
        />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, color: C.accent, fontFamily: FONT_DISPLAY }}>
          →
        </div>
        <StateCard
          label="Where you'll be in 15 minutes"
          level="Level 3 · Practitioner"
          quote="I isolate what's broken, change one variable at a time, and log what I learn."
          color={C.sage}
          bg={C.sageBg}
        />
      </div>

      {/* Objectives */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.ink3, textTransform: "uppercase", marginBottom: 14, fontWeight: 600 }}>
          By the end of this chapter, you will:
        </div>
        {[
          "Diagnose which part of a prompt is causing a bad output — instead of rewriting the whole thing.",
          "Run a small, controlled test comparing two prompt variations to learn what actually moves the needle.",
          "Keep a simple debug log so you build a personal library of what works — and can hand it to an AI developer.",
        ].map((o, i) => (
          <div key={i} style={{ display: "flex", gap: 14, padding: "12px 0", borderBottom: i < 2 ? `1px solid ${C.rule}` : "none" }}>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 22, fontWeight: 600, color: C.accent, minWidth: 28 }}>
              0{i + 1}
            </div>
            <div style={{ fontSize: 15, lineHeight: 1.5, color: C.ink2, paddingTop: 4 }}>{o}</div>
          </div>
        ))}
      </div>

      {/* Why this matters for her */}
      <div style={{ background: C.paper3, borderRadius: 8, padding: "16px 20px", marginTop: 20, fontSize: 13, color: C.ink2, fontStyle: "italic", fontFamily: FONT_DISPLAY }}>
        <span style={{ fontWeight: 600, fontStyle: "normal", color: C.ink, marginRight: 6 }}>Why this matters:</span>
        The AI Content Editor role you're eyeing asks you to "collaborate with AI developers to refine
        content generation algorithms." That's prompt debugging. This is the skill that makes you
        useful to that team — not just another person typing into a chat box.
      </div>

      <NextButton onClick={onDone} label="Start the concepts" />
    </div>
  );
}

function StateCard({ label, level, quote, color, bg }) {
  return (
    <div style={{ background: bg, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "18px 20px" }}>
      <div style={{ fontSize: 10, letterSpacing: "0.18em", color: C.ink3, textTransform: "uppercase", marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: color, marginBottom: 12 }}>{level}</div>
      <div style={{ fontFamily: FONT_DISPLAY, fontStyle: "italic", fontSize: 15, lineHeight: 1.5, color: C.ink2 }}>
        "{quote}"
      </div>
    </div>
  );
}

// ============================================================
// SECTION 2 — CONCEPTS: the PIVOT method (3 cards)
// ============================================================

function Section2({ onDone }) {
  const [flipped, setFlipped] = useState({});
  const toggle = (i) => setFlipped((p) => ({ ...p, [i]: !p[i] }));

  const concepts = [
    {
      letter: "I",
      word: "Isolate",
      headline: "Find the one piece that's broken.",
      body: "A prompt has parts: role, task, context, examples, format, constraints. When output is off, one of those parts is usually the culprit — not the whole prompt.",
      analogy: "Like editing a paragraph: you find the weak sentence, not rewrite the whole page.",
      color: C.accent,
      bg: "#f9e9e1",
    },
    {
      letter: "V",
      word: "Vary one thing",
      headline: "Change one variable. Keep the rest constant.",
      body: "If you change three things at once and the output improves, you don't know which change worked. Change one, compare the output, then move on.",
      analogy: "Like testing a recipe: don't swap the flour AND the oven temp in the same batch.",
      color: C.accent2,
      bg: "#faefdc",
    },
    {
      letter: "L",
      word: "Log it",
      headline: "Write down what you tried and what happened.",
      body: "Memory lies. A simple log (prompt version, what changed, output quality 1-5, note) turns 'I'm fiddling' into 'I'm learning.' It's also what separates L2 from L3.",
      analogy: "Like a writer's notebook: you don't remember every good line, you capture it.",
      color: C.sage,
      bg: C.sageBg,
    },
  ];

  return (
    <div className="fade">
      <SectionHeader
        num={2}
        kicker="The mental model."
        title="The IVL method: three moves, in order"
        minutes={3}
      />

      <Prose>
        Most people at Level 2 treat a bad output as a signal to <em>rewrite the whole prompt</em>. Level 3
        treats it as a <span className="marker">diagnostic puzzle</span>. Here are the three moves that make the difference.
      </Prose>

      <div style={{ display: "grid", gap: 14, marginTop: 24 }}>
        {concepts.map((c, i) => (
          <div
            key={i}
            onClick={() => toggle(i)}
            style={{
              background: c.bg,
              border: `1px solid ${C.rule}`,
              borderLeft: `5px solid ${c.color}`,
              borderRadius: 8,
              padding: "18px 22px",
              cursor: "pointer",
              transition: "transform 0.15s",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", gap: 18 }}>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: 48, fontWeight: 700, color: c.color, lineHeight: 1, minWidth: 40 }}>
                {c.letter}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: FONT_DISPLAY, fontSize: 22, fontWeight: 600, color: C.ink, marginBottom: 4 }}>
                  {c.word}
                </div>
                <div style={{ fontSize: 15, fontWeight: 500, color: C.ink, marginBottom: 8 }}>
                  {c.headline}
                </div>
                <div style={{ fontSize: 14, lineHeight: 1.6, color: C.ink2, marginBottom: flipped[i] ? 10 : 0 }}>
                  {c.body}
                </div>
                {flipped[i] && (
                  <div className="fade" style={{ fontSize: 13, fontStyle: "italic", color: C.ink2, fontFamily: FONT_DISPLAY, paddingTop: 10, borderTop: `1px dashed ${C.rule}` }}>
                    <span style={{ fontWeight: 600, fontStyle: "normal", color: c.color, marginRight: 6 }}>Analogy →</span>
                    {c.analogy}
                  </div>
                )}
                {!flipped[i] && (
                  <div style={{ fontSize: 11, color: C.ink3, marginTop: 8, letterSpacing: "0.08em" }}>
                    Tap for the writer's analogy
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 28, padding: "16px 20px", background: C.paper2, borderRadius: 8, display: "flex", gap: 14, alignItems: "center" }}>
        <div style={{ fontFamily: FONT_DISPLAY, fontSize: 36, color: C.accent, fontStyle: "italic", lineHeight: 1 }}>
          "
        </div>
        <div style={{ fontSize: 14, color: C.ink2, lineHeight: 1.55, fontStyle: "italic", fontFamily: FONT_DISPLAY }}>
          If you only remember one thing: <strong style={{ color: C.ink, fontStyle: "normal" }}>change one variable at a time.</strong>
          Every other move flows from that.
        </div>
      </div>

      <NextButton onClick={onDone} label="See it in action →" />
    </div>
  );
}

// ============================================================
// SECTION 3 — EXAMPLE 1: Tone debugging (beginner applied)
// ============================================================

function Section3({ onDone }) {
  const [step, setStep] = useState(0);

  return (
    <div className="fade">
      <SectionHeader
        num={3}
        kicker="Example one."
        title="Debugging a tone problem"
        minutes={3}
      />

      <Prose>
        The client wants warm, human financial-wellness emails. Your first draft prompt gets you
        output that reads like a bank pamphlet. Let's debug it — with the IVL method.
      </Prose>

      <ExamplePanel label="The original prompt (v1)" color={C.ink3}>
        <PromptBlock
          text={`Write a weekly email to subscribers about building an emergency fund. Make it friendly.`}
        />
        <OutputBlock
          rating={2}
          text={`Dear Valued Subscriber,
An emergency fund is a critical financial instrument that provides stability during unexpected circumstances. Experts recommend saving 3–6 months of expenses...`}
          diagnosis={`Reads like a bank pamphlet. The word "friendly" is doing all the work — and ChatGPT doesn't know what friendly means to this brand.`}
        />
      </ExamplePanel>

      {step >= 1 && (
        <div className="fade">
          <StepLabel step={1} title="Isolate: which part is broken?" color={C.accent} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 24, fontSize: 13 }}>
            {[
              { part: "Task", status: "✓ clear", broken: false },
              { part: "Audience", status: "partial", broken: false },
              { part: "Tone guidance", status: "✗ vague", broken: true },
              { part: "Examples", status: "✗ missing", broken: true },
            ].map((p, i) => (
              <div key={i} style={{
                padding: "10px 14px",
                background: p.broken ? "#fdecec" : C.paper2,
                border: `1px solid ${p.broken ? C.accent : C.rule}`,
                borderRadius: 6,
                display: "flex", justifyContent: "space-between", alignItems: "center",
              }}>
                <span style={{ fontWeight: 500 }}>{p.part}</span>
                <span style={{ color: p.broken ? C.accent : C.ink3, fontSize: 12 }}>{p.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {step >= 2 && (
        <div className="fade">
          <StepLabel step={2} title="Vary one thing: replace 'friendly' with a concrete tone sample" color={C.accent2} />
          <ExamplePanel label="The iterated prompt (v2)" color={C.accent2}>
            <PromptBlock
              text={`Write a weekly email to subscribers about building an emergency fund.

Match the tone of this sample from our brand:
"Hey — real talk. Life throws curveballs, and an emergency fund is what keeps a flat tire from becoming a financial crisis. Here's how to start one, without feeling like you're punishing yourself."

Keep it conversational, use "you," avoid words like "instrument" or "strategically."`}
            />
            <OutputBlock
              rating={4}
              text={`Hey — let's talk about the one thing that separates "I've got this" from "I'm panicking at 2am": an emergency fund.
The good news? You don't need thousands to start. Even $20 a week, tucked into a separate account, is a real safety net in 6 months...`}
              diagnosis={`Big improvement. One variable changed — tone guidance — and the fix landed. That's your L3 move.`}
            />
          </ExamplePanel>
        </div>
      )}

      {step >= 3 && (
        <div className="fade">
          <StepLabel step={3} title="Log it: what did you learn?" color={C.sage} />
          <div style={{ background: C.sageBg, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "18px 22px", marginBottom: 20 }}>
            <div style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.ink2, lineHeight: 1.8 }}>
              <div><span style={{ color: C.ink3 }}>prompt_id:</span> emergency-fund-email-v2</div>
              <div><span style={{ color: C.ink3 }}>change:</span> replaced "friendly" with sample paragraph + banned words</div>
              <div><span style={{ color: C.ink3 }}>output_quality:</span> 4/5 (was 2/5)</div>
              <div><span style={{ color: C.ink3 }}>lesson:</span> abstract tone words don't work. Show, don't tell.</div>
              <div><span style={{ color: C.ink3 }}>reuse:</span> paste brand sample into every copywriting prompt from now on</div>
            </div>
          </div>
        </div>
      )}

      <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
        {step < 3 ? (
          <button
            onClick={() => setStep(step + 1)}
            style={{
              background: C.ink,
              color: C.paper,
              padding: "10px 18px",
              borderRadius: 6,
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            {step === 0 ? "Show me step 1 →" : step === 1 ? "Show me step 2 →" : "Show me step 3 →"}
          </button>
        ) : (
          <NextButton onClick={onDone} label="Ready for example 2 →" />
        )}
      </div>
    </div>
  );
}

function StepLabel({ step, title, color }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "24px 0 14px" }}>
      <div style={{ background: color, color: C.paper, width: 28, height: 28, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT_DISPLAY, fontSize: 14, fontWeight: 600 }}>
        {step}
      </div>
      <div style={{ fontFamily: FONT_DISPLAY, fontSize: 20, fontWeight: 500, color: C.ink }}>{title}</div>
    </div>
  );
}

function ExamplePanel({ label, color, children }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <div style={{ fontSize: 11, letterSpacing: "0.18em", color: color, textTransform: "uppercase", marginBottom: 10, fontWeight: 600 }}>
        {label}
      </div>
      {children}
    </div>
  );
}

function PromptBlock({ text }) {
  return (
    <div style={{ background: "#2d2a24", color: "#f0ebdb", fontFamily: FONT_MONO, fontSize: 12.5, lineHeight: 1.6, padding: "14px 18px", borderRadius: 6, marginBottom: 10, whiteSpace: "pre-wrap" }}>
      <div style={{ fontSize: 10, letterSpacing: "0.15em", color: "#8a8578", marginBottom: 8, textTransform: "uppercase" }}>
        Prompt
      </div>
      {text}
    </div>
  );
}

function OutputBlock({ text, rating, diagnosis }) {
  return (
    <div style={{ background: C.paper, border: `1px solid ${C.rule}`, borderRadius: 6, padding: "14px 18px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <div style={{ fontSize: 10, letterSpacing: "0.15em", color: C.ink3, textTransform: "uppercase" }}>
          Output
        </div>
        <Stars n={rating} />
      </div>
      <div style={{ fontSize: 13.5, lineHeight: 1.6, color: C.ink2, marginBottom: 12, fontStyle: "italic", fontFamily: FONT_DISPLAY }}>
        {text}
      </div>
      {diagnosis && (
        <div style={{ fontSize: 12, color: C.accent, borderTop: `1px dashed ${C.rule}`, paddingTop: 10, fontStyle: "italic" }}>
          <strong style={{ fontStyle: "normal" }}>Diagnosis:</strong> {diagnosis}
        </div>
      )}
    </div>
  );
}

function Stars({ n }) {
  return (
    <div style={{ display: "flex", gap: 2 }}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} style={{ color: i <= n ? C.accent2 : C.rule, fontSize: 13 }}>★</span>
      ))}
    </div>
  );
}

// ============================================================
// SECTION 4 — EXAMPLE 2: A/B testing two prompt variations
// ============================================================

function Section4({ onDone }) {
  const [picked, setPicked] = useState(null);

  const variants = [
    {
      id: "A",
      label: "Variant A — Role first",
      prompt: `You are a fitness copywriter who writes for busy parents.

Write a 40-word product description for a noise-cancelling yoga mat.
Emphasize: durability, quiet use (kids sleeping), 60-day trial.`,
      output: `Yoga on your schedule — even when the baby's finally down. Our noise-cancelling mat grips quietly on any floor, holds up to daily use, and comes with a 60-day trial. No creaks. No excuses. Just ten stolen minutes.`,
      rating: 5,
      why: "The role ('fitness copywriter for busy parents') primes the model with an audience + voice before it sees the task. Result reads like a human wrote it.",
    },
    {
      id: "B",
      label: "Variant B — Task first",
      prompt: `Write a 40-word product description for a noise-cancelling yoga mat.
Emphasize: durability, quiet use (kids sleeping), 60-day trial.
Target audience: busy parents.`,
      output: `Introducing our premium noise-cancelling yoga mat — designed for durability and quiet use, so you can exercise without waking the kids. Built to last, backed by a 60-day trial. Perfect for busy parents who need a reliable fitness solution.`,
      rating: 3,
      why: "Same information, different order. Without a role framing, the model defaults to generic product-catalog voice ('Introducing our premium...', 'fitness solution').",
    },
  ];

  return (
    <div className="fade">
      <SectionHeader
        num={4}
        kicker="Example two — closer to real work."
        title="A/B testing two prompt variations"
        minutes={4}
      />

      <Prose>
        Same task. Same information. Two different ways to <em>structure</em> the prompt. Which one wins?
        This is what Level 3 looks like in the wild: you run the test, compare, and
        <span className="marker"> log what you learned</span>.
      </Prose>

      <div style={{ background: C.paper2, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "16px 20px", marginBottom: 24, fontSize: 13, color: C.ink2 }}>
        <strong style={{ color: C.ink }}>The test:</strong> Does putting the role <em>before</em> the task produce better output than putting it after?
        One variable changed. Everything else identical.
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 24 }}>
        {variants.map((v) => {
          const isPicked = picked === v.id;
          return (
            <button
              key={v.id}
              onClick={() => setPicked(v.id)}
              style={{
                background: isPicked ? C.paper : C.paper2,
                border: `2px solid ${isPicked ? C.accent : C.rule}`,
                borderRadius: 8,
                padding: "16px 18px",
                textAlign: "left",
                transition: "all 0.2s",
              }}
            >
              <div style={{ fontSize: 11, letterSpacing: "0.15em", color: C.accent, marginBottom: 6, fontWeight: 600, textTransform: "uppercase" }}>
                {v.label}
              </div>
              <div style={{ fontFamily: FONT_MONO, fontSize: 11.5, lineHeight: 1.5, color: C.ink2, whiteSpace: "pre-wrap", background: "#2d2a24", color: "#f0ebdb", padding: "10px 12px", borderRadius: 4 }}>
                {v.prompt}
              </div>
              {!isPicked && (
                <div style={{ fontSize: 12, color: C.ink3, marginTop: 10, textAlign: "center", fontStyle: "italic" }}>
                  Tap to see the output
                </div>
              )}
              {isPicked && (
                <div className="fade" style={{ marginTop: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <div style={{ fontSize: 10, letterSpacing: "0.15em", color: C.ink3, textTransform: "uppercase" }}>Output</div>
                    <Stars n={v.rating} />
                  </div>
                  <div style={{ fontSize: 13, lineHeight: 1.55, color: C.ink2, fontFamily: FONT_DISPLAY, fontStyle: "italic", marginBottom: 10 }}>
                    {v.output}
                  </div>
                  <div style={{ fontSize: 11.5, color: C.ink2, borderTop: `1px dashed ${C.rule}`, paddingTop: 8 }}>
                    <strong style={{ color: C.accent }}>Why:</strong> {v.why}
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {picked && (
        <div className="fade">
          <div style={{ background: C.sageBg, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "18px 22px", marginBottom: 20 }}>
            <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.sage, textTransform: "uppercase", marginBottom: 10, fontWeight: 600 }}>
              Entry added to your debug log
            </div>
            <div style={{ fontFamily: FONT_MONO, fontSize: 12, color: C.ink2, lineHeight: 1.8 }}>
              <div><span style={{ color: C.ink3 }}>test:</span> role placement — before vs. after task</div>
              <div><span style={{ color: C.ink3 }}>winner:</span> Variant A (role first) — 5/5 vs 3/5</div>
              <div><span style={{ color: C.ink3 }}>lesson:</span> prime voice before asking for work. Role = audience lens.</div>
              <div><span style={{ color: C.ink3 }}>apply to:</span> all voicey copy tasks (emails, social, landing pages)</div>
            </div>
          </div>

          <div style={{ background: C.paper3, borderRadius: 8, padding: "16px 20px", fontSize: 13, color: C.ink2, fontStyle: "italic", fontFamily: FONT_DISPLAY, marginBottom: 8 }}>
            <span style={{ fontWeight: 600, fontStyle: "normal", color: C.ink, marginRight: 6 }}>What just happened:</span>
            You ran a controlled A/B test. One variable. Two outputs. A reusable lesson. That's
            the exact workflow an AI developer would expect you to bring to a content-optimization sprint.
          </div>
        </div>
      )}

      {picked ? (
        <NextButton onClick={onDone} label="Build your own debug agent →" />
      ) : (
        <div style={{ marginTop: 30, padding: "14px 18px", background: C.paper2, borderRadius: 6, fontSize: 13, color: C.ink3, textAlign: "center", fontStyle: "italic" }}>
          Tap a variant above to see how it performed.
        </div>
      )}
    </div>
  );
}

// ============================================================
// SECTION 5 — BUILD YOUR OWN AGENT
// A reusable custom GPT / system prompt: "Prompt Debug Coach"
// Scaffolded for curious explorer / no-code level
// ============================================================

function Section5({ onDone, done }) {
  const [copied, setCopied] = useState(false);
  const [filled, setFilled] = useState({ topic: "", tone: "", avoid: "" });

  const systemPrompt = `You are my Prompt Debug Coach. You help me (a ${LEARNER.role}) systematically improve prompts for ChatGPT using the IVL method.

When I paste in a prompt and its output, you will:

1. ISOLATE — identify which part of the prompt is likely causing the issue. Check these parts in order:
   • Role / persona
   • Task clarity
   • Audience
   • Tone (is it described abstractly, or shown with a sample?)
   • Format / length
   • Constraints

2. VARY — suggest exactly ONE change to test. Not three. One. Explain why this variable.

3. LOG — after I share the new output, help me record a one-line lesson in this format:
   "[What I changed] → [quality change 1-5] → [what I learned]"

Rules for you:
• Ask me for the output quality on a 1-5 scale before diagnosing.
• Never rewrite the whole prompt. Suggest isolated changes.
• If I try to change multiple things at once, push back — remind me the test only works with one variable.
• When I've logged 5 lessons, suggest a "patterns recap" — what's worked across my tests.

My domain: ${filled.topic || "[YOUR CONTENT AREA — e.g., financial wellness emails]"}
My brand tone: ${filled.tone || "[PASTE A 2-3 SENTENCE SAMPLE OF YOUR BRAND VOICE]"}
Words I never use: ${filled.avoid || "[LIST 3-5 BANNED WORDS — e.g., instrument, solution, utilize]"}`;

  const copyPrompt = () => {
    navigator.clipboard.writeText(systemPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fade">
      <SectionHeader
        num={5}
        kicker="Your turn."
        title="Build your Prompt Debug Coach"
        minutes={3}
      />

      <Prose>
        Here's your takeaway artifact. It's a <strong style={{ color: C.ink }}>custom GPT instruction set</strong> that turns
        ChatGPT into a debugging partner — one that forces the IVL method on you every time.
        No code. Copy, paste, and personalize three fields.
      </Prose>

      {/* What it does */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 24 }}>
        {[
          { t: "Asks for a rating", d: "Before diagnosing, it asks you to score the output 1-5." },
          { t: "Suggests ONE change", d: "Blocks you from changing three things at once." },
          { t: "Logs your lessons", d: "Formats your learnings into a reusable log." },
        ].map((f, i) => (
          <div key={i} style={{ background: C.paper2, border: `1px solid ${C.rule}`, borderRadius: 6, padding: "14px 16px" }}>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 14, fontWeight: 600, color: C.accent, marginBottom: 6 }}>
              {f.t}
            </div>
            <div style={{ fontSize: 12, color: C.ink2, lineHeight: 1.5 }}>{f.d}</div>
          </div>
        ))}
      </div>

      {/* Three fill-ins */}
      <div style={{ background: C.paper2, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "20px 24px", marginBottom: 20 }}>
        <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.accent, textTransform: "uppercase", marginBottom: 14, fontWeight: 600 }}>
          Step 1 · Personalize three fields
        </div>
        <FormField
          label="Your content area"
          placeholder="e.g., financial wellness emails for first-time savers"
          value={filled.topic}
          onChange={(v) => setFilled({ ...filled, topic: v })}
        />
        <FormField
          label="Your brand tone (2-3 sentence sample)"
          placeholder="e.g., Hey — real talk. Life throws curveballs..."
          value={filled.tone}
          onChange={(v) => setFilled({ ...filled, tone: v })}
          textarea
        />
        <FormField
          label="Banned words (comma separated)"
          placeholder="e.g., instrument, solution, utilize, leverage"
          value={filled.avoid}
          onChange={(v) => setFilled({ ...filled, avoid: v })}
        />
      </div>

      {/* The prompt */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.accent, textTransform: "uppercase", fontWeight: 600 }}>
            Step 2 · Copy this and paste it as your first message to ChatGPT
          </div>
          <button
            onClick={copyPrompt}
            style={{
              background: copied ? C.sage : C.ink,
              color: C.paper,
              padding: "8px 14px",
              borderRadius: 5,
              fontSize: 12,
              fontWeight: 500,
            }}
          >
            {copied ? "✓ Copied" : "Copy prompt"}
          </button>
        </div>
        <div style={{ background: "#2d2a24", color: "#f0ebdb", fontFamily: FONT_MONO, fontSize: 11.5, lineHeight: 1.65, padding: "18px 22px", borderRadius: 6, whiteSpace: "pre-wrap", maxHeight: 320, overflowY: "auto" }}>
          {systemPrompt}
        </div>
      </div>

      {/* How to use */}
      <div style={{ background: C.paper3, borderRadius: 8, padding: "18px 22px", marginBottom: 24 }}>
        <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.ink, textTransform: "uppercase", marginBottom: 12, fontWeight: 600 }}>
          Step 3 · Use it
        </div>
        <ol style={{ margin: 0, paddingLeft: 20, fontSize: 13.5, color: C.ink2, lineHeight: 1.8 }}>
          <li>Open a new ChatGPT conversation and paste the prompt above as your first message.</li>
          <li>Next time you have a prompt that isn't working, paste the prompt and the bad output.</li>
          <li>Answer its 1-5 rating question. Follow its ONE suggested change.</li>
          <li>Paste the new output. Log the lesson in whatever tool you like (Notion, a Google Doc, even a notes app).</li>
          <li>After 5 lessons, ask it: <em>"What patterns do you see across my tests?"</em></li>
        </ol>
      </div>

      {/* Final A→B confirmation */}
      <div style={{ background: C.sageBg, border: `1px solid ${C.rule}`, borderRadius: 8, padding: "20px 24px", marginBottom: 20 }}>
        <div style={{ fontSize: 11, letterSpacing: "0.18em", color: C.sage, textTransform: "uppercase", marginBottom: 10, fontWeight: 600 }}>
          You just leveled up
        </div>
        <div style={{ fontFamily: FONT_DISPLAY, fontSize: 18, lineHeight: 1.55, color: C.ink, fontStyle: "italic", marginBottom: 12 }}>
          "I isolate what's broken, change one variable at a time, and log what I learn."
        </div>
        <div style={{ fontSize: 13, color: C.ink2, lineHeight: 1.6 }}>
          That sentence is the rubric for Level 3 Practitioner on SK.PRM.003. Keep your log going
          for two weeks and you'll have the exact kind of artifact an AI developer wants to see
          when you apply for that AI Content Editor role.
        </div>
      </div>

      {!done && <NextButton onClick={onDone} label="Mark chapter complete ✓" />}

      {done && (
        <div style={{ textAlign: "center", padding: "24px 0", fontFamily: FONT_DISPLAY, fontSize: 18, fontStyle: "italic", color: C.accent }}>
          Chapter complete. Next up: <strong style={{ fontStyle: "normal" }}>SK.PRM.011 — Rubrics as prompts</strong>.
        </div>
      )}
    </div>
  );
}

function FormField({ label, placeholder, value, onChange, textarea }) {
  const Comp = textarea ? "textarea" : "input";
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: "block", fontSize: 12, color: C.ink2, marginBottom: 6, fontWeight: 500 }}>
        {label}
      </label>
      <Comp
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={textarea ? 3 : undefined}
        style={{
          width: "100%",
          fontFamily: FONT_BODY,
          fontSize: 13.5,
          padding: "10px 12px",
          background: C.paper,
          border: `1px solid ${C.rule}`,
          borderRadius: 5,
          color: C.ink,
          resize: textarea ? "vertical" : "none",
          outline: "none",
        }}
      />
    </div>
  );
}
