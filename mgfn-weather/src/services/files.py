"""Business logic for files and operations with them."""

import io
import typing as t
from uuid import UUID

from fastapi import status, HTTPException, Response

from src.db.file_storages.repositories import AbstractFileStorageRepository
from src.db.storages.abstract_repository import AbstractRepository
from src.models.db_entities.files import File
from src.models.schemas.api_responses import get_file_response
from src.models.schemas.files import FileCreate
from src.services import BaseService


class FileService(BaseService[File]):
    """Interface for handling operations with files."""

    not_found_msg = "Файл не найден"

    def __init__(
        self, repo: AbstractRepository, fs_repo: AbstractFileStorageRepository
    ):
        self.repo = repo
        self.fs_repo = fs_repo

    def _validate_format(
        self, filename: str, available_formats: list[str]
    ) -> None | t.NoReturn:
        """Validates file format by checking it's extension."""
        file_ext = filename.split(".")[-1]
        if file_ext not in available_formats:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Допустимые форматы файла: {', '.join(available_formats)}",
            )

    async def add_to_system(
        self,
        file: bytes,
        file_params: FileCreate,
        available_formats: list[str] | None = None,
    ) -> File | t.NoReturn:
        """Validates file and adds it to system:
        - Validates file's format if you pass formats to validate as `available_formats` attribute value;
        - Adds file to system  - creates new db File instance and uploads it to file storage.
        Returns file's DB instance. Doesn't commit db transaction!
        """
        file_io_obj = io.BytesIO(file)
        if not file_params.size:
            file_params.size = file_io_obj.getbuffer().nbytes
        if available_formats:
            self._validate_format(file_params.name, available_formats)
        new_file: File = await self.repo.create(**file_params.model_dump())
        await self.fs_repo.upload(file_io_obj, new_file.id)
        return new_file

    async def drop_from_system(self, file_id: UUID):
        """Drops db file instance and removes file from file storage.
        ! Make sure, that there is no instances, that references to this
        file instance at the moment of calling this method !
        Doesn't commmit transaction.
        """
        await self.repo.delete(file_id)
        await self.fs_repo.delete(file_id)

    async def api_download_file(self, file_id: UUID) -> Response | t.NoReturn:
        """Handles downloading file API:
        `GET: /api/weather/files/{id}/download`
        """
        file = await self.get_or_404(file_id)
        file_bytes = await self.fs_repo.get(file_id)
        file_name = file.name
        return get_file_response(file_bytes, file_name)
