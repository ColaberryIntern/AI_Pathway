"""User schemas."""
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a user."""

    email: EmailStr | None = None
    name: str | None = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    name: str | None = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str
    email: str | None
    name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
