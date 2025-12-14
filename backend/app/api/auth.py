"""Authentication dependencies and utilities."""

from typing import Optional

from app.api.dependencies import get_database_session
from app.core.logging_config import logger
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
            logger.warning("Invalid JWT token: failed to decode")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            logger.warning("Invalid JWT token: missing user ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found for ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Authentication failed: inactive user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        logger.debug(f"User authenticated: {user_id}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while authenticating user",
        ) from e
