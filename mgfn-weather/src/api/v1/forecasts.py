"""REST API for forecasts."""

import uuid

from fastapi import Depends, APIRouter, status

from src.deps.services import get_forecast_service

from src.models.schemas.forecasts import (
    ForecastRecordSchema,
    PaginatedForecastRecordsList,
    ForecastRecordListQueryParams,
    GenerateForecastParams,
    generate_forecast_responses,
)
from src.models.schemas.geo.cities import CityEnum
from src.services.forecasts import ForecastService


forecasts_router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@forecasts_router.get(
    "",
    response_model=PaginatedForecastRecordsList,
)
async def read_forecast_records(
    query_params: ForecastRecordListQueryParams = Depends(),
    forecast_service: ForecastService = Depends(get_forecast_service),
):
    """Read paginated list of forecasts."""

    return await forecast_service.api_read_forecast_records(query_params)


@forecasts_router.post(
    "",
    response_model=ForecastRecordSchema,
    responses=generate_forecast_responses,
    status_code=status.HTTP_201_CREATED,
    description="Generate a new weather forecast for given coordinates.\n"
    "Behavior description:\n"
    "\n"
    "| Response format |                       Behavior                        |\n"
    "|----------------:|:------------------------------------------------------|\n"
    "|     JSON        | Forecast report generating was failed and saved in DB |\n"
    "|     File        | Successfull report generation                         |\n",
)
async def generate_forecast(
    params: GenerateForecastParams,
    forecast_service: ForecastService = Depends(get_forecast_service),
):
    """
    Generate a new weather forecast for given coordinates.
    Request data will be saved in DB as a new record.
    """
    return await forecast_service.api_generate_forecast(params)


@forecasts_router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast_record(
    forecast_id: uuid.UUID,
    forecast_service: ForecastService = Depends(get_forecast_service),
):
    """Delete forecast record."""

    await forecast_service.api_delete_forecast_record(forecast_id)


@forecasts_router.post(
    "/by-city/{city}",
    response_model=ForecastRecordSchema,
    responses=generate_forecast_responses,
    status_code=status.HTTP_201_CREATED,
    description="Generate a new weather forecast for given city.\n"
    "Behavior description:\n"
    "\n"
    "| Response format |                       Behavior                        |\n"
    "|----------------:|:------------------------------------------------------|\n"
    "|     JSON        | Forecast report generating was failed and saved in DB |\n"
    "|     File        | Successfull report generation                         |\n",
)
async def generate_forecast_by_city(
    city: CityEnum,
    forecast_service: ForecastService = Depends(get_forecast_service),
):
    """
    Generate a new weather forecast for given city.
    Request data will be saved in DB as a new record.
    """
    return await forecast_service.api_generate_forecast_by_city(city)
