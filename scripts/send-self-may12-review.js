require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const TO = 'ali@colaberry.com';
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Walkthrough HTML for personal review - 7 cards (4 fixes + 3 follow-ups) (May 12)';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Personal review copy of the WALKTHROUGH.html before sending to Luda/Vivek. Filtered to only the 7 cards relevant to this round (4 fixes shipped + 3 follow-up status updates). Previously-approved items are not re-listed.</p>
  <p><strong>4 fixes shipped since Luda's review:</strong></p>
  <ul>
    <li><strong>Card 18</strong> - Skills render in sequential rank order (was: rank-1 last, two #2s, no #7).</li>
    <li><strong>Card 19</strong> - Back to skill review link on the Learning Dashboard.</li>
    <li><strong>Card 20</strong> - Rating persistence across navigation (localStorage by profileId).</li>
    <li><strong>Card 21</strong> - Per-skill, per-level hover descriptions (no longer generic "Aware: Can explain basics").</li>
  </ul>
  <p><strong>3 follow-up status cards for items they flagged:</strong></p>
  <ul>
    <li><strong>Card 22</strong> - Item 06 (interstitial skill rating step) DEFERRED per Luda's note - can come after Jennifer demo. Spec captured at docs/follow_ups/06_interstitial_skill_rating.md.</li>
    <li><strong>Card 23</strong> - Item 14 (Build Your Agent: description / instructions / knowledge base) QUEUED for next chapter-format round. Vivek's ask is understood; planned changes documented in the card.</li>
    <li><strong>Card 24</strong> - Item 17 (deterministic ordering) NEEDS CLARIFICATION - Vivek marked Issue with no comment. Asking on the card and in the reply email.</li>
  </ul>
  <p><strong>Verification done before sending this email:</strong></p>
  <ul>
    <li>7 cards present, 7 images loaded in browser (Playwright headless load)</li>
    <li>All 7 anchor IDs present, content checks for rank ordering / back link / localStorage / hover label / deferred / queued / clarification all pass</li>
    <li>parseJDSkills API confirmed to return per-skill rubric strings (not generic scale)</li>
  </ul>
  <p>Open the attachment in Safari/Chrome. If the 7 cards look correct, reply with "send the customer emails" and I will send the two replies to Luda+Vivek (with this HTML attached to the walkthrough thread).</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Personal review copy of the WALKTHROUGH.html before sending to Luda/Vivek. Filtered to only the 7 cards relevant to this round (4 fixes shipped + 3 follow-up status updates).

4 fixes shipped since Luda's review:
- Card 18 - Skills render in sequential rank order
- Card 19 - Back to skill review link on the Learning Dashboard
- Card 20 - Rating persistence across navigation (localStorage by profileId)
- Card 21 - Per-skill, per-level hover descriptions

3 follow-up status cards:
- Card 22 - Item 06 (interstitial skill rating) DEFERRED per Luda
- Card 23 - Item 14 (Build Your Agent fields) QUEUED for next round
- Card 24 - Item 17 (deterministic ordering) NEEDS CLARIFICATION from Vivek

Verification done before sending this email:
- 7 cards present, 7 images loaded in browser
- All 7 anchor IDs present, content checks pass
- parseJDSkills API confirmed to return per-skill rubric strings

Open the attachment in Safari/Chrome. If the 7 cards look correct, reply with "send the customer emails" and I will send the two replies to Luda+Vivek.

Best,
Ali Muwwakkil`;

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'walkthrough_report', 'WALKTHROUGH.html');

async function send() {
  if (!SHOULD_SEND) {
    console.log('DRAFT - to send: node scripts/send-self-may12-review.js --send');
    if (fs.existsSync(ATTACHMENT_PATH)) {
      console.log(`Attachment: ${(fs.statSync(ATTACHMENT_PATH).size/1024/1024).toFixed(2)} MB`);
    }
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
  const headers = [
    'From: Ali Muwwakkil <ali@colaberry.com>',
    `To: ${TO}`,
    `Bcc: ${BCC.join(', ')}`,
    `Subject: ${SUBJECT}`,
    'MIME-Version: 1.0',
    `Content-Type: multipart/mixed; boundary="${boundaryMixed}"`,
  ].join('\r\n');
  const attachmentB64 = fs.readFileSync(ATTACHMENT_PATH).toString('base64').match(/.{1,76}/g).join('\r\n');
  const message = headers + '\r\n\r\n' +
    `--${boundaryMixed}\r\nContent-Type: multipart/alternative; boundary="${boundaryAlt}"\r\n\r\n` +
    `--${boundaryAlt}\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n${BODY_TEXT}\r\n\r\n` +
    `--${boundaryAlt}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<!DOCTYPE html><html><body>${BODY_HTML}</body></html>\r\n\r\n` +
    `--${boundaryAlt}--\r\n\r\n` +
    `--${boundaryMixed}\r\nContent-Type: text/html; name="WALKTHROUGH.html"\r\nContent-Transfer-Encoding: base64\r\nContent-Disposition: attachment; filename="WALKTHROUGH.html"\r\n\r\n${attachmentB64}\r\n\r\n` +
    `--${boundaryMixed}--\r\n`;
  const encoded = Buffer.from(message).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const sendResp = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
    method: 'POST',
    headers: { Authorization: `Bearer ${access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw: encoded }),
  });
  const result = await sendResp.json();
  console.log(sendResp.ok ? `SENT! ${result.id}` : `Failed: ${sendResp.status} ${JSON.stringify(result)}`);
}
send().catch(e => console.error('Error:', e.message));
