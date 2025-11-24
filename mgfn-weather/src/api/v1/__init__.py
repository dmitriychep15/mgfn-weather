"""API routers version 1."""

from fastapi import APIRouter

from src.api.v1.cities import cities_router
from src.api.v1.files import files_router
from src.api.v1.forecasts import forecasts_router


v1_api_router = APIRouter(prefix="/v1")
v1_api_router.include_router(forecasts_router)
v1_api_router.include_router(cities_router)
v1_api_router.include_router(files_router)
