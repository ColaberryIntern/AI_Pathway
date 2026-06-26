"""Auth / SSO routes (multi-tenancy increment 2 foundation).

  GET  /api/auth/status    -> {"enabled": bool}  (frontend asks before showing login)
  GET  /api/auth/login     -> 302 to the IdP (503 when not configured)
  GET  /api/auth/callback  -> exchange code, find/create user, assign org by email
                              domain, mint a session cookie, redirect into the app
  GET  /api/auth/me        -> the current user (or null) from the session cookie
  POST /api/auth/logout    -> clear the session cookie

OFF by default: when no provider is configured, login/callback return 503 and
the rest of the app keeps working without auth. No existing route is gated yet
(enforcement is the next increment).
"""
from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_database
from app.config import get_settings
from app.models.organization import Organization
from app.models.user import User
from app.services.auth import oidc
from app.services.auth.org_assign import org_id_for_email
from app.services.auth.tokens import issue_session

logger = logging.getLogger(__name__)
router = APIRouter()

SESSION_COOKIE = "ai_pathway_session"
_STATE_COOKIE = "ai_pathway_oidc_state"


@router.get("/status")
async def auth_status():
    return {"enabled": oidc.is_configured()}


@router.get("/login")
async def login():
    if not oidc.is_configured():
        return JSONResponse(status_code=503, content={"error": "SSO not configured"})
    state = secrets.token_urlsafe(24)
    try:
        url = await oidc.build_authorize_url(state)
    except oidc.OIDCError as e:
        logger.warning("oidc_login_failed", extra={"error": str(e)})
        return JSONResponse(status_code=502, content={"error": "identity provider unavailable"})
    resp = RedirectResponse(url, status_code=302)
    resp.set_cookie(_STATE_COOKIE, state, httponly=True, samesite="lax", max_age=600)
    return resp


@router.get("/callback")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: AsyncSession = Depends(get_database),
):
    if not oidc.is_configured():
        return JSONResponse(status_code=503, content={"error": "SSO not configured"})
    # CSRF: the state we set on /login must come back unchanged.
    expected = request.cookies.get(_STATE_COOKIE)
    if not code or not state or not expected or state != expected:
        return JSONResponse(status_code=400, content={"error": "invalid state or code"})

    try:
        userinfo = await oidc.exchange_code_for_userinfo(code)
    except oidc.OIDCError as e:
        logger.warning("oidc_callback_failed", extra={"error": str(e)})
        return JSONResponse(status_code=502, content={"error": "identity provider error"})

    email = (userinfo.get("email") or "").strip().lower()
    name = userinfo.get("name") or userinfo.get("given_name")
    if not email:
        return JSONResponse(status_code=400, content={"error": "no email from provider"})

    # Find or create the user by email.
    user = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if not user:
        user = User(email=email, name=name)
        db.add(user)

    # Assign org by email domain (falls back to default).
    orgs = (await db.execute(select(Organization))).scalars().all()
    domain_to_org = {o.domain.strip().lower(): o.id for o in orgs if o.domain}
    user.org_id = org_id_for_email(email, domain_to_org)
    await db.commit()
    await db.refresh(user)

    s = get_settings()
    token = issue_session(user.id, s.session_secret, s.session_ttl_hours)
    resp = RedirectResponse(s.oidc_post_login_redirect, status_code=302)
    resp.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax",
                    max_age=s.session_ttl_hours * 3600)
    resp.delete_cookie(_STATE_COOKIE)
    return resp


@router.get("/me")
async def me(request: Request, db: AsyncSession = Depends(get_database)):
    from app.services.auth.tokens import verify_session
    s = get_settings()
    token = request.cookies.get(SESSION_COOKIE)
    claims = verify_session(token, s.session_secret) if token else None
    if not claims:
        return {"user": None}
    user = (await db.execute(select(User).where(User.id == claims["sub"]))).scalars().first()
    if not user:
        return {"user": None}
    return {"user": {"id": user.id, "email": user.email, "name": user.name, "org_id": user.org_id}}


@router.post("/logout")
async def logout():
    resp = JSONResponse(content={"ok": True})
    resp.delete_cookie(SESSION_COOKIE)
    return resp
