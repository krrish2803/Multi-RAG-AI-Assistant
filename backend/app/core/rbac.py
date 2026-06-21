"""Role-Based Access Control (RBAC) implementation.

This module defines the role-to-department access matrix and provides
functions to build Qdrant filters for retrieval-time authorization.
"""

from typing import Optional

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchAny,
)

from app.models.user import Role


# Role -> Department access matrix
# Each role can access documents from these departments
ROLE_ACCESS_MATRIX: dict[str, list[str]] = {
    Role.EMPLOYEE: ["company-wide"],
    Role.HR: ["company-wide", "hr"],
    Role.FINANCE: ["company-wide", "finance"],
    Role.MARKETING: ["company-wide", "marketing"],
    Role.ENGINEERING: ["company-wide", "engineering"],
    Role.EXECUTIVE: ["company-wide", "hr", "finance", "marketing", "engineering"],
    Role.ADMIN: ["company-wide", "hr", "finance", "marketing", "engineering"],
}

# Sensitivity access by role
SENSITIVITY_ACCESS: dict[str, list[str]] = {
    Role.EMPLOYEE: ["public", "internal"],
    Role.HR: ["public", "internal", "confidential"],
    Role.FINANCE: ["public", "internal", "confidential"],
    Role.ENGINEERING: ["public", "internal", "confidential"],
    Role.MARKETING: ["public", "internal"],
    Role.EXECUTIVE: ["public", "internal", "confidential", "restricted"],
    Role.ADMIN: ["public", "internal", "confidential", "restricted"],
}

# Roles that can perform admin actions
ADMIN_ROLES = [Role.ADMIN]
MANAGEMENT_ROLES = [Role.ADMIN, Role.EXECUTIVE]


def get_accessible_departments(user_role: str, user_departments: Optional[list[str]] = None) -> list[str]:
    """Get list of departments accessible to a user based on their role."""
    base_departments = ROLE_ACCESS_MATRIX.get(user_role, ["company-wide"])
    if user_departments:
        # Union of role-based access and explicit department assignments
        base_departments = list(set(base_departments) | set(user_departments))
    return base_departments


def get_accessible_sensitivity(user_role: str) -> list[str]:
    """Get list of sensitivity levels accessible to a user based on their role."""
    return SENSITIVITY_ACCESS.get(user_role, ["public"])


def build_qdrant_filter(
    user_role: str,
    user_departments: Optional[list[str]] = None,
) -> Filter:
    """Build a Qdrant Filter object for RBAC-enforced retrieval.
    
    This filter ensures that vector search only returns document chunks
    that the user is authorized to access based on their role.
    """
    accessible_depts = get_accessible_departments(user_role, user_departments)
    accessible_sensitivity = get_accessible_sensitivity(user_role)

    return Filter(
        must=[
            FieldCondition(
                key="department",
                match=MatchAny(any=accessible_depts),
            ),
            FieldCondition(
                key="sensitivity",
                match=MatchAny(any=accessible_sensitivity),
            ),
        ]
    )


def check_role_permission(user_role: str, required_roles: list[str]) -> bool:
    """Check if a user role has permission for an action."""
    return user_role in required_roles


def is_admin(user_role: str) -> bool:
    """Check if user has admin privileges."""
    return user_role in ADMIN_ROLES
