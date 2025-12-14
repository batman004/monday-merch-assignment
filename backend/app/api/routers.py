"""API routers - endpoint definitions."""

from app.api.auth import get_current_user
from app.api.controllers import authenticate_user, fetch_products
from app.api.dependencies import get_database_session
from app.api.serializers import (
    LoginRequest,
    ProductListResponse,
    ProductQuery,
    TokenResponse,
)
from app.models.domain import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1")


_QUERY_PARAMS_DEPENDENCY = Depends()
_DB_SESSION_DEPENDENCY = Depends(get_database_session)
_CURRENT_USER_DEPENDENCY = Depends(get_current_user)


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(
    login_data: LoginRequest,
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
) -> TokenResponse:
    """
    Authenticate user and return access token.

    Returns a JWT token that can be used to access protected endpoints.
    Include the token in the Authorization header as: Bearer <token>
    """
    try:
        return await authenticate_user(db, login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during authentication: {str(e)}",
        ) from e


@router.get("/products", response_model=ProductListResponse, tags=["products"])
async def get_products(
    query_params: ProductQuery = _QUERY_PARAMS_DEPENDENCY,
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
    current_user: User = _CURRENT_USER_DEPENDENCY,
) -> ProductListResponse:
    """
    Get list of products with optional filtering and pagination.

    Query Parameters:
    - search: Optional search term for product title
    - category: Optional category name filter
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    """
    try:
        return await fetch_products(db, query_params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching products: {str(e)}",
        ) from e
