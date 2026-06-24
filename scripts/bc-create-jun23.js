/**
 * Create the Jun 23 weekly-sync to-do list + all tickets, and post the
 * message-board overall update for the AI Pathway bucket. Run ON PROD inside
 * accelerator-backend:/app. Prints a JSON manifest of created ids/urls.
 */
const sql = require('mssql');

const ACCOUNT_ID = '3945211';
const BUCKET = '46697389';
const TODOSET = '9733430267';
const MSGBOARD = '9733430264';
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
  const r = await sql.query(`SELECT TOP 1 AccessToken FROM Basecamp_AuthInfo WHERE IsActive = 1 ORDER BY BasecampAuthInfoID DESC`);
  await sql.close();
  let t = r.recordset[0].AccessToken;
  if (typeof t === 'string' && t.startsWith('Bearer ')) t = t.slice(7);
  return t;
}
const H = (t) => ({ Authorization: `Bearer ${t}`, 'User-Agent': UA, Accept: 'application/json', 'Content-Type': 'application/json' });
async function bc(t, p, init = {}) {
  const url = p.startsWith('http') ? p : `${API_BASE}${p}`;
  const r = await fetch(url, { ...init, headers: { ...H(t), ...(init.headers || {}) } });
  if (!r.ok) throw new Error(`${init.method || 'GET'} ${url} -> ${r.status}: ${(await r.text()).slice(0, 400)}`);
  return r.status === 204 ? null : r.json();
}

// One entry per ticket. group: BUILD (built this session), DOC (decision/spec
// doc this session), DEFER (strategic, scoped only), BIZ/OPS (non-engineering).
const TICKETS = [
  { key: 'judge_breadth_depth', group: 'BUILD', title: '[URGENT] Chapter content breadth + depth judge with documented rubric',
    desc: `Luda flagged this as the most urgent to-do: we have not built or documented the judge that scores generated chapter content for <b>breadth</b> and <b>depth</b>. The 6/9 spec (item #4) proposed it but did not contain a visible rubric, so the parameters of judging were unclear.<br><br><b>Deliverable:</b> a deterministic-gated judge (LLM produces per-dimension scores, Python computes the composite + gate) with a written rubric: dimensions, level anchors, pass threshold. Pinned judge model, calibrated against a golden reference. Per Trust-Before-Intelligence: the LLM never grades its own arithmetic.` },
  { key: 'chapter_walkthrough', group: 'BUILD', title: 'Let users walk through chapters themselves (alpha gate)',
    desc: `Today individual users rate the tool 4.5+ but only see what Luda screen-shares; they cannot click through the chapters themselves. For alpha testers we need the chapters reachable and navigable in the live app.` },
  { key: 'linkedin_parser_judge', group: 'BUILD', title: 'LinkedIn profile parser + its judge',
    desc: `Ali + Luda discussed a LinkedIn profile parser. Parser is largely built (uncommitted). Finish it, add a judge that scores how well it parsed (consistent with our per-step judge philosophy), add tests, commit.` },
  { key: 'enterprise_base_curriculum', group: 'BUILD', title: 'Enterprise base-curriculum capability (MVP: data + UI)',
    desc: `The B2B minimum (item D): let an enterprise define a <b>base</b> set of skills everyone must know, then layer personalized pathways on top so every served path includes the base skills. MVP = a data model for the base + a UI to define it (changeable later). Goal: the tool visibly "spells enterprise," not just B2C.` },
  { key: 'ontology_cleanup', group: 'BUILD', title: 'Ontology cleanup (220 skills, remnants, IP hygiene)',
    desc: `Ontology has grown to 220 skills with remnants of features added then removed. Identify dead/placeholder nodes and stale references, clean them, and tighten IP hygiene so the ontology is not "all over the place." Gated: re-run sweep_integrity (Gate 1) + verify_profile_e2e (Gate 2) after.` },
  { key: 'mvp_definition', group: 'DOC', title: 'MVP definition doc (enterprise-show step + alpha-ready criteria)',
    desc: `Capture the two-step MVP Luda defined: (1) something to show enterprises that this is software for them (enterprise base + light monitoring), used to show VCs for pre-seed - explicitly POC/MVP, not production/secure; (2) alpha-ready = chapter content done + cleanup done + private-data handling defined.` },
  { key: 'moa_judges_decision', group: 'DOC', title: 'DECISION: defer self-improving loops; adopt MOA mixture-of-experts judges',
    desc: `Ram is wary of self-improving loops (unbounded cost, fuzzy stop condition, ballooning context). Agreed direction (Luda + Vivek concur): crisply define a judge at each step and simply fix what the judge fails, rather than run a self-improving loop. Adopt the MOA / mixture-of-experts pattern: judges with defined characters for adversarial judging (more reliable + better storytelling). Phase 1 = define how we judge; richer pieces later. Document as the governing decision.` },
  { key: 'multitenancy', group: 'DEFER', title: '[SCOPED] Multi-tenancy (greenfield)',
    desc: `Net-new: no tenant/organization model exists in the backend today. Bare-minimum multi-tenancy: a company onboards (email/domain), gets its own space + a light dashboard to monitor who is doing what. NOT full SOC2. Strategic (DB schema + architecture) per CLAUDE.md, so scoped here with a design doc; not built this session.` },
  { key: 'sso_auth', group: 'DEFER', title: '[SCOPED] Third-party auth / SSO (no stored passwords)',
    desc: `Ram: use a third-party identity provider (Okta-style) with MFA; we do not store passwords. Users log in, we assign them to an organization, no content access without login. Strategic (external dependency + security posture); scoped with a design doc, not built this session.` },
  { key: 'private_data_rls', group: 'DEFER', title: '[SCOPED] Private-data handling definition + row-level security',
    desc: `Define what counts as private data (e.g. the user's target JD/position description: public but feels private; we keep it). Standard DB RLS for tenant isolation; file storage security to follow. Strategic (security posture); scoped with a design doc, not built this session.` },
  { key: 'biz_women_applying_ai', group: 'BIZ', title: '[Luda] Women Applying AI pilot: tracks + pricing',
    desc: `Luda to define tracks in Women Applying AI (2000 members) - base, intermediate, financial, etc. - and use them like an enterprise base with personalized paths on top; figure out pricing and how we work with them. First pilot + data source. Engineering dependency: the enterprise base-curriculum capability above.` },
  { key: 'biz_tester_categories', group: 'BIZ', title: '[All] Define technical tester categories for recruiting',
    desc: `So far testers skewed marketing. Define the categories of people we want to test with (more technical personas) so Luda can recruit them.` },
  { key: 'ops_meeting_time', group: 'OPS', title: '[Ops] Move weekly sync to Tuesdays 3:00 PM ET',
    desc: `Agreed to move the weekly sync from Tuesday evening to Tuesday 3:00-3:30 PM Eastern. Luda to move the invite. (Vivek off next week.)` },
];

const MESSAGE_SUBJECT = 'Weekly sync recap + plan - Tue Jun 23';
const MESSAGE_HTML = `
<div>
<p>Recap of tonight's weekly sync (Luda, Ram, Vivek, Ali) and the plan coming out of it. Full ticket list is in the new to-do list "<b>AI Pathway - actions from June 23 weekly sync</b>."</p>

<h3>MVP definition (Luda)</h3>
<ol>
<li><b>Show enterprises it is software for them</b> - an enterprise base curriculum + light monitoring, used to show VCs for the pre-seed round. Explicitly a POC/MVP, not production or fully secured.</li>
<li><b>Alpha-ready</b> = chapter content done + ontology/code cleanup done + private-data handling defined.</li>
</ol>

<h3>Decisions</h3>
<ul>
<li><b>Self-improving loops: deferred.</b> They are expensive and hard to bound. Instead we crisply define a judge at each step and fix what the judge fails. We adopt the MOA / mixture-of-experts pattern - judges with defined characters for adversarial judging (Ram's recommendation, Luda and Vivek concur).</li>
<li><b>Multi-tenancy is greenfield.</b> It is not in the product yet; it will be built net-new as a scoped effort (bare-minimum tenancy + a light "who is doing what" dashboard, not SOC2).</li>
<li><b>Enterprise angle.</b> Add the ability to load an enterprise base skill set and layer personalized pathways on top so the tool visibly spells enterprise, not just B2C.</li>
<li><b>Private data / auth.</b> Lean on third-party login (Okta-style, MFA, no stored passwords) + standard row-level security; define what private data is and how we keep it.</li>
</ul>

<h3>Most urgent to-do</h3>
<p>The <b>chapter content breadth + depth judge</b> with a documented rubric. The 6/9 spec proposed it but the rubric/parameters were not visible. Building it with a written rubric now.</p>

<h3>Being built this session</h3>
<ul>
<li>Content breadth/depth judge + rubric (urgent)</li>
<li>Users can walk through chapters themselves</li>
<li>LinkedIn profile parser + its judge</li>
<li>Enterprise base-curriculum capability (data + UI)</li>
<li>Ontology cleanup (220 skills, remnants)</li>
<li>MVP definition + MOA-judges decision docs</li>
</ul>
<p>Scoped but not built this session (strategic): multi-tenancy, SSO/third-party auth, private-data + RLS - each gets a design doc and a ticket.</p>

<h3>Non-engineering</h3>
<ul>
<li>Luda: Women Applying AI pilot - define tracks + pricing; first pilot and data source.</li>
<li>All: define technical tester categories so Luda can recruit beyond marketing folks.</li>
<li>Ops: weekly sync moves to <b>Tuesdays 3:00 PM ET</b>.</li>
</ul>
</div>`;

(async () => {
  const t = await getToken();
  const manifest = { created_at_note: 'jun23', list: null, todos: {}, message: null };

  // 1. to-do list
  const ts = await bc(t, `/buckets/${BUCKET}/todosets/${TODOSET}.json`);
  const list = await bc(t, ts.todolists_url, {
    method: 'POST',
    body: JSON.stringify({ name: 'AI Pathway - actions from June 23 weekly sync',
      description: 'Tickets from the Jun 23 weekly sync. BUILD = built this session; DOC = decision/spec; SCOPED = strategic, design only; Luda/Ops = non-engineering.' }),
  });
  manifest.list = { id: list.id, url: list.app_url, todos_url: list.todos_url };
  console.log('LIST_CREATED', list.id, list.app_url);

  // 2. todos
  for (const tk of TICKETS) {
    const todo = await bc(t, list.todos_url, {
      method: 'POST',
      body: JSON.stringify({ content: tk.title, description: tk.desc }),
    });
    manifest.todos[tk.key] = { id: todo.id, url: todo.app_url, group: tk.group, title: tk.title };
    console.log('TODO', tk.group, tk.key, todo.id);
  }

  // 3. message board post
  const msg = await bc(t, `/buckets/${BUCKET}/message_boards/${MSGBOARD}/messages.json`, {
    method: 'POST',
    body: JSON.stringify({ subject: MESSAGE_SUBJECT, content: MESSAGE_HTML, status: 'active' }),
  });
  manifest.message = { id: msg.id, url: msg.app_url };
  console.log('MESSAGE_POSTED', msg.id, msg.app_url);

  console.log('MANIFEST_JSON_START');
  console.log(JSON.stringify(manifest, null, 2));
  console.log('MANIFEST_JSON_END');
})().catch((e) => { console.error('ERR:', e.message); process.exit(1); });
