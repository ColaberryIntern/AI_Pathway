"""Tests for the SSO foundation (increment 1): session tokens, email-domain ->
org assignment, and off-by-default behavior. Pure where possible; no live IdP.

Mandatory types: happy / failure / boundary / idempotency.
"""
from datetime import datetime, timedelta, timezone

from app.services.auth.org_assign import email_domain, org_id_for_email
from app.services.auth.tokens import issue_session, verify_session

SECRET = "test-secret-please-change"


# --- session tokens: happy ----------------------------------------------------

def test_issue_then_verify_roundtrip():
    tok = issue_session("user-1", SECRET, ttl_hours=12)
    claims = verify_session(tok, SECRET)
    assert claims is not None and claims["sub"] == "user-1"


# --- session tokens: failure / boundary ---------------------------------------

def test_tampered_token_rejected():
    tok = issue_session("user-1", SECRET)
    tampered = tok[:-2] + ("aa" if not tok.endswith("aa") else "bb")
    assert verify_session(tampered, SECRET) is None


def test_wrong_secret_rejected():
    tok = issue_session("user-1", SECRET)
    assert verify_session(tok, "different-secret") is None


def test_expired_token_rejected():
    past = datetime.now(timezone.utc) - timedelta(hours=48)
    tok = issue_session("user-1", SECRET, ttl_hours=1, now=past)  # exp ~47h ago
    assert verify_session(tok, SECRET) is None


def test_empty_inputs_return_none():
    assert verify_session("", SECRET) is None
    assert verify_session("anything", "") is None


def test_issue_requires_secret():
    try:
        issue_session("u", "")
        assert False, "expected ValueError"
    except ValueError:
        pass


# --- session tokens: idempotency ----------------------------------------------

def test_verify_idempotent():
    tok = issue_session("user-1", SECRET, now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    a = verify_session(tok, SECRET)
    b = verify_session(tok, SECRET)
    assert a == b


# --- email_domain -------------------------------------------------------------

def test_email_domain_basic():
    assert email_domain("Jane@Acme.COM") == "acme.com"


def test_email_domain_invalid():
    assert email_domain(None) is None
    assert email_domain("not-an-email") is None
    assert email_domain("") is None


# --- org_id_for_email: happy / failure / boundary -----------------------------

D2O = {"acme.com": "org-acme", "globex.io": "org-globex"}


def test_domain_match_assigns_org():
    assert org_id_for_email("a@acme.com", D2O) == "org-acme"


def test_domain_match_case_insensitive():
    assert org_id_for_email("A@ACME.COM", {"Acme.com": "org-acme"}) == "org-acme"


def test_no_domain_match_falls_back_to_default():
    assert org_id_for_email("a@unknown.com", D2O) == "default-org"


def test_bad_email_falls_back_to_default():
    assert org_id_for_email(None, D2O) == "default-org"
    assert org_id_for_email("garbage", D2O) == "default-org"


def test_custom_default_org():
    assert org_id_for_email("a@unknown.com", D2O, default_org_id="fallback") == "fallback"


# --- off by default -----------------------------------------------------------

def test_oidc_disabled_by_default():
    # No OIDC env configured in the test environment -> not configured.
    from app.services.auth import oidc
    assert oidc.is_configured() is False
