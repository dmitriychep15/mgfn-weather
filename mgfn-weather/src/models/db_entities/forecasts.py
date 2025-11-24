"""Forecasts' DB models."""

import uuid

from sqlalchemy import Column, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped, relationship

from src.db.storages.postgres import Base
from src.models.db_entities.files import File
from src.models.db_entities.mixins import IDCreatedAtMixin


class Forecast(IDCreatedAtMixin, Base):
    __tablename__ = "forecasts"

    location = Column(String, nullable=False, doc="Location name")
    lattitude = Column(
        Float,
        nullable=False,
        doc="Lattitude coordinate, for which the forecast was requested.",
    )
    longitude = Column(
        Float,
        nullable=False,
        doc="Longitude coordinate, for which the forecast was requested.",
    )
    file_id: Mapped[uuid.UUID | None] = Column(
        pgUUID(as_uuid=True),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        doc="File with generated forecast report. If it's `None`, generating went wrong.",
    )
    file: Mapped[File] = relationship(lazy="selectin", doc="Forecast report's file")
