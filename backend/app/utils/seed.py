"""Database seeding utilities."""

import json
from decimal import Decimal
from pathlib import Path

from app.core.database import AsyncSessionLocal
from app.models.domain import Category, Product
from sqlalchemy import select


def load_seed_data():
    """Load seed data from JSON file."""
    seed_file = Path(__file__).parent / "seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_database_if_empty():
    """Seed the database with sample data if it's empty."""
    async with AsyncSessionLocal() as session:
        # Check if any products exist
        result = await session.execute(select(Product).limit(1))
        existing_product = result.scalar_one_or_none()

        if existing_product:
            print("Database already contains data, skipping seed.")
            return

        print("Database is empty, seeding with sample data...")

        # Load seed data from JSON
        seed_data = load_seed_data()
        categories_data = seed_data["categories"]
        products_data = seed_data["products"]

        # Seed categories
        categories = {}
        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)
            categories[cat_data["name"]] = category

        await session.flush()  # Flush to get category IDs

        # Seed products
        for product_data in products_data:
            category_name = product_data.pop("category")
            category = categories[category_name]

            # Convert price string to Decimal
            product_data["price"] = Decimal(product_data["price"])

            product = Product(**product_data, category_id=category.id)
            session.add(product)

        await session.commit()
        print(
            f"Seeded database with {len(categories_data)} categories and {len(products_data)} products."
        )
