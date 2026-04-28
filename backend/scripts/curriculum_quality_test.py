"""Curriculum Quality Assessment: Deep analysis of lesson content, implementation tasks,
knowledge checks, and learning outcomes across 10 profiles (5 tech, 5 non-tech).

Generates ALL lessons (not just first per module) and scores on multiple quality factors.
"""
import httpx
import asyncio
import json
from datetime import datetime

BASE = "http://95.216.199.47:3000/api"

# 5 Technical + 5 Non-Technical with diverse industries
PROFILES = [
    # Technical
    {"name": "Marcus Chen", "current_role": "Senior Software Engineer", "industry": "FinTech",
     "experience_years": 8, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate",
     "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"],
     "summary": "Full-stack engineer with 8 years building trading platforms. Python, Java, React, AWS.",
     "technical_skills": ["Python", "Java", "React", "AWS", "PostgreSQL", "Docker"],
     "soft_skills": ["Team leadership", "Code review"],
     "jd": "AI Solutions Architect - Lead the design of enterprise AI solutions integrating LLMs and agentic systems. Translate business requirements into technical architectures. Evaluate and select AI platforms. Build proof-of-concepts. Required: System design, cloud architecture, API development, LLM integration, prompt engineering."},

    {"name": "Priya Sharma", "current_role": "Data Scientist", "industry": "Healthcare",
     "experience_years": 5, "technical_background": "Professional developer", "ai_exposure_level": "Advanced",
     "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot", "OpenAI API / Anthropic API"],
     "summary": "Data scientist specializing in clinical analytics. Built ML models for patient outcome prediction.",
     "technical_skills": ["Python", "R", "TensorFlow", "SQL", "Tableau", "Statistical modeling"],
     "soft_skills": ["Research presentation", "Cross-functional collaboration"],
     "jd": "AI/ML Engineer - Design and implement machine learning pipelines for production healthcare systems. Build and optimize model training infrastructure. Deploy models using containerized microservices. Monitor model performance. Required: Python, PyTorch/TensorFlow, Docker, Kubernetes, AWS/GCP. 3+ years ML engineering."},

    {"name": "Elena Volkov", "current_role": "Data Engineer", "industry": "Retail",
     "experience_years": 6, "technical_background": "Professional developer", "ai_exposure_level": "Basic",
     "tools_used": ["ChatGPT / Claude / Gemini"],
     "summary": "Data engineer building ETL pipelines and data warehouses for retail analytics. Spark, Airflow, Snowflake.",
     "technical_skills": ["Apache Spark", "Airflow", "Snowflake", "Python", "SQL", "dbt", "Kafka"],
     "soft_skills": ["Data governance", "Stakeholder management"],
     "jd": "AI Data Engineer - Build data pipelines feeding AI/ML models. Design real-time streaming architectures. Implement data quality monitoring. Optimize storage for vector embeddings. Required: Spark, Kafka, Python, SQL, vector databases."},

    {"name": "Aisha Patel", "current_role": "Security Engineer", "industry": "Banking",
     "experience_years": 7, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate",
     "tools_used": ["ChatGPT / Claude / Gemini", "OpenAI API / Anthropic API"],
     "summary": "Application security engineer for major bank. Penetration testing, SAST/DAST, compliance frameworks.",
     "technical_skills": ["Penetration testing", "OWASP", "Python", "Burp Suite", "AWS Security", "PCI DSS"],
     "soft_skills": ["Risk assessment", "Security training"],
     "jd": "AI Security Engineer - Develop security frameworks for AI systems. Implement prompt injection defenses, model access controls, and data privacy measures. Audit AI systems for vulnerabilities. Required: Security engineering, Python, LLM security, threat modeling."},

    {"name": "Tom Williams", "current_role": "Full Stack Developer", "industry": "EdTech",
     "experience_years": 5, "technical_background": "Professional developer", "ai_exposure_level": "Intermediate",
     "tools_used": ["ChatGPT / Claude / Gemini", "GitHub Copilot"],
     "summary": "Full stack developer building learning platforms. React, Node.js, MongoDB. Experience with LMS integrations.",
     "technical_skills": ["React", "Node.js", "MongoDB", "TypeScript", "AWS", "GraphQL"],
     "soft_skills": ["UX thinking", "Agile"],
     "jd": "Full Stack AI Developer - Build end-to-end AI-powered learning applications. Frontend with AI features, backend API integration, LLM orchestration. Required: React, Python/FastAPI, LLM APIs, prompt engineering, database design."},

    # Non-Technical
    {"name": "Jennifer Campbell", "current_role": "Content Editor", "industry": "Corporate Communications",
     "experience_years": 9, "technical_background": "No coding experience", "ai_exposure_level": "Basic",
     "tools_used": ["ChatGPT / Claude / Gemini"],
     "summary": "Strategic communications professional with 9+ years. Translates complex technical concepts into accessible content.",
     "technical_skills": ["Executive Communications", "Content Strategy", "Keyword Research"],
     "soft_skills": ["Mentoring", "Training", "Leadership"],
     "jd": "AI Content Editor - Evaluate and edit AI-generated content for accuracy, tone, and clarity. Collaborate with developers to refine content generation algorithms. Develop AI content disclosure guidelines. Review AI outputs for bias and factual accuracy. Implement quality evaluation frameworks."},

    {"name": "Karen Thompson", "current_role": "Nurse Manager", "industry": "Healthcare",
     "experience_years": 14, "technical_background": "No coding experience", "ai_exposure_level": "Basic",
     "tools_used": ["ChatGPT / Claude / Gemini"],
     "summary": "Nurse manager overseeing ICU unit with 30 nurses. Clinical protocols, patient safety, staff scheduling.",
     "technical_skills": ["Clinical Protocols", "EHR Systems", "Staff Scheduling", "Patient Safety"],
     "soft_skills": ["Clinical leadership", "Crisis management", "Patient advocacy"],
     "jd": "Healthcare AI Coordinator - Coordinate AI implementation in clinical settings. Liaise between medical staff and IT. Ensure AI tools meet clinical workflow needs. Evaluate AI-assisted diagnosis tools. Train clinical staff on AI systems."},

    {"name": "Daniel Lee", "current_role": "Sales Director", "industry": "B2B Software",
     "experience_years": 11, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate",
     "tools_used": ["ChatGPT / Claude / Gemini"],
     "summary": "Sales director managing $20M pipeline. Enterprise sales, solution selling, team of 8 account executives.",
     "technical_skills": ["Salesforce CRM", "Sales Forecasting", "Pipeline Management"],
     "soft_skills": ["Negotiation", "Relationship building", "Team coaching"],
     "jd": "AI Sales Enablement Manager - Train sales teams on AI product capabilities. Create demo scripts, competitive positioning, objection handling for AI products. Measure AI tool adoption. Required: Sales training, product knowledge."},

    {"name": "Laura Nguyen", "current_role": "Compliance Officer", "industry": "Financial Services",
     "experience_years": 10, "technical_background": "No coding experience", "ai_exposure_level": "Basic",
     "tools_used": ["ChatGPT / Claude / Gemini"],
     "summary": "Compliance officer managing regulatory requirements for investment firm. SEC, FINRA, AML/KYC compliance.",
     "technical_skills": ["Regulatory Compliance", "AML/KYC", "Risk Assessment", "Audit Management"],
     "soft_skills": ["Policy writing", "Regulatory liaison", "Training delivery"],
     "jd": "AI Governance Analyst - Monitor AI systems for compliance with regulations and internal policies. Document model decisions, maintain audit trails, report to leadership. Develop AI usage policies. Required: Governance/audit experience."},

    {"name": "Michelle Kim", "current_role": "L&D Manager", "industry": "Consulting",
     "experience_years": 9, "technical_background": "No coding experience", "ai_exposure_level": "Intermediate",
     "tools_used": ["ChatGPT / Claude / Gemini", "Midjourney / DALL-E"],
     "summary": "Learning & Development manager designing training programs for Big 4 consulting firm. Instructional design, facilitation.",
     "technical_skills": ["Instructional Design", "LMS Administration", "Articulate Storyline", "Needs Assessment"],
     "soft_skills": ["Facilitation", "Curriculum design", "Executive coaching"],
     "jd": "AI Training Specialist - Design and deliver AI literacy training programs. Create workshops for non-technical employees. Develop training materials explaining AI concepts. Evaluate training effectiveness. Required: L&D experience, instructional design."},
]


async def generate_all_lessons(client, path_id, modules):
    """Generate ALL lessons for every module, not just the first."""
    all_lesson_data = []
    for mod in modules:
        mod_lessons = []
        for lesson_info in mod.get("lesson_outline", []):
            lid = lesson_info.get("id")
            lesson_data = {
                "module": mod.get("chapter_number"),
                "module_skill": mod.get("skill_name"),
                "lesson_number": lesson_info.get("lesson_number"),
                "title": lesson_info.get("title"),
                "type": lesson_info.get("type"),
            }
            if lid:
                try:
                    r = await client.post(
                        f"{BASE}/learning/{path_id}/lessons/{lid}/start",
                        timeout=120,
                    )
                    if r.status_code == 200:
                        content = r.json().get("content", {})
                        lesson_data["concept_snapshot"] = content.get("concept_snapshot", "")
                        lesson_data["has_code"] = bool(content.get("code_examples"))

                        # Implementation task details
                        impl = content.get("implementation_task") or {}
                        if isinstance(impl, dict):
                            lesson_data["impl_title"] = impl.get("title", "")
                            lesson_data["impl_description"] = impl.get("description", "")
                            reqs = impl.get("requirements", [])
                            lesson_data["impl_requirements"] = reqs if isinstance(reqs, list) else []
                            lesson_data["impl_deliverable"] = impl.get("deliverable", "")
                            lesson_data["impl_tools"] = [
                                t.get("name", "") for t in (impl.get("tools", []) or [])
                                if isinstance(t, dict)
                            ]
                            lesson_data["impl_minutes"] = impl.get("estimated_minutes", 0)

                        # Knowledge checks
                        kcs = content.get("knowledge_checks", [])
                        lesson_data["knowledge_checks"] = [
                            {"question": kc.get("question", ""), "options": kc.get("options", [])}
                            for kc in (kcs if isinstance(kcs, list) else [])
                        ]

                        # Reflection questions
                        refs = content.get("reflection_questions", [])
                        lesson_data["reflection_questions"] = [
                            rq.get("question", "") if isinstance(rq, dict) else str(rq)
                            for rq in (refs if isinstance(refs, list) else [])
                        ]
                    else:
                        lesson_data["error"] = f"status:{r.status_code}"
                except Exception as e:
                    lesson_data["error"] = str(e)[:80]
            mod_lessons.append(lesson_data)
        all_lesson_data.append({
            "module_number": mod.get("chapter_number"),
            "skill_id": mod.get("skill_id"),
            "skill_name": mod.get("skill_name"),
            "lessons": mod_lessons,
        })
    return all_lesson_data


async def run_profile(client, profile, index):
    """Run full pipeline for one profile and return detailed results."""
    print(f"\n[{index+1}/10] {profile['name']} ({profile['current_role']}, {profile['industry']})")
    result = {
        "name": profile["name"],
        "role": profile["current_role"],
        "industry": profile["industry"],
        "technical": profile["technical_background"] != "No coding experience",
        "experience_years": profile["experience_years"],
        "target_jd": profile["jd"].split(" - ")[0],
    }

    try:
        # Create profile
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

        # Run analysis
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
            print(f"FAIL")
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

        # Activate
        r = await client.post(f"{BASE}/learning/{path_id}/activate")
        if r.status_code != 200:
            result["status"] = f"activate_fail:{r.status_code}"
            await client.delete(f"{BASE}/profiles/{pid}")
            print(f"FAIL activate")
            return result

        act = r.json()
        modules = act.get("modules", [])
        total_lessons = act.get("total_lessons", 0)
        print(f"{total_lessons} lessons.", end=" ", flush=True)

        # Generate ALL lessons
        print(f"Generating content...", end=" ", flush=True)
        result["modules"] = await generate_all_lessons(client, path_id, modules)

        result["total_lessons"] = total_lessons
        result["status"] = "success"
        print(f"Done!")

        # Cleanup
        await client.delete(f"{BASE}/profiles/{pid}")

    except Exception as e:
        result["status"] = f"error:{str(e)[:80]}"
        print(f"ERROR: {str(e)[:80]}")

    return result


async def main():
    all_results = []

    async with httpx.AsyncClient(timeout=180) as client:
        for i, profile in enumerate(PROFILES):
            result = await run_profile(client, profile, i)
            all_results.append(result)

            # Auto-recover from 502
            if "502" in result.get("status", ""):
                import subprocess
                subprocess.run(["ssh", "root@95.216.199.47",
                               "cd /opt/ai-pathway && docker compose restart backend"],
                              capture_output=True)
                await asyncio.sleep(15)

    # Save raw data
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"../docs/curriculum_quality_{ts}.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Generate quality report
    print(f"\n\n{'='*80}")
    print("CURRICULUM QUALITY ASSESSMENT")
    print(f"{'='*80}")

    successful = [r for r in all_results if r["status"] == "success"]
    print(f"\nProfiles tested: {len(all_results)} | Successful: {len(successful)}")

    for r in successful:
        tech_label = "TECHNICAL" if r["technical"] else "NON-TECHNICAL"
        print(f"\n{'='*80}")
        print(f"{r['name']} | {r['role']} | {r['industry']} | {tech_label}")
        print(f"Target: {r['target_jd']}")
        print(f"{'='*80}")

        total_impl = 0
        total_kc = 0
        total_ref = 0
        total_with_code = 0
        total_lessons_generated = 0
        topic_relevant_impl = 0
        topic_relevant_kc = 0

        for mod in r.get("modules", []):
            print(f"\n  Module {mod['module_number']}: {mod['skill_name']} ({mod['skill_id']})")
            for l in mod["lessons"]:
                if "concept_snapshot" not in l:
                    print(f"    L{l['lesson_number']}: {l['title']} [{l.get('type','')}] - NOT GENERATED")
                    continue

                total_lessons_generated += 1
                has_code = l.get("has_code", False)
                if has_code:
                    total_with_code += 1

                impl_title = l.get("impl_title", "")
                impl_desc = l.get("impl_description", "")
                impl_reqs = l.get("impl_requirements", [])
                impl_tools = l.get("impl_tools", [])
                impl_mins = l.get("impl_minutes", 0)
                kcs = l.get("knowledge_checks", [])
                refs = l.get("reflection_questions", [])

                if impl_title:
                    total_impl += 1
                total_kc += len(kcs)
                total_ref += len(refs)

                code_label = "CODE" if has_code else "NO-CODE"
                print(f"    L{l['lesson_number']}: {l['title']} [{l.get('type','')}] [{code_label}]")
                print(f"      Concept: {l.get('concept_snapshot','')[:100]}...")

                if impl_title:
                    print(f"      TASK: {impl_title}")
                    print(f"        What: {impl_desc[:120]}...")
                    if impl_reqs:
                        for req in impl_reqs[:3]:
                            print(f"        Req: {req[:80] if isinstance(req, str) else str(req)[:80]}")
                    if impl_tools:
                        print(f"        Tools: {', '.join(impl_tools[:5])}")
                    print(f"        Time: ~{impl_mins} min")

                if kcs:
                    print(f"      QUIZ: {len(kcs)} questions")
                    for kc in kcs[:2]:
                        q = kc.get("question", "")[:100]
                        print(f"        Q: {q}...")

                if refs:
                    print(f"      REFLECT: {len(refs)} questions")
                    for rq in refs[:1]:
                        print(f"        R: {str(rq)[:100]}...")

        # Scoring
        print(f"\n  --- SCORES ---")
        print(f"  Lessons generated: {total_lessons_generated}")
        print(f"  Implementation tasks: {total_impl}")
        print(f"  Knowledge check questions: {total_kc}")
        print(f"  Reflection questions: {total_ref}")
        print(f"  Lessons with code: {total_with_code} ({'expected' if r['technical'] else 'ISSUE' if total_with_code > 0 else 'correct - no code'})")

    # Summary scores
    print(f"\n\n{'='*80}")
    print("OVERALL QUALITY SCORES")
    print(f"{'='*80}")

    for r in successful:
        total_lessons = 0
        total_impl = 0
        total_kc = 0
        total_code = 0
        for mod in r.get("modules", []):
            for l in mod["lessons"]:
                if "concept_snapshot" in l:
                    total_lessons += 1
                    if l.get("impl_title"):
                        total_impl += 1
                    total_kc += len(l.get("knowledge_checks", []))
                    if l.get("has_code"):
                        total_code += 1

        impl_rate = total_impl * 100 // max(total_lessons, 1)
        kc_avg = total_kc / max(total_lessons, 1)
        code_correct = (total_code > 0) == r["technical"]
        tech_label = "TECH" if r["technical"] else "NON-TECH"

        print(f"  {r['name']:<25} [{tech_label:<8}] Lessons:{total_lessons:>3} Tasks:{total_impl:>3} ({impl_rate}%) KCs:{total_kc:>3} ({kc_avg:.1f}/lesson) Code:{'OK' if code_correct else 'FAIL'}")

    print(f"\nReport saved to ../docs/curriculum_quality_{ts}.json")


asyncio.run(main())
