"""Dependency injections for getting DB connections."""

import typing as t

from aiohttp import ClientSession
from fastapi import Depends
from miniopy_async import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.file_storages import minio
from src.db.file_storages.repositories import (
    AbstractFileStorageRepository,
    MinioRepository,
)
from src.db.storages.postgres import async_session


async def get_db() -> t.AsyncGenerator[AsyncSession, t.Any]:
    """Returns DB storage connection."""
    async with async_session() as session:
        yield session


def get_fs() -> Minio:
    """Returns File storage client."""
    return minio.minio_client


async def get_fs_conn() -> t.AsyncGenerator[ClientSession, None]:
    """Returns file storage connection."""
    async with ClientSession() as session:
        yield session


async def get_fs_repo(
    fs: Minio = Depends(get_fs),
    session: ClientSession = Depends(get_fs_conn),
) -> AbstractFileStorageRepository:
    """Returns file storage repository."""
    return MinioRepository(fs, session)
