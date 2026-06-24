# Design (SCOPED): Third-party auth / SSO

Status: SCOPED, NOT BUILT. Strategic (external dependency + security posture) per
CLAUDE.md - requires sign-off. Captured Jun 23.

## Goal (per Ram)

Use a third-party identity provider rather than rolling our own auth. Users log
in via the provider (Okta-style), MFA available by default, and **we store no
passwords**. On login we assign the user to an organization; no content access
without login. We do not manage the credential.

## Proposed shape

1. **Identity provider:** an OIDC-compatible provider (Okta / Auth0 / similar -
   provider choice is itself a Strategic decision: paid external service).
2. **Flow:** OIDC authorization-code login -> we receive verified identity
   (email + sub) -> map to a user record -> assign to org (by email domain or
   invite) -> issue our own short-lived session token. No password ever stored.
3. **Gate:** all content routes require a valid session; anonymous access denied.
4. **MFA:** delegated to the provider; we do not implement it.

## Dependencies / ordering

- Hard pair with **multi-tenancy**: login is where org assignment happens.
- Enables **private-data** controls (an authenticated identity to attach data to).

## Why deferred

External paid dependency + security posture + new auth surface = Strategic, and
MVP is explicitly "not production / not fully secured." Do this when we move from
POC to real alpha with external users.

## Open decisions for sign-off

- Which provider (cost model).
- Org assignment policy (email-domain auto-join vs. invite-only).
- Session model (JWT vs. server session).
