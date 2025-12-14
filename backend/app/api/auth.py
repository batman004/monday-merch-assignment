"""Authentication dependencies and utilities."""

from typing import Optional

from app.api.dependencies import get_database_session
from app.core.security import decode_access_token
from app.models.domain import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

# Module-level constants for FastAPI Depends (fixes B008)
_SECURITY_DEPENDENCY = Depends(security)
_DB_SESSION_DEPENDENCY = Depends(get_database_session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = _SECURITY_DEPENDENCY,
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
) -> User:
    """Get the current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return user
    except HTTPException:
        # Re-raise HTTP exceptions (they're already properly formatted)
        raise
    except Exception as e:
        # Handle database and other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while authenticating user",
        ) from e
