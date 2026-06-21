"""Authentication API routes."""

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, settings: Settings = Depends(get_settings)):
    """Authenticate user and return JWT tokens."""
    user = await User.find_one(User.email == request.email)
    if user is None or not verify_password(request.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        settings=settings,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        settings=settings,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, settings: Settings = Depends(get_settings)):
    """Refresh an access token using a valid refresh token."""
    payload = verify_token(request.refresh_token, settings)
    if payload is None or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")

    email = payload.get("sub")
    user = await User.find_one(User.email == email)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or disabled")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        settings=settings,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        settings=settings,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        departments=user.departments,
        is_active=user.is_active,
        created_at=user.created_at,
    )
