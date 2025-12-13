"""API dependencies for dependency injection."""
from app.core.database import get_db

# Re-export get_db for use in routers
get_database_session = get_db

