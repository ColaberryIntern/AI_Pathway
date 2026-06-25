"""Organization model (multi-tenancy, increment 1).

The tenant root. A User belongs to at most one Organization (User.org_id).
For MVP the org is used to group learners for the enterprise "who is doing
what" dashboard; full per-entity row scoping + request enforcement land with
auth (increment 2). See docs/jun23_weekly_sync/design_multitenancy.md.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

DEFAULT_ORG_ID = "default-org"
DEFAULT_ORG_NAME = "Colaberry (default)"


class Organization(Base):
    """A tenant. Learners (Users) are grouped under an organization."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Email domain used to auto-assign members once SSO lands; optional for MVP.
    domain: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
