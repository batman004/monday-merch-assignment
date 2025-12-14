"""Pagination utilities."""

from typing import Tuple


def calculate_pagination(page: int, page_size: int) -> Tuple[int, int]:
    """
    Calculate offset and limit for pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (offset, limit)
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10  # Default page size

    offset = (page - 1) * page_size
    return offset, page_size
