"""Run PathQualityEvaluator against 3 personas x 3 quality levels."""
import json
import sys

sys.path.insert(0, ".")

from app.services.path_quality_evaluator import PathQualityEvaluator
from app.services.path_generator import LearningPathGenerator
from app.services.ontology import get_ontology_service

ont = get_ontology_service()
gen = LearningPathGenerator(ontology_service=ont)
evaluator = PathQualityEvaluator()

# --- Load 3 profiles ---
profiles = {}
for fname, key in [
    ("app/data/profiles/profile_01_alex_rivera.json", "Alex Rivera"),
    ("app/data/profiles/profile_04_dana_morales.json", "Dana Morales"),
    ("app/data/profiles/profile_10_john_miller.json", "John Miller"),
]:
    with open(fname) as f:
        profiles[key] = json.load(f)


def build_inputs(profile):
    state_a = profile["estimated_current_skills"]
    state_b = {}
    for g in profile["expected_skill_gaps"]:
        for sid in g["skills"]:
            skill = ont.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
    rc = {
        "target_role": profile["target_role"],
        "target_domains": [g["domain"] for g in profile["expected_skill_gaps"]],
    }
    return state_a, state_b, rc


# --- Enrichment simulators ---

BLOOM_VERBS_BY_POS = [
    ["Identify", "Describe", "Explain"],
    ["Explain", "Describe", "Identify"],
    ["Apply", "Implement", "Compare"],
    ["Analyze", "Evaluate", "Differentiate"],
    ["Design", "Evaluate", "Propose"],
]


def enrich_high(scaffold):
    chapters = []
    for i, ch in enumerate(scaffold["chapters"]):
        verbs = BLOOM_VERBS_BY_POS[i % len(BLOOM_VERBS_BY_POS)]
        sn = ch["primary_skill_name"]
        chapters.append({
            "chapter_number": ch["chapter_number"],
            "skill_id": ch["primary_skill_id"],
            "skill_name": sn,
            "title": f"Understanding {sn}",
            "learning_objectives": [
                f"{verbs[0]} the core principles of {sn} and their role in production systems",
                f"{verbs[1]} how {sn} integrates with monitoring and observability pipelines",
                f"{verbs[2]} the relationship between {sn} and operational reliability metrics",
            ],
            "current_level": ch["current_level"],
            "target_level": ch["target_level"],
            "core_concepts": [
                {"title": "Concept A", "content": "Detailed explanation.", "examples": ["Ex1"]},
                {"title": "Concept B", "content": "In-depth discussion.", "examples": ["Ex2"]},
            ],
            "exercises": [
                {"id": f"ex-{i}-1", "title": "Lab", "description": "Build it", "type": "hands-on",
                 "estimated_time_minutes": 45, "instructions": ["Step 1"], "deliverable": "Prototype"},
            ],
            "applied_project": {
                "project_title": f"Build a {sn} Dashboard for Your Team",
                "project_description": (
                    f"Design and implement a functional {sn} monitoring dashboard "
                    f"that integrates with your existing toolchain. The dashboard should "
                    f"display real-time metrics, historical trends, and alert thresholds "
                    f"relevant to your production environment."
                ),
                "deliverable": f"A deployed {sn} dashboard with at least 3 key metrics",
                "estimated_time_minutes": 90,
            },
            "self_assessment_questions": [
                {"question": "What is the primary purpose?", "options": ["A", "B", "C"], "answer": "A"},
            ],
            "industry_context": f"{sn} is critical for reliable AI operations.",
            "estimated_time_hours": 3.0,
        })
    return {
        "title": "AI Skills Learning Path",
        "description": "Comprehensive path",
        "chapters": chapters,
        "total_estimated_hours": 3.0 * len(chapters),
    }


def enrich_mediocre(scaffold):
    chapters = []
    for i, ch in enumerate(scaffold["chapters"]):
        sn = ch["primary_skill_name"]
        chapters.append({
            "chapter_number": ch["chapter_number"],
            "skill_id": ch["primary_skill_id"],
            "skill_name": sn,
            "title": f"Chapter on {sn}",
            "learning_objectives": [
                f"Understand {sn}",
                f"Learn about {sn} features",
                f"Know the basics of {sn}",
            ],
            "current_level": ch["current_level"],
            "target_level": ch["target_level"],
            "core_concepts": [],
            "exercises": [],
            "applied_project": {
                "project_title": f"{sn} project",
                "project_description": "Build something related to this skill.",
                "deliverable": "A report",
                "estimated_time_minutes": 30,
            },
            "self_assessment_questions": [],
            "industry_context": "This is important.",
            "estimated_time_hours": 2.0,
        })
    return {
        "title": "Path",
        "description": "Path",
        "chapters": chapters,
        "total_estimated_hours": 2.0 * len(chapters),
    }


def enrich_poor(scaffold):
    chapters = []
    for i, ch in enumerate(scaffold["chapters"]):
        chapters.append({
            "chapter_number": ch["chapter_number"],
            "skill_id": ch["primary_skill_id"],
            "skill_name": ch["primary_skill_name"],
            "title": "",
            "learning_objectives": ["Learn stuff"],
            "current_level": ch["current_level"],
            "target_level": ch["target_level"],
            "core_concepts": [],
            "exercises": [],
            "applied_project": None,
            "self_assessment_questions": [],
            "industry_context": "",
            "estimated_time_hours": 0,
        })
    return {
        "title": "",
        "description": "",
        "chapters": chapters,
        "total_estimated_hours": 0,
    }


# --- Run evaluation ---
print("=" * 80)
print("PATH QUALITY EVALUATION - 3 PERSONAS x 3 QUALITY LEVELS")
print("=" * 80)

for name, profile in profiles.items():
    state_a, state_b, rc = build_inputs(profile)
    scaffold = gen.generate_path(state_a, state_b, role_context=rc)

    print(f"\n{'=' * 60}")
    print(f"PERSONA: {name} ({profile['current_role']} -> {profile['target_role']})")
    print(f"  Scaffold: {scaffold['total_chapters']} chapters")
    print(f"{'=' * 60}")

    for level_name, enricher in [("HIGH", enrich_high), ("MEDIOCRE", enrich_mediocre), ("POOR", enrich_poor)]:
        enriched = enricher(scaffold)
        report = evaluator.evaluate(enriched)

        print(f"\n  --- {level_name} QUALITY ---")
        print(f"  Overall score: {report['overall_score']}/5.0")
        print(f"  Progression consistency: {report['progression_consistency_score']}/5.0")
        print(f"  Domain balance: {report['domain_balance_score']}/5.0")
        for cs in report["chapter_scores"]:
            print(
                f"    Ch {cs['chapter_number']}: "
                f"obj={cs['objective_clarity_score']} "
                f"bloom={cs['bloom_progression_score']} "
                f"proj={cs['project_specificity_score']} "
                f"avg={cs['chapter_average']}"
            )
        if report["weakness_flags"]:
            print(f"  Weakness flags ({len(report['weakness_flags'])}):")
            for flag in report["weakness_flags"][:5]:
                print(f"    - {flag}")
            remaining = len(report["weakness_flags"]) - 5
            if remaining > 0:
                print(f"    ... and {remaining} more")
