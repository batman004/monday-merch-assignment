"""API controllers - HTTP orchestration layer."""
from math import ceil
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.product_service import get_product_list
from app.api.serializers import ProductListResponse, ProductQuery, ProductResponse


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
