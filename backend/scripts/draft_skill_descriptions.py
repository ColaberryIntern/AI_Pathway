"""Draft per-skill descriptions for SME review (Natural +1 prep).

The ontology has 0/220 skill `description` fields (see ontology_gap_audit.md). This
LLM-drafts a 1-2 sentence description for every skill from its name + domain + rubric
L1/L6 anchors, so Luda's pass is approve-not-author. Writes DRAFTS only - it does NOT
modify ontology.json (SME sign-off first, then a separate wiring step).

Run: cd backend && py -3.12 scripts/draft_skill_descriptions.py
Outputs: docs/compliance/skill_descriptions_draft.{json,md}
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.getLogger("httpx").setLevel(logging.WARNING)

from app.services.llm.factory import get_judge_provider  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "backend" / "app" / "data" / "ontology.json"
OUT_JSON = ROOT / "docs" / "compliance" / "skill_descriptions_draft.json"
OUT_MD = ROOT / "docs" / "compliance" / "skill_descriptions_draft.md"

BATCH = 15
CONCURRENCY = 5
SCHEMA = {
    "type": "object",
    "properties": {
        "descriptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "description": {"type": "string"}},
                "required": ["id", "description"],
            },
        }
    },
    "required": ["descriptions"],
}
SYSTEM = ("You write the canonical one-to-two sentence description for skills in a GenAI "
          "skills ontology used to build personalized AI upskilling paths. For each skill, "
          "describe in plain English WHAT the skill is and WHY it matters for someone using "
          "AI at work. 1-2 sentences, present tense, concrete, no marketing fluff, no "
          "restating the name verbatim.")


async def _draft_batch(judge, batch: list[dict], sem: asyncio.Semaphore) -> list[dict]:
    lines = []
    for s in batch:
        rbl = s.get("rubric_by_level") or []
        lines.append(
            f"- id={s['id']} | name={s['name']} | domain={s['domain_label']} | "
            f"beginner: {rbl[0] if rbl else ''} | expert: {rbl[-1] if rbl else ''}"
        )
    prompt = ("Write a description for EACH skill below. Return JSON "
              "{descriptions:[{id, description}]} covering every id.\n\n" + "\n".join(lines))
    async with sem:
        raw = await judge.generate_structured(prompt=prompt, output_schema=SCHEMA,
                                              system_prompt=SYSTEM, temperature=0.2)
    return raw.get("descriptions", []) or []


async def main() -> int:
    d = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    dom_label = {x["id"]: x.get("label", x["id"]) for x in d.get("domains", [])}
    skills = [{**s, "domain_label": dom_label.get(s.get("domain"), s.get("domain", ""))}
              for s in d.get("skills", [])]
    batches = [skills[i:i + BATCH] for i in range(0, len(skills), BATCH)]
    judge = get_judge_provider()
    sem = asyncio.Semaphore(CONCURRENCY)
    print(f"Drafting descriptions for {len(skills)} skills in {len(batches)} batches...")

    results = await asyncio.gather(*[_draft_batch(judge, b, sem) for b in batches],
                                   return_exceptions=True)
    desc: dict[str, str] = {}
    for r in results:
        if isinstance(r, Exception):
            print("  batch failed:", type(r).__name__, str(r)[:80])
            continue
        for item in r:
            if item.get("id") and item.get("description"):
                desc[item["id"]] = item["description"].strip()

    by_id = {s["id"]: s for s in skills}
    missing = [sid for sid in by_id if sid not in desc]
    print(f"Drafted {len(desc)}/{len(skills)} ({len(missing)} missing: {missing[:8]})")

    OUT_JSON.write_text(json.dumps(desc, indent=2, ensure_ascii=False), encoding="utf-8")

    # Readable review file grouped by domain.
    from collections import defaultdict
    groups = defaultdict(list)
    for s in skills:
        groups[s["domain_label"]].append(s)
    md = ["# Skill descriptions - DRAFTS for SME review",
          "",
          f"LLM-drafted ({len(desc)}/{len(skills)}) from name + rubric anchors. **Not yet in "
          "ontology.json** - review/edit, then a separate step wires approved text into the "
          "ontology (that is what moves Natural 4 -> 5).",
          ""]
    for dom in sorted(groups):
        md.append(f"## {dom}")
        md.append("")
        md.append("| id | name | draft description |")
        md.append("|---|---|---|")
        for s in groups[dom]:
            txt = desc.get(s["id"], "_(missing - re-run)_").replace("|", "\\|")
            md.append(f"| {s['id']} | {s['name']} | {txt} |")
        md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)} + {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
