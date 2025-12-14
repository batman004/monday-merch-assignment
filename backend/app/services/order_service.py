"""Order service - business logic layer."""

from decimal import Decimal
from typing import List, Tuple

from app.models.domain import Order, OrderItem, Product, User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def create_order(
    session: AsyncSession,
    user: User,
    items: List[dict],
    shipping_address: dict,
) -> Tuple[Order, List[OrderItem]]:
    """
    Create an order with order items.

    Args:
        session: Database session
        user: User creating the order
        items: List of items with product_id and quantity
        shipping_address: Shipping address dictionary

    Returns:
        Tuple of (Order, List[OrderItem])

    Raises:
        ValueError: If product not found, insufficient inventory, or invalid data
    """
    logger.debug(f"Creating order for user {user.id} with {len(items)} items")

    # Fetch all products in one query
    product_ids = [item["product_id"] for item in items]
    result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
    products = {product.id: product for product in result.scalars().all()}

    # Validate products exist and check inventory
    order_items = []
    total_amount = Decimal("0.00")

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        if product_id not in products:
            raise ValueError(f"Product with ID {product_id} not found")

        product = products[product_id]

        if product.inventory < quantity:
            raise ValueError(
                f"Insufficient inventory for product {product.title}. "
                f"Available: {product.inventory}, Requested: {quantity}"
            )

        # Calculate item total
        item_total = product.price * quantity
        total_amount += item_total

        # Create order item (will be added to order later)
        order_items.append(
            {
                "product": product,
                "quantity": quantity,
                "price_at_purchase": product.price,
            }
        )

    # Create order
    order = Order(
        user_id=user.id,
        status="PENDING",
        total_amount=total_amount,
        shipping_street=shipping_address.get("shipping_street"),
        shipping_city=shipping_address.get("shipping_city"),
        shipping_state=shipping_address.get("shipping_state"),
        shipping_postal_code=shipping_address.get("shipping_postal_code"),
        shipping_country=shipping_address.get("shipping_country") or "USA",
    )
    session.add(order)
    await session.flush()  # Get order ID

    # Create order items and update inventory
    created_order_items = []
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price_at_purchase=item_data["price_at_purchase"],
        )
        session.add(order_item)
        created_order_items.append(order_item)

        # Update product inventory
        item_data["product"].inventory -= item_data["quantity"]

    logger.info(
        f"Order {order.id} created for user {user.id} with total ${total_amount}"
    )
    return order, created_order_items


async def get_user_orders(
    session: AsyncSession,
    user_id: int,
) -> List[Order]:
    """
    Get all orders for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of Order objects with order_items loaded
    """
    logger.debug(f"Fetching orders for user {user_id}")
    result = await session.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.order_items)
            .selectinload(OrderItem.product)
            .selectinload(Product.category)
        )
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    logger.debug(f"Found {len(orders)} orders for user {user_id}")
    return orders
