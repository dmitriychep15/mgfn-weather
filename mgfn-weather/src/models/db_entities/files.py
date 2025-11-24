"""Files db enities."""

from sqlalchemy import Column, String, BigInteger

from src.db.storages.postgres import Base
from src.models.db_entities.mixins import IDCreatedAtMixin


class File(IDCreatedAtMixin, Base):
    __tablename__ = "files"

    name = Column(String, nullable=False, doc="File's name")
    size = Column(BigInteger, nullable=False, doc="File's size in bytes")
