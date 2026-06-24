# Design (SCOPED): Multi-tenancy - greenfield

Status: SCOPED, NOT BUILT. Strategic (DB schema + architecture) per CLAUDE.md
Autonomy Model - requires sign-off before implementation. Captured Jun 23.

## Reality check

On the call this was described as "just flip the switch." It is not: there is
**no tenant / organization / org_id model anywhere in `backend/app`**. This is a
greenfield build (confirmed by Ali). Treat accordingly.

## Goal (bare-minimum, per Luda + Ram)

A company onboards, gets its own space, and a light dashboard to **monitor who is
doing what**. Explicitly NOT SOC 2 / fully-secured - just "can we do multi-
tenancy, then harden around it."

## Proposed minimal shape

1. **`organizations` table**: id, name, domain (for email-domain join), created_at.
2. **`org_id` FK** on the user-owned entities (profile, goal, learning_path,
   etc.). Backfill existing rows to a default "Colaberry" org.
3. **Tenant scoping** at the query boundary: every read/write filters by the
   caller's org_id. Cleanest as a dependency that injects the current org and a
   helper that all repository queries go through.
4. **Light enterprise dashboard**: per-org list of learners + their path
   progress (who is doing what). Read-only for MVP.
5. **Per-tenant enterprise base curriculum**: generalize the global base
   curriculum (built this session) to per-org once orgs exist.

## Dependencies / ordering

- Pairs with **SSO / third-party auth** (separate doc): login assigns a user to
  an org.
- Pairs with **private-data / RLS** (separate doc): RLS is the enforcement layer
  for tenant isolation.

## Why deferred

DB schema redesign + cross-module dependency shift + architecture = Strategic.
Doing it half-way during a demo crunch risks the existing single-tenant flow.
Build deliberately with Gate 1 + Gate 2 coverage, after the keep-set/cleanup and
the fundraise-facing MVP are stable.

## Estimate / risk

Medium-large. Blast radius touches every user-owned model + every query. Migration
+ backfill required. Recommend a dedicated branch + full gate run.
