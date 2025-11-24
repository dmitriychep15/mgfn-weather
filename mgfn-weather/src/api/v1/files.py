"""Files API."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from src.deps.services import get_file_service
from src.models.schemas.api_responses import file_responses

from src.services.files import FileService


files_router = APIRouter(prefix="/files", tags=["Files"])


@files_router.get(
    "/{file_id}/download",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    responses=file_responses,
)
async def download_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service),
):
    """Download the file."""
    return await file_service.api_download_file(file_id)
