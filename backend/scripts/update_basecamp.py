"""Update Basecamp with new tickets and mark completed ones done."""
import httpx
import asyncio

TOKEN = "BAhbB0kiAbB7ImNsaWVudF9pZCI6IjNkMzNmMzFiNDQ3YjRmODg1YTA1NTQwNzBjZjNmMWQ1ODdlMjM5MzAiLCJleHBpcmVzX2F0IjoiMjAyNi0wNS0wMVQwMTo0MDo0N1oiLCJ1c2VyX2lkcyI6WzQ1MzIxNzUxXSwidmVyc2lvbiI6MSwiYXBpX2RlYWRib2x0IjoiNmQ5NDQ4OThkN2U4ZDdhMmU4YmExMjg4M2ViOWYyYWQifQY6BkVUSXU6CVRpbWUNIZAfwJSA8aIJOg1uYW5vX251bWlcOg1uYW5vX2RlbmkGOg1zdWJtaWNybyIHCHA6CXpvbmVJIghVVEMGOwBG--d68baff8b7762d6b84a8f293414938a446868ea7"
PROJECT = '46697389'
BASE = 'https://3.basecampapi.com/3945211'
ALI_ID = 17454835


async def main():
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'User-Agent': 'AI Pathway (ali@colaberry.com)',
        'Content-Type': 'application/json',
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f'{BASE}/projects/{PROJECT}.json', headers=headers)
        project = r.json()
        ts_id = next(d['id'] for d in project['dock'] if d['name'] == 'todoset')

        # Create new todolist
        r = await client.post(
            f'{BASE}/buckets/{PROJECT}/todosets/{ts_id}/todolists.json',
            headers=headers,
            json={
                'name': 'Apr 10 Meeting Actions & Flow Changes',
                'description': 'From April 10 IIA meeting and Luda page-by-page feedback (Apr 15).',
            }
        )
        nl = r.json()
        nl_id = nl['id']
        print(f'Created: {nl["name"]}')
        print(f'  https://3.basecamp.com/3945211/buckets/{PROJECT}/todolists/{nl_id}')

        # Completed items
        done = [
            ("Simplify homepage - remove How it works and Ready to start", "Completed Apr 15."),
            ("Rename Detected Role to Targeted Role throughout tool", "Completed Apr 15."),
            ("Merge skill selection + self-assessment into one page", "Completed Apr 15. Inline proficiency rating below each skill."),
            ("Build skills-match-target-level logic", "Completed Apr 16. Tested end-to-end. Skills at target removed, path backfills."),
            ("Rename analyzing step to Generating Your Learning Path", "Completed Apr 15."),
            ("Remove intermediate pages 6-8 for cleaner flow", "Completed Apr 15."),
            ("Deterministic 5-factor rubric scoring engine", "Completed Apr 6. 5/5 match with Claude. 20/20 consistency."),
            ("Dynamic lesson format - no code for non-technical", "Completed Apr 2. Verified 50 profiles."),
            ("Knowledge checks only test taught content", "Completed Apr 8."),
            ("Implementation tasks provide all data inline", "Completed Apr 8."),
            ("Reflection questions reference specific task", "Completed Apr 8."),
            ("Time estimates capped at 60 minutes", "Completed Apr 8."),
        ]

        for title, note in done:
            r = await client.post(
                f'{BASE}/buckets/{PROJECT}/todolists/{nl_id}/todos.json',
                headers=headers,
                json={'content': title, 'description': f'<div>{note}</div>', 'assignee_ids': [ALI_ID]}
            )
            tid = r.json()['id']
            await client.post(f'{BASE}/buckets/{PROJECT}/todos/{tid}/completion.json', headers=headers)
            print(f'  [DONE] {title[:55]}')

        # Open items
        todo = [
            ("Vivek: Ontology proficiency level definitions per skill", "Waiting on Vivek. Detailed objectives for each level."),
            ("Vivek: Chapter schema - 1 chapter per skill level", "Waiting on Vivek. 15-30 min chapters, no sub-lessons."),
            ("Tie-breaking UI when skills score similarly", "Let user choose preference when 2 skills are tied."),
            ("Reprioritize after 3 chapters completed", "Rerun prioritization with updated skill levels."),
            ("Generate next 5 skills when all at target", "Include learned skills in current state, rerun."),
            ("End of April POC - 3 examples ready for demo", "Jennifer + 2 others for Luda/Vivek/Ram to evaluate."),
        ]

        for title, note in todo:
            r = await client.post(
                f'{BASE}/buckets/{PROJECT}/todolists/{nl_id}/todos.json',
                headers=headers,
                json={'content': title, 'description': f'<div>{note}</div>', 'assignee_ids': [ALI_ID]}
            )
            tid = r.json()['id']
            print(f'  [OPEN] {title[:55]}')
            print(f'    https://3.basecamp.com/3945211/buckets/{PROJECT}/todos/{tid}')

        # Post message board update
        mb_id = next(d['id'] for d in project['dock'] if d['name'] == 'message_board')
        msg_body = "<div><h2>April 22 Status Update</h2>"
        msg_body += "<h3>Completed Since Last Update</h3><ul>"
        msg_body += "<li>All page-by-page flow changes from Luda's Apr 15 feedback</li>"
        msg_body += "<li>Skills matching logic: user level = target removes skill, backfills</li>"
        msg_body += "<li>Merged skill selection + self-assessment into one page</li>"
        msg_body += "<li>5-factor rubric scoring (5/5 Claude match, 20/20 consistency)</li>"
        msg_body += "<li>Dynamic lessons: no code for non-tech (50 profiles verified)</li>"
        msg_body += "<li>Homepage simplified, Detected Role renamed to Targeted Role</li>"
        msg_body += "<li>Knowledge checks, reflections, data inline fixes deployed</li>"
        msg_body += "</ul>"
        msg_body += "<h3>Waiting On</h3><ul>"
        msg_body += "<li>Vivek: Ontology proficiency definitions + chapter schema</li>"
        msg_body += "</ul>"
        msg_body += "<h3>Next Steps</h3><ul>"
        msg_body += "<li>Integrate Vivek's ontology when ready</li>"
        msg_body += "<li>Tie-breaking UI for close-scoring skills</li>"
        msg_body += "<li>Reprioritization after 3 chapters</li>"
        msg_body += "<li>Prepare 3 examples for end-of-April POC</li>"
        msg_body += "</ul>"
        msg_body += "<p>Tool: http://95.216.199.47:3000</p></div>"

        r = await client.post(
            f'{BASE}/buckets/{PROJECT}/message_boards/{mb_id}/messages.json',
            headers=headers,
            json={'subject': 'April 22 - Status Update', 'content': msg_body}
        )
        if r.status_code in (200, 201):
            msg_data = r.json()
            print(f'\nMessage board: https://3.basecamp.com/3945211/buckets/{PROJECT}/messages/{msg_data["id"]}')
        else:
            print(f'\nMessage board: failed ({r.status_code})')


asyncio.run(main())
