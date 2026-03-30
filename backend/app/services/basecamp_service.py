"""Basecamp 4 API Service.

REST client for creating topics, todolists, and todos in Basecamp.
Uses the Basecamp 4 API: https://github.com/basecamp/bc3-api
"""
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_config():
    s = get_settings()
    return s.basecamp_account_id, s.basecamp_project_id, s.basecamp_token

# Required by Basecamp API
USER_AGENT = "AI Pathway Communication Intelligence (ali@colaberry.com)"


def _get_headers() -> dict[str, str]:
    """Build request headers with auth and user-agent."""
    _, _, token = _get_config()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }


async def _request(
    method: str, path: str, json_data: dict | None = None
) -> dict[str, Any]:
    """Make an authenticated request to Basecamp API."""
    account_id, _, _ = _get_config()
    url = f"https://3.basecampapi.com/{account_id}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method, url, headers=_get_headers(), json=json_data
        )
        if response.status_code == 429:
            logger.warning("Basecamp rate limit hit, retry after: %s", response.headers.get("Retry-After"))
            raise Exception("Basecamp rate limit exceeded")
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()


# ── Message Board (Topics) ──────────────────────────────────────────

async def get_message_board(project_id: str | None = None) -> dict:
    """Get the message board for a project."""
    pid = project_id or _get_config()[1]
    project = await _request("GET", f"/projects/{pid}.json")
    # Find the message board dock
    for dock in project.get("dock", []):
        if dock.get("name") == "message_board":
            return await _request("GET", f"/buckets/{pid}/message_boards/{dock['id']}.json")
    raise Exception("No message board found in project")


async def create_topic(
    title: str,
    content: str,
    project_id: str | None = None,
) -> str:
    """Create a new message board topic. Returns the topic ID."""
    pid = project_id or _get_config()[1]
    board = await get_message_board(pid)
    board_id = board["id"]

    result = await _request("POST", f"/buckets/{pid}/message_boards/{board_id}/messages.json", {
        "subject": title,
        "content": f"<div>{content}</div>",
        "status": "active",
    })
    topic_id = str(result["id"])
    logger.info("Created Basecamp topic: %s (ID: %s)", title, topic_id)
    return topic_id


async def append_comment(
    topic_id: str,
    content: str,
    project_id: str | None = None,
) -> str:
    """Append a comment to an existing topic. Returns comment ID."""
    pid = project_id or _get_config()[1]
    result = await _request("POST", f"/buckets/{pid}/recordings/{topic_id}/comments.json", {
        "content": f"<div>{content}</div>",
    })
    return str(result["id"])


# ── Todo Lists & Todos ──────────────────────────────────────────────

async def get_todoset(project_id: str | None = None) -> dict:
    """Get the todoset for a project."""
    pid = project_id or _get_config()[1]
    project = await _request("GET", f"/projects/{pid}.json")
    for dock in project.get("dock", []):
        if dock.get("name") == "todoset":
            return await _request("GET", f"/buckets/{pid}/todosets/{dock['id']}.json")
    raise Exception("No todoset found in project")


async def create_todo_list(
    title: str,
    description: str = "",
    project_id: str | None = None,
) -> str:
    """Create a new todo list. Returns the todolist ID."""
    pid = project_id or _get_config()[1]
    todoset = await get_todoset(pid)
    todoset_id = todoset["id"]

    result = await _request("POST", f"/buckets/{pid}/todosets/{todoset_id}/todolists.json", {
        "name": title,
        "description": description,
    })
    todolist_id = str(result["id"])
    logger.info("Created Basecamp todolist: %s (ID: %s)", title, todolist_id)
    return todolist_id


async def add_todo(
    todolist_id: str,
    content: str,
    assignee_ids: list[int] | None = None,
    project_id: str | None = None,
) -> str:
    """Add a single todo to a todolist. Returns the todo ID."""
    pid = project_id or _get_config()[1]
    payload: dict[str, Any] = {"content": content}
    if assignee_ids:
        payload["assignee_ids"] = assignee_ids

    result = await _request("POST", f"/buckets/{pid}/todolists/{todolist_id}/todos.json", payload)
    return str(result["id"])


async def add_todos(
    todolist_id: str,
    todos: list[str],
    project_id: str | None = None,
) -> list[str]:
    """Add multiple todos to a todolist. Returns list of todo IDs."""
    ids = []
    for todo in todos:
        todo_id = await add_todo(todolist_id, todo, project_id=project_id)
        ids.append(todo_id)
    return ids


# ── People ──────────────────────────────────────────────────────────

async def get_people(project_id: str | None = None) -> list[dict]:
    """Get all people in a project."""
    pid = project_id or _get_config()[1]
    return await _request("GET", f"/projects/{pid}/people.json")
