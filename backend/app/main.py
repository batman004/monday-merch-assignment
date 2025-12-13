"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine, Base
from app.utils.seed import seed_database_if_empty
from app.api.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed database if empty
    await seed_database_if_empty()
    
    yield
    
    # Shutdown: (if needed, add cleanup here)
    pass


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Include routers
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

