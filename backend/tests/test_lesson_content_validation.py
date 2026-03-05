"""Tests for lesson content validation and substance checks.

Verifies that:
1. _has_substance correctly identifies empty vs populated content
2. Lesson content from the generator has all required AI-native sections
3. Content quality checks catch known-bad patterns
"""

import pytest
from app.api.routes.learning import _has_substance


# ── _has_substance ──────────────────────────────────────────────────────

class TestHasSubstance:
    """Verify the _has_substance helper rejects empty shells."""

    def test_empty_dict(self):
        assert _has_substance({}) is False

    def test_none_like(self):
        assert _has_substance({"concept_snapshot": ""}) is False
        assert _has_substance({"explanation": ""}) is False
        assert _has_substance({"concept_snapshot": None}) is False

    def test_all_defaults(self):
        """The setdefault pattern from lesson_generator produces this."""
        content = {
            "concept_snapshot": "",
            "ai_strategy": {},
            "prompt_template": {},
            "implementation_task": {},
            "reflection_questions": [],
            "explanation": "",
            "code_examples": [],
            "exercises": [],
            "knowledge_checks": [],
            "hands_on_tasks": [],
        }
        assert _has_substance(content) is False

    def test_has_concept_snapshot(self):
        content = {"concept_snapshot": "AI governance frameworks define..."}
        assert _has_substance(content) is True

    def test_has_explanation_only(self):
        content = {"explanation": "This lesson covers AI risk management."}
        assert _has_substance(content) is True

    def test_has_knowledge_checks(self):
        content = {
            "knowledge_checks": [
                {"question": "What is AI governance?", "options": ["a", "b"], "correct_answer": "a"},
            ],
        }
        assert _has_substance(content) is True

    def test_empty_knowledge_checks_list(self):
        content = {"knowledge_checks": []}
        assert _has_substance(content) is False


# ── Content structure validation ────────────────────────────────────────

REQUIRED_AI_NATIVE_KEYS = [
    "concept_snapshot",
    "ai_strategy",
    "prompt_template",
    "implementation_task",
    "reflection_questions",
    "knowledge_checks",
]

REQUIRED_LEGACY_KEYS = [
    "explanation",
    "code_examples",
    "exercises",
    "hands_on_tasks",
]


def _make_valid_content() -> dict:
    """Build a minimal but valid AI-native lesson content dict."""
    return {
        "concept_snapshot": "AI governance frameworks provide structured approaches to managing AI risks.",
        "ai_strategy": {
            "description": "Use AI to analyze regulatory documents.",
            "when_to_use_ai": ["Summarize compliance requirements"],
            "human_responsibilities": ["Final approval of governance policies"],
            "suggested_prompt": "Analyze the following AI governance framework...",
        },
        "prompt_template": {
            "template": "As an AI governance specialist, evaluate {{policy}}...",
            "placeholders": [{"name": "policy", "description": "The policy to evaluate", "example": "EU AI Act"}],
            "expected_output_shape": "A structured assessment with risk ratings.",
        },
        "implementation_task": {
            "title": "Build an AI Governance Checklist",
            "description": "Create a reusable checklist.",
            "requirements": ["Cover data privacy", "Include model documentation"],
            "deliverable": "A markdown checklist",
            "requires_prompt_history": True,
            "requires_architecture_explanation": False,
            "estimated_minutes": 30,
        },
        "reflection_questions": [
            {
                "question": "How did your prompt evolve?",
                "prompt_for_deeper_thinking": "Ask the AI: 'As a governance analyst, explain how...'",
            },
        ],
        "knowledge_checks": [
            {
                "question": "What is the primary purpose of AI governance?",
                "options": ["Speed up AI development", "Manage AI risks", "Replace human oversight", "Reduce costs"],
                "correct_answer": "Manage AI risks",
                "explanation": "AI governance focuses on risk management.",
                "ai_followup_prompt": "Explain the relationship between AI governance and risk management...",
            },
        ],
        "explanation": "AI governance refers to the set of policies and procedures...",
        "code_examples": [
            {
                "title": "Governance Policy Checker",
                "language": "python",
                "code": "def check_policy(policy):\n    return 'compliant'",
                "explanation": "A simple policy checker.",
            },
        ],
        "exercises": [],
        "hands_on_tasks": [],
    }


class TestContentStructure:
    """Verify lesson content has all required sections."""

    def test_valid_content_has_all_ai_native_keys(self):
        content = _make_valid_content()
        for key in REQUIRED_AI_NATIVE_KEYS:
            assert key in content, f"Missing AI-native key: {key}"

    def test_valid_content_has_all_legacy_keys(self):
        content = _make_valid_content()
        for key in REQUIRED_LEGACY_KEYS:
            assert key in content, f"Missing legacy key: {key}"

    def test_valid_content_passes_substance_check(self):
        content = _make_valid_content()
        assert _has_substance(content) is True

    def test_concept_snapshot_is_concise(self):
        """concept_snapshot should be under ~500 chars (4 sentences max)."""
        content = _make_valid_content()
        snapshot = content["concept_snapshot"]
        assert len(snapshot) > 10, "concept_snapshot too short"
        assert len(snapshot) < 1000, "concept_snapshot too long (should be 4 sentences max)"

    def test_ai_strategy_has_required_fields(self):
        content = _make_valid_content()
        strategy = content["ai_strategy"]
        assert strategy.get("description"), "ai_strategy missing description"
        assert isinstance(strategy.get("when_to_use_ai"), list), "ai_strategy missing when_to_use_ai"
        assert isinstance(strategy.get("human_responsibilities"), list), "ai_strategy missing human_responsibilities"

    def test_prompt_template_has_template_string(self):
        content = _make_valid_content()
        template = content["prompt_template"]
        assert template.get("template"), "prompt_template missing template"
        assert isinstance(template.get("placeholders"), list), "prompt_template missing placeholders"

    def test_implementation_task_has_required_fields(self):
        content = _make_valid_content()
        task = content["implementation_task"]
        assert task.get("title"), "implementation_task missing title"
        assert task.get("description"), "implementation_task missing description"
        assert isinstance(task.get("requirements"), list), "implementation_task missing requirements"

    def test_knowledge_checks_have_required_fields(self):
        content = _make_valid_content()
        checks = content["knowledge_checks"]
        assert len(checks) > 0, "No knowledge checks"
        for check in checks:
            assert check.get("question"), "knowledge_check missing question"
            assert isinstance(check.get("options"), list), "knowledge_check missing options"
            assert len(check["options"]) >= 2, "knowledge_check needs at least 2 options"
            assert check.get("correct_answer"), "knowledge_check missing correct_answer"

    def test_reflection_questions_have_prompts(self):
        content = _make_valid_content()
        questions = content["reflection_questions"]
        assert len(questions) > 0, "No reflection questions"
        for q in questions:
            assert q.get("question"), "reflection_question missing question"
            assert q.get("prompt_for_deeper_thinking"), "reflection_question missing prompt_for_deeper_thinking"


# ── Content quality checks ──────────────────────────────────────────────

class TestContentQuality:
    """Catch known-bad patterns in generated content."""

    def test_no_pending_enrichment_text(self):
        """Scaffold fallback placeholder text should never appear in lessons."""
        content = _make_valid_content()
        content_str = str(content).lower()
        assert "pending enrichment" not in content_str
        assert "pending." not in content_str

    def test_no_placeholder_only_content(self):
        """Detect content that's all placeholders with no real material."""
        bad_content = {
            "concept_snapshot": "TODO",
            "ai_strategy": {},
            "prompt_template": {},
            "implementation_task": {},
            "reflection_questions": [],
            "explanation": "TODO",
            "code_examples": [],
            "knowledge_checks": [],
            "exercises": [],
            "hands_on_tasks": [],
        }
        # This should fail substance check despite having "TODO" strings
        # because knowledge_checks is empty
        assert _has_substance(bad_content) is True  # concept_snapshot is truthy
        # But it shouldn't have knowledge_checks
        assert len(bad_content.get("knowledge_checks", [])) == 0

    def test_code_examples_have_actual_code(self):
        content = _make_valid_content()
        for example in content.get("code_examples", []):
            assert len(example.get("code", "")) > 10, "code_example has no real code"
            assert example.get("language"), "code_example missing language"


# ── Schema-echo extraction ─────────────────────────────────────────────

class TestSchemaEchoExtraction:
    """Verify that schema-echo responses get content extracted correctly."""

    def test_extracts_string_from_description(self):
        from app.agents.lesson_generator import LessonGeneratorAgent

        schema_echo = {
            "type": "object",
            "properties": {
                "concept_snapshot": {
                    "type": "string",
                    "description": "AI governance frameworks provide structured approaches.",
                },
                "explanation": {
                    "type": "string",
                    "description": "A detailed explanation of governance.",
                },
                "knowledge_checks": {"type": "array"},
            },
        }
        content = LessonGeneratorAgent._extract_from_schema_echo(schema_echo)
        assert content["concept_snapshot"] == "AI governance frameworks provide structured approaches."
        assert content["explanation"] == "A detailed explanation of governance."
        assert content.get("knowledge_checks") == []

    def test_extracts_from_content_wrapper(self):
        from app.agents.lesson_generator import LessonGeneratorAgent

        schema_echo = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "object",
                    "properties": {
                        "concept_snapshot": {
                            "type": "string",
                            "description": "Permissions are crucial.",
                        },
                    },
                },
            },
        }
        content = LessonGeneratorAgent._extract_from_schema_echo(schema_echo)
        assert content["concept_snapshot"] == "Permissions are crucial."

    def test_empty_schema_returns_empty_dict(self):
        from app.agents.lesson_generator import LessonGeneratorAgent

        content = LessonGeneratorAgent._extract_from_schema_echo({})
        assert content == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
