"""Run just the 5 non-technical profiles with pauses between each to avoid OOM."""
import httpx
import asyncio
import json
import subprocess
from datetime import datetime
import sys
sys.path.insert(0, '.')
from scripts.curriculum_quality_test import PROFILES, generate_all_lessons

BASE = "http://95.216.199.47:3000/api"

# Just the non-technical profiles (indices 5-9)
NONTECH = PROFILES[5:]


async def run_one(client, profile, index):
    result = {
        "name": profile["name"],
        "role": profile["current_role"],
        "industry": profile["industry"],
        "technical": False,
        "experience_years": profile["experience_years"],
        "target_jd": profile["jd"].split(" - ")[0],
    }
    try:
        r = await client.post(f"{BASE}/profiles/", json={
            "name": profile["name"],
            "current_role": profile["current_role"],
            "industry": profile["industry"],
            "experience_years": profile["experience_years"],
            "ai_exposure_level": profile["ai_exposure_level"],
            "technical_background": profile["technical_background"],
            "learning_intent": f"Transition to AI role in {profile['industry']}",
            "target_jd_text": profile["jd"],
            "tools_used": profile["tools_used"],
            "current_profile": {
                "summary": profile["summary"],
                "technical_skills": profile["technical_skills"],
                "soft_skills": profile["soft_skills"],
            },
        })
        pid = r.json()["id"]

        print(f"  Analyzing...", end=" ", flush=True)
        r = await client.post(f"{BASE}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": profile["jd"],
            "target_role": profile["jd"].split(" - ")[0].strip(),
            "skip_assessment": True,
        }, timeout=180)
        if r.status_code != 200:
            result["status"] = f"analysis_fail:{r.status_code}"
            await client.delete(f"{BASE}/profiles/{pid}")
            return result

        analysis = r.json()
        path_id = analysis.get("learning_path_id")
        chapters = analysis.get("result", {}).get("learning_path", {}).get("chapters", [])
        result["chapters"] = [
            {"skill_id": ch.get("primary_skill_id", ch.get("skill_id", "")),
             "skill_name": ch.get("primary_skill_name", ch.get("skill_name", ""))}
            for ch in chapters
        ]
        print(f"{len(chapters)} chapters.", end=" ", flush=True)

        r = await client.post(f"{BASE}/learning/{path_id}/activate")
        if r.status_code != 200:
            result["status"] = f"activate_fail:{r.status_code}"
            await client.delete(f"{BASE}/profiles/{pid}")
            return result

        act = r.json()
        modules = act.get("modules", [])
        result["total_lessons"] = act.get("total_lessons", 0)
        print(f"{result['total_lessons']} lessons. Generating...", end=" ", flush=True)

        result["modules"] = await generate_all_lessons(client, path_id, modules)
        result["status"] = "success"
        print("Done!")

        await client.delete(f"{BASE}/profiles/{pid}")
    except Exception as e:
        result["status"] = f"error:{str(e)[:80]}"
        print(f"ERROR: {str(e)[:80]}")
    return result


async def main():
    results = []
    for i, profile in enumerate(NONTECH):
        print(f"\n[{i+1}/5] {profile['name']} ({profile['current_role']}, {profile['industry']})")

        async with httpx.AsyncClient(timeout=180) as client:
            result = await run_one(client, profile, i)
            results.append(result)

        if result["status"] != "success":
            print("  Restarting backend...")
            subprocess.run(["ssh", "root@95.216.199.47",
                           "cd /opt/ai-pathway && docker compose restart backend"],
                          capture_output=True)
            await asyncio.sleep(15)
        else:
            # Brief pause between profiles
            await asyncio.sleep(5)

    # Merge with existing tech results
    with open('../docs/curriculum_quality_20260408_1424.json') as f:
        existing = json.load(f)
    tech_results = [r for r in existing if r["status"] == "success"]

    all_results = tech_results + results
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"../docs/curriculum_quality_full_{ts}.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Print summary
    success = [r for r in results if r["status"] == "success"]
    print(f"\n\nNon-technical results: {len(success)}/5 successful")
    for r in success:
        total = sum(1 for m in r.get("modules", []) for l in m["lessons"] if "concept_snapshot" in l)
        impl = sum(1 for m in r.get("modules", []) for l in m["lessons"] if l.get("impl_title"))
        code = sum(1 for m in r.get("modules", []) for l in m["lessons"] if l.get("has_code"))
        print(f"  {r['name']}: {total} lessons, {impl} tasks, code={code} {'(ISSUE!)' if code > 0 else '(correct)'}")

    print(f"\nFull results saved to ../docs/curriculum_quality_full_{ts}.json")


asyncio.run(main())
