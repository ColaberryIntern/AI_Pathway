/** Post the Jun 23 build-session closing summary to the AI Pathway message board. Run on prod. */
const sql = require('mssql');
const ACCOUNT_ID = '3945211', BUCKET = '46697389', MSGBOARD = '9733430264';
const API_BASE = `https://3.basecampapi.com/${ACCOUNT_ID}`;
const UA = 'Colaberry Internal Tools (ali@colaberry.com)';
const sqlConfig = { server: process.env.MSSQL_HOST, port: parseInt(process.env.MSSQL_PORT || '1433', 10), user: process.env.MSSQL_USER, password: process.env.MSSQL_PASS, database: process.env.MSSQL_DATABASE || 'CCPP', options: { encrypt: true, trustServerCertificate: true } };
async function getToken() { await sql.connect(sqlConfig); const r = await sql.query(`SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive=1 ORDER BY BasecampAuthInfoID DESC`); await sql.close(); let t = r.recordset[0].AccessToken; if (t.startsWith('Bearer ')) t = t.slice(7); return t; }
const H = (t) => ({ Authorization: `Bearer ${t}`, 'User-Agent': UA, Accept: 'application/json', 'Content-Type': 'application/json' });

const HTML = `
<div>
<p>Follow-up to the Jun 23 recap: I worked the ticket list as a loop (build -> break -> harden -> verify -> update ticket -> close). Status below.</p>

<h3>Built + verified + closed</h3>
<ul>
<li><b>Chapter breadth + depth judge (the urgent one)</b> - with a written rubric (the piece that was missing from the 6/9 spec). LLM scores per criterion 1-5; Python owns the composite + gate. 15 tests.</li>
<li><b>Users can walk through chapters themselves</b> - added path-wide Previous/Next to the chapter view; no longer have to mark complete and bounce through the dashboard to advance.</li>
<li><b>LinkedIn parser judge</b> - turned the script-only judge into a reusable tested module, fixed it to use the pinned judge model, made ontology precision deterministic. 19 new tests.</li>
<li><b>Enterprise base curriculum (MVP)</b> - admin UI to define the base skills + paths now layer personalized gaps on top. One global base for MVP (per-tenant comes with multi-tenancy). No-op until a base is set, so nothing existing changes. 12 tests.</li>
</ul>

<h3>Delivered, decision needed from you</h3>
<ul>
<li><b>Ontology cleanup</b> - audit done: of 220 skills, only 66 are actually used in real paths; 154 are orphans, and 7 whole domains have zero usage. Structurally clean, no integrity issues. I did NOT delete anything - pruning is your + Vivek's IP call and is gated. Ticket left open with the candidate list + a safe approach (decide the keep-set, quarantine before delete, re-run the gates).</li>
</ul>

<h3>Docs written</h3>
<ul>
<li>MVP definition (the two steps).</li>
<li>Decision: defer self-improving loops, adopt MOA mixture-of-experts judges (Ram's call).</li>
</ul>

<h3>Scoped, NOT built (Strategic - need sign-off)</h3>
<ul>
<li><b>Multi-tenancy</b> - confirmed greenfield (no org model exists today; the "switch" was not actually there). Design doc written.</li>
<li><b>Third-party auth / SSO</b> - design doc written.</li>
<li><b>Private-data handling + RLS</b> - design doc written.</li>
</ul>
<p>Each of these three has a ticket left open with a design doc and the open decisions.</p>

<h3>Not engineering (yours)</h3>
<ul>
<li>Women Applying AI pilot (tracks + pricing), tester categories, and the meeting move to Tuesdays 3:00 PM ET are tracked as tickets.</li>
</ul>

<p>Caveat: the code changes are in the working tree and tested, not yet deployed. The frontend + path-generator changes need a Gate 2 (verify_profile_e2e) run after deploy.</p>
</div>`;

(async () => {
  const t = await getToken();
  const r = await fetch(`${API_BASE}/buckets/${BUCKET}/message_boards/${MSGBOARD}/messages.json`, {
    method: 'POST', headers: H(t),
    body: JSON.stringify({ subject: 'Jun 23 build session - results', content: HTML, status: 'active' }),
  });
  if (!r.ok) { console.error('ERR', r.status, (await r.text()).slice(0, 300)); process.exit(1); }
  const m = await r.json();
  console.log('CLOSING_POSTED', m.id, m.app_url);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
