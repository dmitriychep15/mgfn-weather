"""
Service pre start checks:
- Check connection to Postres DB,
- Check connection to Yandex weather API.
"""

import asyncio
import logging
from http import HTTPStatus

import httpx
from miniopy_async import Minio
from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.config import settings
from src.db.storages.postgres import async_session


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 2


async def check_postgres_connection() -> None:
    """Checks Postgres DB availability."""

    logger.info("Checking if database %s is available...", settings.POSTGRES_SERVER)
    async with async_session() as session:
        await session.execute(text("SELECT 1;"))
    logger.info("SUCCESS - database is available")


async def check_minio_connection() -> None:
    logging.info("Checking if file storage %s is available...", settings.MINIO_ADDRESS)
    minio_client = Minio(
        endpoint=settings.MINIO_ADDRESS,
        secure=False,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
    )
    await minio_client.bucket_exists(settings.MINIO_BUCKET)
    logging.info("SUCCESS - file storage is available")


async def check_yandex_weather_connection() -> None:
    """Checks Yandex weather service availability."""

    logger.info("Checking if weather service is available...")
    async with httpx.AsyncClient() as client:
        response = await client.get(url="https://api.weather.yandex.ru/v2/forecast")
        if response.status_code != HTTPStatus.FORBIDDEN:
            logger.warning(
                "Ping weather service results: status code: %s, body: %s",
                response.status_code,
                response.text,
            )
            raise Exception("Weather API service is unavailable")

    logger.info("SUCCESS - weather service is available")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        await check_postgres_connection()
        await check_minio_connection()
        await check_yandex_weather_connection()
    except Exception as e:
        logger.error("Error initializing service: %s", str(e))
        raise


async def main():
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
