/**
 * Download attachments from a Gmail message ID (or list of IDs) into a
 * given output directory.
 *
 * Usage:
 *   node scripts/download-gmail-attachments.js <outDir> <messageId> [<messageId> ...]
 */
require('dotenv').config();
const fs = require('fs');
const path = require('path');

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

function collect(part, into) {
  if (part.body && part.body.attachmentId) {
    into.push({
      filename: part.filename || `attachment-${into.length + 1}`,
      mimeType: part.mimeType,
      attachmentId: part.body.attachmentId,
      size: part.body.size,
    });
  }
  if (part.parts) part.parts.forEach(p => collect(p, into));
}

(async () => {
  const [, , outDir, ...messageIds] = process.argv;
  if (!outDir || messageIds.length === 0) {
    console.error('Usage: node scripts/download-gmail-attachments.js <outDir> <messageId> [<messageId> ...]');
    process.exit(1);
  }
  fs.mkdirSync(outDir, { recursive: true });
  const token = await getAccessToken();

  for (const messageId of messageIds) {
    console.log(`\n=== ${messageId} ===`);
    const msg = await fetchJson(
      `https://gmail.googleapis.com/gmail/v1/users/me/messages/${messageId}?format=full`,
      token
    );
    const attachments = [];
    collect(msg.payload, attachments);
    if (!attachments.length) {
      console.log('  (no attachments)');
      continue;
    }
    let counter = 0;
    for (const a of attachments) {
      counter += 1;
      const data = await fetchJson(
        `https://gmail.googleapis.com/gmail/v1/users/me/messages/${messageId}/attachments/${a.attachmentId}`,
        token
      );
      const bytes = Buffer.from(data.data.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
      let outName = a.filename || `attachment-${counter}.bin`;
      if (!path.extname(outName)) {
        const ext = a.mimeType === 'image/png' ? '.png' :
                    a.mimeType === 'image/jpeg' ? '.jpg' :
                    a.mimeType === 'text/html' ? '.html' :
                    a.mimeType === 'application/pdf' ? '.pdf' : '.bin';
        outName = `attachment-${counter}${ext}`;
      }
      outName = outName.replace(/[^\w.\-]+/g, '_');
      // Prefix with message id + index so files from different messages don't collide
      const finalName = `${messageId.slice(-8)}_${counter}_${outName}`;
      const outPath = path.join(outDir, finalName);
      fs.writeFileSync(outPath, bytes);
      console.log(`  Saved: ${path.basename(outPath)} (${bytes.length} bytes, ${a.mimeType})`);
    }
  }
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
