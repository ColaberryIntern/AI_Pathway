require('dotenv').config();
const fs = require('fs');
const path = require('path');

const SHOULD_SEND = process.argv.includes('--send');

const ATTACHMENT_PATH = path.resolve(__dirname, '..', 'docs', 'walkthrough_report', 'WALKTHROUGH.html');
const ATTACHMENT_NAME = 'WALKTHROUGH.html';

const TO = ['vivmuk@gmail.com', 'ludakopeikina@gmail.com'];
const CC = ['ram@colaberry.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'AI Pathway - walkthrough wrap, 4-buttons answer, and Jennifer C asks captured';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Luda, Vivek,</p>
  <p>Luda, congrats on the Jennifer C demo. Great signal. Wrapping up a few open threads in one note so the version you are demoing is fully hardened and the new asks from JC are visibly captured.</p>
  <p>Attached is an updated WALKTHROUGH.html with 7 cards (4 fixes shipped + 3 follow-up status updates). Open in any browser, no extraction needed.</p>

  <p><strong>1. Walkthrough wrap - shipped since your review:</strong></p>
  <ul>
    <li>Skills now render in sequential rank order (1, 2, 3, 4, 5).</li>
    <li>"Back to skill review" link added on the Learning Dashboard.</li>
    <li>Ratings persist across navigation (localStorage by profile).</li>
    <li>Hover tooltip on each proficiency level now shows the per-skill, per-level rubric pulled from our ontology (Vivek, this matches the data in your ai-fluency-assessment.html).</li>
  </ul>

  <p><strong>2. Walkthrough wrap - 3 items still open:</strong></p>
  <ul>
    <li>Item 06 (interstitial rating step) is deferred per Luda's note - can come after the demo round. Spec captured in the repo.</li>
    <li>Item 14 (Build Your Agent: description / instructions / knowledge base) is queued for the next chapter-format round.</li>
    <li>Item 17 - Vivek, you marked this Issue with no comment. Quick clarifier when you have a moment: implementation concern or result concern?</li>
  </ul>

  <p><strong>3. Answer to Luda's 4-buttons question:</strong></p>
  <ul>
    <li><strong>View Profile</strong> - keep as-is.</li>
    <li><strong>Skills Profile</strong> - redesigning per your 9-point spec (~2.5h, queued).</li>
    <li><strong>Learning Path</strong> - keep as-is.</li>
    <li><strong>Ontology Path</strong> - confirmed your instinct: it routes to the older Learning Path page and duplicates the dashboard. <strong>Recommend removing the button.</strong></li>
  </ul>

  <p><strong>4. From Jennifer's feedback - captured for the next round so nothing is dropped:</strong></p>
  <ul>
    <li>"How do I know these are the right skills?" - adding an ontology-narrative surface in the UI. Luda, will wait for your proposed copy.</li>
    <li>"How do we know the AI isn't hallucinating?" - building out evaluation metrics + a disclosure pattern. Aligns with Ram's MoE-validation idea.</li>
    <li>"Make it feel like a coach" - revisiting the coach interface concept. Will sketch options for the next review.</li>
    <li>Stickiness: post-chapter progress report + next-step recommendations. Designing as a separate end-of-path surface, not inline.</li>
  </ul>

  <p>Happy to fold all of the above into Ram's proposed next-steps call so we can prioritize together.</p>
  <p>Best,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Luda, Vivek,

Luda, congrats on the Jennifer C demo. Great signal. Wrapping up a few open threads in one note so the version you are demoing is fully hardened and the new asks from JC are visibly captured.

Attached is an updated WALKTHROUGH.html with 7 cards (4 fixes shipped + 3 follow-up status updates). Open in any browser, no extraction needed.

1. Walkthrough wrap - shipped since your review:
- Skills now render in sequential rank order (1, 2, 3, 4, 5).
- Back to skill review link added on the Learning Dashboard.
- Ratings persist across navigation (localStorage by profile).
- Hover tooltip on each proficiency level now shows the per-skill, per-level rubric pulled from our ontology (Vivek, this matches the data in your ai-fluency-assessment.html).

2. Walkthrough wrap - 3 items still open:
- Item 06 (interstitial rating step) is deferred per Luda's note - can come after the demo round. Spec captured in the repo.
- Item 14 (Build Your Agent: description / instructions / knowledge base) is queued for the next chapter-format round.
- Item 17 - Vivek, you marked this Issue with no comment. Quick clarifier when you have a moment: implementation concern or result concern?

3. Answer to Luda's 4-buttons question:
- View Profile - keep as-is.
- Skills Profile - redesigning per your 9-point spec (~2.5h, queued).
- Learning Path - keep as-is.
- Ontology Path - confirmed your instinct: it routes to the older Learning Path page and duplicates the dashboard. Recommend removing the button.

4. From Jennifer's feedback - captured for the next round so nothing is dropped:
- "How do I know these are the right skills?" - adding an ontology-narrative surface in the UI. Luda, will wait for your proposed copy.
- "How do we know the AI isn't hallucinating?" - building out evaluation metrics + a disclosure pattern. Aligns with Ram's MoE-validation idea.
- "Make it feel like a coach" - revisiting the coach interface concept. Will sketch options for the next review.
- Stickiness: post-chapter progress report + next-step recommendations. Designing as a separate end-of-path surface, not inline.

Happy to fold all of the above into Ram's proposed next-steps call so we can prioritize together.

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
    } else {
      console.log('  WARNING: attachment file does not exist yet');
    }
    console.log('---');
    console.log(BODY_TEXT);
    console.log('---');
    console.log('To send: node scripts/send-vivek-reply-may12.js --send');
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
