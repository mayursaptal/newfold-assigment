"""API v1 routes."""

from fastapi import APIRouter
from api.v1 import film_routes, rental_routes, ai_routes

router = APIRouter()

router.include_router(film_routes.router, prefix="/films", tags=["films"])
router.include_router(rental_routes.router, prefix="/rentals", tags=["rentals"])
router.include_router(ai_routes.router, prefix="/ai", tags=["ai"])

