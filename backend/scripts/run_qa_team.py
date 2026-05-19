"""Run the multi-agent QA team against one persona and write a dossier.

Usage (inside the backend container or with backend on PYTHONPATH):
    python backend/scripts/run_qa_team.py <persona_id>

Exits with:
    0  - GREEN (demo ready)
    1  - YELLOW (ready with caveats; review the dossier)
    2  - RED (not ready; do not demo)
    3  - usage error
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import urllib.request
import json
from pathlib import Path

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: run_qa_team.py <persona_id>\n")
        return 3

    persona_id = sys.argv[1]

    # Make persona_corpus importable. Layout varies:
    #   - repo: backend/scripts/persona_corpus.py
    #   - container: /app/persona_corpus.py OR /app/scripts/persona_corpus.py
    here = Path(__file__).resolve()
    candidate_paths = [
        here.parent,                           # alongside this script
        Path("/app"),                          # container root
        Path("/app/scripts"),                  # container scripts
    ]
    # Also try repo layout: backend/scripts
    if len(here.parents) >= 2:
        candidate_paths.append(here.parents[1] / "backend" / "scripts")
    for p in candidate_paths:
        if (p / "persona_corpus.py").exists() and str(p) not in sys.path:
            sys.path.insert(0, str(p))
            break

    try:
        from persona_corpus import PERSONAS  # type: ignore
    except ImportError as exc:
        sys.stderr.write(
            f"Could not import persona_corpus: {exc}\n"
            f"Tried: {[str(p) for p in candidate_paths]}\n"
        )
        return 3

    # Output dir: prefer repo docs/qa_dossier when running from a repo,
    # fall back to /tmp inside container.
    out_dir = None
    for p in candidate_paths:
        if p and (p.parent / "docs").exists():
            out_dir = p.parent / "docs" / "qa_dossier"
            break
    if out_dir is None:
        out_dir = Path("/tmp/qa_dossier")

    persona = next((p for p in PERSONAS if p["id"] == persona_id), None)
    if not persona:
        sys.stderr.write(f"Unknown persona: {persona_id}\n")
        sys.stderr.write(f"Known: {[p['id'] for p in PERSONAS]}\n")
        return 3

    print(f"=== QA team running for: {persona_id} ===")
    print(f"    role: {persona.get('role')}")
    profile_id = persona.get("profile_id")
    print(f"    profile_id: {profile_id}")
    print()

    # Gather context: hit the parse-jd-skills endpoint and the
    # analysis/results endpoint for this profile so the agents have
    # everything they need.
    top_10_skills: list[dict] = []
    maintain: list[dict] | None = None
    develop: list[dict] | None = None
    path_id: str | None = None

    api_root = os.environ.get("AI_PATHWAY_API", "http://localhost:8080/api")

    if profile_id:
        # Latest analysis result has top_10_target_skills + maintain/develop
        try:
            with urllib.request.urlopen(
                f"{api_root}/analysis/results/{profile_id}", timeout=20
            ) as r:
                data = json.loads(r.read().decode("utf-8"))
                result = data.get("result") or {}
                top_10_skills = result.get("top_10_target_skills") or []
                maintain = result.get("maintain_skills")
                develop = result.get("develop_skills")
                path_id = data.get("learning_path_id")
        except Exception as exc:
            print(f"  (no saved analysis - {exc})")

    context = {
        "persona_id": persona_id,
        "persona": persona,
        "profile_id": profile_id,
        "path_id": path_id,
        "top_10_skills": top_10_skills,
        "maintain_skills": maintain,
        "develop_skills": develop,
    }

    from app.qa_agents.orchestrator import run_qa_team
    from app.qa_agents.demo_gate import render_dossier
    from app.qa_agents.verdict import VerdictColor

    verdicts = await run_qa_team(context)

    dossier = render_dossier(persona_id, verdicts)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{persona_id}.md"
    out_path.write_text(dossier, encoding="utf-8")

    print(dossier)
    print()
    print(f"Dossier written to {out_path}")

    final = verdicts[-1]
    if final.color == VerdictColor.GREEN:
        return 0
    if final.color == VerdictColor.YELLOW:
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
