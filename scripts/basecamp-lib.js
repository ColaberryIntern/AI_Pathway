/**
 * Basecamp 4 helper for the AI Pathway project.
 *
 * Token rotates every two weeks and lives in CCPP.Basecamp_AuthInfo on the
 * Hosted Applied Insights MSSQL server. Pull the latest active row at the
 * top of every script run; never cache across runs.
 */
require('dotenv').config();

const sql = require('mssql');

const ACCOUNT_ID = '3945211';
const API_BASE = `https://3.basecampapi.com/${ACCOUNT_ID}`;
const USER_AGENT = 'Colaberry Internal Tools (ali@colaberry.com)';

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
  if (!process.env.MSSQL_HOST || !process.env.MSSQL_USER || !process.env.MSSQL_PASS) {
    throw new Error('Missing MSSQL_HOST / MSSQL_USER / MSSQL_PASS in .env');
  }
  await sql.connect(sqlConfig);
  const r = await sql.query(
    `SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo
     WHERE IsActive = 1 ORDER BY BasecampAuthInfoID DESC`
  );
  await sql.close();
  if (!r.recordset.length) {
    throw new Error('No active Basecamp token in CCPP.Basecamp_AuthInfo');
  }
  let t = r.recordset[0].AccessToken;
  if (typeof t === 'string' && t.startsWith('Bearer ')) t = t.slice(7);
  return t;
}

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    'User-Agent': USER_AGENT,
    Accept: 'application/json',
    'Content-Type': 'application/json',
  };
}

async function bc(token, pathOrUrl, init = {}) {
  const url = pathOrUrl.startsWith('http') ? pathOrUrl : `${API_BASE}${pathOrUrl}`;
  const resp = await fetch(url, {
    ...init,
    headers: { ...authHeaders(token), ...(init.headers || {}) },
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Basecamp ${init.method || 'GET'} ${url} -> ${resp.status}: ${text.slice(0, 300)}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

async function paginate(token, path) {
  const out = [];
  let url = `${API_BASE}${path}`;
  while (url) {
    const resp = await fetch(url, { headers: authHeaders(token) });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`Basecamp paginate ${url} -> ${resp.status}: ${text.slice(0, 300)}`);
    }
    out.push(...(await resp.json()));
    const link = resp.headers.get('link') || '';
    const m = /<([^>]+)>;\s*rel="next"/.exec(link);
    url = m ? m[1] : null;
  }
  return out;
}

module.exports = { ACCOUNT_ID, API_BASE, USER_AGENT, getToken, authHeaders, bc, paginate };
