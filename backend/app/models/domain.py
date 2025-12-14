"""SQLAlchemy domain models."""

from datetime import datetime

from app.core.database import Base
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class User(Base):
    """User/Customer model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)

    # Address fields
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, default="USA")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"


class Category(Base):
    """Product category model."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return string representation of Category."""
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(Base):
    """Product model."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)  # Using Decimal for precision
    inventory = Column(Integer, nullable=False, default=0)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )

    # Optional timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    category = relationship("Category", back_populates="products")
    order_items = relationship(
        "OrderItem", back_populates="product", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("inventory >= 0", name="check_inventory_non_negative"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
    )

    def __repr__(self) -> str:
        """Return string representation of Product."""
        return f"<Product(id={self.id}, title='{self.title}', price={self.price})>"


class Order(Base):
    """Order model."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        String(50), nullable=False, default="PENDING", index=True
    )  # PENDING, COMPLETED, CANCELLED
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Shipping address (snapshot at time of order)
    shipping_street = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(100), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_total_amount_non_negative"),
    )

    def __repr__(self) -> str:
        """Return string representation of Order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, status='{self.status}', total={self.total_amount})>"


class OrderItem(Base):
    """Order item model (junction table for Order-Product relationship)."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(
        Numeric(10, 2), nullable=False
    )  # Snapshot of price at time of purchase

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    # Constraints
    __table_args__ = (CheckConstraint("quantity > 0", name="check_quantity_positive"),)

    def __repr__(self) -> str:
        """Return string representation of OrderItem."""
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
