/**
 * Download attachments from Luda's 2026-05-09 email (thread 19e08b66b97f172e,
 * message 19e0e3bd0b82f0dd) so we can Read() them as images.
 *
 * Saves to docs/luda_may9/<filename>.
 */
require('dotenv').config();
const fs = require('fs');
const path = require('path');

const MESSAGE_ID = '19e0e3bd0b82f0dd';
const OUT_DIR = path.resolve(__dirname, '..', 'docs', 'luda_may9');

async function getAccessToken() {
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: process.env.GMAIL_CLIENT_ID,
      client_secret: process.env.GMAIL_CLIENT_SECRET,
      refresh_token: process.env.GMAIL_REFRESH_TOKEN,
      grant_type: 'refresh_token',
    }).toString(),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error('No access_token: ' + JSON.stringify(j));
  return j.access_token;
}

async function fetchJson(url, token) {
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!r.ok) throw new Error(`${url} -> ${r.status}: ${await r.text()}`);
  return r.json();
}

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const token = await getAccessToken();

  // Get the full message with payload metadata so we can iterate parts
  const msg = await fetchJson(
    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${MESSAGE_ID}?format=full`,
    token
  );

  const collect = (part, into) => {
    if (part.body && part.body.attachmentId) {
      into.push({
        filename: part.filename || `attachment-${into.length + 1}`,
        mimeType: part.mimeType,
        attachmentId: part.body.attachmentId,
        size: part.body.size,
      });
    }
    if (part.parts) part.parts.forEach(p => collect(p, into));
  };
  const attachments = [];
  collect(msg.payload, attachments);
  console.log(`Found ${attachments.length} attachment(s):`);
  for (const a of attachments) {
    console.log(`  ${a.filename}  (${a.mimeType}, ${a.size} bytes)`);
  }

  let idx = 0;
  for (const a of attachments) {
    idx += 1;
    const data = await fetchJson(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages/${MESSAGE_ID}/attachments/${a.attachmentId}`,
      token
    );
    const bytes = Buffer.from(data.data.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
    let outName = a.filename || `attachment-${idx}.bin`;
    if (!path.extname(outName)) {
      const ext = a.mimeType === 'image/png' ? '.png' : a.mimeType === 'image/jpeg' ? '.jpg' : '.bin';
      outName = `attachment-${idx}${ext}`;
    }
    // sanitize filename
    outName = outName.replace(/[^\w.\-]+/g, '_');
    const outPath = path.join(OUT_DIR, outName);
    fs.writeFileSync(outPath, bytes);
    console.log(`Saved: ${outPath} (${bytes.length} bytes)`);
  }
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
