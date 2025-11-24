"""Schemas for files."""

import uuid
from datetime import datetime

from pydantic import Field

from src.models.schemas.common import CustomBaseModel


class FileCreate(CustomBaseModel):
    """Schema for creating new file."""

    name: str = Field(min_length=1, max_length=256)
    size: int = Field(
        default=0,
        description="""
        File's size in bytes.
        You can define the file's size directly here, or it would be set in file_service, when adding the file to system.
        """,
    )


class FileSchema(CustomBaseModel):
    """Schema with full file fields."""

    id: uuid.UUID
    name: str
    size: int = Field(description="File's size in bytes.")
    created_at: datetime
