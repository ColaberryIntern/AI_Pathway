require('dotenv').config();

const SHOULD_SEND = process.argv.includes('--send');

const TO = ['ludakopeikina@gmail.com'];
const CC = ['ram@colaberry.com', 'vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: AI Pathway - clarifying 4 buttons on each profile';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda,</p>
  <p>Quick read on the 4 buttons:</p>
  <ul>
    <li><strong>View Profile</strong> - keep as-is.</li>
    <li><strong>Skills Profile</strong> - redesigning per your 9-point spec (~2.5h, queued).</li>
    <li><strong>Learning Path</strong> - keep as-is.</li>
    <li><strong>Ontology Path</strong> - confirmed your instinct: it routes to the older Learning Path page and duplicates the dashboard. <strong>Recommend removing the button.</strong></li>
  </ul>
  <p>Separately - three items you raised over the weekend (rank ordering, dashboard back-nav, rating persistence) are live in the build. The walkthrough HTML I'm sending in the other thread has them documented as cards 18, 19, 20.</p>
  <p>Happy to jump on a quick call to walk through the Skills Profile schematic if useful.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

Quick read on the 4 buttons:

- View Profile - keep as-is.
- Skills Profile - redesigning per your 9-point spec (~2.5h, queued).
- Learning Path - keep as-is.
- Ontology Path - confirmed your instinct: it routes to the older Learning Path page and duplicates the dashboard. Recommend removing the button.

Separately - three items you raised over the weekend (rank ordering, dashboard back-nav, rating persistence) are live in the build. The walkthrough HTML I'm sending in the other thread has them documented as cards 18, 19, 20.

Happy to jump on a quick call to walk through the Skills Profile schematic if useful.

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
    console.log('To send: node scripts/send-luda-4buttons-reply.js --send');
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
