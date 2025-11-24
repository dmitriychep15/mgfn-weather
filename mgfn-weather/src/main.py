"""Main app's module."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import v1_api_router
from src.core.config import settings
from src.core.logging import configure_logging
from src.db.file_storages import minio

from src.models.schemas.api_responses import common_responses


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    minio.minio_client = await minio.init_minio(
        settings.MINIO_ADDRESS,
        settings.MINIO_ACCESS_KEY,
        settings.MINIO_SECRET_KEY,
        settings.MINIO_BUCKET,
    )
    yield


app = FastAPI(
    title="MGFN Weather",
    description="""Service, that is responsible for the weather info processing.""",
    debug=settings.DEBUG,
    responses=common_responses,
    docs_url="/swagger",
    redoc_url=None,
    root_path="/api/weather",
    lifespan=lifespan,
)
app.include_router(v1_api_router)
