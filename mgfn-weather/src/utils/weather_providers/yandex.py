"""Yandex weather provider."""

import logging

from pydantic_core import ValidationError
from yaweather import YaWeatherAsync, ResponseForecast, YaWeatherAPIError

from src.models.schemas.weather_providers import ForecastInfoSchema
from src.models.schemas.geo.coordinates import GeoCorrdinates
from src.utils.weather_providers import AbstractWeatherProvider


logger = logging.getLogger(__name__)


class YandexWeatherProvider(AbstractWeatherProvider):
    def __init__(self, client: YaWeatherAsync):
        self.client = client

    def _convert_forecast(
        self, forecast: ResponseForecast
    ) -> ForecastInfoSchema | None:
        """Converts Yandex weather response with forecast to system suitable format."""
        converted_forecast = None
        try:
            converted_forecast = ForecastInfoSchema.model_validate(forecast)
        except ValidationError as ve:
            logger.error(
                "An error occured during converting the weather forecast response to system format: %s",
                ve,
            )
        return converted_forecast

    async def _get_forecast(
        self,
        coordinates: GeoCorrdinates,
    ) -> ResponseForecast | None:
        """
        Makes forecast request to provider.
        Returns it's response or None if something goes wrong during the request.
        """

        forecast_response = None
        try:
            forecast_response = await self.client.forecast(
                (coordinates.lattitude, coordinates.longitude)
            )
        except YaWeatherAPIError as e:
            logger.error(
                "An error occured during the weather request for coordinates (lat: %s, long: %s): %s",
                coordinates.lattitude,
                coordinates.longitude,
                e,
            )
        return forecast_response

    async def get_forecast(self, coordinates):
        forecast_response = await self._get_forecast(coordinates)
        if not forecast_response:
            return
        return self._convert_forecast(forecast_response)
