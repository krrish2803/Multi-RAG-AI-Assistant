"""API dependency injection utilities."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import Settings, get_settings
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> User:
    """Decode JWT and return the current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token, settings)

    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    email = payload.get("sub")
    if email is None:
        raise AuthenticationError("Invalid token payload")

    user = await User.find_one(User.email == email)
    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is disabled")

    return user


def require_role(*roles: str):
    """Factory that returns a dependency enforcing specific roles."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise AuthorizationError(
                f"Role '{user.role}' is not authorized. Required: {', '.join(roles)}"
            )
        return user

    return _check


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if user.role.value != "admin":
        raise AuthorizationError("Admin access required")
    return user
