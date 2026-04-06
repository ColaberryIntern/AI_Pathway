"""JD Parser Agent - Extracts State B from job descriptions.

Identifies the skills required by the target job (3-10), each mapped
to the GenAI Skills Ontology with a rationale explaining *why* the
skill is needed based on the job description text.
"""
import json
from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service


class JDParserAgent(BaseAgent):
    """Agent for parsing job descriptions and extracting required skills (State B)."""

    name = "JDParserAgent"
    description = "Parses job descriptions to extract required skills and proficiency levels"

    system_prompt = """You are an expert job description analyst specializing in AI/ML roles.
Your task is to analyze job descriptions and extract exactly 10 required skills mapped to
the GenAI Skills Ontology. Always return 10 skills — include both explicit requirements
AND implied skills from the responsibilities. Cast a wide net across domains.

PROFICIENCY SCALE (use this when assigning required levels):
- Level 1 (Aware): Can explain the concept. Entry-level familiarity.
- Level 2 (User): Can apply with guidance. Uses existing tools/frameworks.
- Level 3 (Practitioner): Adapts independently. Configures, customizes, troubleshoots.
- Level 4 (Builder): Ships production solutions. Designs and implements systems end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction and standards.

CALIBRATION GUIDANCE:
- JD says "strong understanding of", "deep knowledge of" → Level 3 (Practitioner)
- JD says "hands-on experience building", "implement", "develop" → Level 4 (Builder)
- JD says "design systems", "lead architecture", "define strategy" → Level 5 (Architect)
- JD says "familiarity with", "awareness of", "exposure to" → Level 2 (User)
- Senior/lead/staff roles typically require Level 3-5 for core skills
- Mid-level roles typically require Level 2-4 for core skills
- Entry-level roles typically require Level 1-3 for core skills

For each identified skill requirement, determine:
1. The skill ID from the ontology
2. The required proficiency level (1-5) using the calibration guidance above
3. The importance/criticality (high/medium/low)
4. A rationale explaining WHY this skill is needed, referencing specific text from the JD

Focus on:
- Explicit skill requirements
- Implied skills from responsibilities
- Tools and technologies mentioned
- Soft skills and collaboration requirements

Map everything to the GenAI Skills Ontology structure."""

    async def execute(self, task: dict) -> dict:
        """Parse a job description and extract State B skills.

        Args:
            task: {
                "jd_text": str - Job description text
                "target_role": str - Target role title (optional)
            }

        Returns:
            {
                "state_b_skills": dict - Skill IDs mapped to required levels
                "top_10_target_skills": list - Top 10 skills with rationale
                "extracted_requirements": list - Detailed skill requirements
                "role_analysis": dict - Analysis of the role
            }
        """
        self._start_execution()

        jd_text = task.get("jd_text", "")
        target_role = task.get("target_role", "")
        learner_profile = task.get("learner_profile") or {}

        # Get similar JDs and relevant skills from RAG
        relevant_skills = await self.rag.retrieve_skills(jd_text, n_results=40)

        # Fallback: when RAG is unavailable (NoOpRetriever), inject full ontology
        # so the LLM sees all valid skill IDs instead of hallucinating.
        ontology_context = ""
        if not relevant_skills:
            ontology = get_ontology_service()
            ontology_context = ontology.format_skills_for_prompt()

        # Build prompt
        prompt = self._build_parsing_prompt(
            jd_text, target_role, relevant_skills,
            ontology_context=ontology_context,
            learner_profile=learner_profile,
        )

        output_schema = {
            "type": "object",
            "properties": {
                "top_10_target_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer", "description": "Priority rank 1-10"},
                            "skill_id": {"type": "string", "description": "Ontology skill ID (e.g. SK.PRM.010)"},
                            "skill_name": {"type": "string"},
                            "domain": {"type": "string", "description": "Domain ID (e.g. D.PRM)"},
                            "domain_label": {"type": "string", "description": "Human-readable domain name"},
                            "required_level": {"type": "integer", "description": "Required proficiency 1-5"},
                            "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                            "rationale": {"type": "string", "description": "Why this skill is needed, referencing the JD text"}
                        },
                        "required": ["rank", "skill_id", "skill_name", "domain", "required_level", "importance", "rationale"]
                    },
                    "minItems": 10,
                    "maxItems": 10,
                    "description": "Exactly 10 skills ranked by importance. Include both explicit and implied skills."
                },
                "state_b_skills": {
                    "type": "object",
                    "description": "Mapping of skill IDs to required proficiency levels (0-5) — same skills as top_10_target_skills"
                },
                "extracted_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill_id": {"type": "string"},
                            "skill_name": {"type": "string"},
                            "required_level": {"type": "integer"},
                            "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                            "evidence": {"type": "string"}
                        }
                    },
                    "description": "Detailed breakdown of skill requirements"
                },
                "role_analysis": {
                    "type": "object",
                    "properties": {
                        "primary_function": {"type": "string", "description": "The exact job title for this role. Extract from the title field, first sentence, or 'We are looking for a [TITLE]' pattern. Do NOT use section headers or category names."},
                        "key_domains": {"type": "array", "items": {"type": "string"}},
                        "seniority_level": {"type": "string"},
                        "technical_depth": {"type": "string"}
                    }
                },
                "industry": {"type": "string"},
                "experience_level": {"type": "string"}
            },
            "required": ["top_10_target_skills", "state_b_skills", "extracted_requirements", "role_analysis"]
        }

        result = await self._call_llm_structured(prompt, output_schema, temperature=0.0)

        # Post-process: validate and remap skill IDs to ontology.
        # Critical for custom profiles where the LLM may hallucinate
        # IDs despite instructions — ensures state_b is grounded.
        ontology = get_ontology_service()
        valid_ids = ontology.get_all_skill_ids()

        # Build a name lookup from the top_10 for remapping
        name_to_orig = {}
        for entry in result.get("top_10_target_skills", []):
            name_to_orig[entry.get("skill_id", "")] = entry.get("skill_name", "")

        cleaned_b = {}
        for sid, lvl in result.get("state_b_skills", {}).items():
            if sid in valid_ids:
                cleaned_b[sid] = lvl
            else:
                name = name_to_orig.get(sid, "")
                matches = ontology.search_skills(name) if name else []
                if matches:
                    cleaned_b[matches[0]["id"]] = lvl
        result["state_b_skills"] = cleaned_b

        if "top_10_target_skills" in result:
            for entry in result["top_10_target_skills"]:
                sid = entry.get("skill_id", "")
                if sid not in valid_ids:
                    name = entry.get("skill_name", "")
                    matches = ontology.search_skills(name) if name else []
                    if matches:
                        entry["skill_id"] = matches[0]["id"]
                        entry["domain"] = matches[0]["domain"]

        if "extracted_requirements" in result:
            for req in result["extracted_requirements"]:
                sid = req.get("skill_id", "")
                if sid not in valid_ids:
                    name = req.get("skill_name", "")
                    matches = ontology.search_skills(name) if name else []
                    if matches:
                        req["skill_id"] = matches[0]["id"]

        # Ensure we have at least 10 skills - if LLM returned fewer, pad with
        # ontology-matched skills from JD keywords
        import logging
        _logger = logging.getLogger(__name__)
        top_skills = result.get("top_10_target_skills", [])
        print(f"[JD_PARSER] Returned {len(top_skills)} skills, padding to 10 if needed")
        if len(top_skills) < 10:
            existing_ids = {s.get("skill_id") for s in top_skills}
            # Extract key terms from JD and search ontology for each
            # Search terms mapped to implied skills - broader than exact JD keywords
            search_terms = [
                "prompt", "bias", "hallucin", "Recognizing AI",
                "copyright", "disclosure", "Output quality",
                "draft", "grounding", "collaboration",
                "debug", "evaluation", "governance",
                "critique", "citation", "iteration",
            ]
            # Also add terms derived from common JD phrases
            jd_lower = jd_text.lower()
            if "edit" in jd_lower or "refine" in jd_lower or "generat" in jd_lower:
                search_terms.extend(["prompt", "debug", "draft"])
            if "accuracy" in jd_lower or "tone" in jd_lower or "clarity" in jd_lower:
                search_terms.extend(["hallucin", "bias"])
            if "ai-generated" in jd_lower or "ai generated" in jd_lower:
                search_terms.extend(["disclosure", "copyright"])
            if "data analysis" in jd_lower or "performance" in jd_lower:
                search_terms.extend(["evaluation", "quality"])
            # Deduplicate
            search_terms = list(dict.fromkeys(search_terms))
            for term in search_terms:
                if len(top_skills) >= 10:
                    break
                matches = ontology.search_skills(term)
                # Take only the first match per term for broader coverage
                for match in matches[:1]:
                    if match["id"] not in existing_ids:
                        top_skills.append({
                            "rank": len(top_skills) + 1,
                            "skill_id": match["id"],
                            "skill_name": match.get("name", match["id"]),
                            "domain": match.get("domain", ""),
                            "domain_label": match.get("domain_label", ""),
                            "required_level": 2,
                            "importance": "low",  # Padded skills rank below LLM-selected ones
                            "rationale": f"Implied by '{term}' in the job description",
                        })
                        existing_ids.add(match["id"])
                        result.setdefault("state_b_skills", {})[match["id"]] = 2
                        print(f"[JD_PARSER] Padded: {match['id']} - {match.get('name')} (from '{term}')")
            result["top_10_target_skills"] = top_skills

        self._log_execution("parse_jd", {"jd_length": len(jd_text)}, result)
        result["duration_ms"] = self._end_execution()

        return result

    def _build_parsing_prompt(
        self, jd_text: str, target_role: str, relevant_skills: list,
        *, ontology_context: str = "", learner_profile: dict | None = None
    ) -> str:
        """Build the JD parsing prompt for the LLM."""
        if relevant_skills:
            skills_context = "\n".join([
                f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']}, Level: {s['level']})"
                for s in relevant_skills
            ])
        elif ontology_context:
            skills_context = ontology_context
        else:
            skills_context = "(No skills available)"

        # Build learner context for prioritization
        learner_section = ""
        if learner_profile:
            cp = (learner_profile.get("current_profile") or {})
            parts = []
            if cp.get("summary"):
                parts.append(f"Background: {cp['summary'][:300]}")
            if learner_profile.get("current_role"):
                parts.append(f"Current Role: {learner_profile['current_role']}")
            if learner_profile.get("industry"):
                parts.append(f"Industry: {learner_profile['industry']}")
            if learner_profile.get("experience_years"):
                parts.append(f"Experience: {learner_profile['experience_years']} years")
            if parts:
                learner_section = f"""

LEARNER PROFILE (use this to PRIORITIZE skills by gap):
{chr(10).join(parts)}

RANKING RULE: Rank by what creates the most VALUE for THIS learner.
Skills the learner ALREADY HAS from their career background should be ranked LOWER (they have less to learn).
Skills where the learner has the BIGGEST GAP should be ranked HIGHER (most learning value).
For example, if the learner has 9+ years of editorial experience, skills like "recognizing content" and
"understanding bias" are partially covered by their background. Prioritize skills they have ZERO experience
with, like prompt engineering and AI mechanics."""

        return f"""Analyze this job description and identify the TOP 10 required skills.
IMPORTANT: Always return exactly 10 skills ranked by PRIORITY for THIS learner.
Skills where the learner has the biggest gap should be ranked highest.
Skills the learner already partially has from their career should be ranked lower.
Include both explicit requirements AND implied skills from the responsibilities.

TARGET ROLE: {target_role or 'Not specified'}

JOB DESCRIPTION:
{jd_text}{learner_section}

AVAILABLE SKILLS FROM ONTOLOGY:
{skills_context}

PROFICIENCY SCALE (use this to assign required_level):
- Level 1 (Aware): Can explain the concept. Entry-level familiarity.
- Level 2 (User): Can apply with guidance. Uses existing tools.
- Level 3 (Practitioner): Adapts independently. Configures, customizes, troubleshoots.
- Level 4 (Builder): Ships production solutions. Designs and implements end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction.

CALIBRATION RULES:
- "strong understanding", "deep knowledge" → Level 3+
- "hands-on experience building", "implement", "develop" → Level 4
- "design systems", "lead architecture", "define strategy" → Level 5
- "familiarity with", "awareness of" → Level 2
- Senior/Lead roles: core skills should be Level 3-5
- Mid-level roles: core skills should be Level 2-4
- For HIGH importance skills, assign Level 3 minimum (the role NEEDS proficiency)
- For skills central to the role's primary function, prefer Level 4 (Builder)

ROLE TITLE EXTRACTION:
- For role_analysis.primary_function, extract the exact job title from the opening sentence or explicit title field
  (e.g., "We are looking for an AI Operations Manager" -> "AI Operations Manager")
- Do NOT use section headers like "Key Responsibilities" subsections as the role title
- The role title should be the position someone would put on their business card

INSTRUCTIONS:
CRITICAL: You MUST ONLY use skill_id values from the AVAILABLE SKILLS list above.
Do NOT invent new skill IDs. Every skill_id in your response must exactly match one from that list.
If a JD requirement doesn't map perfectly to an ontology skill, choose the closest match.

1. Select exactly 10 skills from the ontology that are required or strongly implied by this role.
   Include both explicit requirements AND implied skills from responsibilities.
2. For each skill, determine the required proficiency level (1-5) using the CALIBRATION RULES above.
   Do NOT default to low levels -- match the level to the JD's actual demands.
3. For each skill, rate its importance (high/medium/low).
4. For each skill, write a rationale (1-2 sentences) explaining WHY this skill is needed,
   referencing specific text or requirements from the job description.
5. Rank the skills from most important (rank 1) to least important.
6. Also populate state_b_skills with the same skill_id -> required_level mapping.
7. Also populate extracted_requirements with the same data for backward compatibility.

SKILL SELECTION PRIORITY (follow this order):
- FIRST: Practical AI workflow skills -- how the person actually DOES their work with AI day-to-day.
  Examples: prompt debugging & iteration, draft-critique-revise, grounding & citations,
  cross-functional AI collaboration, facilitating AI workshops, evaluating AI outputs.
  These describe HOW the person works, not just WHAT the role is.
- SECOND: Domain-specific applied skills -- specialized knowledge for the industry/function.
  Examples: learning design with AI, healthcare clinical risk, marketing ethics.
- THIRD: Generic management/strategy skills -- only if genuinely AI-specific.
  "Stakeholder management" and "Teaching others AI skills" are generic to any role.
  Prefer the AI-specific version: e.g., "AI enablement & training strategy" over generic
  "stakeholder management" when both apply.
- AVOID: Skills that any professional already has from general work experience
  (basic communication, general project management, basic stakeholder engagement)
  unless the JD requires an AI-SPECIFIC version of that skill.

Example rationale: "The JD requires 'Define evaluation criteria, launch experiments, and
iterate based on performance' -- this directly maps to Eval Types (offline/online/red team)
at Practitioner level (L3), as the role needs independent evaluation capability."

Include both explicit requirements and implied skills from the responsibilities.
Focus on AI/GenAI related skills but also include relevant prerequisites and soft skills.

TECHNICAL DEPTH MATCHING:
- Match the technical depth of recommended skills to the role's actual needs.
- For non-technical roles (L&D, marketing, HR, management, strategy): Do NOT recommend
  ML-engineering skills like "Hugging Face ecosystem", "Prompt vs fine-tune decision",
  "LLM-as-judge patterns", model training, or infrastructure skills unless the JD explicitly
  requires them. These roles need AI USER skills, not AI BUILDER skills.
- For technical roles (engineering, data science, ML): include deeper technical skills.
- When in doubt, check: does the JD say "build/implement/deploy" (technical) or
  "use/leverage/apply" (user-level)?

DOMAIN COVERAGE - LOOK FOR THESE IMPLIED SKILLS:
Do NOT only match explicit keywords. Also surface skills implied by the role's responsibilities:
- If the JD mentions "quality", "accuracy", "standards", "metrics", or "performance measurement"
  -> include an Evaluation skill (D.EVL) such as output quality evaluation or eval types
- If the JD mentions "ethical", "responsible AI", "compliance", "disclosure", "guidelines", or "standards"
  -> include a Governance skill (D.GOV) such as AI-generated content disclosure or AI governance fundamentals
- If the JD mentions "iterative", "drafting", "editing", "refining", "writing", or "content development"
  -> include Draft-critique-revise (D.PRM) as a practical AI workflow skill
- If the JD mentions "collaborate", "partner with", "cross-functional", "work with stakeholders"
  -> include Cross-functional AI collaboration (D.COM) rather than generic stakeholder management
- If the JD mentions "facilitate", "deliver training", "workshops", "live sessions", or "virtual training"
  -> include Facilitating AI workshops (D.COM) as a practical delivery skill
- If the JD mentions "content creation" + "AI tools"
  -> include IP/copyright awareness (D.FND) since AI-generated content carries IP risks
- If the JD mentions "evaluate", "review", "assess", "accuracy", "tone", "clarity" of AI content
  -> include Recognizing AI-generated content (D.CTIC) as a critical thinking skill
- If the JD mentions "bias", "fairness", "inclusive", "brand voice", "alignment"
  -> include Understanding bias in content (D.CTIC) as a critical thinking skill
- If the JD mentions "AI-generated", "hallucination", "factual", "verify", "accuracy"
  -> include Capabilities vs limitations/hallucinations (D.FND)
- If the JD mentions "prompt", "generation", "refine", "iterate", "debug"
  -> include Prompt debugging & iteration (D.PRM)
- Avoid recommending 3+ skills from the same domain. Spread across domains for breadth.

Only recommend skills the person in this role would actually USE day-to-day."""
