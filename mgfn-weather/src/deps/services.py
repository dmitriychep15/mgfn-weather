"""Business logic service dependency injections for using in FastAPI routes."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.file_storages.repositories import AbstractFileStorageRepository
from src.db.storages.postgres.repositories import (
    ForecastSQLAlchemyRepository,
    FileSQLAlchemyRepository,
)
from src.deps.db import get_db, get_fs_repo
from src.deps.weather_providers import get_weather_provider
from src.deps.http import get_geodecoder_http_communicator
from src.http.communicators.geodecoders import GeoDecoderHTTPCommunicator
from src.services.files import FileService
from src.services.forecasts import ForecastService
from src.utils.weather_providers import AbstractWeatherProvider


async def get_file_service(
    db: AsyncSession = Depends(get_db),
    fs_repo: AbstractFileStorageRepository = Depends(get_fs_repo),
) -> FileService:
    """Returns file service."""
    return FileService(FileSQLAlchemyRepository(db), fs_repo)


async def get_forecast_service(
    db: AsyncSession = Depends(get_db),
    weather_provider: AbstractWeatherProvider = Depends(get_weather_provider),
    geodecoder: GeoDecoderHTTPCommunicator = Depends(get_geodecoder_http_communicator),
    file_service: FileService = Depends(get_file_service),
) -> ForecastService:
    """Returns forecast service."""
    return ForecastService(
        ForecastSQLAlchemyRepository(db),
        weather_provider,
        geodecoder,
        file_service,
    )
