require('dotenv').config();

const SHOULD_SEND = process.argv.includes('--send');

const TO = ['ram@colaberry.com'];
const CC = ['ludakopeikina@gmail.com', 'vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: AI Pathway - status across your 4 prep personas';
// In-Reply-To header so Gmail threads it correctly on Ram's reply
const IN_REPLY_TO = '<CAAJ4MpcsW0WGcLQ4xT0Z4cKK4Y@example.com>';  // placeholder; gmail will thread by subject regardless

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Ram,</p>

  <p>Good questions. Quick context first, then the role of each agent, then how they actually assure quality.</p>

  <p><strong>Why we introduced this team</strong></p>
  <p>Across the last five rounds of customer testing with Luda, every issue surfaced AFTER she found it. The pattern was reactive. Each fix was correct on its own, but a real reviewer kept being the one to catch drift first. That is a bad look for a tool we want to demo to enterprise buyers, and it does not scale to multiple personas or external pilots.</p>
  <p>The five-agent team is the structural answer: it runs the same checks Luda would run, before Luda has to run them. When the team flags an issue, we fix it before the customer sees it. Result: the May 19 Halyna depth concern was the first issue the team caught and surfaced on its own, before Luda re-tested.</p>

  <p><strong>What each agent does</strong></p>
  <table cellpadding="6" cellspacing="0" border="0" style="border-collapse:collapse;font-size:13px;margin:8px 0">
    <thead>
      <tr style="background:#edf2f7">
        <th style="text-align:left;border-bottom:2px solid #cbd5e0;padding:8px">Agent</th>
        <th style="text-align:left;border-bottom:2px solid #cbd5e0;padding:8px">Job</th>
        <th style="text-align:left;border-bottom:2px solid #cbd5e0;padding:8px">Can block?</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top"><strong>Customer Voice</strong></td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Reads Luda's verbatim quotes from each persona and compares them against the current engine output. Asks: does the tool address what the customer actually wants, not just the literal request? Pushes back when intent is missed.</td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Yes</td>
      </tr>
      <tr>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top"><strong>Skill Curator</strong></td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Independent ontology expert. Re-runs Luda's 5-parameter rubric scoring (Importance, Breadth, Momentum, Connectivity, Career Signal) from scratch, compares against the engine output, and blocks if forbidden skills appear in the top 5 or expected skills are missing.</td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Yes</td>
      </tr>
      <tr>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top"><strong>Path Coherence Auditor</strong></td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Deterministic database checks. Verifies that every chapter's skill ID resolves in the ontology, dashboard module names match the Top 5 page, cached chapter content matches its parent module, and chapter numbering is contiguous. Catches the May 16 Dorothy F bug class structurally.</td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Yes</td>
      </tr>
      <tr>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top"><strong>Chapter Reviewer</strong></td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Reads the actual generated chapter content. Identity check (does the chapter actually teach the right skill?) plus prose-fit check (does a marketing chapter mention campaigns, not generic documents?). Catches the SK.PRM.003 hallucination class of bug.</td>
        <td style="border-bottom:1px solid #e2e8f0;padding:8px;vertical-align:top">Yes</td>
      </tr>
      <tr>
        <td style="padding:8px;vertical-align:top"><strong>Demo-Readiness Gate</strong></td>
        <td style="padding:8px;vertical-align:top">Synthesizes the four upstream verdicts into one GREEN / YELLOW / RED signal and renders a readable dossier per persona suitable for attaching to a "ready to share" decision.</td>
        <td style="padding:8px;vertical-align:top">Yes</td>
      </tr>
    </tbody>
  </table>

  <p><strong>How they assure quality</strong></p>
  <ul>
    <li><strong>Independence.</strong> Each agent runs separately and produces its own verdict. They are not aware of each other's conclusions while they reason. When they agree, that is high signal; when they disagree, that is exactly where we look closely. On the May 19 Halyna pass, the deterministic Skill Curator and the LLM-based Customer Voice independently arrived at the same finding from different starting points.</li>
    <li><strong>Customer-quote grounded.</strong> Every Customer Voice finding cites Luda's exact words from her emails. We are not asking the model to imagine what the customer would want; we are asking it to compare engine output against quoted customer feedback. The persona corpus pins these quotes in the repo so they cannot drift.</li>
    <li><strong>Deterministic where possible, LLM where necessary.</strong> Path Coherence and the Skill Curator's rubric math are pure Python. There is no model temperature affecting whether the database has the right state. The LLM agents only judge things that require reading prose (Customer Voice, Chapter Reviewer prose-fit).</li>
    <li><strong>Auditable.</strong> Every run produces a Markdown dossier with the per-agent reasoning and the customer quotes that drove each finding. We can show this dossier to a customer ("here is exactly why we are confident") or to ourselves on the next round ("here is what we missed last time").</li>
    <li><strong>Pre-demo gate.</strong> Nothing is shipped to a customer until the Demo-Readiness Gate returns GREEN or YELLOW with documented caveats. RED blocks the share until the underlying finding is fixed.</li>
  </ul>

  <p>One concrete proof point: on the May 19 Halyna pass, the Customer Voice agent independently quoted Luda's "tool pulled rather rudimentary skills" line and flagged that even after our P0 / P1 fixes, the engine still was not surfacing foundational PRM skills the way Claude did. We shipped the foundational-PRM injection on May 20 specifically because the agent caught it. Without the team, we would have learned that from Luda's next email instead.</p>

  <p>Happy to walk you through a live run on any persona whenever you want. Each agent's dossier is checked into the repo under <code>docs/qa_dossier/</code>.</p>

  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Ram,

Good questions. Quick context first, then the role of each agent, then how they actually assure quality.

Why we introduced this team:
Across the last five rounds of customer testing with Luda, every issue surfaced AFTER she found it. The pattern was reactive. Each fix was correct on its own, but a real reviewer kept being the one to catch drift first. That is a bad look for a tool we want to demo to enterprise buyers, and it does not scale to multiple personas or external pilots.

The five-agent team is the structural answer: it runs the same checks Luda would run, before Luda has to run them. When the team flags an issue, we fix it before the customer sees it. Result: the May 19 Halyna depth concern was the first issue the team caught and surfaced on its own, before Luda re-tested.

What each agent does:

- Customer Voice - Reads Luda's verbatim quotes from each persona and compares them against the current engine output. Asks: does the tool address what the customer actually wants, not just the literal request? Pushes back when intent is missed. Can block.

- Skill Curator - Independent ontology expert. Re-runs Luda's 5-parameter rubric scoring (Importance, Breadth, Momentum, Connectivity, Career Signal) from scratch, compares against the engine output, and blocks if forbidden skills appear in the top 5 or expected skills are missing. Can block.

- Path Coherence Auditor - Deterministic database checks. Verifies that every chapter's skill ID resolves in the ontology, dashboard module names match the Top 5 page, cached chapter content matches its parent module, and chapter numbering is contiguous. Catches the May 16 Dorothy F bug class structurally. Can block.

- Chapter Reviewer - Reads the actual generated chapter content. Identity check (does the chapter actually teach the right skill?) plus prose-fit check (does a marketing chapter mention campaigns, not generic documents?). Catches the SK.PRM.003 hallucination class of bug. Can block.

- Demo-Readiness Gate - Synthesizes the four upstream verdicts into one GREEN / YELLOW / RED signal and renders a readable dossier per persona suitable for attaching to a "ready to share" decision.

How they assure quality:

- Independence. Each agent runs separately and produces its own verdict. They are not aware of each other's conclusions while they reason. When they agree, that is high signal; when they disagree, that is exactly where we look closely. On the May 19 Halyna pass, the deterministic Skill Curator and the LLM-based Customer Voice independently arrived at the same finding from different starting points.

- Customer-quote grounded. Every Customer Voice finding cites Luda's exact words from her emails. We are not asking the model to imagine what the customer would want; we are asking it to compare engine output against quoted customer feedback. The persona corpus pins these quotes in the repo so they cannot drift.

- Deterministic where possible, LLM where necessary. Path Coherence and the Skill Curator's rubric math are pure Python. There is no model temperature affecting whether the database has the right state. The LLM agents only judge things that require reading prose (Customer Voice, Chapter Reviewer prose-fit).

- Auditable. Every run produces a Markdown dossier with the per-agent reasoning and the customer quotes that drove each finding. We can show this dossier to a customer ("here is exactly why we are confident") or to ourselves on the next round ("here is what we missed last time").

- Pre-demo gate. Nothing is shipped to a customer until the Demo-Readiness Gate returns GREEN or YELLOW with documented caveats. RED blocks the share until the underlying finding is fixed.

One concrete proof point: on the May 19 Halyna pass, the Customer Voice agent independently quoted Luda's "tool pulled rather rudimentary skills" line and flagged that even after our P0 / P1 fixes, the engine still was not surfacing foundational PRM skills the way Claude did. We shipped the foundational-PRM injection on May 20 specifically because the agent caught it. Without the team, we would have learned that from Luda's next email instead.

Happy to walk you through a live run on any persona whenever you want. Each agent's dossier is checked into the repo under docs/qa_dossier/.

Best,
Ali Muwwakkil
Managing Director -- AI Systems Architect
Colaberry Inc.

200 Chisholm Place, Suite 200 - Plano, TX 75075
ali@colaberry.com   -   enterprise.colaberry.ai

Design Your AI Organization`;

async function send() {
  if (!SHOULD_SEND) {
    console.log('=== DRAFT MODE (no email sent) ===');
    console.log('To:', TO.join(', '));
    if (CC.length) console.log('Cc:', CC.join(', '));
    console.log('Bcc:', BCC.join(', '));
    console.log('Subject:', SUBJECT);
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send: node scripts/send-ram-qa-team-reply-may20.js --send');
    return;
  }
  const tokenResp = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: process.env.GMAIL_CLIENT_ID, client_secret: process.env.GMAIL_CLIENT_SECRET,
      refresh_token: process.env.GMAIL_REFRESH_TOKEN, grant_type: 'refresh_token',
    }).toString(),
  });
  const { access_token } = await tokenResp.json();
  const boundary = '----=_B_' + Date.now();
  const headerLines = ['From: Ali Muwwakkil <ali@colaberry.com>', `To: ${TO.join(', ')}`];
  if (CC.length) headerLines.push(`Cc: ${CC.join(', ')}`);
  headerLines.push(`Bcc: ${BCC.join(', ')}`);
  headerLines.push(`Subject: ${SUBJECT}`);
  headerLines.push('MIME-Version: 1.0');
  headerLines.push(`Content-Type: multipart/alternative; boundary="${boundary}"`);
  const message = headerLines.join('\r\n') + '\r\n\r\n' +
    `--${boundary}\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n${BODY_TEXT}\r\n\r\n` +
    `--${boundary}\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n<!DOCTYPE html><html><body>${BODY_HTML}</body></html>\r\n\r\n` +
    `--${boundary}--\r\n`;
  const encoded = Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const sendResp = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
    method: 'POST',
    headers: { Authorization: `Bearer ${access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw: encoded }),
  });
  const result = await sendResp.json();
  if (sendResp.ok) console.log('SENT! Message ID:', result.id);
  else console.log('Failed:', sendResp.status, JSON.stringify(result));
}

send().catch(e => console.error('Error:', e.message));
