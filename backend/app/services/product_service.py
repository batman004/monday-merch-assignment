"""Product service - business logic layer."""

from typing import Any, Dict, List

from app.core.logging_config import logger
from app.models.domain import Category, Product
from app.utils.pagination import calculate_pagination
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_product_list(
    session: AsyncSession,
    filter_params: Dict[str, Any],
) -> tuple[List[Product], int]:
    """Get list of products with filtering, searching, and pagination."""
    logger.debug(f"Building product query with filters: {filter_params}")

    # Start building query
    query = select(Product).options(selectinload(Product.category))
    count_query = select(func.count(Product.id))

    # Apply search filter
    search_term = filter_params.get("search")
    if search_term:
        logger.debug(f"Applying search filter: {search_term}")
        search_filter = Product.title.ilike(f"%{search_term}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Apply category filter
    category_name = filter_params.get("category")
    if category_name:
        logger.debug(f"Applying category filter: {category_name}")
        # Join with Category table
        query = query.join(Category).where(Category.name == category_name)
        count_query = count_query.join(Category).where(Category.name == category_name)

    # Get total count before pagination
    result = await session.execute(count_query)
    total_count = result.scalar_one()
    logger.debug(f"Total products found: {total_count}")

    # Apply pagination
    page = filter_params.get("page", 1)
    page_size = filter_params.get("page_size", 10)
    offset, limit = calculate_pagination(page, page_size)
    logger.debug(
        f"Applying pagination: page={page}, page_size={page_size}, offset={offset}"
    )

    query = query.offset(offset).limit(limit)

    # Execute query
    result = await session.execute(query)
    products = result.scalars().all()

    logger.debug(f"Returning {len(products)} products")
    return products, total_count
