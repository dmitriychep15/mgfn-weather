"""Openstreetmap Geo decoder HTTP communicator."""

import typing as t
import logging
from json import JSONDecodeError

from httpx import ConnectError, TimeoutException
from fastapi import status

from src.http.communicators.geodecoders import GeoDecoderHTTPCommunicator


logger = logging.getLogger(__name__)


class OpenstreetmapHTTPCommunicator(GeoDecoderHTTPCommunicator):
    """Interface for communication with Openstreetmap geo decoder."""

    service_url = "https://nominatim.openstreetmap.org"

    async def get_location_name(self, coordinates):
        try:
            response = await self.http_client.get(
                f"{self.service_url}/reverse",
                params={
                    "lat": coordinates.lattitude,
                    "lon": coordinates.longitude,
                    "format": "json",
                    "accept-language": "ru",
                },
                headers={
                    "User-Agent": "mgfn-weather",
                },
            )
        except (ConnectError, TimeoutException) as ce:
            logger.error(
                "Can't decode coordinates (%s, %s): openstreetmap geodecoder service is unavailable: %s",
                coordinates.lattitude,
                coordinates.longitude,
                ce,
            )
            return
        if response.status_code != status.HTTP_200_OK:
            logger.error(
                "Error decoding coordinates (%s, %s): %s - %s",
                coordinates.lattitude,
                coordinates.longitude,
                response.status_code,
                response.text,
            )
            return
        try:
            json_response: dict[str, t.Any] = response.json()
        except JSONDecodeError as jde:
            logger.error(
                "Can't decode coordinates (%s, %s): openstreetmap response is not JSON serializable: %s",
                coordinates.lattitude,
                coordinates.longitude,
                jde,
            )
            return
        location_name = json_response.get("display_name", None)
        if location_name is None:
            logger.error(
                "Can't decode coordinates (%s, %s): there is no `display_name` field in openstreetmap response",
                coordinates.lattitude,
                coordinates.longitude,
            )
        return location_name
