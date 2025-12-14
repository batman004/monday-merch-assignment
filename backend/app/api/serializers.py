"""Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CategoryEnum(str, Enum):
    """Category enum for filtering products."""

    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    BOOKS = "Books"
    HOME_GARDEN = "Home & Garden"
    SPORTS_OUTDOORS = "Sports & Outdoors"


class CategoryResponse(BaseModel):
    """Category response schema."""

    id: int
    name: str
    slug: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ProductResponse(BaseModel):
    """Product response schema."""

    id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    inventory: int
    category_id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductQuery(BaseModel):
    """Query parameters for product list endpoint."""

    search: Optional[str] = Field(None, description="Search term for product title")
    category: Optional[CategoryEnum] = Field(
        None, description="Filter by category name"
    )
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
