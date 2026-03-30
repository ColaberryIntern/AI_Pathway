"""Email Ingestion Service - Gmail API integration.

Fetches emails from specific senders, normalizes, and stores
in the database for processing by the intelligence pipeline.
"""
import base64
import logging
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_thread import EmailThread

logger = logging.getLogger(__name__)

# Senders to monitor
MONITORED_SENDERS = [
    "vivmuk@gmail.com",
    "ludakopeikina@gmail.com",
]


def _build_gmail_service():
    """Build Gmail API service using stored credentials."""
    import os
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials/gmail_credentials.json")
    token_path = os.getenv("GMAIL_TOKEN_PATH", "credentials/gmail_token.json")
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _extract_email_data(msg: dict) -> dict:
    """Extract normalized fields from a Gmail message."""
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Decode body
    body = ""
    payload = msg.get("payload", {})
    if "body" in payload and payload["body"].get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    elif "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break

    # Parse timestamp
    timestamp = datetime.utcnow()
    if "date" in headers:
        try:
            timestamp = parsedate_to_datetime(headers["date"])
        except Exception:
            pass

    return {
        "thread_id": msg.get("threadId", ""),
        "message_id": msg.get("id", ""),
        "sender": headers.get("from", ""),
        "recipients": [r.strip() for r in headers.get("to", "").split(",") if r.strip()],
        "subject": headers.get("subject", "(no subject)"),
        "body": body,
        "timestamp": timestamp,
        "raw_payload": msg,
    }


async def fetch_new_emails(
    db: AsyncSession,
    lookback_hours: int = 24,
) -> list[EmailThread]:
    """Fetch new emails from monitored senders and store in DB.

    Returns the list of newly created EmailThread records.
    """
    service = _build_gmail_service()

    # Build query for monitored senders
    sender_query = " OR ".join(f"from:{s}" for s in MONITORED_SENDERS)
    after = datetime.utcnow() - timedelta(hours=lookback_hours)
    after_epoch = int(after.timestamp())
    query = f"({sender_query}) after:{after_epoch}"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=50
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        logger.info("No new emails from monitored senders")
        return []

    new_threads = []
    for msg_ref in messages:
        msg_id = msg_ref["id"]

        # Check if already ingested
        existing = await db.execute(
            select(EmailThread).where(EmailThread.message_id == msg_id)
        )
        if existing.scalars().first():
            continue

        # Fetch full message
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        data = _extract_email_data(msg)
        thread = EmailThread(
            thread_id=data["thread_id"],
            message_id=data["message_id"],
            sender=data["sender"],
            recipients=data["recipients"],
            subject=data["subject"],
            body=data["body"],
            timestamp=data["timestamp"],
            processed=False,
            skipped=False,
            raw_payload=data["raw_payload"],
        )
        db.add(thread)
        new_threads.append(thread)

    if new_threads:
        await db.commit()
        logger.info("Ingested %d new emails", len(new_threads))

    return new_threads


async def get_unprocessed(db: AsyncSession) -> list[EmailThread]:
    """Get all unprocessed email threads."""
    result = await db.execute(
        select(EmailThread)
        .where(EmailThread.processed == False, EmailThread.skipped == False)
        .order_by(EmailThread.timestamp.asc())
    )
    return list(result.scalars().all())
