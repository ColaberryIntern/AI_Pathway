"""Session tokens (pure). We mint our own short-lived signed token after a
successful OIDC login; we never store passwords. HS256 via PyJWT.

Pure + unit-tested: no I/O, no DB.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

_ALG = "HS256"


def issue_session(user_id: str, secret: str, ttl_hours: int = 12,
                  now: datetime | None = None) -> str:
    """Mint a signed session token for a user. `now` is injectable for tests."""
    if not secret:
        raise ValueError("session_secret is not configured")
    issued = now or datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(issued.timestamp()),
        "exp": int((issued + timedelta(hours=ttl_hours)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=_ALG)


def verify_session(token: str, secret: str) -> dict | None:
    """Return the claims dict for a valid token, or None if missing/expired/
    tampered/wrong-secret. Never raises on bad input."""
    if not token or not secret:
        return None
    try:
        return jwt.decode(token, secret, algorithms=[_ALG])
    except jwt.PyJWTError:
        return None
