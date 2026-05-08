require('dotenv').config();

const SHOULD_SEND = process.argv.includes('--send');

const TO = ['vivmuk@gmail.com'];
const CC = ['ludakopeikina@gmail.com', 'ram@colaberry.com'];
const BCC = ['ali@colaberry.com'];
const SUBJECT = 'Need your eyes on 7 chapter items - Luda routed to you';

const SIGNATURE_HTML = `<table cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;line-height:1.5;margin-top:24px"><tr><td style="padding-bottom:6px"><strong style="font-size:15px;color:#000000">Ali Muwwakkil</strong><br><span style="color:#1a8fb5">Managing Director &mdash; AI Systems Architect</span></td></tr><tr><td style="padding-bottom:6px;color:#666666">Colaberry Inc.</td></tr><tr><td style="padding-bottom:4px"><span>&#128205; 200 Chisholm Place, Suite 200 &middot; Plano, TX 75075</span></td></tr><tr><td style="padding-bottom:8px"><a href="mailto:ali@colaberry.com" style="color:#0066cc;text-decoration:none">ali@colaberry.com</a> &nbsp;&middot;&nbsp; <a href="https://enterprise.colaberry.ai" style="color:#0066cc;text-decoration:none">enterprise.colaberry.ai</a></td></tr><tr><td><a href="https://enterprise.colaberry.ai" style="display:inline-block;padding:8px 18px;background-color:#1a8fb5;color:#ffffff;text-decoration:none;border-radius:20px;font-size:13px">&#128640; Design Your AI Organization</a></td></tr></table>`;

const ANALYSIS_URL = 'http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869?view=skill_selection';
const LESSON_URL = 'http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038';

const BODY_HTML = `<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#222222;line-height:1.55;max-width:680px">
  <p>Hi Vivek,</p>
  <p>Luda finished her walkthrough review and routed 7 items to you. They are mostly on chapter content and quality, which is your domain. The walkthrough HTML is in the thread Luda CC'd you on yesterday if you want the full context.</p>
  <p>For each item below, please reply with: <strong>approve as-is</strong>, <strong>change to X</strong>, or <strong>need to discuss</strong>. The first one (item 04) is the only one with a substantive question from Luda; the other six are open for your judgment.</p>

  <p><strong>Item 04 - Hover tooltip with ontology description on skill name</strong><br>
  <a href="${ANALYSIS_URL}">${ANALYSIS_URL}</a><br>
  <em>Luda's question:</em> "I thought that we will pull from the ontology the description of the proficiency level for EACH skill. Meaning that the description will be relevant to that skill, e.g. Prompt Debugging and Iteration. And it will be different from AI Generated Content Disclosure."<br>
  <em>Current behavior:</em> the tooltip shows a generic ontology description per skill (the skill's own description). Luda is asking if instead it should show a proficiency-LEVEL-specific description that varies by both skill AND level.</p>

  <p><strong>Item 11 - Concepts section with mnemonic + pull_quote</strong><br>
  <a href="${LESSON_URL}">Open chapter, Concepts tab</a><br>
  <em>Luda:</em> "I am ok with this, we can incorporate into the tool for the first POC review with Jennifer. Vivek, please review as well."</p>

  <p><strong>Item 12 - Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)</strong><br>
  <a href="${LESSON_URL}">Open chapter, Example 1 tab</a><br>
  <em>Luda:</em> "Vivek to review."</p>

  <p><strong>Item 13 - Example 2 A/B comparison</strong><br>
  <a href="${LESSON_URL}">Open chapter, Example 2 tab</a><br>
  <em>Luda:</em> "Vivek to review."</p>

  <p><strong>Item 14 - Build Your Agent section</strong><br>
  <a href="${LESSON_URL}">Open chapter, Build tab</a><br>
  <em>Luda:</em> "Vivek to review."</p>

  <p><strong>Item 15 - Try-in-LLM buttons (Run in ChatGPT / Claude)</strong><br>
  <a href="${LESSON_URL}">Open chapter, Example 1 tab (look for Run in ChatGPT button)</a><br>
  <em>Luda:</em> "Vivek to review."</p>

  <p><strong>Item 16 - Implementation Task as 6th section</strong><br>
  <a href="${LESSON_URL}">Open chapter, Assignment tab</a><br>
  <em>Luda:</em> "Vivek to review."</p>

  <p>Once you reply, I will fold your decisions into the next round and send Luda a confirmation. She is ready to demo with Jennifer on the current build, so this is not blocking the demo - just shaping what we change for the next iteration.</p>
  <p>Thanks,</p>
</div>${SIGNATURE_HTML}`;

const BODY_TEXT = `Hi Vivek,

Luda finished her walkthrough review and routed 7 items to you. They are mostly on chapter content and quality, which is your domain. The walkthrough HTML is in the thread Luda CC'd you on yesterday if you want the full context.

For each item below, please reply with: approve as-is, change to X, or need to discuss. The first one (item 04) is the only one with a substantive question from Luda; the other six are open for your judgment.

Item 04 - Hover tooltip with ontology description on skill name
${ANALYSIS_URL}
Luda's question: "I thought that we will pull from the ontology the description of the proficiency level for EACH skill. Meaning that the description will be relevant to that skill, e.g. Prompt Debugging and Iteration. And it will be different from AI Generated Content Disclosure."
Current behavior: the tooltip shows a generic ontology description per skill (the skill's own description). Luda is asking if instead it should show a proficiency-LEVEL-specific description that varies by both skill AND level.

Item 11 - Concepts section with mnemonic + pull_quote
${LESSON_URL}
(Open chapter, Concepts tab)
Luda: "I am ok with this, we can incorporate into the tool for the first POC review with Jennifer. Vivek, please review as well."

Item 12 - Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)
${LESSON_URL}
(Open chapter, Example 1 tab)
Luda: "Vivek to review."

Item 13 - Example 2 A/B comparison
${LESSON_URL}
(Open chapter, Example 2 tab)
Luda: "Vivek to review."

Item 14 - Build Your Agent section
${LESSON_URL}
(Open chapter, Build tab)
Luda: "Vivek to review."

Item 15 - Try-in-LLM buttons (Run in ChatGPT / Claude)
${LESSON_URL}
(Open chapter, Example 1 tab, look for Run in ChatGPT button)
Luda: "Vivek to review."

Item 16 - Implementation Task as 6th section
${LESSON_URL}
(Open chapter, Assignment tab)
Luda: "Vivek to review."

Once you reply, I will fold your decisions into the next round and send Luda a confirmation. She is ready to demo with Jennifer on the current build, so this is not blocking the demo - just shaping what we change for the next iteration.

Thanks,
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
    console.log('To send for real: node scripts/send-vivek-chapter-questions.js --send');
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
