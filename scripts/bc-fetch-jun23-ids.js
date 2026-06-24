/** Find the Jun 23 to-do list and dump all todo ids + titles as JSON. Run on prod. */
const sql = require('mssql');
const ACCOUNT_ID = '3945211', BUCKET = '46697389', TODOSET = '9733430267';
const API_BASE = `https://3.basecampapi.com/${ACCOUNT_ID}`;
const UA = 'Colaberry Internal Tools (ali@colaberry.com)';
const sqlConfig = { server: process.env.MSSQL_HOST, port: parseInt(process.env.MSSQL_PORT || '1433', 10), user: process.env.MSSQL_USER, password: process.env.MSSQL_PASS, database: process.env.MSSQL_DATABASE || 'CCPP', options: { encrypt: true, trustServerCertificate: true } };
async function getToken() { await sql.connect(sqlConfig); const r = await sql.query(`SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive=1 ORDER BY BasecampAuthInfoID DESC`); await sql.close(); let t = r.recordset[0].AccessToken; if (t.startsWith('Bearer ')) t = t.slice(7); return t; }
const H = (t) => ({ Authorization: `Bearer ${t}`, 'User-Agent': UA, Accept: 'application/json', 'Content-Type': 'application/json' });
async function bc(t, p) { const r = await fetch(p.startsWith('http') ? p : `${API_BASE}${p}`, { headers: H(t) }); if (!r.ok) throw new Error(r.status + ': ' + (await r.text()).slice(0, 200)); return r.json(); }
(async () => {
  const t = await getToken();
  const ts = await bc(t, `/buckets/${BUCKET}/todosets/${TODOSET}.json`);
  const lists = await bc(t, ts.todolists_url);
  const list = lists.find((l) => l.title.includes('June 23 weekly sync'));
  const todos = await bc(t, list.todos_url);
  const out = { list: { id: list.id, url: list.app_url, todos_url: list.todos_url }, todos: todos.map((x) => ({ id: x.id, title: x.content, url: x.app_url, completed: x.completed })) };
  console.log('FETCH_JSON_START'); console.log(JSON.stringify(out, null, 2)); console.log('FETCH_JSON_END');
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
