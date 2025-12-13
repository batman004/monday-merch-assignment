from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.controllers import fetch_products
from app.api.serializers import ProductQuery, ProductListResponse
from app.api.dependencies import get_database_session

router = APIRouter(prefix="/api/v1", tags=["products"])


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    query_params: ProductQuery = Depends(),
    db: AsyncSession = Depends(get_database_session),
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

