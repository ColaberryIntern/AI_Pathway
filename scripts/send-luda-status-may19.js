require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'status_may19', 'STATUS_MAY19.html');
const ATTACHMENT_NAME = 'STATUS_MAY19.html';

const TO = ['ludakopeikina@gmail.com'];
const CC = ['ram@colaberry.com', 'vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'AI Pathway - status across your 4 prep personas';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda,</p>
  <p>Quick wrap on everything that has shipped since your May 15 Brittany rerun and May 19 Halyna case. Full screenshots and details are in the attached STATUS_MAY19.html (open in any browser, no extraction needed).</p>

  <p><strong>Where your 4 prep personas stand right now:</strong></p>
  <ul>
    <li><strong>Brittany W</strong> - READY. All 5 role-essence skills (Explaining AI, ROI Measurement, Use Case ID, Stakeholder Management, Capabilities vs Limitations) are now in her top 5 deterministically. The May 15 result is structurally resolved.</li>
    <li><strong>Halyna M</strong> - Ready with caveats. Marketing domain skill at #1, plus foundational prompting (SK.PRM.000 and SK.PRM.001) injected in her top 5 to address the depth concern you raised. Same skills Claude picked in your shared chat.</li>
    <li><strong>Dorothy F</strong> - Ready with caveats. Education domain skill at #1, cross-functional collaboration in top 5. May 16 dashboard and chapter routing fixes all in.</li>
    <li><strong>Jennifer C</strong> - Ready with caveats. Top 5 is content-editor relevant. The 4 strategic asks from her demo are now live in product (see below).</li>
  </ul>

  <p><strong>4 new surfaces for Jennifer's May 12 asks:</strong></p>
  <ul>
    <li><strong>Ontology narrative panel</strong> on every Top 5 page - collapsible, explains how the tool matched against the ontology, the 5-parameter rubric, and the role-specific guarantees we applied (with the exact skill IDs).</li>
    <li><strong>AI disclosure + grounding sources</strong> on every chapter - banner up top, expandable panel showing the exact ontology rubric strings the chapter was built from so the learner can compare them against the narrative.</li>
    <li><strong>Coach voice intro and outro</strong> on every chapter - warm framing of what they are working on and what comes next, using the actual skill name and level rubric (not generic copy).</li>
    <li><strong>End-of-path summary</strong> - completing the last chapter routes to a new summary page with skills mastered, ontology-grounded next-step recommendations, and a 60-day retake reminder.</li>
  </ul>

  <p><strong>What changed structurally that you cannot see in the UI:</strong></p>
  <ul>
    <li>A 5-agent QA team (Customer Voice, Skill Curator, Path Coherence, Chapter Reviewer, Demo Gate) now runs against every persona before any demo. Each agent can block; each grounds its reasoning in your exact customer quotes. Verdicts above came from running it.</li>
    <li>A persona corpus that codifies your customer feedback as testable assertions. New personas (Srushti when you create her) automatically inherit the gate.</li>
    <li>Every original Goal or Path from your prior tests is preserved in the database under its original ID, so we can always reproduce exactly what you saw at any point. New verification runs are logged alongside originals.</li>
  </ul>

  <p>You should be able to re-load any of the 4 prep profiles right now and see all of the above. If you spot anything off, the dossiers from the QA team are checked into the repo under <code>docs/qa_dossier/</code> with the per-agent reasoning, so I can act on the specific finding.</p>

  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

Quick wrap on everything that has shipped since your May 15 Brittany rerun and May 19 Halyna case. Full screenshots and details are in the attached STATUS_MAY19.html (open in any browser, no extraction needed).

Where your 4 prep personas stand right now:
- Brittany W - READY. All 5 role-essence skills are now in her top 5 deterministically. The May 15 result is structurally resolved.
- Halyna M - Ready with caveats. Marketing domain skill at #1, plus foundational prompting (SK.PRM.000 and SK.PRM.001) injected in her top 5 to address the depth concern you raised. Same skills Claude picked in your shared chat.
- Dorothy F - Ready with caveats. Education domain skill at #1, cross-functional collaboration in top 5. May 16 dashboard and chapter routing fixes all in.
- Jennifer C - Ready with caveats. Top 5 is content-editor relevant. The 4 strategic asks from her demo are now live in product (see below).

4 new surfaces for Jennifer's May 12 asks:
- Ontology narrative panel on every Top 5 page - collapsible, explains how the tool matched against the ontology, the 5-parameter rubric, and the role-specific guarantees we applied.
- AI disclosure and grounding sources on every chapter - banner up top, expandable panel showing the exact ontology rubric strings the chapter was built from.
- Coach voice intro and outro on every chapter - warm framing using the actual skill name and level rubric.
- End-of-path summary - completing the last chapter routes to a summary page with skills mastered, ontology-grounded next-step recommendations, and a 60-day retake reminder.

What changed structurally that you cannot see in the UI:
- A 5-agent QA team (Customer Voice, Skill Curator, Path Coherence, Chapter Reviewer, Demo Gate) now runs against every persona before any demo. Each agent can block.
- A persona corpus that codifies your customer feedback as testable assertions.
- Every original Goal or Path from your prior tests is preserved in the database.

You should be able to re-load any of the 4 prep profiles right now and see all of the above.

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
    console.log('Attachment:', ATTACHMENT_PATH);
    if (fs.existsSync(ATTACHMENT_PATH)) {
      const bytes = fs.statSync(ATTACHMENT_PATH).size;
      console.log(`  Size: ${bytes} bytes (${(bytes/1024/1024).toFixed(2)} MB)`);
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send: node scripts/send-luda-status-may19.js --send');
    return;
  }
  if (!process.env.GMAIL_CLIENT_ID || !process.env.GMAIL_CLIENT_SECRET || !process.env.GMAIL_REFRESH_TOKEN) {
    console.error('ERROR: missing GMAIL_* env vars');
    process.exit(1);
  }
  if (!fs.existsSync(ATTACHMENT_PATH)) {
    console.error(`ERROR: attachment not found at ${ATTACHMENT_PATH}`);
    process.exit(1);
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
  const boundaryAlt = '----=_Alt_' + Date.now();
  const boundaryMixed = '----=_Mixed_' + Date.now();
  const headerLines = ['From: Ali Muwwakkil <ali@colaberry.com>', `To: ${TO.join(', ')}`];
  if (CC.length) headerLines.push(`Cc: ${CC.join(', ')}`);
  headerLines.push(`Bcc: ${BCC.join(', ')}`);
  headerLines.push(`Subject: ${SUBJECT}`);
  headerLines.push('MIME-Version: 1.0');
  headerLines.push(`Content-Type: multipart/mixed; boundary="${boundaryMixed}"`);
  const attachmentB64 = fs.readFileSync(ATTACHMENT_PATH).toString('base64').match(/.{1,76}/g).join('\r\n');
  const message = headerLines.join('\r\n') + '\r\n\r\n' +
    `--${boundaryMixed}\r\nContent-Type: multipart/alternative; boundary="${boundaryAlt}"\r\n\r\n` +
    `--${boundaryAlt}\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n${BODY_TEXT}\r\n\r\n` +
    `--${boundaryAlt}\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n<!DOCTYPE html><html><body>${BODY_HTML}</body></html>\r\n\r\n` +
    `--${boundaryAlt}--\r\n\r\n` +
    `--${boundaryMixed}\r\nContent-Type: text/html; charset=UTF-8; name="${ATTACHMENT_NAME}"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename="${ATTACHMENT_NAME}"\r\n\r\n${attachmentB64}\r\n\r\n` +
    `--${boundaryMixed}--\r\n`;
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
