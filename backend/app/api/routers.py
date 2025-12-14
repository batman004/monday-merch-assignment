"""API routers - endpoint definitions."""

from app.api.auth import get_current_user
from app.api.controllers import (
    authenticate_user,
    create_user_order,
    fetch_products,
    fetch_user_orders,
)
from app.api.dependencies import get_database_session
from app.api.serializers import (
    LoginRequest,
    OrderRequest,
    OrderResponse,
    ProductListResponse,
    ProductQuery,
    TokenResponse,
)
from app.core.logging_config import logger
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
        logger.error(f"Unexpected error in login endpoint: {e}", exc_info=True)
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
    logger.info(f"Products endpoint accessed by user {current_user.id}")
    try:
        return await fetch_products(db, query_params)
    except Exception as e:
        logger.error(f"Unexpected error in products endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching products: {str(e)}",
        ) from e


@router.post("/orders", response_model=OrderResponse, tags=["orders"])
async def create_order(
    order_data: OrderRequest,
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
    current_user: User = _CURRENT_USER_DEPENDENCY,
) -> OrderResponse:
    """
    Create a new order for the current user.

    The order will use the user's address if shipping address is not provided.
    """
    logger.info(f"Order creation requested by user {current_user.id}")
    try:
        return await create_user_order(db, current_user, order_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the order",
        ) from e


@router.get("/orders", response_model=list[OrderResponse], tags=["orders"])
async def get_orders(
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
    current_user: User = _CURRENT_USER_DEPENDENCY,
) -> list[OrderResponse]:
    """Get all orders for the current user."""
    logger.info(f"Fetching orders for user {current_user.id}")
    try:
        return await fetch_user_orders(db, current_user)
    except Exception as e:
        logger.error(f"Unexpected error fetching orders: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching orders",
        ) from e
