"""AI Mentor API routes — conversational learning assistant."""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_database
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.mentor_conversation import MentorConversation
from app.agents.mentor_agent import MentorAgent
from app.schemas.mentor import (
    MentorChatRequest,
    MentorChatResponse,
    MentorMessage,
    MentorHistoryResponse,
)

router = APIRouter()


@router.post("/{path_id}/mentor/chat", response_model=MentorChatResponse)
async def mentor_chat(
    path_id: str,
    request: MentorChatRequest,
    db: AsyncSession = Depends(get_database),
):
    """Send a message to the AI mentor and get a contextual response.

    If lesson_id is provided, the mentor gets lesson context (concept, skill, level).
    Conversation history is loaded from the database.
    """
    # Build lesson context if lesson_id provided
    lesson_context = {}
    if request.lesson_id:
        lesson = await db.get(Lesson, request.lesson_id)
        if lesson:
            module = await db.get(Module, lesson.module_id)
            content = lesson.content or {}
            lesson_context = {
                "lesson_title": lesson.title,
                "skill_name": module.skill_name if module else "",
                "skill_level": f"L{module.current_level} → L{module.target_level}" if module else "",
                "concept_snapshot": content.get("concept_snapshot", content.get("explanation", "")[:200]),
            }

    # Find or create conversation
    conv_query = select(MentorConversation).where(
        MentorConversation.path_id == path_id,
    )
    if request.lesson_id:
        conv_query = conv_query.where(MentorConversation.lesson_id == request.lesson_id)
    else:
        conv_query = conv_query.where(MentorConversation.lesson_id.is_(None))

    result = await db.execute(conv_query.order_by(MentorConversation.updated_at.desc()).limit(1))
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = MentorConversation(
            user_id="default_user",  # TODO: replace with auth
            path_id=path_id,
            lesson_id=request.lesson_id,
            messages=[],
        )
        db.add(conversation)
        await db.flush()

    # Get existing messages
    messages = conversation.messages or []

    # Add user message
    now = datetime.utcnow().isoformat()
    messages.append({"role": "user", "content": request.message, "timestamp": now})

    # Call MentorAgent
    agent = MentorAgent()
    agent_result = await agent.execute({
        "message": request.message,
        "conversation_history": messages,
        "lesson_context": lesson_context,
    })

    # Add mentor response
    mentor_response = agent_result.get("response", "I'm here to help! Could you tell me more about what you're working on?")
    messages.append({"role": "mentor", "content": mentor_response, "timestamp": datetime.utcnow().isoformat()})

    # Save conversation
    conversation.messages = messages
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conversation)

    return MentorChatResponse(
        response=mentor_response,
        suggested_prompts=agent_result.get("suggested_prompts", []),
        conversation_id=conversation.id,
    )


@router.get("/{path_id}/mentor/history", response_model=MentorHistoryResponse)
async def get_mentor_history(
    path_id: str,
    lesson_id: str | None = None,
    db: AsyncSession = Depends(get_database),
):
    """Get mentor conversation history."""
    conv_query = select(MentorConversation).where(
        MentorConversation.path_id == path_id,
    )
    if lesson_id:
        conv_query = conv_query.where(MentorConversation.lesson_id == lesson_id)
    else:
        conv_query = conv_query.where(MentorConversation.lesson_id.is_(None))

    result = await db.execute(conv_query.order_by(MentorConversation.updated_at.desc()).limit(1))
    conversation = result.scalar_one_or_none()

    if not conversation:
        return MentorHistoryResponse(conversation_id="", messages=[])

    messages = [
        MentorMessage(
            role=m.get("role", "user"),
            content=m.get("content", ""),
            timestamp=m.get("timestamp", ""),
        )
        for m in (conversation.messages or [])
    ]

    return MentorHistoryResponse(
        conversation_id=conversation.id,
        messages=messages,
    )
