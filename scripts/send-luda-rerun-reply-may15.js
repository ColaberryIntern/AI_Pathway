require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'proposal_may15', 'BRITTANY_W_BEFORE_AFTER.html');
const ATTACHMENT_NAME = 'BRITTANY_W_BEFORE_AFTER.html';

const TO = ['ludakopeikina@gmail.com'];
const CC = ['ram@colaberry.com', 'vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: Rerun of Brittany White case';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda,</p>
  <p>Thank you for the rerun and for the rubric. You are right that the prioritization is off, and the cause is in the engine, not the UI. Attached is a single HTML file showing what will change and what Brittany's profile will look like after the changes are in.</p>
  <p><strong>Six changes going into the tool:</strong></p>
  <ol>
    <li>JD-to-skills extraction rewritten so it surfaces role-essence skills (communication, product, governance for an AI PMM), not tooling skills.</li>
    <li>Always generate 10 candidates, then score and rank.</li>
    <li>Add the 5-parameter weighted rubric scoring engine using your formula.</li>
    <li>Split results into Maintain (already at level) and Develop (genuine gap) groups.</li>
    <li>Enforce ontology diversity: max 2 Develop skills per parent node.</li>
    <li>New skills page UI matching your May 15 mockup, with the score breakdown visible.</li>
  </ol>
  <p>Separately, profile parsing accuracy will be retested across all 5 prep profiles before the next demo round so the stored data matches reality.</p>
  <p><strong>Brittany's after view (full table in the attachment):</strong></p>
  <ul>
    <li>8 skills shown as Maintain, 2 as Develop.</li>
    <li>Develop #1: SK.GOV.001 AI Governance &amp; Compliance, score 42/42.</li>
    <li>Develop #2: SK.FND.002 Capabilities vs Limitations, score 42/42.</li>
    <li>The learning path generates chapters only for the 2 Develop skills.</li>
  </ul>
  <p>This matches your conclusion that she is close to being a good fit for this role and only needs to develop those two.</p>
  <p>If the after view in the attachment looks right, reply with "proceed" and the changes go in. If anything in the rubric weights, the diversity rule, the Maintain vs Develop threshold, or the proposed UI is off, send the change and the build adjusts before starting. The same engine will then run on Jennifer C, Dorothy F, Halyna M, and Srushti M, and you will get a similar before and after for each before the next demo round.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

Thank you for the rerun and for the rubric. You are right that the prioritization is off, and the cause is in the engine, not the UI. Attached is a single HTML file showing what will change and what Brittany's profile will look like after the changes are in.

Six changes going into the tool:
1. JD-to-skills extraction rewritten so it surfaces role-essence skills (communication, product, governance for an AI PMM), not tooling skills.
2. Always generate 10 candidates, then score and rank.
3. Add the 5-parameter weighted rubric scoring engine using your formula.
4. Split results into Maintain (already at level) and Develop (genuine gap) groups.
5. Enforce ontology diversity: max 2 Develop skills per parent node.
6. New skills page UI matching your May 15 mockup, with the score breakdown visible.

Separately, profile parsing accuracy will be retested across all 5 prep profiles before the next demo round so the stored data matches reality.

Brittany's after view (full table in the attachment):
- 8 skills shown as Maintain, 2 as Develop.
- Develop #1: SK.GOV.001 AI Governance & Compliance, score 42/42.
- Develop #2: SK.FND.002 Capabilities vs Limitations, score 42/42.
- The learning path generates chapters only for the 2 Develop skills.

This matches your conclusion that she is close to being a good fit for this role and only needs to develop those two.

If the after view in the attachment looks right, reply with "proceed" and the changes go in. If anything in the rubric weights, the diversity rule, the Maintain vs Develop threshold, or the proposed UI is off, send the change and the build adjusts before starting. The same engine will then run on Jennifer C, Dorothy F, Halyna M, and Srushti M, and you will get a similar before and after for each before the next demo round.

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
      console.log(`  Size: ${bytes} bytes (${(bytes/1024).toFixed(1)} KB)`);
    } else {
      console.log('  WARNING: attachment file does not exist yet');
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send: node scripts/send-luda-rerun-reply-may15.js --send');
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
