require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const TO = 'ludakopeikina@gmail.com';
const CC = ['ram@colaberry.com', 'vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: AI Pathway - 17 changes ready for review + new feedback process';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda,</p>
  <p>Re-sending with corrected screenshots. You were right that several screenshots in the previous zip were not matching their descriptions. The script that captures them was navigating to the analysis URL and getting auto-redirected to the learning dashboard, so 6 of the 17 cards ended up showing the same dashboard image instead of the page they were supposed to document.</p>
  <p>I fixed two underlying problems:</p>
  <ol>
    <li>The auto-redirect itself (now deployed): clicking <code>/analysis/{profileId}</code> goes to the proper review page, not the learning dashboard.</li>
    <li>The screenshot script: it now captures the skill review state directly (before analysis runs) so the images match what each card describes.</li>
  </ol>
  <p>Attached is the new zip. Same usage as before:</p>
  <ol>
    <li>Unzip and open <strong>WALKTHROUGH.html</strong> in a browser.</li>
    <li>Mark each card Approved / Issue / Question.</li>
    <li>Click <strong>Generate Feedback Email</strong> at the bottom right when done.</li>
  </ol>
  <p>This is the version to use. Your earlier in-progress notes will not carry over (browser local storage is keyed to the file), so you will need to re-mark items 01 and 02. Sorry for the rework.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

Re-sending with corrected screenshots. You were right that several screenshots in the previous zip were not matching their descriptions. The script that captures them was navigating to the analysis URL and getting auto-redirected to the learning dashboard, so 6 of the 17 cards ended up showing the same dashboard image instead of the page they were supposed to document.

I fixed two underlying problems:

1. The auto-redirect itself (now deployed): clicking /analysis/{profileId} goes to the proper review page, not the learning dashboard.
2. The screenshot script: it now captures the skill review state directly (before analysis runs) so the images match what each card describes.

Attached is the new zip. Same usage as before:

1. Unzip and open WALKTHROUGH.html in a browser.
2. Mark each card Approved / Issue / Question.
3. Click Generate Feedback Email at the bottom right when done.

This is the version to use. Your earlier in-progress notes will not carry over (browser local storage is keyed to the file), so you will need to re-mark items 01 and 02. Sorry for the rework.

Best,
Ali Muwwakkil
Managing Director -- AI Systems Architect
Colaberry Inc.

200 Chisholm Place, Suite 200 - Plano, TX 75075
ali@colaberry.com   -   enterprise.colaberry.ai

Design Your AI Organization`;

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'walkthrough_report.zip');
const ATTACHMENT_NAME = 'walkthrough_report.zip';

async function send() {
  if (!SHOULD_SEND) {
    console.log('=== DRAFT MODE (no email sent) ===');
    console.log('To:', TO);
    if (CC.length) console.log('Cc:', CC.join(', '));
    console.log('Bcc:', BCC.join(', '));
    console.log('Subject:', SUBJECT);
    console.log('Attachment:', ATTACHMENT_PATH);
    if (!fs.existsSync(ATTACHMENT_PATH)) {
      console.log('  WARNING: attachment file does not exist yet');
    } else {
      console.log('  Size:', fs.statSync(ATTACHMENT_PATH).size, 'bytes');
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send for real: node scripts/send-luda-corrected-zip.js --send');
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
    `Content-Type: application/zip; name="${ATTACHMENT_NAME}"`,
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
