"""Schemas and  data related to cities."""

from enum import StrEnum

from pydantic import computed_field

from src.models.schemas.common import CustomBaseModel
from src.models.schemas.geo.coordinates import GeoCorrdinates


class CityEnum(StrEnum):
    """Possible cities for generating the weather forecast."""

    SAINT_PETERSBURG = "SAINT_PETERSBURG"
    MOSCOW = "MOSCOW"

    @classmethod
    def ru_names(cls) -> dict["CityEnum", str]:
        return {
            cls.SAINT_PETERSBURG: "Санкт-Петербург",
            cls.MOSCOW: "Москва",
        }

    @classmethod
    def coordinates(cls) -> dict["CityEnum", GeoCorrdinates]:
        return {
            cls.SAINT_PETERSBURG: GeoCorrdinates(
                lattitude=59.9386,
                longitude=30.3141,
            ),
            cls.MOSCOW: GeoCorrdinates(
                lattitude=55.7522,
                longitude=37.6156,
            ),
        }


class CitySchema(CustomBaseModel):
    """Schema with full city info."""

    code: CityEnum

    @computed_field
    @property
    def name(self) -> str:
        return CityEnum.ru_names()[self.code]

    @computed_field
    @property
    def coordinates(self) -> GeoCorrdinates:
        return CityEnum.coordinates()[self.code]
