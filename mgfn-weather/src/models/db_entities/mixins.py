"""Common mixins for db entities' models."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped


class _IDMixin:
    """
    Mixin to set UUID identifier to entity.
    Fields to be added:
    - `id`.
    """

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        doc="DB entity record's ID",
    )


class _CreatedAtMixin:
    """
    Mixin to set creation time to entity.
    Fields to be added:
    - `created_at`.
    """

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Date and time of creating DB entity record",
    )


class IDCreatedAtMixin(_IDMixin, _CreatedAtMixin):
    """
    Mixin to set UUID identifier and creation time to entity.
    Fields to be added:
    - `id`,
    - `created_at`.
    """
