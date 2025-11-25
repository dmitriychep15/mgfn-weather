"""Pydantic schemas for data related to weather providers."""

import datetime
from enum import StrEnum

from pydantic import Field, computed_field

from src.models.schemas.common import CustomBaseModel, weekdays_ru_aliases


class WeatherConditionEnum(StrEnum):
    """Possible weather conditions."""

    clear = "clear"
    partly_cloudy = "partly-cloudy"
    cloudy = "cloudy"
    overcast = "overcast"
    light_rain = "light-rain"
    rain = "rain"
    heavy_rain = "heavy-rain"
    showers = "showers"
    wet_snow = "wet-snow"
    light_snow = "light-snow"
    snow = "snow"
    snow_showers = "snow-showers"
    hail = "hail"
    thunderstorm = "thunderstorm"
    thunderstorm_with_rain = "thunderstorm-with-rain"
    thunderstorm_with_hail = "thunderstorm-with-hail"

    @classmethod
    def ru_names(cls) -> dict["WeatherConditionEnum", str]:
        return {
            cls.clear: "Ясно",
            cls.partly_cloudy: "Малооблачно",
            cls.cloudy: "Облачно с прояснениями",
            cls.overcast: "Пасмурно",
            cls.light_rain: "Небольшой дождь",
            cls.rain: "Дождь",
            cls.heavy_rain: "Сильный дождь",
            cls.showers: "Ливень",
            cls.wet_snow: "Дождь со снегом",
            cls.light_snow: "Небольшой снег",
            cls.snow: "Снег",
            cls.snow_showers: "Снегопад",
            cls.hail: "Град",
            cls.thunderstorm: "Гроза",
            cls.thunderstorm_with_rain: "Дождь с грозой",
            cls.thunderstorm_with_hail: "Гроза с градом",
        }


class WeatherConditionSchema(CustomBaseModel):
    """Schema for weather condition output with it's code and name for user."""

    code: WeatherConditionEnum

    @computed_field
    @property
    def name(self) -> str:
        return WeatherConditionEnum.ru_names()[self.code]


class ForecastData(CustomBaseModel):
    """System's suitable weather parameters from forecast."""

    humidity: float
    pressure_mm: int
    temp_avg: float
    feels_like: float | None = Field(
        default=None,
        description="This parameter is not so important. So, if it wasn't received from weather provider, whatever...",
    )
    imfBt: float | None = Field(
        default=None,
        description="Magnetic field, nTl. Available not for all provider's usage rates.",
    )
    input_condition: WeatherConditionEnum | None = Field(
        default=None, alias="condition"
    )

    @computed_field
    @property
    def condition(self) -> WeatherConditionSchema | None:
        if not self.input_condition:
            return
        return WeatherConditionSchema(code=self.input_condition)

    @computed_field
    @property
    def temp_avg_view(self) -> str:
        return self.get_temp_view(self.temp_avg)

    @computed_field
    @property
    def feels_like_view(self) -> str:
        if not self.feels_like:
            return "-"
        return self.get_temp_view(self.feels_like)


class ForecastDayParts(CustomBaseModel):
    """Forecast for one day, splitted by day parts."""

    night: ForecastData = Field(description="Nighttime forecast")
    morning: ForecastData = Field(description="Morning forecast")
    day: ForecastData = Field(description="Afternoon forecast")
    evening: ForecastData = Field(description="Evening forecast")


class DailyForecast(CustomBaseModel):
    """System's suitable weather forecast for one day."""

    date: datetime.date
    parts: ForecastDayParts

    @computed_field
    @property
    def date_view(self) -> str:
        """Forecast's date in user readable format."""
        return self.get_date_view(self.date)

    @computed_field
    @property
    def weekday(self) -> str:
        """Forecast date's weekday in user readable format."""
        return weekdays_ru_aliases.get(self.date.weekday(), "")

    @computed_field
    @property
    def daylight_avg_temp_view(self) -> str:
        """Dailight (morning, day, evening) average temperature, °C"""
        avg_temp = (
            self.parts.morning.temp_avg
            + self.parts.day.temp_avg
            + self.parts.evening.temp_avg
        ) / 3
        return self.get_temp_view(avg_temp)

    @computed_field
    @property
    def pressure_comment(self) -> str:
        """
        Comment, if there is a sharp increase/decrease
        in atmospheric pressure >= 5 mm during the day.
        """
        pressures = [
            self.parts.night.pressure_mm,
            self.parts.morning.pressure_mm,
            self.parts.day.pressure_mm,
            self.parts.evening.pressure_mm,
        ]

        min_p = min(pressures)
        max_p = max(pressures)
        diff = max_p - min_p
        if diff < 5:
            return ""

        if pressures.index(min_p) < pressures.index(max_p):
            return "Ожидается резкое увеличение атмосферного давления!"
        return "Ожидается резкое падение атмосферного давления!"


class ForecastInfoSchema(CustomBaseModel):
    """
    System's suitable weather forecast info.
    Convert the specific provider's response to this schema.
    """

    now_dt: datetime.datetime
    forecasts: list[DailyForecast]
