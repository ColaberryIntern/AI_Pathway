"""Email-domain -> organization assignment (pure).

On SSO login a user is assigned to the org whose `domain` matches their email
domain; otherwise the default org. This is the concrete link between auth and
multi-tenancy. Pure + unit-tested.
"""
from __future__ import annotations

from app.models.organization import DEFAULT_ORG_ID


def email_domain(email: str | None) -> str | None:
    """Lowercased domain part of an email, or None if not a valid-looking email."""
    if not email or "@" not in email:
        return None
    domain = email.rsplit("@", 1)[1].strip().lower()
    return domain or None


def org_id_for_email(
    email: str | None,
    domain_to_org: dict[str, str],
    default_org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Resolve the org for an email by domain, falling back to the default org.

    `domain_to_org` maps lowercased domain -> org_id. Matching is case-insensitive.
    """
    domain = email_domain(email)
    if domain:
        normalized = {(k or "").strip().lower(): v for k, v in domain_to_org.items()}
        if domain in normalized:
            return normalized[domain]
    return default_org_id
