"""Provider-agnostic OIDC client (authorization-code flow).

Works with any OIDC provider (Okta / Auth0 / Cognito / Google) via the standard
discovery document, so the provider choice is configuration, not code. Off until
`is_configured()` is true. We exchange the code for tokens and read the standard
userinfo endpoint (no JWKS handling needed for MVP); we store no passwords.

External calls use httpx with an explicit timeout (Failure-First / Security
layer). Errors raise OIDCError, which the routes map to a clean 502/503.
"""
from __future__ import annotations

import httpx

from app.config import get_settings

_TIMEOUT = 15.0


class OIDCError(Exception):
    """OIDC handshake failure (discovery/token/userinfo)."""


def is_configured() -> bool:
    """True only when a provider AND a session secret are configured."""
    s = get_settings()
    return bool(
        s.oidc_enabled and s.oidc_issuer and s.oidc_client_id
        and s.oidc_client_secret and s.oidc_redirect_uri and s.session_secret
    )


async def _discover() -> dict:
    s = get_settings()
    url = s.oidc_issuer.rstrip("/") + "/.well-known/openid-configuration"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except (httpx.HTTPError, ValueError) as e:
        raise OIDCError(f"discovery failed: {e}") from e


async def build_authorize_url(state: str) -> str:
    s = get_settings()
    disc = await _discover()
    authorize = disc.get("authorization_endpoint")
    if not authorize:
        raise OIDCError("no authorization_endpoint in discovery")
    from urllib.parse import urlencode
    params = {
        "response_type": "code",
        "client_id": s.oidc_client_id,
        "redirect_uri": s.oidc_redirect_uri,
        "scope": "openid email profile",
        "state": state,
    }
    return f"{authorize}?{urlencode(params)}"


async def exchange_code_for_userinfo(code: str) -> dict:
    """Exchange an auth code for tokens, then fetch userinfo. Returns the
    userinfo dict (expects at least `email`; `name` optional)."""
    s = get_settings()
    disc = await _discover()
    token_ep = disc.get("token_endpoint")
    userinfo_ep = disc.get("userinfo_endpoint")
    if not token_ep or not userinfo_ep:
        raise OIDCError("discovery missing token/userinfo endpoint")
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            tok = await client.post(token_ep, data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": s.oidc_redirect_uri,
                "client_id": s.oidc_client_id,
                "client_secret": s.oidc_client_secret,
            }, headers={"Accept": "application/json"})
            tok.raise_for_status()
            access_token = tok.json().get("access_token")
            if not access_token:
                raise OIDCError("no access_token in token response")
            ui = await client.get(userinfo_ep, headers={
                "Authorization": f"Bearer {access_token}",
            })
            ui.raise_for_status()
            return ui.json()
    except (httpx.HTTPError, ValueError) as e:
        raise OIDCError(f"code exchange failed: {e}") from e
