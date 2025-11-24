"""REST API for cities."""

from fastapi import APIRouter

from src.models.schemas.geo.cities import CityEnum, CitySchema


cities_router = APIRouter(prefix="/cities", tags=["Cities"])


@cities_router.get("", response_model=list[CitySchema])
async def read_cities():
    """
    Read list of cities with known geo coordinates
    to generate a forecast by just using specific city.
    The list is ordered by the city name in alphabetical order.
    """
    return sorted(
        (CitySchema(code=city_code) for city_code in CityEnum),
        key=lambda city: city.name,
    )
