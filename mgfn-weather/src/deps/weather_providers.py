"""Dependency injections for cross services' communication."""

import typing as t

from fastapi import Depends
from yaweather import YaWeatherAsync

from src.core.config import settings
from src.utils.weather_providers import AbstractWeatherProvider
from src.utils.weather_providers.yandex import YandexWeatherProvider


async def _get_ya_weather_client() -> t.AsyncGenerator[YaWeatherAsync, None]:
    """
    Returns client for making requests to yandex weather API.
    Do not use it directly, use `get_weather_provider` dependency instead.
    """

    async with YaWeatherAsync(api_key=settings.WEATHER_PROVIDER_API_KEY) as client:
        yield client


async def get_weather_provider(
    client: YaWeatherAsync = Depends(_get_ya_weather_client),
) -> AbstractWeatherProvider:
    """
    Returns weather provider.
    If the weather provider is gonna be changed return
    here another suitable impolementation of `AbstractWeatherProvider`.
    """
    return YandexWeatherProvider(client)
