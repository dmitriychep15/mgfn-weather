"""Pydantic schemas for data related to weather forecasts."""

import datetime
import uuid
from copy import deepcopy
from enum import StrEnum

from fastapi import Query
from pydantic import Field, computed_field

from src.models.schemas.api_responses import file_responses
from src.models.schemas.common import (
    CustomBaseModel,
    PaginatedListQueryParams,
    PaginatedList,
)
from src.models.schemas.files import FileSchema
from src.models.schemas.geo.coordinates import (
    GeoCorrdinates,
    LatitudeType,
    LongitudeType,
)
from src.models.schemas.weather_providers import DailyForecast


class ForecastRequestStatusEnum(StrEnum):
    """Possible forecast request's statuses."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    @classmethod
    def ru_names(cls) -> dict["ForecastRequestStatusEnum", str]:
        return {
            cls.SUCCESS: "Успешно",
            cls.FAILED: "Ошибка",
        }


class ForecastRequestStatusSchema(CustomBaseModel):
    """Schema for weather forecast reques status output with it's code and name for user."""

    code: ForecastRequestStatusEnum

    @computed_field
    @property
    def name(self) -> str:
        return ForecastRequestStatusEnum.ru_names()[self.code]


class GenerateForecastParams(CustomBaseModel):
    """Params for generating a new weather forecast."""

    lattitude: LatitudeType
    longitude: LongitudeType


class ForecastRecordCreate(CustomBaseModel):
    """Params for creating a new forecast record in DB."""

    location: str
    lattitude: LatitudeType
    longitude: LongitudeType
    file_id: uuid.UUID | None = Field(None)


class ForecastRecordSchema(CustomBaseModel):
    """Schema fro showing forecast record."""

    id: uuid.UUID
    location: str
    lattitude: float
    longitude: float
    created_at: datetime.datetime
    file: FileSchema | None

    @computed_field
    @property
    def status(self) -> ForecastRequestStatusSchema:
        """Indicates, whether the request was successful or not."""
        status = ForecastRequestStatusEnum.FAILED
        if self.file:
            status = ForecastRequestStatusEnum.SUCCESS
        return ForecastRequestStatusSchema(code=status)


generate_forecast_responses = deepcopy(file_responses)
generate_forecast_responses[200]["content"]["application/json"] = {
    "schema": ForecastRecordSchema.model_json_schema(
        ref_template="#/components/schemas/{model}"
    ),
}


class ForecastRecordOrdering(StrEnum):
    """Possible orderings for forecast records."""

    LOCATION_ASC = "location"
    LOCATION_DESC = "-location"
    CREATED_AT_ASC = "created_at"
    CREATED_AT_DESC = "-created_at"


class PaginatedForecastRecordsList(PaginatedList):
    """Forecast records' paginated list output"""

    content: list[ForecastRecordSchema]


class ForecastRecordListQueryParams(PaginatedListQueryParams):
    """Query params for reading forecast records"""

    ordering: ForecastRecordOrdering = Field(
        Query(ForecastRecordOrdering.CREATED_AT_DESC)
    )
    search: str | None = Field(Query(None, description="Search by `location` field"))


class ForecastReportSchema(CustomBaseModel):
    """Schema with data, required for generating weather forecast report."""

    location: str
    coordinates: GeoCorrdinates
    dt: datetime.datetime
    forecasts: list[DailyForecast]

    @computed_field
    @property
    def dt_view(self) -> str:
        return self.get_datetime_view(self.dt)
