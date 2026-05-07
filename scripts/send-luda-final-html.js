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
  <p>I owe you an apology for the volume of emails today. This is a new review process I am setting up, and I really wanted to get it right rather than send you something half-finished. Each iteration this afternoon was solving a different issue you surfaced (URL routing, screenshot mismatches, missing review-name field) and I appreciate your patience while I worked through them.</p>
  <p>Attached is the <strong>final, clean version</strong>. Please use this one going forward and ignore everything earlier in the thread:</p>
  <ul>
    <li><strong>One file.</strong> No zip, no folder. Just open <strong>WALKTHROUGH.html</strong> directly from the attachment in Safari or Chrome.</li>
    <li><strong>Screenshots are embedded.</strong> No separate image files to manage.</li>
    <li><strong>"Your name" field is at the top of the left sidebar</strong> (yellow highlighted box). Fill it in before you click Generate Feedback Email.</li>
    <li><strong>All 17 URLs land on the right page</strong> when you click them, no redirects.</li>
    <li><strong>Notes auto-save</strong> in the browser - safe to stop and come back.</li>
  </ul>
  <p>When you are done, click <strong>Generate Feedback Email</strong> at the bottom right. It opens a structured email pre-filled back to me, and the system on my end reads it and routes each requested fix directly to the right files.</p>
  <p>Going forward, every round will be a single HTML attachment in this format. No more iterations like today.</p>
  <p>Thanks for sticking with me through this.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

I owe you an apology for the volume of emails today. This is a new review process I am setting up, and I really wanted to get it right rather than send you something half-finished. Each iteration this afternoon was solving a different issue you surfaced (URL routing, screenshot mismatches, missing review-name field) and I appreciate your patience while I worked through them.

Attached is the final, clean version. Please use this one going forward and ignore everything earlier in the thread:

- One file. No zip, no folder. Just open WALKTHROUGH.html directly from the attachment in Safari or Chrome.
- Screenshots are embedded. No separate image files to manage.
- "Your name" field is at the top of the left sidebar (yellow highlighted box). Fill it in before you click Generate Feedback Email.
- All 17 URLs land on the right page when you click them, no redirects.
- Notes auto-save in the browser - safe to stop and come back.

When you are done, click Generate Feedback Email at the bottom right. It opens a structured email pre-filled back to me, and the system on my end reads it and routes each requested fix directly to the right files.

Going forward, every round will be a single HTML attachment in this format. No more iterations like today.

Thanks for sticking with me through this.

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
    if (fs.existsSync(ATTACHMENT_PATH)) {
      const bytes = fs.statSync(ATTACHMENT_PATH).size;
      console.log(`  Size: ${bytes} bytes (${(bytes/1024/1024).toFixed(2)} MB)`);
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send for real: node scripts/send-luda-final-html.js --send');
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
