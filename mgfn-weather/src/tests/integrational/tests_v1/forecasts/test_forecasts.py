import pytest
from http import HTTPStatus
from httpx import AsyncClient

from src.models.schemas.geo.cities import CityEnum
from src.models.schemas.forecasts import GenerateForecastParams


class TestV1ForecastsAPI:
    @pytest.mark.asyncio(scope="session")
    async def test_generate_forecast_by_city(self, client: AsyncClient):
        response = await client.post(
            f"/v1/forecasts/by-city/{CityEnum.SAINT_PETERSBURG.value}",
        )
        assert response.status_code == HTTPStatus.CREATED

    @pytest.mark.asyncio(scope="session")
    async def test_generate_forecast(self, client: AsyncClient):
        response = await client.post(
            "/v1/forecasts",
            json=GenerateForecastParams(
                lattitude=50.0331,
                longitude=30.7632,
            ).model_dump(),
        )
        assert response.status_code == HTTPStatus.CREATED
