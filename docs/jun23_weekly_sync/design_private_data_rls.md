# Design (SCOPED): Private-data handling + row-level security

Status: SCOPED, NOT BUILT. Strategic (security posture) per CLAUDE.md - requires
sign-off. Captured Jun 23.

## Goal (per Ram + Luda)

Define what counts as private data and how we handle it, before alpha.

## What is private data here (working definition)

- **Credentials:** never stored - delegated to the third-party IdP (see SSO doc).
- **The learner's target JD / position description:** technically public, but
  feels private to the user. Decision on the call: **we keep it.** So it must be
  handled as sensitive even though it is not legally PII.
- **Profile + progress data:** tied to an identified user; sensitive.
- Minimize collection: avoid capturing financial / regulated info; if ever
  needed, use third-party systems rather than storing it ourselves.

## Controls

1. **Row-level security (RLS):** standard DB RLS to enforce tenant + user
   isolation (Ram: "very standard in almost every database"). This is the
   enforcement layer for multi-tenancy.
2. **File storage:** if/when we store uploaded files, secure them (not immediate,
   but planned).
3. **No secrets in logs**, no PII in logs (already a CLAUDE.md rule).
4. **Retention / deletion policy:** define how long we keep the JD/profile data
   and how a user can have it removed.

## Compliance posture (Ram)

SOC 2 likely NOT needed for a learning product if we minimize/eliminate PII and
financial data and lean on third-party systems. Keep SOC 2 "in the back of the
mind" for later, not a blocker for MVP.

## Dependencies / ordering

- RLS is the enforcement half of **multi-tenancy** - build together.
- Identity comes from **SSO** - build after/with that.

## Why deferred

Security posture = Strategic. MVP is explicitly POC/not-secured. Define now (this
doc), implement with multi-tenancy + SSO.

## Open decisions for sign-off

- Data retention window for JD/profile data.
- Whether file uploads are in scope at all for alpha.
