require('dotenv').config();

const SHOULD_SEND = process.argv.includes('--send');

const TO = ['ludakopeikina@gmail.com', 'ram@colaberry.com'];
const CC = ['vivmuk@gmail.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Re: AI Pathway walkthrough feedback - 2026-05-07';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda,</p>
  <p>Thanks for the structured feedback. Got it cleanly through the parser. Here is what I am taking from it:</p>
  <p><strong>Approved (9):</strong> 01, 02, 03, 05, 07, 08, 09, 10, 17. Shipping these as-is. The current build has all of these in it, so you are clear to demo with Jennifer whenever you are ready.</p>
  <p><strong>Deferred (item 06):</strong> The message change you approved. Your separate note about adding an interstitial proficiency-rating step for the swapped-in skills (6, 7, 8) is a real product requirement, not a quick fix. I have written it up as a tracked work item and will pick it up after the Jennifer demo, per your note that #6 can be done later.</p>
  <p><strong>Routed to Vivek (7 items):</strong> 04, 11, 12, 13, 14, 15, 16. I am sending Vivek a separate note with each item, the live URL, and your specific question on item 04 (the per-skill proficiency description for the hover tooltip). I will fold his decisions into the next round.</p>
  <p><strong>One quick note on item 03:</strong> your note said the URL leads to "Define Your Target" - that was the bug from yesterday's earlier zip. The version attached to last night's email has the URL fix deployed. I just re-tested the URL on the card and it lands on the correct skill review page now. Most likely your browser cached your earlier note via localStorage. Not a current issue; you marked it Approved either way.</p>
  <p><strong>Item 17 (deterministic ordering):</strong> you said you will validate again. Let me know if your second run produces a different top 5 - that would be a real regression to investigate.</p>
  <p>Net: the build is demo-ready right now. I will send a wrap-up once Vivek weighs in and we have a plan for #6.</p>
  <p>Thanks again for working through this with me.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda,

Thanks for the structured feedback. Got it cleanly through the parser. Here is what I am taking from it:

Approved (9): 01, 02, 03, 05, 07, 08, 09, 10, 17. Shipping these as-is. The current build has all of these in it, so you are clear to demo with Jennifer whenever you are ready.

Deferred (item 06): The message change you approved. Your separate note about adding an interstitial proficiency-rating step for the swapped-in skills (6, 7, 8) is a real product requirement, not a quick fix. I have written it up as a tracked work item and will pick it up after the Jennifer demo, per your note that #6 can be done later.

Routed to Vivek (7 items): 04, 11, 12, 13, 14, 15, 16. I am sending Vivek a separate note with each item, the live URL, and your specific question on item 04 (the per-skill proficiency description for the hover tooltip). I will fold his decisions into the next round.

One quick note on item 03: your note said the URL leads to "Define Your Target" - that was the bug from yesterday's earlier zip. The version attached to last night's email has the URL fix deployed. I just re-tested the URL on the card and it lands on the correct skill review page now. Most likely your browser cached your earlier note via localStorage. Not a current issue; you marked it Approved either way.

Item 17 (deterministic ordering): you said you will validate again. Let me know if your second run produces a different top 5 - that would be a real regression to investigate.

Net: the build is demo-ready right now. I will send a wrap-up once Vivek weighs in and we have a plan for #6.

Thanks again for working through this with me.

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
    console.log('To send for real: node scripts/send-luda-feedback-ack.js --send');
    return;
  }

  if (!process.env.GMAIL_CLIENT_ID || !process.env.GMAIL_CLIENT_SECRET || !process.env.GMAIL_REFRESH_TOKEN) {
    console.error('ERROR: missing one of GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN in .env');
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

  const boundary = '----=_Boundary_' + Date.now();
  const headerLines = [
    'From: Ali Muwwakkil <ali@colaberry.com>',
    `To: ${TO.join(', ')}`,
  ];
  if (CC.length) headerLines.push(`Cc: ${CC.join(', ')}`);
  headerLines.push(`Bcc: ${BCC.join(', ')}`);
  headerLines.push(`Subject: ${SUBJECT}`);
  headerLines.push('MIME-Version: 1.0');
  headerLines.push(`Content-Type: multipart/alternative; boundary="${boundary}"`);
  const headers = headerLines.join('\r\n');

  const body = [
    '',
    `--${boundary}`,
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    BODY_TEXT,
    '',
    `--${boundary}`,
    'Content-Type: text/html; charset=UTF-8',
    'Content-Transfer-Encoding: 7bit',
    '',
    `<!DOCTYPE html><html><body>${BODY_HTML}</body></html>`,
    '',
    `--${boundary}--`,
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
