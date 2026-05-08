/**
 * Basecamp updates for the AI Pathway project, end of 2026-05-08 session.
 *
 *  a) Mark todo 9733661947 complete (validation re-run with Luda).
 *  b) Comment on todos 9814450162 and 9814450256 with status updates.
 *  c) Create new todolist "Walkthrough Round - May 7 Luda Feedback"
 *     with 5 items, mark the "9 approved" item complete on creation.
 *  d) Post a session summary to the message board.
 *
 * All writes report the resulting URL so the user can verify.
 */
const { getToken, bc, ACCOUNT_ID } = require('./basecamp-lib');

const PROJECT_ID = '46697389';

// --- (b) comment bodies ---
const COMMENT_VIVEK_PROFICIENCY = `Update 2026-05-08: This is now formally routed to Vivek as part of Luda's walkthrough feedback (item 04). Per Luda: the hover tooltip on a skill name should show a proficiency-LEVEL-specific description that varies by both skill AND level (currently shows generic per-skill description). Vivek email sent 2026-05-08 with the live URL and the question; awaiting his decision on approve/change/discuss.`;

const COMMENT_POC_DEMO = `Update 2026-05-08: Build is demo-ready. Luda confirmed via walkthrough feedback (9 of 17 items approved; the rest awaiting Vivek's chapter review or deferred per her note). She is starting to show the tool to people now. The live build at http://95.216.199.47:3000 has all 17 walkthrough changes deployed.`;

// --- (c) new todolist contents ---
const NEW_LIST_TITLE = 'Walkthrough Round - May 7 Luda Feedback';
const NEW_LIST_DESCRIPTION = 'Outcomes from the 2026-05-07 walkthrough HTML reviewed by Luda. Created via automated Basecamp update on 2026-05-08.';

const NEW_LIST_TODOS = [
  {
    content: '9 walkthrough items approved by Luda (01, 02, 03, 05, 07, 08, 09, 10, 17) - shipped',
    description: 'Items: homepage simplified, profiles copy, skills review merged, Targeted Role rename, learning dashboard auto-activates, Journey Roadmap removed, chapter section nav, ontology-name chapter title, deterministic skill ordering. All in the build at http://95.216.199.47:3000.',
    completed: true,
  },
  {
    content: 'Item 06: Add interstitial proficiency-rating step when system swaps in replacement skills',
    description: 'Deferred per Luda. New product requirement: when a user rates initial top-5 skills at target level, the system swaps in replacement skills (6, 7, 8). Current behavior goes straight to chapters. Required: insert a page that shows the final 5-skill path (retained + added), lets the user rate proficiency on the newly-added ones, and only then proceeds to chapter generation. Spec: docs/follow_ups/06_interstitial_skill_rating.md (in repo).',
  },
  {
    content: 'Item 04: Per-skill + per-level proficiency descriptions in hover tooltip (awaiting Vivek)',
    description: "Luda's question: tooltip should pull a proficiency-level description specific to BOTH the skill AND the level (e.g. Prompt Debugging at L3 has a different description than AI Disclosure at L3). Currently shows a generic per-skill description. Vivek pinged 2026-05-08; awaiting decision.",
  },
  {
    content: 'Items 11-16: Vivek review of chapter content quality (awaiting Vivek)',
    description: '6 chapter items routed to Vivek for approve/change/discuss: 11 (concepts mnemonic + pull_quote), 12 (Example 1 3-step structure), 13 (Example 2 A/B), 14 (Build Your Agent section), 15 (Try-in-LLM buttons), 16 (Implementation Task as 6th section). Standalone email sent 2026-05-08.',
  },
  {
    content: 'Item 17: Re-validate deterministic skill ordering (Luda doing on her side; close when she confirms)',
    description: 'Luda approved item 17 with note "I will try it again to validate." Re-running Jennifer C profile multiple times should produce identical top 5 (profile_analyzer is now temperature=0). Close this todo when Luda confirms or flag as a regression if she sees variance.',
  },
];

// --- (d) message board post ---
const MESSAGE_TITLE = 'Walkthrough Round Complete - 2026-05-07/08 (Luda Feedback)';
const MESSAGE_BODY = `<div>
<p><strong>What happened:</strong> shipped the 17-change walkthrough HTML to Luda + Ram (cc Vivek) on 2026-05-06, iterated through 4 follow-up emails over 2 days fixing UX issues she surfaced, and received her structured feedback this morning (2026-05-08).</p>

<p><strong>Walkthrough delivery system established:</strong> single self-contained HTML file with embedded base64 screenshots. Reviewer marks each item Approved / Issue / Question, hits "Generate Feedback Email", and the response comes back in a parseable format (magic header <code>[ai-pathway-walkthrough-feedback-v1]</code>). Documented in CLAUDE.md so the workflow survives the session.</p>

<p><strong>Outcomes from this round:</strong></p>
<ul>
<li><strong>9 of 17 items approved</strong> by Luda - all shipped at http://95.216.199.47:3000</li>
<li><strong>1 deferred</strong> (item 06: interstitial rating page for swapped-in skills) - tracked in new todolist below</li>
<li><strong>7 routed to Vivek</strong> for chapter content review - awaiting his decisions</li>
</ul>

<p><strong>Production fixes deployed today:</strong></p>
<ul>
<li><code>frontend/src/pages/AnalysisPage.tsx</code>: fixed redirect that was sending /analysis/{pid} to /learn/{path_id} on revisit. Added <code>?view=skill_selection</code> URL param so walkthrough links land on the correct page state. Pushed to main, hot-deployed to ai-pathway-frontend-1.</li>
<li>Walkthrough script: two-phase screenshot capture (skill_selection BEFORE analysis runs, results_review/learn AFTER), Playwright audit script that verifies each card's URL and content match before send.</li>
</ul>

<p><strong>Demo status:</strong> Luda confirmed she is starting to show the tool to people. All 17 changes are live in the deployed build. Vivek's review will refine items 04 and 11-16 in the next iteration; nothing held back.</p>

<p><em>Detailed item-06 spec: docs/follow_ups/06_interstitial_skill_rating.md in the repo.</em></p>
</div>`;

(async () => {
  const token = await getToken();
  console.log('Token OK. Starting Basecamp updates for AI Pathway...\n');

  // (a) Mark 9733661947 complete
  console.log('(a) Marking todo 9733661947 complete (Validate 3-step skill selection chain)...');
  await bc(token, `/buckets/${PROJECT_ID}/todos/9733661947/completion.json`, { method: 'POST' });
  console.log('    DONE: https://3.basecamp.com/3945211/buckets/46697389/todos/9733661947\n');

  // (b) Comments
  console.log('(b1) Commenting on todo 9814450162 (Vivek: Ontology proficiency level definitions per skill)...');
  const c1 = await bc(token, `/buckets/${PROJECT_ID}/recordings/9814450162/comments.json`, {
    method: 'POST',
    body: JSON.stringify({ content: `<div>${COMMENT_VIVEK_PROFICIENCY}</div>` }),
  });
  console.log(`    DONE: ${c1.app_url}\n`);

  console.log('(b2) Commenting on todo 9814450256 (End of April POC - 3 examples ready for demo)...');
  const c2 = await bc(token, `/buckets/${PROJECT_ID}/recordings/9814450256/comments.json`, {
    method: 'POST',
    body: JSON.stringify({ content: `<div>${COMMENT_POC_DEMO}</div>` }),
  });
  console.log(`    DONE: ${c2.app_url}\n`);

  // (c) Create new todolist + add todos
  console.log(`(c) Creating new todolist "${NEW_LIST_TITLE}"...`);
  const project = await bc(token, `/projects/${PROJECT_ID}.json`);
  const todosetDock = (project.dock || []).find(d => d.name === 'todoset');
  const todosetId = todosetDock.id;
  const newList = await bc(token, `/buckets/${PROJECT_ID}/todosets/${todosetId}/todolists.json`, {
    method: 'POST',
    body: JSON.stringify({
      name: NEW_LIST_TITLE,
      description: `<div>${NEW_LIST_DESCRIPTION}</div>`,
    }),
  });
  console.log(`    LIST CREATED: ${newList.app_url}`);

  for (const t of NEW_LIST_TODOS) {
    const todo = await bc(token, `/buckets/${PROJECT_ID}/todolists/${newList.id}/todos.json`, {
      method: 'POST',
      body: JSON.stringify({
        content: t.content,
        description: t.description ? `<div>${t.description}</div>` : '',
      }),
    });
    if (t.completed) {
      await bc(token, `/buckets/${PROJECT_ID}/todos/${todo.id}/completion.json`, { method: 'POST' });
      console.log(`    + [x] ${todo.id}  ${t.content.slice(0, 80)}`);
    } else {
      console.log(`    + [ ] ${todo.id}  ${t.content.slice(0, 80)}`);
    }
  }
  console.log('');

  // (d) Message board post
  console.log('(d) Posting session summary to message board...');
  const mbDock = (project.dock || []).find(d => d.name === 'message_board');
  const post = await bc(token, `/buckets/${PROJECT_ID}/message_boards/${mbDock.id}/messages.json`, {
    method: 'POST',
    body: JSON.stringify({
      subject: MESSAGE_TITLE,
      content: MESSAGE_BODY,
      status: 'active',
    }),
  });
  console.log(`    POSTED: ${post.app_url}\n`);

  console.log('All Basecamp updates complete.');
})().catch(e => {
  console.error('FAILED:', e.message);
  process.exit(1);
});
