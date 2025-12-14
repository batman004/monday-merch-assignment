"""API controllers - HTTP orchestration layer."""

from datetime import timedelta
from math import ceil
from typing import Any, Dict

from app.api.serializers import (
    LoginRequest,
    ProductListResponse,
    ProductQuery,
    ProductResponse,
    TokenResponse,
)
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.domain import User
from app.services.product_service import get_product_list
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_products(
    db: AsyncSession,
    params: ProductQuery,
) -> ProductListResponse:
    """
    Fetch products with filtering and pagination.

    Args:
        db: Database session
        params: Query parameters

    Returns:
        ProductListResponse with paginated results
    """
    # Convert Pydantic model to dict for service layer
    filter_params: Dict[str, Any] = {
        "search": params.search,
        "category": params.category.value if params.category else None,
        "page": params.page,
        "page_size": params.page_size,
    }

    # Call service layer
    products, total_count = await get_product_list(db, filter_params)

    # Calculate total pages
    total_pages = ceil(total_count / params.page_size) if total_count > 0 else 0

    # Convert to response models
    product_responses = [
        ProductResponse.model_validate(product) for product in products
    ]

    return ProductListResponse(
        products=product_responses,
        total=total_count,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )


async def authenticate_user(
    db: AsyncSession,
    login_data: LoginRequest,
) -> TokenResponse:
    """
    Authenticate user and return access token.

    Args:
        db: Database session
        login_data: Login credentials

    Returns:
        TokenResponse with access token

    Raises:
        HTTPException: If authentication fails
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return TokenResponse(access_token=access_token, token_type="bearer")
