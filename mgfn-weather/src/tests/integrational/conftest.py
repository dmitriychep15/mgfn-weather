import datetime

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)

import backend_pre_start
from src.db.file_storages import minio
from src.db.storages.postgres import Base
from src.deps.db import get_db
from src.deps.http import get_geodecoder_http_communicator
from src.deps.weather_providers import get_weather_provider
from src.http.communicators.geodecoders import GeoDecoderHTTPCommunicator
from src.main import app
from src.core.config import settings
from src.models.schemas.weather_providers import (
    ForecastInfoSchema,
    DailyForecast,
    ForecastDayParts,
    ForecastData,
    WeatherConditionEnum,
)
from src.utils.weather_providers import AbstractWeatherProvider


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """
    Fixture to create database engine.
    Drops all tables after tests have been finished.
    """
    engine = create_async_engine(settings.DATABASE_URL.unicode_string())
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class MockWeatherProvider(AbstractWeatherProvider):
    async def get_forecast(self, coordinates):
        return ForecastInfoSchema(
            now_dt=datetime.datetime.now(),
            forecasts=[
                DailyForecast(
                    date=datetime.date.today(),
                    parts=ForecastDayParts(
                        night=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        morning=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        day=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        evening=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                    ),
                ),
                DailyForecast(
                    date=datetime.date.today() + datetime.timedelta(days=1),
                    parts=ForecastDayParts(
                        night=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        morning=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        day=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                        evening=ForecastData(
                            humidity=20,
                            pressure_mm=700,
                            temp_avg=-3,
                            feels_like=0,
                            condition=WeatherConditionEnum.clear,
                            imfBt=3,
                        ),
                    ),
                ),
            ],
        )


def get_weather_provider_mock():
    return MockWeatherProvider()


class MockGeoDecoderHTTPCommunicator(GeoDecoderHTTPCommunicator):
    """Mock for communication with geo decoder."""

    async def get_location_name(self, coordinates):
        return "Городишко"


def get_geodecoder_http_communicator_mock():
    return MockGeoDecoderHTTPCommunicator("mock_http_client")


@pytest_asyncio.fixture(scope="session")
async def client(db_engine: AsyncEngine):
    """
    Fixture to get HTTP client for FastAPI app.
    overrides some app's dependencies to test ones.
    Yields new DB session for each client's HTTP request.
    """

    async def get_db_test():
        async_session = async_sessionmaker(
            db_engine,
            autocommit=False,
            autoflush=False,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as db_session:
            yield db_session

    await backend_pre_start.main()

    minio.minio_client = await minio.init_minio(
        settings.MINIO_ADDRESS,
        settings.MINIO_ACCESS_KEY,
        settings.MINIO_SECRET_KEY,
        settings.MINIO_BUCKET,
    )
    app.dependency_overrides[get_db] = get_db_test
    app.dependency_overrides[get_weather_provider] = get_weather_provider_mock
    app.dependency_overrides[get_geodecoder_http_communicator] = (
        get_geodecoder_http_communicator_mock
    )

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://0.0.0.0:5000/api/weather"
    ) as client:
        yield client
