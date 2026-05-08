/**
 * Read-only: show all to-dos (open + completed) for the lists most likely
 * to overlap with today's session work, so we know which to close vs.
 * which to add.
 */
const { getToken, paginate } = require('./basecamp-lib');

const PROJECT_ID = '46697389';
const RELEVANT_LISTS = [
  { id: '9814449650', label: 'Apr 10 Meeting Actions & Flow Changes' },
  { id: '9746826846', label: 'Luda Feedback - Jennifer C Test Run (Apr 1)' },
  { id: '9733448989', label: 'Tasks: AI Pathway feedback and demo preparation' },
  { id: '9733661887', label: 'Current Sprint - Week of March 31' },
];

(async () => {
  const token = await getToken();
  for (const list of RELEVANT_LISTS) {
    console.log(`\n=== [${list.id}] ${list.label} ===`);
    // Open + completed in one paginated call
    const open = await paginate(token, `/buckets/${PROJECT_ID}/todolists/${list.id}/todos.json`);
    const closed = await paginate(token, `/buckets/${PROJECT_ID}/todolists/${list.id}/todos.json?completed=true`);
    console.log(`  OPEN (${open.length}):`);
    for (const t of open) {
      console.log(`    [ ] ${t.id}  ${t.title.replace(/\s+/g, ' ').slice(0, 110)}`);
    }
    console.log(`  DONE (${closed.length}):`);
    for (const t of closed) {
      console.log(`    [x] ${t.id}  ${t.title.replace(/\s+/g, ' ').slice(0, 110)}`);
    }
  }
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
