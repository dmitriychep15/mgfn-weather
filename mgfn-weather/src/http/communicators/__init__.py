"""HTTP communicators."""

import abc

from httpx import AsyncClient


class HTTPCommunicator(abc.ABC):
    """Abstract interface for communication using HTTP protocol."""

    service_url: str

    def __init__(self, http_client: AsyncClient):
        self.http_client = http_client
