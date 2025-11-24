"""Dependency injections for communication throhg HTTP protocol."""

from fastapi import Depends
from httpx import AsyncClient

from src.http.communicators.geodecoders import GeoDecoderHTTPCommunicator
from src.http.communicators.geodecoders.openstreetmap import (
    OpenstreetmapHTTPCommunicator,
)


async def _get_async_http_client():
    """
    Returns async HTTP client.
    Don't use it directly, better use `get_*_http_communicator`
    dependency and `HTTPCommunicator`'s methods instead.
    """
    async with AsyncClient() as client:
        yield client


async def get_geodecoder_http_communicator(
    http_client: AsyncClient = Depends(_get_async_http_client),
) -> GeoDecoderHTTPCommunicator:
    """Returns geo decoder communicator."""
    return OpenstreetmapHTTPCommunicator(http_client)
