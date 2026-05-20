require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'qa_dossier', 'halyna_mushak.md');
const ATTACHMENT_NAME = 'halyna_mushak_qa_dossier.md';

const TO = ['ram@colaberry.com', 'ludakopeikina@gmail.com'];
const CC = ['vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: AI Pathway - status across your 4 prep personas';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda, Ram,</p>

  <p>Luda - thank you, that means a lot. The whole reason for the QA team was exactly what you said: if we cannot create a personalized skill set reliably, there is no product. Good luck with the Dorothy demo at 10, and with the Halyna and Brittany reruns after.</p>

  <p><strong>On the enterprise slide</strong> - agreed, this is a hard question and we should be ready to answer it cleanly. I will send a slide deck later today that walks through the QA system end-to-end, so you have something ready to drop into any enterprise deck.</p>

  <p>Ram - your four follow-ups, in order:</p>

  <p><strong>1. When do the agents run?</strong></p>
  <p>Every persona, before every demo. The full run takes ~2 minutes and the cost is trivial (one Gemini call for the Customer Voice agent, one per cached chapter for the Chapter Reviewer prose-fit; the other three agents are pure Python). We also run the deterministic subset (Path Coherence + Skill Curator) on every commit that touches the relevant code paths, so engine drift is caught at the diff, not at demo time.</p>

  <p><strong>2. Who makes the final call on fix vs override?</strong></p>
  <p>Ali. The Demo Gate produces the verdict, but the human ships the demo. The dossier writes the override reason into the same file the gate wrote the block reason in, so future audits can see "blocked, then overridden by Ali on 5/20 because the underlying issue was already known and tracked under item X." YELLOW is shippable with a brief reviewer prep; RED requires either a fix or a documented override. We have never overridden a RED to date.</p>

  <p><strong>3. How do we keep them from converging into slop?</strong></p>
  <p>Two deliberate safeguards:</p>
  <ul>
    <li><strong>The agents read different inputs.</strong> Customer Voice reads the persona's customer-feedback quotes. Skill Curator reads the engine's skill-set output. Path Coherence reads the database. Chapter Reviewer reads chapter prose. They cannot agree on the same observation because they are not looking at the same thing.</li>
    <li><strong>Three of five are deterministic.</strong> Path Coherence, Skill Curator's rubric math, and the Demo Gate aggregator are all pure Python with no LLM in the loop. They compute facts, so they cannot drift toward consensus over time. Only Customer Voice and Chapter Reviewer's prose-fit use an LLM, and they ground every finding in either a verbatim customer quote (CV) or the literal chapter text (CR).</li>
  </ul>
  <p>If the team ever does start to converge in a way that hides real issues, the persona corpus is the canary: the deterministic <code>forbidden_in_top5</code> / <code>expected_top5_includes</code> assertions are hard contracts that cannot be argued away by any agent's reasoning. They either pass or they fail.</p>

  <p><strong>4. Sample dossier</strong></p>
  <p>Halyna's latest dossier is attached as <code>halyna_mushak_qa_dossier.md</code>. It is the actual file the team wrote on the most recent run. You will see the per-agent verdict, the reasoning, the exact customer quote each finding is grounded in, the proposed fix on each open finding, and the rolled-up Demo Gate verdict at the bottom. This is what a "ready to demo" decision is based on.</p>

  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda, Ram,

Luda - thank you, that means a lot. The whole reason for the QA team was exactly what you said: if we cannot create a personalized skill set reliably, there is no product. Good luck with the Dorothy demo at 10, and with the Halyna and Brittany reruns after.

On the enterprise slide - agreed, this is a hard question and we should be ready to answer it cleanly. I will send a slide deck later today that walks through the QA system end-to-end, so you have something ready to drop into any enterprise deck.

Ram - your four follow-ups, in order:

1. When do the agents run?
Every persona, before every demo. The full run takes ~2 minutes and the cost is trivial (one Gemini call for the Customer Voice agent, one per cached chapter for the Chapter Reviewer prose-fit; the other three agents are pure Python). We also run the deterministic subset (Path Coherence + Skill Curator) on every commit that touches the relevant code paths, so engine drift is caught at the diff, not at demo time.

2. Who makes the final call on fix vs override?
Ali. The Demo Gate produces the verdict, but the human ships the demo. The dossier writes the override reason into the same file the gate wrote the block reason in, so future audits can see "blocked, then overridden by Ali on 5/20 because the underlying issue was already known and tracked under item X." YELLOW is shippable with a brief reviewer prep; RED requires either a fix or a documented override. We have never overridden a RED to date.

3. How do we keep them from converging into slop?
Two deliberate safeguards:

- The agents read different inputs. Customer Voice reads the persona's customer-feedback quotes. Skill Curator reads the engine's skill-set output. Path Coherence reads the database. Chapter Reviewer reads chapter prose. They cannot agree on the same observation because they are not looking at the same thing.

- Three of five are deterministic. Path Coherence, Skill Curator's rubric math, and the Demo Gate aggregator are all pure Python with no LLM in the loop. They compute facts, so they cannot drift toward consensus over time. Only Customer Voice and Chapter Reviewer's prose-fit use an LLM, and they ground every finding in either a verbatim customer quote (CV) or the literal chapter text (CR).

If the team ever does start to converge in a way that hides real issues, the persona corpus is the canary: the deterministic forbidden_in_top5 / expected_top5_includes assertions are hard contracts that cannot be argued away by any agent's reasoning. They either pass or they fail.

4. Sample dossier
Halyna's latest dossier is attached as halyna_mushak_qa_dossier.md. It is the actual file the team wrote on the most recent run. You will see the per-agent verdict, the reasoning, the exact customer quote each finding is grounded in, the proposed fix on each open finding, and the rolled-up Demo Gate verdict at the bottom. This is what a "ready to demo" decision is based on.

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
    console.log('Attachment:', ATTACHMENT_PATH, fs.existsSync(ATTACHMENT_PATH) ? `(${fs.statSync(ATTACHMENT_PATH).size} bytes)` : '(MISSING)');
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send: node scripts/send-ram-luda-followup-may20.js --send');
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
    `--${boundaryMixed}\r\nContent-Type: text/markdown; charset=UTF-8; name="${ATTACHMENT_NAME}"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename="${ATTACHMENT_NAME}"\r\n\r\n${attachmentB64}\r\n\r\n` +
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
