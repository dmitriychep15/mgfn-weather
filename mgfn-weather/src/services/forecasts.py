"""Forecasts' business logic services."""

import logging
import typing as t
import uuid

from fastapi import Response, HTTPException, status

from src.db.storages.abstract_repository import AbstractRepository
from src.db.storages.postgres.query_models import SQLAlchemyQueryEssentials
from src.http.communicators.geodecoders import GeoDecoderHTTPCommunicator
from src.models.db_entities.forecasts import Forecast
from src.models.schemas.api_responses import get_file_response
from src.models.schemas.common import FileFormatEnum
from src.models.schemas.files import FileCreate
from src.models.schemas.forecasts import (
    ForecastRecordCreate,
    GenerateForecastParams,
    ForecastRecordOrdering,
    PaginatedForecastRecordsList,
    ForecastRecordListQueryParams,
    ForecastReportSchema,
)
from src.models.schemas.geo.coordinates import GeoCorrdinates
from src.models.schemas.geo.cities import CityEnum
from src.services import BaseService
from src.services.files import FileService
from src.utils.file_generators.forecasts import generators_by_format
from src.utils.weather_providers import AbstractWeatherProvider


logger = logging.getLogger(__name__)


class ForecastService(BaseService[Forecast]):
    """Interface for handling business opertions with forecasts."""

    not_found_msg = "Прогноз не найден"

    def __init__(
        self,
        repo: AbstractRepository,
        weather_provider: AbstractWeatherProvider,
        geodecoder: GeoDecoderHTTPCommunicator,
        file_service: FileService,
    ):
        self.repo = repo
        self.weather_provider = weather_provider
        self.geodecoder = geodecoder
        self.file_service = file_service

    async def generate(
        self,
        coordinates: GeoCorrdinates,
    ) -> Response | Forecast | t.NoReturn:
        """
        Generates a new forecast for given coordinates:
        - decodes coordinates to geo location's name;
        - generates a file with parsed forecast data and saves it to file storage and DB;
        - saves request params to DB as `Forecast` instance.
        """
        location = await self.geodecoder.get_location_name(coordinates)
        if not location:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "Невозможно распознать географический объект. Повторите запрос позже.",
            )
        forecast_rec_params = ForecastRecordCreate(
            location=location,
            lattitude=coordinates.lattitude,
            longitude=coordinates.longitude,
        )
        forecast_rec: Forecast = await self.repo.create(
            **forecast_rec_params.model_dump()
        )
        response = forecast_rec
        forecast_info = await self.weather_provider.get_forecast(coordinates)
        if forecast_info:
            forecast_report_data = ForecastReportSchema(
                location=location,
                coordinates=coordinates,
                dt=forecast_info.now_dt,
                forecasts=forecast_info.forecasts,
            )
            file_format = FileFormatEnum.XLSX
            FileGenerator = generators_by_format[file_format]
            with FileGenerator() as generator:
                file = await generator.generate(forecast_report_data)

            filename_ending = FileFormatEnum.filename_endings()[file_format]
            filename = f"Прогноз_{forecast_report_data.location}_{forecast_report_data.dt_view}{filename_ending}"

            file_instance = await self.file_service.add_to_system(
                file, FileCreate(name=filename)
            )
            forecast_rec.file_id = file_instance.id

            response = get_file_response(file, filename)
        await self.repo.save()
        return response

    async def api_generate_forecast(
        self,
        params: GenerateForecastParams,
    ) -> Response | Forecast | t.NoReturn:
        """
        Handles API on generating a new weather forecast by coordinates:
        `POST: /api/weather/forecasts`
        """
        coordinates = GeoCorrdinates.model_validate(params)
        return await self.generate(coordinates)

    async def api_generate_forecast_by_city(
        self,
        city: CityEnum,
    ) -> Response | Forecast | t.NoReturn:
        """
        Handles API on generating a new weather forecast by the specific city:
        `POST: /api/weather/forecasts/by-city/{city}`
        """
        coordinates = CityEnum.coordinates()[city]
        return await self.generate(coordinates)

    async def api_read_forecast_records(
        self,
        query_params: ForecastRecordListQueryParams,
    ) -> PaginatedForecastRecordsList | t.NoReturn:
        """
        Handles reading list of forecast records API:
        `GET: /api/weather/forecasts`
        """

        content, total_pages, total_items = await self.repo.get_paginated_list(
            SQLAlchemyQueryEssentials(
                ordering=query_params.ordering,
                order_expressions={
                    ForecastRecordOrdering.LOCATION_ASC: [
                        Forecast.location.asc(),
                        Forecast.created_at.desc(),
                    ],
                    ForecastRecordOrdering.LOCATION_DESC: [
                        Forecast.location.desc(),
                        Forecast.created_at.desc(),
                    ],
                    ForecastRecordOrdering.CREATED_AT_ASC: [Forecast.created_at.asc()],
                    ForecastRecordOrdering.CREATED_AT_DESC: [
                        Forecast.created_at.desc()
                    ],
                },
                search=query_params.search,
                search_attrs=[Forecast.location],
                page_number=query_params.page_number,
                page_size=query_params.page_size,
            )
        )
        return PaginatedForecastRecordsList(
            content=content,
            total_pages=total_pages,
            total_items=total_items,
        )

    async def api_delete_forecast_record(self, forecast_id: uuid.UUID):
        """
        Handles forecast record's deletion API:
        `DELETE: /api/weather/forecasts/{forecast_id}`
        """
        forecast = await self.get_or_404(forecast_id)
        file_id = forecast.file_id
        await self.repo.delete(forecast_id)
        if file_id:
            await self.file_service.drop_from_system(file_id)
        await self.repo.save()
