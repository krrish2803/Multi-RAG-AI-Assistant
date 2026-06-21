"""User management API routes (admin only)."""

from fastapi import APIRouter, Depends
from typing import Optional

from app.models.user import User, Role
from app.schemas import UserResponse, UserUpdateRequest
from app.api.deps import require_admin

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_users(
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
):
    """List all users (admin only)."""
    query = {}
    if role:
        query["role"] = role

    users = await User.find(query).skip(skip).limit(limit).to_list()

    return [
        UserResponse(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            departments=u.departments,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    request: UserUpdateRequest,
    admin: User = Depends(require_admin),
):
    """Update a user's role or departments (admin only)."""
    user = await User.get(user_id)
    if user is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User")

    if request.role is not None:
        user.role = request.role
    if request.departments is not None:
        user.departments = request.departments
    if request.is_active is not None:
        user.is_active = request.is_active

    await user.save()

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        departments=user.departments,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
):
    """Delete a user (admin only)."""
    user = await User.get(user_id)
    if user is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User")

    await user.delete()
    return {"message": "User deleted"}
