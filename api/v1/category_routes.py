"""Category API routes.

This module defines FastAPI routes for category-related endpoints. It provides
read-only endpoints for retrieving film categories.

Endpoints:
    GET /api/v1/categories - Get all categories with pagination
    GET /api/v1/categories/{category_id} - Get category by ID

Example:
    ```python
    # Get all categories
    GET /api/v1/categories?skip=0&limit=10

    # Get category by ID
    GET /api/v1/categories/1
    ```
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from domain.services import CategoryService
from domain.schemas import CategoryRead
from core.dependencies import get_category_service

router = APIRouter()


@router.get("", response_model=List[CategoryRead])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    service: CategoryService = Depends(get_category_service),
) -> List[CategoryRead]:
    """
    Get all categories with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        service: Category service (injected)

    Returns:
        List of categories
    """
    return await service.get_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
) -> CategoryRead:
    """
    Get category by ID.

    Args:
        category_id: Category ID
        service: Category service (injected)

    Returns:
        Category details

    Raises:
        HTTPException: If category not found
    """
    category = await service.get_category(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category
