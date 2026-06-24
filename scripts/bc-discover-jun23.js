/**
 * Discovery: pull active Basecamp token from CCPP.Basecamp_AuthInfo, then map
 * the AI Pathway bucket (46697389) dock -> message board id + todoset id, and
 * list existing to-do lists. Run ON PROD inside accelerator-backend:/app.
 * Self-contained: no dotenv, reads MSSQL_* from process env directly.
 */
const sql = require('mssql');

const ACCOUNT_ID = '3945211';
const BUCKET = '46697389';
const API_BASE = `https://3.basecampapi.com/${ACCOUNT_ID}`;
const UA = 'Colaberry Internal Tools (ali@colaberry.com)';

const sqlConfig = {
  server: process.env.MSSQL_HOST,
  port: parseInt(process.env.MSSQL_PORT || '1433', 10),
  user: process.env.MSSQL_USER,
  password: process.env.MSSQL_PASS,
  database: process.env.MSSQL_DATABASE || 'CCPP',
  options: { encrypt: true, trustServerCertificate: true },
  pool: { max: 5, min: 0, idleTimeoutMillis: 30000 },
};

async function getToken() {
  await sql.connect(sqlConfig);
  const r = await sql.query(
    `SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive = 1 ORDER BY BasecampAuthInfoID DESC`
  );
  await sql.close();
  if (!r.recordset.length) throw new Error('No active token');
  let t = r.recordset[0].AccessToken;
  if (typeof t === 'string' && t.startsWith('Bearer ')) t = t.slice(7);
  return t;
}

const H = (t) => ({ Authorization: `Bearer ${t}`, 'User-Agent': UA, Accept: 'application/json', 'Content-Type': 'application/json' });

async function bc(t, p, init = {}) {
  const url = p.startsWith('http') ? p : `${API_BASE}${p}`;
  const r = await fetch(url, { ...init, headers: { ...H(t), ...(init.headers || {}) } });
  if (!r.ok) throw new Error(`${init.method || 'GET'} ${url} -> ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.status === 204 ? null : r.json();
}

(async () => {
  const t = await getToken();
  console.log('TOKEN_OK len=' + t.length);
  const proj = await bc(t, `/projects/${BUCKET}.json`);
  console.log('PROJECT:', proj.name);
  const dock = proj.dock || [];
  for (const d of dock) {
    console.log(`DOCK ${d.name} | id=${d.id} | enabled=${d.enabled} | title=${d.title || ''}`);
  }
  const mb = dock.find((d) => d.name === 'message_board');
  const todoset = dock.find((d) => d.name === 'todoset');
  if (todoset && todoset.enabled) {
    const ts = await bc(t, todoset.url || `/buckets/${BUCKET}/todosets/${todoset.id}.json`);
    const lists = await bc(t, ts.todolists_url);
    console.log('--- TODOLISTS ---');
    for (const l of lists) console.log(`LIST id=${l.id} | ${l.title} | todos=${l.completed_ratio || ''}`);
  }
  if (mb) console.log('MESSAGE_BOARD url=' + (mb.url || '') + ' id=' + mb.id);
})().catch((e) => { console.error('ERR:', e.message); process.exit(1); });
