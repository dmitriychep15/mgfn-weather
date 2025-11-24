"""Modules with business logic."""

import abc
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm.strategy_options import _AbstractLoad

from src.db.storages.abstract_repository import AbstractRepository


class BaseService[DBModel](abc.ABC):
    """Base service with common logic."""

    repo: AbstractRepository
    not_found_msg: str = "Не найдено"  # Redefine this messsage in each specific service

    async def get_or_404(
        self,
        entity_id: UUID | str | None = None,
        relationships_to_load: list[_AbstractLoad] | None = None,
        **attrs,
    ) -> DBModel:
        """
        Returns entity by it's ID or by other attrs.
        Raises 404 if such one was not found.
        """
        entity = await self.repo.get(entity_id, relationships_to_load, **attrs)
        if not entity:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self.not_found_msg)
        return entity
