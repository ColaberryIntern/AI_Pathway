/**
 * Read-only: list all to-do lists and their open/closed counts in the
 * AI Pathway Basecamp project, so we know where to post updates.
 */
const { getToken, bc } = require('./basecamp-lib');

const PROJECT_ID = '46697389'; // AI Pathway

(async () => {
  const token = await getToken();
  const project = await bc(token, `/projects/${PROJECT_ID}.json`);
  console.log(`Project: ${project.name} (id=${project.id})\n`);

  // The todoset dock entry on the project tells us where the todolists live.
  const todosetDock = (project.dock || []).find(d => d.name === 'todoset');
  if (!todosetDock) {
    console.log('No todoset dock found.');
    return;
  }
  console.log(`Todoset URL: ${todosetDock.app_url}`);
  const todoset = await bc(token, `/buckets/${PROJECT_ID}/todosets/${todosetDock.id}.json`);
  console.log(`Open todolists: ${todoset.todolists_count}\n`);

  const todolists = await bc(token, `/buckets/${PROJECT_ID}/todosets/${todosetDock.id}/todolists.json`);
  for (const tl of todolists) {
    console.log(`- [${tl.id}] "${tl.title}"  (${tl.completed_ratio || '0/0'} done)`);
    console.log(`    ${tl.app_url}`);
  }

  // Also fetch the message board id for posting summaries
  const mbDock = (project.dock || []).find(d => d.name === 'message_board');
  if (mbDock) {
    console.log(`\nMessage board: id=${mbDock.id}  url=${mbDock.app_url}`);
  }
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
