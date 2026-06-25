"""Organization admin API (multi-tenancy increment 1).

  POST /api/admin/organizations/                    create an org
  GET  /api/admin/organizations/                    list orgs + member counts
  PUT  /api/admin/organizations/{org_id}/members    assign a user to the org
  GET  /api/admin/organizations/{org_id}/dashboard  the org's learners + progress

No request-level auth yet (SSO deferred). These are admin endpoints; org-scoped
enforcement on the learner-facing routes lands with auth (increment 2).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_database
from app.models.learning_path import LearningPath
from app.models.organization import Organization
from app.models.profile import Profile
from app.models.progress import Progress
from app.models.user import User
from app.schemas.organization import (
    AssignMemberRequest,
    LearnerSummary,
    OrgDashboardResponse,
    OrganizationCreate,
    OrganizationResponse,
)
from app.services.organization_service import summarize_learner_paths

router = APIRouter()


async def _member_count(db: AsyncSession, org_id: str) -> int:
    return (await db.execute(
        select(func.count()).select_from(User).where(User.org_id == org_id)
    )).scalar() or 0


def _org_response(org: Organization, member_count: int) -> OrganizationResponse:
    return OrganizationResponse(
        id=org.id, name=org.name, domain=org.domain,
        created_at=org.created_at.isoformat(), member_count=member_count,
    )


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    body: OrganizationCreate,
    db: AsyncSession = Depends(get_database),
):
    org = Organization(name=body.name, domain=body.domain)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return _org_response(org, 0)


@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(db: AsyncSession = Depends(get_database)):
    orgs = (await db.execute(
        select(Organization).order_by(Organization.created_at)
    )).scalars().all()
    out = []
    for org in orgs:
        out.append(_org_response(org, await _member_count(db, org.id)))
    return out


@router.put("/{org_id}/members", response_model=OrganizationResponse)
async def assign_member(
    org_id: str,
    body: AssignMemberRequest,
    db: AsyncSession = Depends(get_database),
):
    """Move a user into this org. Validates both org and user exist."""
    org = (await db.execute(
        select(Organization).where(Organization.id == org_id)
    )).scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="organization not found")
    user = (await db.execute(
        select(User).where(User.id == body.user_id)
    )).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    user.org_id = org_id
    await db.commit()
    return _org_response(org, await _member_count(db, org_id))


@router.get("/{org_id}/dashboard", response_model=OrgDashboardResponse)
async def org_dashboard(org_id: str, db: AsyncSession = Depends(get_database)):
    """List the org's learners with each learner's path-progress summary."""
    org = (await db.execute(
        select(Organization).where(Organization.id == org_id)
    )).scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="organization not found")

    users = (await db.execute(
        select(User).where(User.org_id == org_id)
    )).scalars().all()

    learners: list[LearnerSummary] = []
    for user in users:
        paths = (await db.execute(
            select(LearningPath).where(LearningPath.user_id == user.id)
        )).scalars().all()
        progress_by_path: dict = {}
        for p in paths:
            progress_by_path[p.id] = (await db.execute(
                select(Progress).where(Progress.path_id == p.id)
            )).scalars().first()
        summary = summarize_learner_paths(paths, progress_by_path)

        # Best-effort display name from the user's most recent profile.
        prof = (await db.execute(
            select(Profile).where(Profile.user_id == user.id)
        )).scalars().first()
        display_name = user.name
        if not display_name and prof and isinstance(prof.profile_data, dict):
            display_name = prof.profile_data.get("name")

        learners.append(LearnerSummary(
            user_id=user.id, name=display_name, email=user.email, **summary,
        ))

    return OrgDashboardResponse(
        org_id=org.id, org_name=org.name,
        learner_count=len(learners), learners=learners,
    )
