"""Run the LinkedIn Parser Judge against a set of (LinkedIn text, parser output) pairs.

Per the 2026-06-09 / 2026-06-23 weekly calls: build a quality judge on the
LinkedIn parser so we can validate it independently of the JD parser, and "fix
what the judge doesn't pass" rather than run a self-improving loop.

The judge's deterministic core + pinned-model scoring live in
`app.services.linkedin_parse_judge` (single source of truth). This script is the
batch runner: it parses synthetic LinkedIn profiles (one per role family) and
judges each, then writes a results file.

Usage (inside ai-pathway-backend-1):
    python /app/run_linkedin_parser_judge.py [--limit N]
"""
import argparse
import asyncio
import json
import logging
from pathlib import Path

from app.services.linkedin_parse_judge import GATES, WEIGHTS, judge_linkedin_parse

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def load_ontology_md() -> str:
    for cand in (Path("/app/docs/ONTOLOGIES.md"), Path("docs/ONTOLOGIES.md")):
        if cand.exists():
            return cand.read_text(encoding="utf-8")
    raise FileNotFoundError("ONTOLOGIES.md not found")


# Synthetic LinkedIn profiles per role family for initial smoke testing
SYNTHETIC_LI_PROFILES = {
    "marketing_leadership": "Senior B2B SaaS marketing leader with 12+ years across demand gen, content, and AI-augmented campaign operations. Recent: rolled out an internal prompt library for the campaign team and launched A/B test framework on AI-drafted subject lines. Tools: ChatGPT, Jasper, Anyword, HubSpot. Led integrated campaigns for 4 product launches in the last 2 years. Comfortable explaining AI choices to non-technical execs.",
    "learning_and_development": "L&D Specialist at a state university with 6 years of instructional design experience. Started using AI tools to draft initial course outlines in late 2024, but moved away from them after the first attempts produced generic content. Now uses ChatGPT for brainstorming. Has not built any custom prompts or evaluation frameworks. Collaborates with department chairs and IT.",
    "healthcare_clinical": "Clinical informatics specialist with 10 years at a major hospital system. Recently deployed a vendor AI tool for radiology triage; led the validation effort against expert reads. Comfortable with bias and reliability discussions in a clinical context. Familiar with HIPAA and PHI considerations. Has read 2-3 recent papers on LLM hallucination in clinical settings.",
    "content_editorial": "Senior content editor at a digital media company, 8 years. Edits AI-generated draft articles daily; has built a personal QA checklist for AI fact-checking. Comfortable identifying hallucinated citations. Not yet using AI for ideation or research at scale.",
    "product_management": "Senior PM at a B2B SaaS company. Shipped 2 AI features in the last 18 months: a smart-search feature and an AI summarization feature. Wrote the eval rubric for both. Comfortable with prompt iteration, less so with LLM-as-judge patterns. 11 years of PM experience overall.",
    "operations_bizops": "BizOps manager at a fast-growing AI platform. Built internal workflow automations using Zapier + GPT-4 to route customer support tickets. Comfortable mapping cross-functional processes. Has not done any model evaluation work.",
    "sales": "Senior account executive at an AI platform company. Uses Gong + ChatGPT daily for call notes and follow-up drafts. Quota carrier for the last 5 years. Comfortable explaining the company's AI value proposition to technical buyers.",
    "engineering_data": "Senior data scientist with 7 years in tech. Currently working on LLM eval and prompt engineering for an internal AI assistant. Wrote a fine-tuning notebook used by the team. Strong Python, mid SQL, comfortable with LangChain and DSPy.",
    "finance_accounting": "FP&A manager at a Series C startup. Started using Excel Copilot in 2025, finds it useful for narrative generation. Has not done any model evaluation. Familiar with financial regulations but not AI-specific compliance.",
    "hr_recruiting": "Talent acquisition lead at a 1500-person tech company. Currently piloting an AI screening tool from Beamery. Concerned about bias and is working with legal on a disclosure policy. Has read about disparate impact in AI hiring.",
}


def synthetic_li(role_family: str) -> str:
    return SYNTHETIC_LI_PROFILES.get(role_family, SYNTHETIC_LI_PROFILES["product_management"])


async def parse_linkedin(li_text: str, current_role: str, experience_years: int, industry: str):
    from app.agents.linkedin_parser import LinkedInParserAgent
    agent = LinkedInParserAgent()
    return await agent.execute({
        "linkedin_text": li_text,
        "current_role": current_role,
        "experience_years": experience_years,
        "industry": industry,
    })


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from app.services.ontology import get_ontology_service
    valid_skill_ids = get_ontology_service().get_all_skill_ids()

    corpus_path = None
    for cand in (Path("/app/backend/data/stress_test_jds/corpus.json"),
                 Path("backend/data/stress_test_jds/corpus.json")):
        if cand.exists():
            corpus_path = cand
            break
    if not corpus_path:
        raise FileNotFoundError("corpus.json not found")
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    if args.limit:
        corpus = corpus[: args.limit]
    ontology_md = load_ontology_md()

    # One representative per role family for the initial pass
    by_family = {}
    for jd in corpus:
        by_family.setdefault(jd["role_family"], jd)
    sample = list(by_family.values())
    print(f"Running LinkedIn parser + judge on {len(sample)} role-family representatives...")
    print(f"WEIGHTS={WEIGHTS} GATES={GATES}")

    results = []
    for i, jd in enumerate(sample, 1):
        print(f"\n[{i}/{len(sample)}] {jd['role_family']} - {jd['title']}")
        li_text = synthetic_li(jd["role_family"])
        try:
            exp = 8 if jd["seniority"] == "senior" else (5 if jd["seniority"] == "mid" else 2)
            parser_result = await parse_linkedin(li_text, jd["title"], exp, jd["industry"])
            print(f"  Parser found {len(parser_result.get('existing_skills', []))} existing skills, "
                  f"fluency={parser_result.get('ai_fluency_assessment', {}).get('level', '?')}")

            jr = await judge_linkedin_parse(parser_result, li_text, ontology_md, valid_skill_ids)
            p = jr.parameter_scores
            print(f"  composite={jr.composite:.3f}  verdict={jr.verdict}  gates_failed={jr.gate_failures}")
            print(f"  P={p.get('ontology_precision', 0):.2f}  E={p.get('evidence_quality', 0):.2f}  "
                  f"C={p.get('conservativeness', 0):.2f}  Cov={p.get('coverage', 0):.2f}")

            results.append({
                "jd_id": jd["id"],
                "role_family": jd["role_family"],
                "title": jd["title"],
                "linkedin_text": li_text,
                "parser_result": parser_result,
                "judge": {
                    "verdict": jr.verdict,
                    "composite": jr.composite,
                    "parameter_scores": jr.parameter_scores,
                    "gate_failures": jr.gate_failures,
                    "invalid_skill_ids": jr.invalid_skill_ids,
                    "summary": jr.summary,
                },
                "composite": jr.composite,
                "verdict": jr.verdict,
            })
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            results.append({"jd_id": jd["id"], "role_family": jd["role_family"],
                            "title": jd["title"], "error": str(e)})

    out_path = Path(args.out or "/app/backend/data/stress_test_jds/linkedin_judge_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} results -> {out_path}")

    by_verdict = {}
    for r in results:
        if "error" in r:
            continue
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    print(f"\nVerdicts: {by_verdict}")


if __name__ == "__main__":
    asyncio.run(main())
