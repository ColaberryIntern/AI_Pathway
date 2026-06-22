"""Tests for MentorAgent with a MOCKED LLM. Covers a normal turn, the "Confused?"
path, implementation-briefing mode, the no-context boundary, and idempotency.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.agents.mentor_agent import MentorAgent  # noqa: E402


def _agent(reply="Here is some guidance.", capture=None):
    agent = MentorAgent()

    async def fake_llm(prompt, context=None, system_prompt=None, temperature=0.7):
        if capture is not None:
            capture["prompt"] = prompt
            capture["system_prompt"] = system_prompt
        return reply

    agent._call_llm = fake_llm
    return agent


def _run(c):
    return asyncio.run(c)


# --- happy path: normal turn returns a response + non-empty suggested prompts ---

def test_normal_turn():
    agent = _agent("Think about what the model sees.")
    out = _run(agent.execute({
        "message": "How do I write a better prompt?",
        "lesson_context": {"lesson_title": "Prompting", "skill_name": "Clear requests",
                           "skill_level": "L2", "concept_snapshot": "be specific"},
    }))
    assert out["response"] == "Think about what the model sees."
    assert isinstance(out["suggested_prompts"], list) and len(out["suggested_prompts"]) >= 1


# --- the "Confused?" path uses a different prompt but still returns a response ---

def test_confusion_path_builds_confusion_prompt():
    cap = {}
    agent = _agent("Let me explain with an analogy.", capture=cap)
    out = _run(agent.execute({
        "message": "",
        "confusion_context": "tokenization section",
        "lesson_context": {"lesson_title": "LLM basics"},
    }))
    assert out["response"].startswith("Let me explain")
    assert "Confused" in cap["prompt"] and "tokenization section" in cap["prompt"]


# --- implementation-briefing mode -> structured briefing, no suggested prompts ---

def test_briefing_mode():
    cap = {}
    agent = _agent("## Briefing\n...", capture=cap)
    out = _run(agent.execute({
        "mode": "implementation-briefing",
        "message": "Build a prompt-debugging workflow",
        "lesson_context": {"skill_name": "Prompt debugging", "skill_level": "L3"},
    }))
    assert out["response"].startswith("## Briefing")
    assert out["suggested_prompts"] == []
    assert cap["system_prompt"] is not None  # briefing uses its own system prompt


# --- boundary: no message / no lesson context still returns safely ---

def test_no_context_boundary():
    agent = _agent("ok")
    out = _run(agent.execute({}))
    assert out["response"] == "ok"
    assert isinstance(out["suggested_prompts"], list)


# --- idempotency ---

def test_idempotent():
    def once():
        agent = _agent("stable reply")
        out = _run(agent.execute({"message": "hi", "lesson_context": {"skill_name": "X"}}))
        return out["response"], out["suggested_prompts"]

    assert once() == once()
