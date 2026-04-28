"""Comprehensive E2E test: fresh profile matching Jennifer C's data, compare with Claude reference."""
import httpx
import asyncio

BASE = "http://95.216.199.47:3000/api"

# Jennifer C's JD (from Luda's personas file)
JD_TEXT = """AI Content Editor
Join our team as an AI Content Editor and help us create engaging and informative content using the latest AI technologies. Your expertise in natural language processing, machine learning, and content strategy will be invaluable in shaping our content creation process.

Key Responsibilities:
- Evaluate and edit AI-generated content for accuracy, tone, and clarity
- Collaborate with developers to refine content generation algorithms
- Ensure content aligns with brand voice and messaging standards
- Use data analysis to identify content performance trends
- Develop AI content disclosure guidelines and best practices
- Manage editorial workflows incorporating AI tools
- Review AI outputs for bias and factual accuracy
- Create and maintain style guides for AI-generated content
- Implement quality evaluation frameworks for AI content
- Knowledge of IP and copyright considerations for AI-generated material
- Facilitate cross-functional collaboration between content, legal, and tech teams
- Stay current with AI content generation trends and tools

Requirements:
- 3+ years of experience in content editing or content strategy
- Strong understanding of AI and machine learning concepts
- Experience with natural language processing tools
- Excellent written and verbal communication skills
- Ability to work in a fast-paced, dynamic environment
- Experience with content management systems
- Knowledge of SEO best practices
- Familiarity with AI ethics and responsible AI practices"""

# Claude's expected results (from Luda's document)
CLAUDE_TOP10 = [
    "SK.PRM.003", "SK.CTIC.006", "SK.FND.002", "SK.CTIC.004", "SK.GOV.022",
    "SK.FND.021", "SK.PRM.020", "SK.PRM.021", "SK.EVL.001",
]
CLAUDE_TOP5 = [
    "SK.PRM.003", "SK.FND.002", "SK.PRM.020", "SK.GOV.022", "SK.EVL.001",
]


async def full_test():
    async with httpx.AsyncClient(timeout=180) as client:
        print("=" * 70)
        print("FULL E2E TEST: Fresh Profile (Jennifer C data)")
        print("=" * 70)

        # 1. Create fresh profile matching Jennifer C
        print("\n1. Creating fresh profile...")
        r = await client.post(f"{BASE}/profiles/", json={
            "name": "Jennifer C Test",
            "current_role": "Content Editor",
            "industry": "Corporate Communications",
            "experience_years": 9,
            "ai_exposure_level": "Basic",
            "technical_background": "No coding experience",
            "learning_intent": "Content creation and writing generative reports, emails, articles or marketing content faster",
            "target_jd_text": JD_TEXT,
            "tools_used": ["ChatGPT / Claude / Gemini"],
        })
        profile = r.json()
        pid = profile["id"]
        print(f"  Created: {pid}")

        # 2. Run analysis
        print("\n2. Running analysis...")
        r = await client.post(f"{BASE}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": JD_TEXT,
            "target_role": "AI Content Editor",
            "skip_assessment": True,
        })
        if r.status_code != 200:
            print(f"  FAIL: {r.status_code} {r.text[:300]}")
            await client.delete(f"{BASE}/profiles/{pid}")
            return

        result = r.json()
        our = result.get("result", {})
        our_top = our.get("top_10_target_skills", [])
        our_ids = [s.get("skill_id", "") for s in our_top]
        path_id = result.get("learning_path_id")

        # 3. Top 10 comparison
        print(f"\n{'=' * 70}")
        print(f"TOP 10 EXTRACTION (returned {len(our_ids)} skills)")
        print(f"{'=' * 70}")
        for i, s in enumerate(our_top):
            in_claude = "MATCH" if s.get("skill_id") in CLAUDE_TOP10 else "extra"
            print(f"  {i+1:>2}. {s.get('skill_id'):<16} {s.get('skill_name', ''):<45} [{in_claude}]")

        claude_set = set(CLAUDE_TOP10)
        our_set = set(our_ids)
        overlap10 = claude_set & our_set
        missing = claude_set - our_set
        extra = our_set - claude_set
        print(f"\n  Overlap: {len(overlap10)}/{len(claude_set)}")
        if missing:
            print(f"  Missing from Claude's list: {missing}")
        if extra:
            print(f"  Extra (not in Claude): {extra}")

        # 4. Top 5 comparison
        print(f"\n{'=' * 70}")
        print("TOP 5 PRIORITIZED (rubric re-ranking)")
        print(f"{'=' * 70}")
        our5 = our_ids[:5]
        for i in range(5):
            c = CLAUDE_TOP5[i] if i < len(CLAUDE_TOP5) else "-"
            o = our5[i] if i < len(our5) else "-"
            m = "EXACT" if o == c else ("IN TOP5" if o in CLAUDE_TOP5 else "MISS")
            name = our_top[i].get("skill_name", "?") if i < len(our_top) else "?"
            print(f"  {i+1}. Claude: {c:<16} Ours: {o:<16} {m}  ({name})")

        overlap5 = set(CLAUDE_TOP5) & set(our5)
        print(f"\n  Top 5 overlap: {len(overlap5)}/5")

        # 4b. ACTUAL CHAPTERS comparison (what user sees in learning path)
        chapters = our.get("learning_path", {}).get("chapters", [])
        chapter_ids = [ch.get("primary_skill_id", ch.get("skill_id", "")) for ch in chapters]
        print(f"\n{'=' * 70}")
        print(f"ACTUAL LEARNING PATH CHAPTERS ({len(chapters)})")
        print(f"{'=' * 70}")
        for ch in chapters:
            sid = ch.get("primary_skill_id", ch.get("skill_id", ""))
            name = ch.get("primary_skill_name", ch.get("skill_name", ""))
            in_claude = "MATCH" if sid in CLAUDE_TOP5 else "extra"
            print(f"  Ch{ch.get('chapter_number','?')}: {sid:<16} {name:<40} [{in_claude}]")

        chapter_set = set(chapter_ids)
        claude5_set = set(CLAUDE_TOP5)
        chapter_overlap = claude5_set & chapter_set
        print(f"\n  Chapter overlap with Claude top 5: {len(chapter_overlap)}/5")
        if claude5_set - chapter_set:
            print(f"  Missing: {claude5_set - chapter_set}")

        # 5. Activate and test lesson (FRESH - no cached content)
        print(f"\n{'=' * 70}")
        print("LESSON GENERATION (non-technical, fresh)")
        print(f"{'=' * 70}")
        r = await client.post(f"{BASE}/learning/{path_id}/activate")
        if r.status_code != 200:
            print(f"  Activate FAIL: {r.status_code}")
            await client.delete(f"{BASE}/profiles/{pid}")
            return

        act = r.json()
        modules = act.get("modules", [])
        print(f"  Modules: {len(modules)}, Lessons: {act.get('total_lessons')}")

        lesson_id = modules[0].get("lesson_outline", [{}])[0].get("id") if modules else None
        content = {}
        if lesson_id:
            r = await client.post(f"{BASE}/learning/{path_id}/lessons/{lesson_id}/start")
            if r.status_code == 200:
                content = r.json().get("content", {})
                has_code = bool(content.get("code_examples"))
                print(f"  concept_snapshot: {'OK' if content.get('concept_snapshot') else 'MISSING'}")
                print(f"  code_examples: {'FAIL (present for non-technical!)' if has_code else 'OK (absent)'}")
                print(f"  knowledge_checks: {len(content.get('knowledge_checks', []))}")
                print(f"  reflection_questions: {len(content.get('reflection_questions', []))}")
                print(f"  implementation_task: {'OK' if content.get('implementation_task') else 'MISSING'}")
            else:
                print(f"  Lesson FAIL: {r.status_code} {r.text[:200]}")

        # 6. Cleanup
        print(f"\n6. Cleanup...")
        await client.delete(f"{BASE}/profiles/{pid}")
        print("  Done")

        # Summary
        print(f"\n{'=' * 70}")
        print("FINAL REPORT")
        print(f"{'=' * 70}")
        results = {
            "Skills returned (want 10)": f"{len(our_ids)}",
            "Top 10 overlap with Claude": f"{len(overlap10)}/{len(claude_set)}",
            "JD parser top 5 vs Claude": f"{len(overlap5)}/5",
            "CHAPTERS vs Claude top 5": f"{len(chapter_overlap)}/5",
            "No code for non-technical": "PASS" if not content.get("code_examples") else "FAIL",
            "Learning path generated": "PASS" if modules else "FAIL",
            "Knowledge checks": "PASS" if content.get("knowledge_checks") else "FAIL",
        }
        all_pass = True
        for test, val in results.items():
            is_pass = "PASS" in val or ("/" in val and val.split("/")[0] == val.split("/")[1])
            is_warn = "/" in val and int(val.split("/")[0]) >= int(val.split("/")[1]) * 0.6
            status = "PASS" if is_pass else ("WARN" if is_warn else "FAIL")
            if status == "FAIL":
                all_pass = False
            print(f"  [{status:>4}] {test}: {val}")

        print(f"\n  Overall: {'ALL PASS' if all_pass else 'ISSUES FOUND'}")


asyncio.run(full_test())
