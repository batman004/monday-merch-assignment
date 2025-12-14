"""Custom exception handlers."""

from app.core.logging_config import logger
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


async def database_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle database-related exceptions."""
    # Check if it's a schema migration issue
    error_message = str(exc.orig) if hasattr(exc, "orig") else str(exc)

    if (
        "no such column" in error_message.lower()
        or "no such table" in error_message.lower()
    ):
        logger.error(f"Database schema error: {error_message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Database schema is out of date. Please restart the application to apply migrations.",
                "error": "schema_migration_required",
            },
        )

    # Generic database error
    logger.error(f"Database error: {error_message}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "A database error occurred. Please try again later.",
            "error": "database_error",
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error": "internal_server_error",
        },
    )
