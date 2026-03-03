"""Ontology service for skill queries."""
import json
from pathlib import Path
from functools import lru_cache
from typing import Any


class OntologyService:
    """Service for querying the GenAI Skills Ontology."""

    def __init__(self, ontology_path: str | None = None):
        if ontology_path is None:
            ontology_path = Path(__file__).parent.parent / "data" / "ontology.json"
        self.ontology_path = Path(ontology_path)
        self._data = None

    @property
    def data(self) -> dict:
        """Lazy load ontology data."""
        if self._data is None:
            with open(self.ontology_path, "r") as f:
                self._data = json.load(f)
        return self._data

    @property
    def skills(self) -> list[dict]:
        """Get all skills."""
        return self.data.get("skills", [])

    @property
    def domains(self) -> list[dict]:
        """Get all domains."""
        return self.data.get("domains", [])

    @property
    def layers(self) -> list[dict]:
        """Get all layers."""
        return self.data.get("layers", [])

    @property
    def proficiency_scale(self) -> list[dict]:
        """Get proficiency scale."""
        return self.data.get("proficiency_scale", [])

    @property
    def roles(self) -> list[dict]:
        """Get all roles."""
        return self.data.get("roles", [])

    def get_skill(self, skill_id: str) -> dict | None:
        """Get a skill by ID."""
        for skill in self.skills:
            if skill["id"] == skill_id:
                return skill
        return None

    def get_skills_by_domain(self, domain_id: str) -> list[dict]:
        """Get all skills in a domain."""
        return [s for s in self.skills if s["domain"] == domain_id]

    def get_domain(self, domain_id: str) -> dict | None:
        """Get a domain by ID."""
        for domain in self.domains:
            if domain["id"] == domain_id:
                return domain
        return None

    def get_skill_prerequisites(self, skill_id: str) -> list[dict]:
        """Get prerequisite skills for a skill."""
        skill = self.get_skill(skill_id)
        if not skill:
            return []

        prereqs = []
        for prereq_id in skill.get("prerequisites", []):
            prereq_skill = self.get_skill(prereq_id)
            if prereq_skill:
                prereqs.append(prereq_skill)
        return prereqs

    def get_skill_dependents(self, skill_id: str) -> list[dict]:
        """Get skills that depend on this skill."""
        dependents = []
        for skill in self.skills:
            if skill_id in skill.get("prerequisites", []):
                dependents.append(skill)
        return dependents

    def search_skills(
        self,
        query: str,
        domain_filter: str | None = None,
        level_filter: int | None = None,
    ) -> list[dict]:
        """Search skills by name (simple text matching)."""
        query_lower = query.lower()
        results = []

        for skill in self.skills:
            # Check domain filter
            if domain_filter and skill["domain"] != domain_filter:
                continue

            # Check level filter
            if level_filter is not None and skill.get("level") != level_filter:
                continue

            # Check name match
            if query_lower in skill["name"].lower():
                results.append(skill)

        return results

    def get_role_skills(self, role_id: str) -> list[dict]:
        """Get all skills relevant to a role."""
        role = None
        for r in self.roles:
            if r["id"] == role_id:
                role = r
                break

        if not role:
            return []

        skills = []
        for domain_id in role.get("focus_domains", []):
            skills.extend(self.get_skills_by_domain(domain_id))

        return skills

    def calculate_skill_gap(
        self,
        current_level: int,
        target_level: int,
    ) -> dict:
        """Calculate gap between current and target level."""
        gap = target_level - current_level
        return {
            "current_level": current_level,
            "target_level": target_level,
            "gap": max(0, gap),
            "current_label": self._get_level_label(current_level),
            "target_label": self._get_level_label(target_level),
        }

    def _get_level_label(self, level: int) -> str:
        """Get label for a proficiency level."""
        for p in self.proficiency_scale:
            if p["level"] == level:
                return p["label"]
        return "Unknown"

    def get_proficiency_descriptions(self, skill_id: str) -> list[dict]:
        """Get proficiency level descriptions for a skill (PL 0-4).

        Returns per-skill descriptions if available in the ontology,
        otherwise falls back to the generic proficiency scale.
        """
        skill = self.get_skill(skill_id)
        if skill and "proficiency_descriptions" in skill:
            return skill["proficiency_descriptions"]
        # Fallback: generic scale (PL 0-4 only, skip PL 5 for self-assessment)
        return [
            {"level": p["level"], "label": p["label"], "description": p["description"]}
            for p in self.proficiency_scale
            if p["level"] <= 4
        ]

    def get_full_ontology(self) -> dict:
        """Get the full ontology data."""
        return self.data

    def get_all_skill_ids(self) -> set[str]:
        """Return the set of all valid skill IDs in the ontology."""
        return {s["id"] for s in self.skills}

    def format_skills_for_prompt(self) -> str:
        """Format all ontology skills organized by domain for LLM prompt injection.

        Returns a compact string listing every skill grouped under its domain,
        suitable for inclusion in agent prompts when RAG is unavailable.
        Each skill line includes skill_id, name, and level.

        Output is ~5KB of text (~1500 tokens), well within context budget.
        """
        domain_lookup = {d["id"]: d["label"] for d in self.domains}

        # Group skills by domain
        skills_by_domain: dict[str, list[dict]] = {}
        for skill in self.skills:
            domain_id = skill["domain"]
            if domain_id not in skills_by_domain:
                skills_by_domain[domain_id] = []
            skills_by_domain[domain_id].append(skill)

        lines: list[str] = []
        for domain in self.domains:
            domain_id = domain["id"]
            domain_label = domain["label"]
            domain_skills = skills_by_domain.get(domain_id, [])
            if not domain_skills:
                continue
            lines.append(f"\n## {domain_label} ({domain_id})")
            for s in domain_skills:
                lines.append(f"- {s['id']}: {s['name']} (Level: {s['level']})")

        return "\n".join(lines)


@lru_cache
def get_ontology_service() -> OntologyService:
    """Get cached ontology service instance."""
    return OntologyService()
