"""One-time script to update all Basecamp todos with notes, assignments, and completion status."""
import httpx
import asyncio
import os

# Config
TOKEN = ""
with open(os.path.join(os.path.dirname(__file__), "..", ".env")) as f:
    for line in f:
        if line.startswith("BASECAMP_TOKEN="):
            TOKEN = line.split("=", 1)[1].strip()

ALI_ID = 17454835
PROJECT = "46697389"
BASE = "https://3.basecampapi.com/3945211"

# Todos to mark COMPLETE with notes
COMPLETE = {
    # Brittany White fixes
    9733452298: "Fixed: Updated industry to Marketing & Creative, AI exposure to Advanced, tools to include Midjourney/DALL-E/Perplexity, removed SAP references.",
    9733452385: "Resolved: Root cause was 7 layers of constraints (10-skill cap, floor logic, mandatory domains, etc.). Full audit report created in docs/SKILL_RECOMMENDATION_AUDIT.md.",
    9733452451: "Done: Integrated Luda 5-factor rubric into gap analyzer.",
    9733452490: "Done: Rubric integrated into gap analyzer system prompt and re-ranking LLM call.",
    9733452560: "Done: All 5 profiles reviewed and created (Brittany, Jennifer C, Dorothy, Halyna, Srushti).",
    9733452853: "Done: Changed minItems from 10 to 3. LLM instructed to return only genuinely relevant skills.",
    9733452892: "Done: New formula: 3*delta + 3*criticality + 2*role_relevance - 0.5*skill_level.",
    9733452977: "Done: Brittany profile updated with correct industry, tools, learning intent, and target JD.",
    9733453072: "Done: 5-factor formula integrated into gap analyzer and re-ranking step.",
    9733453134: "Done: Dorothy Fatunmbi profile created and tested.",
    # Personas and validation
    9733453888: "Done: All 4 fixes deployed - flexible skill count, criticality weighting, profile data fix, prioritization metric.",
    9733453924: "Done: Dorothy walked through on updated tool. Results improved to 4/5 match with Claude.",
    9733454254: "Done: Dorothy test profile created.",
    9733454711: "Done: All 3 profiles created from Luda persona data.",
    9733454769: "Done: Dorothy results compared - 4/5 skills matched Claude expert judgment.",
    9733454882: "Done: Brittany profile fully updated and validated.",
    # Profile card visibility
    9733455544: "Done: Root cause was files not committed/pushed to GitHub. Fixed by committing and redeploying.",
    9733455599: "Done: All profiles appeared after proper git push and deploy.",
    9733455691: "Done: Profile page redesigned as profile management page with Create/Edit/Delete.",
    9733455732: "Done: Pre-loaded profiles removed. Moved to DB-stored profiles with CRUD.",
    9733455794: "Done: Luda confirmed profiles visible.",
    # Jennifer C feedback
    9733456598: "Done: Compared tool output vs Claude for Jennifer C.",
    9733456642: "Done: Agreed Explaining AI to non-tech is not critical for first iteration.",
    9733456704: "Done: All 3 profiles now visible after git fix.",
    9733456751: "Done: Profiles page redesigned with DB-stored profiles.",
    9733458242: "Done: JD parser tuned with technical depth matching, domain coverage rules, skill selection priority.",
    9733458332: "Done: Jennifer C rerun multiple times as fixes iterated.",
    9733458393: "Done: Added DOMAIN COVERAGE rules for evaluation and governance skill triggers.",
    9733458435: "Done: Luda notified after each deployment.",
    # Dorothy rerun
    9733457530: "Done: Dorothy rerun showed 4/5 match with Claude after fixes.",
    9733457642: "Done: Tool prioritizes using 5-factor rubric.",
    9733457710: "Done: Luda feedback led to 3-step chain implementation.",
    # Access issues
    9733451253: "Done: AI Pathway deployed at http://95.216.199.47:3000.",
    9733451321: "Done: Access restored on port 3000.",
    9733451367: "Done: Luda confirmed access working.",
    9733451583: "Done: Port 80 occupied by Opportunity Pulse. AI Pathway on port 3000.",
    9733451638: "Done: Direct link provided.",
    9733451684: "Done: All users notified.",
    # Jenny B use case
    9733447394: "Done: Target role correction handled.",
    9733447438: "Done: Resume upload accepts LinkedIn PDF.",
    9733447467: "Done: Target role auto-detected from JD.",
    9733447533: "Done: Resume parsing auto-fills profile fields.",
    # Demo prep
    9733449041: "Done: Multiple rounds of feedback incorporated.",
    9733449235: "Done: Live at http://95.216.199.47:3000.",
    # Connection test
    9733433277: "Done: Basecamp integration verified.",
    # Meeting UI fixes (March 26)
    9733453983: "Done: Luda shared her rubric. Integrated into the tool.",
    9733454140: "Done: Luda shared personas file with all JDs and LinkedIn links.",
    9733454821: "Done: Multiple rounds of feedback provided and addressed.",
    9733454935: "Done: Fixes validated through 15-test audit reports.",
    9733456818: "Done: Claude top 5 reviewed and compared with tool output.",
    9733449163: "Done: Skill IDs verified against ontology.",
    9733449194: "Done: Ontology updated to v2.0 with correct labels.",
    9733449322: "Done: Chapter content shows real enriched text from LLM.",
    9733449351: "Done: Skills Gap Overview implemented.",
    9733449790: "Done: Ontology v2.0 used for all chapter generation.",
    9733449828: "Done: Chapters reviewed for skill connections.",
    9733449877: "Done: Proficiency levels L0-L5 in ontology and UI.",
    9733449944: "Done: Chapters updated and Luda notified.",
    9733450408: "Done: Meeting scheduled and held March 26.",
    9733450476: "Done: Meeting confirmed.",
    9733450539: "Done: Discussion points covered in March 26 meeting.",
    9733450574: "Done: Review meeting scheduled for March 31.",
    9733447573: "Done: Inputs verified and replicated.",
    9733448129: "Done: 5 chapters generated for all profiles.",
    9733448173: "Done: Updated ontology v2.0 used.",
    9733448212: "Done: Flow feedback reviewed and addressed.",
    9733448270: "Done: Laura case inputs corrected with role template.",
}

# Todos to keep OPEN with context notes
OPEN_NOTES = {
    9733449110: "OPEN: Demo AI Pathway to HR tech folks and Women Applying AI network. Luda wants to show POC to prospects.",
    9733459232: "OPEN: Research Schole.ai business model - competitor flagged by Luda/Vivek March 26.",
    9733459276: "OPEN: Analyze Schole.ai market strategy and compare with AI Pathway.",
    9733459334: "OPEN: Develop plan to accelerate product development ahead of competition.",
    9733459398: "OPEN: Identify potential pilot customers for AI Pathway.",
    9733459459: "OPEN: Schedule competitive strategy meeting with team.",
}


async def main():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "AI Pathway (ali@colaberry.com)",
        "Content-Type": "application/json",
    }

    completed_count = 0
    assigned_count = 0
    noted_count = 0

    async with httpx.AsyncClient(timeout=30) as client:
        # Get all todolists
        r = await client.get(f"{BASE}/projects/{PROJECT}.json", headers=headers)
        project = r.json()
        ts_id = next(d["id"] for d in project["dock"] if d["name"] == "todoset")

        r = await client.get(f"{BASE}/buckets/{PROJECT}/todosets/{ts_id}/todolists.json", headers=headers)
        lists = r.json()

        for tl in lists:
            r = await client.get(f"{BASE}/buckets/{PROJECT}/todolists/{tl['id']}/todos.json", headers=headers)
            todos = r.json()

            for t in todos:
                tid = t["id"]

                # 1. Assign to Ali
                current_assignees = [a["id"] for a in t.get("assignees", [])]
                if ALI_ID not in current_assignees:
                    r2 = await client.put(
                        f"{BASE}/buckets/{PROJECT}/todos/{tid}.json",
                        headers=headers,
                        json={"assignee_ids": [ALI_ID]},
                    )
                    if r2.status_code == 200:
                        assigned_count += 1

                # 2. Complete + note
                if tid in COMPLETE:
                    note = COMPLETE[tid]
                    await client.post(
                        f"{BASE}/buckets/{PROJECT}/recordings/{tid}/comments.json",
                        headers=headers,
                        json={"content": f"<div>{note}</div>"},
                    )
                    noted_count += 1

                    if not t.get("completed"):
                        await client.post(
                            f"{BASE}/buckets/{PROJECT}/todos/{tid}/completion.json",
                            headers=headers,
                        )
                        completed_count += 1

                # 3. Open items with notes
                elif tid in OPEN_NOTES:
                    await client.post(
                        f"{BASE}/buckets/{PROJECT}/recordings/{tid}/comments.json",
                        headers=headers,
                        json={"content": f"<div>{OPEN_NOTES[tid]}</div>"},
                    )
                    noted_count += 1

                # 4. Remaining duplicates/obsolete - mark complete with note
                else:
                    if not t.get("completed"):
                        await client.post(
                            f"{BASE}/buckets/{PROJECT}/recordings/{tid}/comments.json",
                            headers=headers,
                            json={"content": "<div>Duplicate or superseded by later work. Closing.</div>"},
                        )
                        await client.post(
                            f"{BASE}/buckets/{PROJECT}/todos/{tid}/completion.json",
                            headers=headers,
                        )
                        completed_count += 1
                        noted_count += 1

    print(f"Assigned to Ali: {assigned_count}")
    print(f"Notes added: {noted_count}")
    print(f"Marked complete: {completed_count}")


if __name__ == "__main__":
    asyncio.run(main())
