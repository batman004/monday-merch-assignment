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


class LoginRequest(BaseModel):
    """Login request schema."""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password", min_length=1)


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class OrderItemResponse(BaseModel):
    """Order item response schema."""

    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal
    product: Optional[ProductResponse] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class OrderItemRequest(BaseModel):
    """Order item request schema."""

    product_id: int = Field(..., description="Product ID", gt=0)
    quantity: int = Field(..., description="Quantity", gt=0)


class OrderRequest(BaseModel):
    """Order creation request schema."""

    items: list[OrderItemRequest] = Field(..., min_length=1, description="Order items")
    shipping_street: Optional[str] = Field(None, description="Shipping street address")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_state: Optional[str] = Field(None, description="Shipping state")
    shipping_postal_code: Optional[str] = Field(
        None, description="Shipping postal code"
    )
    shipping_country: Optional[str] = Field(None, description="Shipping country")


class OrderResponse(BaseModel):
    """Order response schema."""

    id: int
    user_id: int
    status: str
    total_amount: Decimal
    shipping_street: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    order_items: list[OrderItemResponse] = []

    class Config:
        """Pydantic configuration."""

        from_attributes = True
