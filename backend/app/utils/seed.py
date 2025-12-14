"""Database seeding utilities."""

import json
from decimal import Decimal
from pathlib import Path

from app.core.database import AsyncSessionLocal
from app.core.logging_config import logger
from app.core.security import get_password_hash
from app.models.domain import Category, Product, User
from sqlalchemy import select


def load_seed_data():
    """Load seed data from JSON file."""
    seed_file = Path(__file__).parent / "seed_data.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_database_if_empty():
    """Seed the database with sample data if it's empty."""
    try:
        async with AsyncSessionLocal() as session:
            # Check if any products exist
            result = await session.execute(select(Product).limit(1))
            existing_product = result.scalar_one_or_none()

            if existing_product:
                logger.info("Database already contains data, skipping seed.")
                return

            logger.info("Database is empty, seeding with sample data...")

            # Load seed data from JSON
            seed_data = load_seed_data()
            categories_data = seed_data.get("categories", [])
            products_data = seed_data.get("products", [])
            users_data = seed_data.get("users", [])

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

            # Seed users
            users_created = 0
            user_credentials = []
            for user_data in users_data:
                try:
                    # Make a copy to preserve original data for logging
                    user_data_copy = user_data.copy()
                    # Extract password and hash it
                    password = user_data.pop("password")
                    user_data["password_hash"] = get_password_hash(password)

                    # Create user with all required fields
                    user = User(**user_data)
                    session.add(user)
                    users_created += 1
                    user_credentials.append((user_data_copy["email"], password))
                    logger.debug(f"User created: {user_data_copy['email']}")
                except Exception as e:
                    logger.warning(
                        f"Failed to create user {user_data.get('email', 'unknown')}: {e}"
                    )
                    logger.warning("Continuing with remaining users...")

            await session.commit()
            logger.info(
                f"Seeded database with {len(categories_data)} categories, "
                f"{len(products_data)} products, and {users_created} users."
            )
            if user_credentials:
                logger.info("Sample user credentials:")
                for email, password in user_credentials:
                    logger.info(f"  - {email} / {password}")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        logger.warning("Application will continue, but database may be incomplete.")
