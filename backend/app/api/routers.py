"""API routers - endpoint definitions."""

from app.api.controllers import fetch_products
from app.api.dependencies import get_database_session
from app.api.serializers import ProductListResponse, ProductQuery
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1", tags=["products"])

# Module-level constants for FastAPI Depends (fixes B008)
_QUERY_PARAMS_DEPENDENCY = Depends()
_DB_SESSION_DEPENDENCY = Depends(get_database_session)


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    query_params: ProductQuery = _QUERY_PARAMS_DEPENDENCY,
    db: AsyncSession = _DB_SESSION_DEPENDENCY,
) -> ProductListResponse:
    """
    Get list of products with optional filtering and pagination.

    Query Parameters:
    - search: Optional search term for product title
    - category: Optional category name filter
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    """
    return await fetch_products(db, query_params)
