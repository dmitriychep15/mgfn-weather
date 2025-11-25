from http import HTTPStatus
from httpx import AsyncClient

import pytest


class TestV1CitiesAPI:
    @pytest.mark.asyncio(scope="session")
    async def test_get_cities(self, client: AsyncClient):
        response = await client.get(
            "/v1/cities",
        )
        assert response.status_code == HTTPStatus.OK
