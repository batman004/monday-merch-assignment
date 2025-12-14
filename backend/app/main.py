"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from app.api.routers import router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import database_exception_handler, general_exception_handler
from app.core.logging_config import logger
from app.utils.seed import seed_database_if_empty
from fastapi import FastAPI
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info("Starting application...")

    # Startup: Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.warning("Application will continue, but database may be incomplete.")

    # Seed database if empty
    try:
        await seed_database_if_empty()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        logger.warning("Application will continue, but seed data may be missing.")

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down application...")
    pass


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Register exception handlers
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello from the other side! check swagger at /docs"}


async def check_database_health() -> tuple[bool, str]:
    """Check database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False, str(e)


@app.get("/health")
async def health_check():
    """
    Health check endpoint that verifies API and database connectivity.

    Returns:
        - 200: Both API and database are healthy
        - 503: Database is unhealthy
    """
    db_healthy, db_message = await check_database_health()

    if not db_healthy:
        return JSONResponse(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "api": "ok",
                "database": "unhealthy",
                "database_error": db_message,
            },
        )

    return {
        "status": "healthy",
        "api": "ok",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
