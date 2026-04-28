"""End-to-end test of skills matching logic.
Tests: when user's self-assessment matches target level, those skills should be removed from the path.
"""
import httpx
import asyncio

BASE = "http://95.216.199.47:3000/api"

JD = ("AI Content Editor - Evaluate and edit AI-generated content for accuracy, "
      "tone, and clarity. Collaborate with developers to refine content generation "
      "algorithms. Ensure content aligns with brand voice. Use data analysis to "
      "identify content performance trends. Develop AI content disclosure guidelines. "
      "Review AI outputs for bias and factual accuracy. Create style guides for "
      "AI-generated content. Implement quality evaluation frameworks. IP and "
      "copyright considerations. Cross-functional collaboration.")


async def test():
    print("=" * 80)
    print("SKILLS MATCHING LOGIC TEST")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=180) as client:
        # Create profile
        print("\n1. Creating Jennifer C profile...")
        r = await client.post(f"{BASE}/profiles/", json={
            "name": "Jennifer Skills Match Test",
            "current_role": "Content Editor",
            "industry": "Corporate Communications",
            "experience_years": 9,
            "ai_exposure_level": "Basic",
            "technical_background": "No coding experience",
            "learning_intent": "Content creation",
            "target_jd_text": JD,
            "tools_used": ["ChatGPT / Claude / Gemini"],
            "current_profile": {
                "summary": "Strategic communications professional with 9+ years.",
                "technical_skills": ["Executive Communications", "Keyword Research"],
                "soft_skills": ["Mentoring", "Training", "Leadership"],
            },
        })
        pid = r.json()["id"]
        print(f"   Created: {pid}")

        # Test 1: Run WITHOUT self-assessment (baseline)
        print("\n2. Running baseline analysis (no self-assessment)...")
        r = await client.post(f"{BASE}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": JD,
            "target_role": "AI Content Editor",
            "skip_assessment": True,
        })
        if r.status_code != 200:
            print(f"   FAIL: {r.status_code} {r.text[:200]}")
            await client.delete(f"{BASE}/profiles/{pid}")
            return

        baseline = r.json().get("result", {})
        baseline_chapters = baseline.get("learning_path", {}).get("chapters", [])
        print(f"   Baseline chapters ({len(baseline_chapters)}):")
        baseline_skills = {}
        for ch in baseline_chapters:
            sid = ch.get("primary_skill_id", ch.get("skill_id", ""))
            name = ch.get("primary_skill_name", ch.get("skill_name", ""))
            target = ch.get("target_level", 2)
            baseline_skills[sid] = {"name": name, "target": target}
            print(f"     {sid} - {name} (target: L{target})")

        # Test 2: Run WITH self-assessment where 2 skills match target
        print("\n3. Running with self-assessment (2 skills at target)...")
        # Pick 2 skills from baseline to mark as "at target"
        sids = list(baseline_skills.keys())
        if len(sids) < 3:
            print("   Not enough skills to test. Aborting.")
            await client.delete(f"{BASE}/profiles/{pid}")
            return

        at_target_1 = sids[-1]  # Last skill
        at_target_2 = sids[-2]  # Second to last
        below_target = sids[:3]  # First 3 skills

        self_assessed = {}
        for sid in below_target:
            self_assessed[sid] = 0  # Way below target
        self_assessed[at_target_1] = baseline_skills[at_target_1]["target"]  # Matches target
        self_assessed[at_target_2] = baseline_skills[at_target_2]["target"]  # Matches target

        print(f"   Skills AT target (should be removed):")
        print(f"     {at_target_1} - {baseline_skills[at_target_1]['name']} (self-assessed: L{self_assessed[at_target_1]})")
        print(f"     {at_target_2} - {baseline_skills[at_target_2]['name']} (self-assessed: L{self_assessed[at_target_2]})")
        print(f"   Skills BELOW target (should remain):")
        for sid in below_target:
            print(f"     {sid} - {baseline_skills[sid]['name']} (self-assessed: L{self_assessed[sid]})")

        r = await client.post(f"{BASE}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": JD,
            "target_role": "AI Content Editor",
            "skip_assessment": True,
            "self_assessed_skills": self_assessed,
        })

        if r.status_code != 200:
            print(f"   FAIL: {r.status_code} {r.text[:200]}")
            await client.delete(f"{BASE}/profiles/{pid}")
            return

        result2 = r.json().get("result", {})
        chapters2 = result2.get("learning_path", {}).get("chapters", [])
        print(f"\n   New chapters ({len(chapters2)}):")
        new_sids = set()
        for ch in chapters2:
            sid = ch.get("primary_skill_id", ch.get("skill_id", ""))
            name = ch.get("primary_skill_name", ch.get("skill_name", ""))
            target = ch.get("target_level", "?")
            current = ch.get("current_level", "?")
            new_sids.add(sid)
            print(f"     {sid} - {name} (current: L{current}, target: L{target})")

        # Validate
        print(f"\n{'='*80}")
        print("VALIDATION RESULTS")
        print(f"{'='*80}")

        at1_removed = at_target_1 not in new_sids
        at2_removed = at_target_2 not in new_sids
        below_kept = all(sid in new_sids for sid in below_target)

        print(f"\n  {at_target_1} ({baseline_skills[at_target_1]['name']}):")
        print(f"    Self-assessed: L{self_assessed[at_target_1]} (= target L{baseline_skills[at_target_1]['target']})")
        print(f"    In new path: {'YES (SHOULD BE REMOVED)' if not at1_removed else 'NO (CORRECT - removed)'}")

        print(f"\n  {at_target_2} ({baseline_skills[at_target_2]['name']}):")
        print(f"    Self-assessed: L{self_assessed[at_target_2]} (= target L{baseline_skills[at_target_2]['target']})")
        print(f"    In new path: {'YES (SHOULD BE REMOVED)' if not at2_removed else 'NO (CORRECT - removed)'}")

        for sid in below_target:
            in_path = sid in new_sids
            print(f"\n  {sid} ({baseline_skills[sid]['name']}):")
            print(f"    Self-assessed: L{self_assessed[sid]} (target: L{baseline_skills[sid]['target']})")
            print(f"    In new path: {'YES (CORRECT)' if in_path else 'NO (SHOULD BE IN PATH)'}")

        print(f"\n  Baseline chapters: {len(baseline_chapters)}")
        print(f"  New chapters: {len(chapters2)}")
        print(f"  Reduction: {len(baseline_chapters) - len(chapters2)} chapters removed")

        all_pass = at1_removed and at2_removed and below_kept
        print(f"\n  OVERALL: {'PASS - Skills at target correctly removed' if all_pass else 'NEEDS WORK'}")

        if not all_pass:
            print("\n  NOTE: The gap engine removes skills where delta <= 0.")
            print("  If self-assessed level >= target, delta = 0 and the skill is excluded.")
            print("  But the scaffold may still have those skills if they were added before")
            print("  the self-assessment was applied.")

        # Cleanup
        await client.delete(f"{BASE}/profiles/{pid}")
        print(f"\n  Cleaned up.")

asyncio.run(test())
