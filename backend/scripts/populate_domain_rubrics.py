"""Populate rubric_by_level for the 8 D.DOM (Domain Applications) skills
that ship with empty rubrics, so chapter generation, hover tooltips, and
the per-skill, per-level descriptions all have authoritative content.

Idempotent: only fills entries that are missing or empty.
"""
from pathlib import Path
import json

ONTOLOGY_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "ontology.json"

RUBRICS = {
    "SK.DOM.EDU.001": [
        "Has not used AI in instructional design",
        "Knows AI can help generate learning materials and personalize content",
        "Uses AI to draft learning objectives, lesson outlines, and assessment questions with human review",
        "Designs AI-enabled learning experiences with personalization paths, scaffolded practice, and feedback loops",
        "Builds adaptive learning systems that adjust content difficulty, modality, and pacing based on learner signals",
        "Designs institution-wide AI learning architectures balancing personalization, pedagogy, equity, and instructor oversight",
    ],
    "SK.DOM.HC.001": [
        "Unaware AI can introduce clinical risk",
        "Knows AI outputs in clinical contexts can mislead diagnosis, treatment, or triage",
        "Identifies AI use cases that require clinician oversight versus those safe for ambient use",
        "Independently evaluates AI clinical tools against risk thresholds and FDA or regulatory guidance",
        "Builds clinical safety guardrails: confidence thresholds, override paths, audit trails for AI-assisted decisions",
        "Designs clinical AI risk management frameworks aligned to ISO 14971, FDA SaMD, and hospital governance",
    ],
    "SK.DOM.HC.002": [
        "Has not used AI to synthesize medical evidence",
        "Knows AI can summarize papers and guidelines but may hallucinate citations",
        "Uses AI to draft literature summaries with manual citation verification",
        "Designs evidence-synthesis workflows pairing AI retrieval with structured human appraisal such as PICO and GRADE",
        "Builds RAG-grounded evidence synthesis tools with provenance tracking and contradiction detection",
        "Architects evidence-synthesis pipelines integrated with clinical guidelines, peer review, and longitudinal updates",
    ],
    "SK.DOM.LGL.001": [
        "Unaware AI can blur the line between information and legal advice",
        "Knows AI legal outputs require disclaimers and cannot substitute for licensed counsel",
        "Adds appropriate disclaimers and routes user requests to attorneys when scope is exceeded",
        "Designs AI legal assistants that detect advice-versus-information boundaries and escalate appropriately",
        "Builds policy-enforcing legal AI with jurisdiction-aware disclaimers and audit logs",
        "Architects legal AI compliance frameworks aligned to state bar regulations and unauthorized practice statutes",
    ],
    "SK.DOM.LGL.002": [
        "Unaware that legal AI can fabricate case citations or statutes",
        "Knows legal AI hallucinations include fake cases, misquoted holdings, and invented citations",
        "Manually verifies case citations and statutory references in AI-generated legal text",
        "Designs evaluation suites that test legal AI against gold-standard citation and holding accuracy",
        "Builds automated hallucination detectors for legal text with citation verification and red-team prompts",
        "Architects continuous evaluation pipelines for production legal AI with regression testing and certification",
    ],
    "SK.DOM.FIN.001": [
        "Unaware that AI numerical outputs need audit trails",
        "Knows AI can miscalculate and that financial outputs require independent verification",
        "Uses AI for financial drafting while manually verifying every number against source data",
        "Designs auditable AI finance workflows that separate generation, calculation, and verification steps",
        "Builds AI finance tools with deterministic numerical engines, formula tracebacks, and reconciliation logs",
        "Architects audit-grade AI finance systems compliant with SOX, GAAP, and internal controls testing",
    ],
    "SK.DOM.MKT.001": [
        "Unaware of ethical concerns with AI marketing content",
        "Knows AI marketing content raises issues of disclosure, copyright, and impersonation",
        "Discloses AI involvement in marketing content and avoids deceptive synthetic media",
        "Designs marketing AI workflows aligned to FTC endorsement guides, brand guidelines, and IP boundaries",
        "Builds marketing AI guardrails: disclosure injection, brand-voice enforcement, IP source attribution",
        "Architects enterprise marketing AI ethics frameworks balancing scale, brand safety, regulation, and trust",
    ],
    "SK.DOM.HR.001": [
        "Unaware that AI in hiring carries discrimination and compliance risk",
        "Knows AI hiring tools must be audited for bias and disparate impact under EEOC and NYC Local Law 144",
        "Uses AI hiring tools only with disclosed scope, candidate consent, and human review of decisions",
        "Designs AI hiring workflows with bias audits, adverse-impact analysis, and explainability for candidates",
        "Builds AI hiring systems with continuous bias monitoring, candidate appeal paths, and regulator-ready audits",
        "Architects enterprise AI hiring frameworks aligned to EEOC, GDPR, NYC Local Law 144, and emerging AI hiring laws",
    ],
}


def main():
    with ONTOLOGY_PATH.open(encoding="utf-8") as fh:
        ontology = json.load(fh)

    skills = ontology.get("skills", [])
    if not isinstance(skills, list):
        raise RuntimeError("ontology.json has unexpected shape: skills is not a list")

    updated = []
    skipped_already_populated = []
    missing_in_data = []

    for skill in skills:
        sid = skill.get("id")
        if sid in RUBRICS:
            if skill.get("rubric_by_level"):
                skipped_already_populated.append(sid)
            else:
                skill["rubric_by_level"] = RUBRICS[sid]
                updated.append(sid)

    declared_ids = set(RUBRICS.keys())
    found_ids = {s.get("id") for s in skills if s.get("id") in declared_ids}
    missing_in_data = list(declared_ids - found_ids)

    if not updated:
        print("Nothing to do (every target skill already has rubrics).")
        return

    with ONTOLOGY_PATH.open("w", encoding="utf-8") as fh:
        json.dump(ontology, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Updated {len(updated)} skills with rubric_by_level:")
    for sid in updated:
        print(f"  - {sid}")
    if skipped_already_populated:
        print(f"Skipped (already populated): {skipped_already_populated}")
    if missing_in_data:
        print(f"WARNING: declared rubrics for skills not present in ontology.json: {missing_in_data}")


if __name__ == "__main__":
    main()
