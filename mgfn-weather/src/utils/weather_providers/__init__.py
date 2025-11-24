"""The weather providers."""

import abc

from src.models.schemas.weather_providers import ForecastInfoSchema
from src.models.schemas.geo.coordinates import GeoCorrdinates


class AbstractWeatherProvider(abc.ABC):
    """
    Abstract interface for communication
    with the weather provider.
    """

    @abc.abstractmethod
    async def get_forecast(
        self, coordinates: GeoCorrdinates
    ) -> ForecastInfoSchema | None:
        """
        ! Keep in mind, that calling this method might affect your requests' limit set by specific weather provider !
        Requests the forecast by given coordinates and returns it in system suitable format.
        Returns `None` in case something goes wrong during request,
        because it's neccessary to save the results of forecast request to DB anyway.
        """
        raise NotImplementedError
