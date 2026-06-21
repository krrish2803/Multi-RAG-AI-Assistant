"""User and Role models for MongoDB using Beanie."""

from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class Role(str, Enum):
    """User roles for RBAC."""
    EMPLOYEE = "employee"
    HR = "hr"
    FINANCE = "finance"
    MARKETING = "marketing"
    ENGINEERING = "engineering"
    EXECUTIVE = "executive"
    ADMIN = "admin"


class User(Document):
    """User document with role-based access control."""

    email: Indexed(str, unique=True)
    hashed_password: str
    full_name: str
    role: Role = Role.EMPLOYEE
    departments: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@company.com",
                "full_name": "John Doe",
                "role": "employee",
                "departments": ["engineering"],
            }
        }
