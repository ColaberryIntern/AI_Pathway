# AI Pathway - MVP Definition (Jun 23 weekly sync)

Owner: Luda. Captured from the Jun 23 weekly sync. This is the shared definition
of what "MVP" means right now, used to align engineering with the fundraise.

## Framing

We are raising **pre-seed**. The MVP is what Luda shows VCs and prospective
enterprises. It is explicitly a **POC / MVP, not production and not fully
secured**. We do not promise security or production-readiness at this stage; we
show capability and direction.

## Two-step definition

### Step 1 - "It is software for enterprises, not just individuals"

The tool today reads as B2C. The MVP must visibly spell **enterprise** so a
company feels it is for them. Minimum:

- Ability to load an **enterprise base curriculum** (the skills everyone in the
  org must know) as a base, with **personalized pathways layered on top** so
  every served path includes the base. (Built this session - MVP: one global
  base set + admin UI. Per-tenant comes with multi-tenancy.)
- A light way to **monitor who is doing what** (a basic enterprise dashboard).
  (Comes with multi-tenancy - scoped, deferred.)

This is what Luda demonstrates to VCs and to pilot enterprises (e.g. Women
Applying AI as the first enterprise-like pilot).

### Step 2 - Alpha-ready

The bar for putting the tool in front of **alpha testers** (real users clicking
through it themselves, not just watching a screen-share):

1. **Chapter content done** - the generated chapters are good enough to stand on
   their own, validated by the breadth+depth judge (built this session) and the
   existing QA council.
2. **Cleanup done** - ontology bloat and code remnants removed so the product is
   coherent (audit delivered this session; prune pending Luda/Vivek).
3. **Private-data handling defined** - what counts as private data and how we
   handle it (scoped this session; third-party auth + RLS).

## Where this stands after the Jun 23 session

| MVP element | Status |
|---|---|
| Enterprise base curriculum (Step 1) | Built (MVP: global base + admin UI) |
| Users walk through chapters themselves (Step 2 enabler) | Built (path-wide Prev/Next) |
| Chapter content quality judge (Step 2.1) | Built (breadth+depth judge + rubric) |
| Cleanup (Step 2.2) | Audit delivered; prune pending owners |
| Private-data handling (Step 2.3) | Scoped (design doc); not built |
| Enterprise monitoring dashboard (Step 1) | Scoped with multi-tenancy; not built |
| Multi-tenancy / SSO | Scoped (greenfield); not built |

## Out of scope for MVP (explicitly)

- SOC 2 / full security hardening.
- Production SLAs.
- Full enterprise admin functionality beyond "show what it is / can be."

## Parallel track (Luda, non-engineering)

- Women Applying AI pilot (define tracks: base / intermediate / financial;
  pricing) - first pilot and data source.
- Letters of intent from a couple of enterprises + warming up VCs/angels.
- Recruit more technical testers (define the categories).
