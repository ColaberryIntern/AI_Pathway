"""Content Curator Agent - Finds and curates learning resources."""
import asyncio
import json
from app.agents.base import BaseAgent


class ContentCuratorAgent(BaseAgent):
    """Agent for finding and curating external learning resources."""

    name = "ContentCuratorAgent"
    description = "Finds and curates relevant learning resources for each skill"

    system_prompt = """You are an expert learning resource curator specializing in AI/ML education.
Your task is to recommend high-quality learning resources for specific skills and topics.

For each skill, recommend resources that:
1. Match the target proficiency level
2. Are relevant to the user's industry
3. Come from reputable sources
4. Provide practical, hands-on learning
5. Are current and up-to-date

Include a mix of:
- Articles and blog posts
- Video tutorials
- Interactive courses
- Documentation
- Practice projects"""

    async def execute(self, task: dict) -> dict:
        """Curate learning resources for chapters.

        Args:
            task: {
                "chapters": list - Generated chapters
                "industry": str - User's industry
            }

        Returns:
            {
                "chapter_resources": list - Resources for each chapter
            }
        """
        self._start_execution()

        chapters = task.get("chapters", [])
        industry = task.get("industry", "")

        # Process all chapters in parallel for better performance
        resource_results = await asyncio.gather(
            *[self._curate_for_chapter(chapter, industry) for chapter in chapters]
        )
        chapter_resources = [
            {
                "chapter_number": chapter.get("chapter_number"),
                "skill_id": chapter.get("skill_id"),
                "resources": resources,
            }
            for chapter, resources in zip(chapters, resource_results)
        ]

        result = {"chapter_resources": chapter_resources}

        self._log_execution("curate_content", task, result)
        result["duration_ms"] = self._end_execution()

        return result

    async def _curate_for_chapter(self, chapter: dict, industry: str) -> list:
        """Curate resources for a single chapter."""
        skill_name = chapter.get("skill_name", "")
        skill_id = chapter.get("skill_id", "")
        target_level = chapter.get("target_level", 2)

        # Try to get content from RAG first
        rag_content = await self.rag.retrieve_learning_content(skill_id, industry)

        prompt = f"""Recommend learning resources for this skill.

SKILL: {skill_name}
SKILL ID: {skill_id}
TARGET LEVEL: {target_level}
INDUSTRY: {industry or 'General'}

CHAPTER TITLE: {chapter.get('title', '')}
LEARNING OBJECTIVES:
{json.dumps(chapter.get('learning_objectives', []), indent=2)}

Recommend 4-6 high-quality resources including:
1. At least one video tutorial
2. At least one article or documentation
3. At least one hands-on tutorial or course
4. Industry-specific resources if applicable

Focus on reputable sources like:
- Official documentation (OpenAI, Anthropic, Hugging Face)
- Educational platforms (Coursera, deeplearning.ai, fast.ai)
- Tech blogs (Towards Data Science, AI blogs)
- YouTube channels (3Blue1Brown, Andrej Karpathy, etc.)"""

        output_schema = {
            "type": "object",
            "properties": {
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["article", "video", "tutorial", "documentation", "course", "tool"]
                            },
                            "source": {"type": "string"},
                            "description": {"type": "string"},
                            "difficulty_level": {"type": "string"},
                            "estimated_time": {"type": "string"}
                        }
                    }
                }
            }
        }

        result = await self._call_llm_structured(prompt, output_schema)
        return result.get("resources", [])
