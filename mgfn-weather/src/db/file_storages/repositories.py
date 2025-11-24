"""Repositories for handling file stoages' operations."""

import abc
import io
import logging
import typing as t
from uuid import UUID

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from fastapi import status, HTTPException
from miniopy_async import Minio
from miniopy_async.error import S3Error

from src.core.config import settings


class AbstractFileStorageRepository(abc.ABC):
    """Abstract interface for handling file stoages' operations."""

    @abc.abstractmethod
    async def upload(self, *args, **kwargs) -> None | t.NoReturn:
        """Upload file to storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, *args, **kwargs) -> bytes | t.NoReturn:
        """Get file from storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, *args, **kwargs) -> None | t.NoReturn:
        """Delete file from storage."""
        raise NotImplementedError


class MinioRepository(AbstractFileStorageRepository):
    """Interface for handling Minio file storage's operations."""

    def __init__(self, client: Minio, client_session: ClientSession):
        self.client = client
        self.bucket_name = settings.MINIO_BUCKET
        self.client_session = client_session

    async def upload(self, file_io_obj: io.BytesIO, file_id: UUID) -> None | t.NoReturn:
        try:
            file_io_obj.__sizeof__()
            await self.client.put_object(
                self.bucket_name,
                file_id.hex,
                file_io_obj,
                file_io_obj.getbuffer().nbytes,
            )
        except (ConnectionError, S3Error, ClientConnectorError) as e:
            self._handle_error(e)

    async def get(self, file_id: UUID) -> bytes | t.NoReturn:
        try:
            response: ClientResponse = await self.client.get_object(
                self.bucket_name, file_id.hex, self.client_session
            )
            if not response.status == status.HTTP_200_OK:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "Файл в хранилище не найден"
                )
            return await response.read()
        except (ConnectionError, S3Error, ClientConnectorError) as e:
            self._handle_error(e)

    async def delete(self, file_id: UUID) -> None | t.NoReturn:
        try:
            await self.client.remove_object(self.bucket_name, file_id.hex)
        except (ConnectionError, S3Error, ClientConnectorError) as e:
            self._handle_error(e)

    def _handle_error(self, error: ConnectionError | S3Error | ClientConnectorError):
        """
        Handles errors:
        - logs the error,
        - raises HTTPException.
        """
        log_msg = f"ERROR connecting to  Minio file storage: {error}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        response_detail = "Файловое хранилище недоступно, повторите запрос позже."
        if isinstance(error, S3Error):
            log_msg = f"ERROR handling Minio file storage: {error}"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_detail = "Ошибка работы с файловым хранилищем."
        logging.error(log_msg)
        raise HTTPException(status_code, response_detail)
