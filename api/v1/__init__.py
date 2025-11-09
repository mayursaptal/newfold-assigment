"""API v1 routes registration.

This module registers all API v1 route modules into a single router.
All routes are prefixed with their resource name and tagged for
organization in the OpenAPI documentation.

Routes:
    - /films - Film CRUD operations
    - /rentals - Rental CRUD operations
    - /customers - Customer rental operations
    - /categories - Category read operations
    - /ai - AI-powered endpoints (chat, summaries)
"""

from fastapi import APIRouter
from api.v1 import film_routes, rental_routes, ai_routes, customer_routes, category_routes

router = APIRouter()

router.include_router(film_routes.router, prefix="/films", tags=["films"])
router.include_router(rental_routes.router, prefix="/rentals", tags=["rentals"])
router.include_router(customer_routes.router, prefix="/customers", tags=["customers"])
router.include_router(category_routes.router, prefix="/categories", tags=["categories"])
router.include_router(ai_routes.router, prefix="/ai", tags=["ai"])

