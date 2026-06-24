/**
 * Apply a batch of ticket actions: post a comment to a to-do and optionally
 * complete it. Reads /app/bc-actions.json = [{ todo, comment, complete }].
 * Run ON PROD inside accelerator-backend:/app.
 */
const fs = require('fs');
const sql = require('mssql');
const ACCOUNT_ID = '3945211', BUCKET = '46697389';
const API_BASE = `https://3.basecampapi.com/${ACCOUNT_ID}`;
const UA = 'Colaberry Internal Tools (ali@colaberry.com)';
const sqlConfig = { server: process.env.MSSQL_HOST, port: parseInt(process.env.MSSQL_PORT || '1433', 10), user: process.env.MSSQL_USER, password: process.env.MSSQL_PASS, database: process.env.MSSQL_DATABASE || 'CCPP', options: { encrypt: true, trustServerCertificate: true } };
async function getToken() { await sql.connect(sqlConfig); const r = await sql.query(`SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive=1 ORDER BY BasecampAuthInfoID DESC`); await sql.close(); let t = r.recordset[0].AccessToken; if (t.startsWith('Bearer ')) t = t.slice(7); return t; }
const H = (t) => ({ Authorization: `Bearer ${t}`, 'User-Agent': UA, Accept: 'application/json', 'Content-Type': 'application/json' });
async function bc(t, p, init = {}) { const url = p.startsWith('http') ? p : `${API_BASE}${p}`; const r = await fetch(url, { ...init, headers: { ...H(t), ...(init.headers || {}) } }); if (!r.ok) throw new Error(`${init.method || 'GET'} ${url} -> ${r.status}: ${(await r.text()).slice(0, 300)}`); return r.status === 204 ? null : r.json(); }
(async () => {
  const actions = JSON.parse(fs.readFileSync('/app/bc-actions.json', 'utf8'));
  const t = await getToken();
  for (const a of actions) {
    if (a.comment) {
      await bc(t, `/buckets/${BUCKET}/recordings/${a.todo}/comments.json`, { method: 'POST', body: JSON.stringify({ content: a.comment }) });
      console.log('COMMENTED', a.todo);
    }
    if (a.complete) {
      await bc(t, `/buckets/${BUCKET}/todos/${a.todo}/completion.json`, { method: 'POST' });
      console.log('COMPLETED', a.todo);
    }
  }
  console.log('DONE', actions.length);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
