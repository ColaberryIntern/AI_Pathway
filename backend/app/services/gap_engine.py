"""Skill Gap Engine — Phase 4: Deterministic 5-Factor Rubric Scoring

Computes the delta between a learner's current skill levels (State A)
and a target skill profile (State B), returning a prioritised list of
gaps scored by Luda's 5-factor rubric.

Scoring formula
---------------
::

    priority_score = (Importance × 4)
                   + (Breadth × 3)
                   + (Momentum × 3)
                   + (Connectivity × 2)
                   + (Career Signal × 2)

Each factor is scored 1-3 (max score = 42).

Momentum is the key differentiator — it captures the learner's
LEARNING ROI: skills they already have from their career get LOW
momentum (small room to grow), skills with zero background get HIGH
momentum (biggest gap, highest return on investment).
"""

from __future__ import annotations

import re
from typing import Any

from app.services.ontology import OntologyService, get_ontology_service

# ── Stopwords for tokenization ──────────────────────────────────────
STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "not", "no", "so", "if",
    "as", "it", "its", "i", "my", "me", "we", "our", "you", "your",
    "he", "she", "they", "them", "their", "this", "that", "these",
    "those", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "than", "too", "very", "just", "also",
    "about", "up", "out", "into", "over", "after", "before", "between",
    "under", "above", "through", "during", "while", "where", "when",
    "how", "what", "which", "who", "whom", "why", "then", "there",
    "here", "well", "back", "being", "been", "having", "new", "old",
    "across", "including", "working", "work", "years", "year",
    "experience", "experienced", "professional", "professionals",
})


def _tokenize(text: str) -> set[str]:
    """Split text into normalized lowercase tokens."""
    if not text:
        return set()
    # Split on whitespace and common punctuation, lowercase
    tokens = set(re.split(r'[\s,;:/&|•·\-–—()\[\]{}]+', text.lower()))
    tokens -= {"", " "}
    tokens -= STOPWORDS
    return tokens


def _extract_capability_signals(learner_profile: dict) -> set[str]:
    """Extract normalized capability keywords from learner profile.

    Deterministic: same profile always produces the same signal set.
    """
    signals: set[str] = set()

    # 1. Role keywords
    signals.update(_tokenize(learner_profile.get("current_role", "")))

    # 2. Industry keywords
    signals.update(_tokenize(learner_profile.get("industry", "")))

    # 3. Technical skills (both as phrases and tokens)
    cp = learner_profile.get("current_profile") or {}
    for skill in cp.get("technical_skills", []):
        if isinstance(skill, str):
            signals.add(skill.lower().strip())
            signals.update(_tokenize(skill))

    # 4. Soft skills
    for skill in cp.get("soft_skills", []):
        if isinstance(skill, str):
            signals.add(skill.lower().strip())
            signals.update(_tokenize(skill))

    # 5. Summary text
    signals.update(_tokenize(cp.get("summary", "")))

    # 6. Tools used
    for tool in learner_profile.get("tools_used", []):
        if isinstance(tool, str):
            signals.add(tool.lower().strip())
            signals.update(_tokenize(tool))

    # 7. AI experience text
    signals.update(_tokenize(cp.get("ai_experience", "")))

    # 8. Learning intent
    signals.update(_tokenize(learner_profile.get("learning_intent", "")))

    return signals


# ── Career signal lookup tables ──────────────────────────────────────
# Maps ontology domains to career keywords indicating transferable experience.
# If a learner's profile contains these keywords, they likely already have
# some foundation in this domain from their career.

DOMAIN_CAREER_SIGNALS: dict[str, set[str]] = {
    "D.CTIC": {
        "editorial", "editor", "editing", "journalism", "journalist",
        "fact-checking", "research", "analyst", "verification",
        "content review", "content moderation", "critical thinking",
        "proofreading", "copyediting", "copy editing",
        "bias", "fairness", "diversity", "inclusion",
    },
    "D.FND": {
        "machine learning", "data science", "artificial intelligence",
        "ai", "ml", "deep learning", "neural network", "nlp",
        "natural language processing", "computer science",
        "statistics", "statistical", "analytics", "data analysis",
        "python", "tensorflow", "pytorch",
    },
    "D.PRM": {
        "prompt engineering", "prompting", "prompt",
        "llm", "large language model", "conversational ai",
    },
    "D.GOV": {
        "governance", "compliance", "regulation", "regulatory",
        "policy", "legal", "privacy", "gdpr", "hipaa",
        "risk management", "audit", "ethics",
        "disclosure", "transparency",
    },
    "D.EVL": {
        "quality assurance", "qa", "testing",
        "metrics", "measurement", "kpi", "evaluation",
        "a/b testing", "data-driven",
        "performance measurement", "benchmarking",
    },
    "D.COM": {
        "communications", "communication", "writing", "writer",
        "copywriting", "content strategy", "content creation",
        "storytelling", "presentation", "presenting",
        "stakeholder", "executive communications",
        "internal communications", "public relations",
        "marketing communications", "brand",
    },
    "D.PRD": {
        "product management", "product manager", "product owner",
        "ux", "user experience", "design thinking",
        "agile", "scrum", "project management",
        "roadmap", "strategy", "strategic planning",
    },
    "D.RAG": {
        "search", "information retrieval", "knowledge management",
        "database", "sql", "elasticsearch",
        "documentation", "taxonomy", "content management", "cms",
    },
    "D.AGT": {
        "automation", "workflow", "orchestration",
        "rpa", "scripting", "devops",
        "systems integration", "api",
    },
    "D.SEC": {
        "security", "cybersecurity", "infosec",
        "risk assessment", "vulnerability",
        "access control", "authentication",
    },
    "D.PRQ": {
        "programming", "coding", "software development",
        "python", "javascript", "typescript", "java",
        "sql", "git", "version control",
        "api", "rest", "backend", "frontend",
    },
    "D.TOOL": {
        "chatgpt", "claude", "gemini", "copilot",
        "midjourney", "dall-e", "stable diffusion",
    },
    "D.LRN": {
        "training", "teaching", "education", "instructor",
        "mentoring", "coaching", "curriculum",
        "learning development",
    },
}

# Skill-specific overrides for high-specificity skills
SKILL_CAREER_SIGNALS: dict[str, set[str]] = {
    "SK.CTIC.006": {  # Recognizing AI-generated content
        "editorial", "editor", "content review",
        "fact-checking", "journalism",
    },
    "SK.CTIC.004": {  # Understanding bias in content
        "editorial", "editor", "journalism", "bias",
        "diversity", "inclusion", "equity",
        "content review", "sensitivity",
    },
    "SK.FND.021": {  # IP/copyright awareness
        "publishing", "publisher", "editorial",
        "copyright", "intellectual property", "licensing",
        "media", "content rights", "random house",
    },
    "SK.PRM.021": {  # Grounding & citations
        "journalism", "journalist", "research",
        "academic", "editorial", "fact-checking",
        "citations", "source", "newsletter",
    },
    "SK.PRM.003": {  # Prompt debugging & iteration
        "prompt engineering", "prompting",
        # Deliberately narrow: most people do NOT have this
    },
    "SK.PRM.020": {  # Draft -> critique -> revise
        "editorial", "editor", "editing",
        "revision", "content strategy",
        # Editorial-adjacent but AI-in-the-loop is new
    },
    "SK.GOV.022": {  # AI-generated content disclosure
        "compliance", "regulatory", "disclosure",
        "transparency", "ai governance",
    },
    "SK.EVL.001": {  # Output quality evaluation
        "quality assurance", "qa", "testing",
        "metrics", "kpi", "evaluation",
        "benchmarking", "a/b testing",
    },
    "SK.FND.002": {  # Capabilities vs limitations (hallucinations)
        "machine learning", "data science", "ai research",
        "model training", "neural network",
        # Technical AI knowledge, not editorial
    },
    "SK.COM.005": {  # Cross-functional AI collaboration
        "communications", "stakeholder", "cross-functional",
        "collaboration", "executive communications",
        "project management",
    },
}

# AI-specific domains where career transfer exists but AI application is new
AI_SPECIFIC_DOMAINS = frozenset({
    "D.PRM", "D.FND", "D.RAG", "D.AGT", "D.MOD",
    "D.MUL", "D.EVL", "D.SEC", "D.OPS", "D.TOOL",
})


def _compute_career_overlap(
    skill_id: str,
    skill_domain: str,
    learner_signals: set[str],
) -> tuple[float, int]:
    """Compute overlap between learner signals and skill's career signals.

    Returns (overlap_ratio, match_count).
    """
    # Merge domain-level and skill-level signal sets
    relevant = set(DOMAIN_CAREER_SIGNALS.get(skill_domain, set()))
    if skill_id in SKILL_CAREER_SIGNALS:
        relevant |= SKILL_CAREER_SIGNALS[skill_id]

    if not relevant:
        return 0.0, 0

    matches = learner_signals & relevant
    return len(matches) / len(relevant), len(matches)


def _compute_momentum_score(
    skill_id: str,
    skill_domain: str,
    learner_signals: set[str],
    ai_exposure_level: str,
    experience_years: int,
    current_level: int,
    domain_floor: int,
) -> int:
    """Compute momentum score 1-3 for a skill.

    Momentum = Learning ROI for THIS learner on THIS skill.
    - 3: Zero background. Huge room to grow. Highest ROI.
    - 2: Some transferable experience but AI application is new.
    - 1: Strong transferable skills. Low room to grow. Lowest ROI.
    """
    # If we have explicit skill levels, use them
    if current_level >= 2:
        return 1  # Already competent = low learning ROI
    if domain_floor >= 2:
        return 1  # Strong in this domain already

    # Career-based momentum from profile text
    if learner_signals:
        overlap, match_count = _compute_career_overlap(
            skill_id, skill_domain, learner_signals,
        )

        # Experience-based thresholds: senior professionals transfer more
        if experience_years >= 7:
            high_threshold, low_threshold = 0.10, 0.03
            high_match_count = 2
        elif experience_years <= 2:
            high_threshold, low_threshold = 0.25, 0.10
            high_match_count = 3
        else:
            high_threshold, low_threshold = 0.15, 0.05
            high_match_count = 2

        is_high = overlap >= high_threshold or match_count >= high_match_count
        is_some = overlap >= low_threshold or match_count >= 1

        if is_high:
            base = 1  # Strong career overlap -> LOW momentum
        elif is_some:
            base = 2  # Some overlap -> MEDIUM
        else:
            base = 3  # No overlap -> HIGH momentum

        # AI-specific boost: even with career transfer, AI application is new
        if base == 1 and skill_domain in AI_SPECIFIC_DOMAINS:
            ai_is_new = ai_exposure_level in ("None", "Basic", "")
            if ai_is_new:
                base = 2  # Career transfer exists but AI is novel

        return base

    # Fallback when no profile available
    if current_level == 1 or domain_floor >= 1:
        return 2
    return 3  # Starting from scratch


class SkillGapEngine:
    """Calculate and rank skill gaps using the 5-factor rubric."""

    def __init__(self, ontology_service: OntologyService | None = None) -> None:
        self._ontology = ontology_service or get_ontology_service()

    def compute_gap(
        self,
        state_a: dict[str, int],
        state_b: dict[str, int],
        role_context: dict[str, Any] | None = None,
        skill_importance: dict[str, str] | None = None,
        skill_rank: dict[str, int] | None = None,
        learner_profile: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Return a sorted list of skill gaps scored by the 5-factor rubric.

        Parameters
        ----------
        state_a : current skill levels {skill_id: level}
        state_b : target skill levels {skill_id: level}
        role_context : role hint for relevance scoring
        skill_importance : JD parser importance ratings {skill_id: "high"|"medium"|"low"}
        skill_rank : JD parser rank order {skill_id: rank_int}
        learner_profile : full learner profile dict for career-based momentum
        """
        self._validate_skill_ids(state_a, label="state_a")
        self._validate_skill_ids(state_b, label="state_b")

        target_domains: set[str] = set()
        primary_domains: set[str] = set()
        if role_context:
            target_domains = set(role_context.get("target_domains") or [])
            primary_domains = set(role_context.get("primary_domains") or [])

        # Extract career signals once for all skills
        learner_signals: set[str] = set()
        ai_exposure = "Basic"
        exp_years = 0
        if learner_profile:
            learner_signals = _extract_capability_signals(learner_profile)
            ai_exposure = learner_profile.get("ai_exposure_level") or "Basic"
            exp_years = learner_profile.get("experience_years") or 0

        # Professional/domain floors
        max_skill = max(state_a.values()) if state_a else 0
        professional_floor = 1 if max_skill >= 2 else 0

        domain_max: dict[str, int] = {}
        for sid, level in state_a.items():
            skill_info = self._ontology.get_skill(sid)
            if skill_info:
                d = skill_info["domain"]
                domain_max[d] = max(domain_max.get(d, 0), level)

        gaps: list[dict[str, Any]] = []

        for skill_id, required_level in state_b.items():
            skill = self._ontology.get_skill(skill_id)

            dm = domain_max.get(skill["domain"], 0)
            domain_floor = max(1, dm - 1) if dm > 0 else 0

            if max_skill >= 3 and skill["level"] >= 3:
                skill_floor = 2
            else:
                skill_floor = professional_floor

            current_level = max(
                state_a.get(skill_id, 0), domain_floor, skill_floor
            )
            delta = required_level - current_level

            if delta <= 0:
                continue

            # Role relevance
            if skill["domain"] in primary_domains:
                role_relevance = 2
            elif skill["domain"] in target_domains:
                role_relevance = 1
            else:
                role_relevance = 0

            # ── 5-Factor Rubric ──

            # 1. IMPORTANCE (x4)
            imp_rating = (skill_importance or {}).get(skill_id, "medium")
            importance_score = {"critical": 3, "high": 3, "medium": 2, "low": 1}.get(imp_rating, 2)

            # 2. BREADTH (x3)
            domain = skill["domain"]
            breadth_score = (
                3 if domain in ("D.PRM", "D.FND", "D.CTIC")
                else 2 if domain in ("D.EVL", "D.GOV", "D.COM")
                else 1
            )

            # 3. MOMENTUM (x3) - career-based learning ROI
            momentum_score = _compute_momentum_score(
                skill_id, domain, learner_signals,
                ai_exposure, exp_years,
                current_level, domain_floor,
            )

            # 4. CONNECTIVITY (x2)
            dependents = self._ontology.get_skill_dependents(skill_id)
            connectivity_score = (
                3 if len(dependents) >= 3
                else 2 if len(dependents) >= 1
                else 1
            )

            # 5. CAREER SIGNAL (x2)
            career_score = (
                3 if imp_rating in ("critical", "high")
                else 2 if imp_rating == "medium"
                else 1
            )
            if skill["domain"] in primary_domains:
                career_score = min(3, career_score + 1)

            priority_score = (
                (importance_score * 4)
                + (breadth_score * 3)
                + (momentum_score * 3)
                + (connectivity_score * 2)
                + (career_score * 2)
            )

            gaps.append({
                "skill_id": skill_id,
                "skill_name": skill["name"],
                "domain": skill["domain"],
                "current_level": current_level,
                "required_level": required_level,
                "delta": delta,
                "skill_level": skill["level"],
                "prerequisites": skill.get("prerequisites", []),
                "role_relevance": role_relevance,
                "priority_score": priority_score,
                "rubric_scores": {
                    "importance": importance_score,
                    "breadth": breadth_score,
                    "momentum": momentum_score,
                    "connectivity": connectivity_score,
                    "career_signal": career_score,
                },
            })

        # Sort by priority_score descending (deterministic, no LLM variance)
        gaps.sort(
            key=lambda g: (g["priority_score"], g["skill_id"]),
            reverse=True,
        )

        # Apply diversity rule: max 2 skills per domain in the top 5
        # If a domain already has 2 skills in the top positions, push
        # additional skills from that domain down
        if len(gaps) > 5:
            diversified: list[dict[str, Any]] = []
            domain_count: dict[str, int] = {}
            deferred: list[dict[str, Any]] = []
            for g in gaps:
                d = g["domain"]
                if domain_count.get(d, 0) < 2 or len(diversified) >= 5:
                    diversified.append(g)
                    domain_count[d] = domain_count.get(d, 0) + 1
                else:
                    deferred.append(g)
            # Re-insert deferred skills after the diversified top
            gaps = diversified + deferred

        return gaps

    def _validate_skill_ids(
        self,
        profile: dict[str, int],
        *,
        label: str,
    ) -> None:
        """Raise ValueError listing every unknown skill ID in profile."""
        unknown = [
            sid for sid in profile if self._ontology.get_skill(sid) is None
        ]
        if unknown:
            raise ValueError(
                f"Unknown skill ID(s) in {label}: {', '.join(unknown)}"
            )
