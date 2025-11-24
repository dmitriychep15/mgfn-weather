"""Geo decoders HTTP communicators."""

import abc
import logging

from src.http.communicators import HTTPCommunicator
from src.models.schemas.geo.coordinates import GeoCorrdinates


logger = logging.getLogger(__name__)


class GeoDecoderHTTPCommunicator(HTTPCommunicator, abc.ABC):
    """Interface for communication with geo decoder."""

    @abc.abstractmethod
    async def get_location_name(self, coordinates: GeoCorrdinates) -> str | None:
        """
        Returns geo location's name by given coordinates
        or `None` if something went wrong.
        """
        raise NotImplementedError
