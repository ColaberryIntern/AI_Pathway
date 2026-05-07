require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const TO = 'ali@colaberry.com';
const CC = [];
const BCC = ['ali@colaberry.com']; // hard requirement, always include
const SUBJECT = 'Walkthrough HTML test - embedded screenshots, single file';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Self-test of the embedded-screenshot walkthrough HTML.</p>
  <p>Attached is a single self-contained HTML file. No zip, no folder, no extraction. Just open the attachment and the entire walkthrough renders with all 17 cards and their screenshots inline.</p>
  <p><strong>What to verify:</strong></p>
  <ul>
    <li>Open the attachment in Safari or Chrome.</li>
    <li>Each card has its screenshot visible (not a broken-image icon).</li>
    <li>Click a screenshot - it should open at full size in a new tab.</li>
    <li>Sidebar TOC, category filters, search, feedback widgets all functional.</li>
    <li>Live URLs on each card still work (they point to the deployed app).</li>
  </ul>
  <p>This is the format that will replace the zip-with-folder structure for future rounds with Luda. Single file delivery, no risk of "click the wrong thing" confusion.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Self-test of the embedded-screenshot walkthrough HTML.

Attached is a single self-contained HTML file. No zip, no folder, no extraction. Just open the attachment and the entire walkthrough renders with all 17 cards and their screenshots inline.

What to verify:
- Open the attachment in Safari or Chrome.
- Each card has its screenshot visible (not a broken-image icon).
- Click a screenshot - it should open at full size in a new tab.
- Sidebar TOC, category filters, search, feedback widgets all functional.
- Live URLs on each card still work (they point to the deployed app).

This is the format that will replace the zip-with-folder structure for future rounds with Luda. Single file delivery, no risk of "click the wrong thing" confusion.

Best,
Ali Muwwakkil
Managing Director -- AI Systems Architect
Colaberry Inc.

200 Chisholm Place, Suite 200 - Plano, TX 75075
ali@colaberry.com   -   enterprise.colaberry.ai

Design Your AI Organization`;

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'walkthrough_report', 'WALKTHROUGH.html');
const ATTACHMENT_NAME = 'WALKTHROUGH.html';

async function send() {
  if (!SHOULD_SEND) {
    console.log('=== DRAFT MODE (no email sent) ===');
    console.log('To:', TO);
    if (CC.length) console.log('Cc:', CC.join(', '));
    console.log('Bcc:', BCC.join(', '));
    console.log('Subject:', SUBJECT);
    console.log('Attachment:', ATTACHMENT_PATH);
    if (!fs.existsSync(ATTACHMENT_PATH)) {
      console.log('  WARNING: attachment file does not exist');
    } else {
      const bytes = fs.statSync(ATTACHMENT_PATH).size;
      console.log(`  Size: ${bytes} bytes (${(bytes/1024/1024).toFixed(2)} MB)`);
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send for real: node scripts/send-self-embedded-test.js --send');
    return;
  }

  if (!process.env.GMAIL_CLIENT_ID || !process.env.GMAIL_CLIENT_SECRET || !process.env.GMAIL_REFRESH_TOKEN) {
    console.error('ERROR: missing one of GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN in .env');
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
      client_id: process.env.GMAIL_CLIENT_ID,
      client_secret: process.env.GMAIL_CLIENT_SECRET,
      refresh_token: process.env.GMAIL_REFRESH_TOKEN,
      grant_type: 'refresh_token',
    }).toString(),
  });
  const { access_token } = await tokenResp.json();

  const boundaryAlt = '----=_Alt_' + Date.now();
  const boundaryMixed = '----=_Mixed_' + Date.now();
  const headerLines = [
    'From: Ali Muwwakkil <ali@colaberry.com>',
    `To: ${TO}`,
  ];
  if (CC.length) headerLines.push(`Cc: ${CC.join(', ')}`);
  headerLines.push(`Bcc: ${BCC.join(', ')}`);
  headerLines.push(`Subject: ${SUBJECT}`);
  headerLines.push('MIME-Version: 1.0');
  headerLines.push(`Content-Type: multipart/mixed; boundary="${boundaryMixed}"`);
  const headers = headerLines.join('\r\n');

  const attachmentB64 = fs.readFileSync(ATTACHMENT_PATH).toString('base64').match(/.{1,76}/g).join('\r\n');

  const body = [
    '',
    `--${boundaryMixed}`,
    `Content-Type: multipart/alternative; boundary="${boundaryAlt}"`,
    '',
    `--${boundaryAlt}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    BODY_TEXT,
    '',
    `--${boundaryAlt}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    `<!DOCTYPE html><html><body>${BODY_HTML}</body></html>`,
    '',
    `--${boundaryAlt}--`,
    '',
    `--${boundaryMixed}`,
    `Content-Type: text/html; charset=UTF-8; name="${ATTACHMENT_NAME}"`,
    'Content-Transfer-Encoding: base64',
    `Content-Disposition: attachment; filename="${ATTACHMENT_NAME}"`,
    '',
    attachmentB64,
    '',
    `--${boundaryMixed}--`,
    '',
  ].join('\r\n');

  const message = headers + '\r\n' + body;
  const encoded = Buffer.from(message).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

  const sendResp = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', {
    method: 'POST',
    headers: { Authorization: `Bearer ${access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw: encoded }),
  });

  const result = await sendResp.json();
  if (sendResp.ok) {
    console.log('SENT! Message ID:', result.id);
  } else {
    console.log('Failed:', sendResp.status, JSON.stringify(result));
  }
}

send().catch(e => console.error('Error:', e.message));
