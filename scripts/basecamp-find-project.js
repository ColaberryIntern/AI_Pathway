/**
 * One-shot: pull the active token, list all Basecamp projects, and report
 * which row looks most like "AI Pathway" (or print all so the user can pick).
 *
 * Read-only. Never writes.
 */
const { getToken, paginate } = require('./basecamp-lib');

(async () => {
  const token = await getToken();
  console.log(`Token fetched (${token.length} chars). Listing projects...`);
  const projects = await paginate(token, '/projects.json');
  console.log(`Found ${projects.length} active projects.\n`);

  const matchTerms = ['ai pathway', 'pathway', 'ai_pathway', 'colaberry ai'];
  const matches = projects.filter(p => {
    const name = (p.name || '').toLowerCase();
    return matchTerms.some(t => name.includes(t));
  });

  if (matches.length) {
    console.log(`Likely AI Pathway candidates:`);
    for (const p of matches) {
      console.log(`  - id=${p.id}  name="${p.name}"  url=${p.app_url}`);
    }
    console.log('');
  }

  console.log(`All projects (id | name):`);
  for (const p of projects) {
    console.log(`  ${p.id}  ${p.name}`);
  }
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
