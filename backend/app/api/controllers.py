"""API controllers - HTTP orchestration layer."""

from datetime import timedelta
from math import ceil
from typing import Any, Dict

from app.api.serializers import (
    LoginRequest,
    OrderRequest,
    OrderResponse,
    ProductListResponse,
    ProductQuery,
    ProductResponse,
    TokenResponse,
)
from app.core.config import settings
from app.core.logging_config import logger
from app.core.security import create_access_token, verify_password
from app.models.domain import Order, User
from app.services.order_service import create_order, get_user_orders
from app.services.product_service import get_product_list
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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
    logger.debug(
        f"Fetching products with filters: search={params.search}, category={params.category}, page={params.page}, page_size={params.page_size}"
    )

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

    logger.info(f"Fetched {len(products)} products (total: {total_count})")

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
    logger.info(f"Authentication attempt for email: {login_data.email}")

    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            f"Authentication failed: user not found for email {login_data.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Authentication failed: invalid password for user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Authentication failed: inactive user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    logger.info(f"Authentication successful for user {user.id}")
    return TokenResponse(access_token=access_token, token_type="bearer")


async def create_user_order(
    db: AsyncSession,
    user: User,
    order_data: OrderRequest,
) -> OrderResponse:
    """
    Create an order for the current user.

    Args:
        db: Database session
        user: Current authenticated user
        order_data: Order creation data

    Returns:
        OrderResponse with created order

    Raises:
        HTTPException: If order creation fails
    """
    logger.info(f"Creating order for user {user.id}")

    try:
        # Prepare items for service
        items = [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in order_data.items
        ]

        # Prepare shipping address (use user's address if not provided)
        shipping_address = {
            "shipping_street": order_data.shipping_street or user.street_address,
            "shipping_city": order_data.shipping_city or user.city,
            "shipping_state": order_data.shipping_state or user.state,
            "shipping_postal_code": order_data.shipping_postal_code or user.postal_code,
            "shipping_country": order_data.shipping_country or user.country or "USA",
        }

        # Create order via service
        order, _ = await create_order(db, user, items, shipping_address)
        await db.commit()

        # Reload order with relationships
        from app.models.domain import OrderItem, Product

        result = await db.execute(
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.order_items)
                .selectinload(OrderItem.product)
                .selectinload(Product.category)
            )
        )
        order = result.scalar_one()

        logger.info(f"Order {order.id} created successfully for user {user.id}")
        return OrderResponse.model_validate(order)

    except ValueError as e:
        logger.warning(f"Order creation failed: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the order",
        ) from e


async def fetch_user_orders(
    db: AsyncSession,
    user: User,
) -> list[OrderResponse]:
    """
    Fetch all orders for the current user.

    Args:
        db: Database session
        user: Current authenticated user

    Returns:
        List of OrderResponse
    """
    logger.debug(f"Fetching orders for user {user.id}")
    orders = await get_user_orders(db, user.id)
    return [OrderResponse.model_validate(order) for order in orders]
