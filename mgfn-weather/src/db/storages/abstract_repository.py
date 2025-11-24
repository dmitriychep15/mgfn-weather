"""Abstract repository for working with permanent storage."""

import abc
import typing as t


class AbstractRepository(abc.ABC):
    """Abstract interface for working with permanent storage."""

    DBModel: t.Any
    pk_attr: str

    @abc.abstractmethod
    async def create(self, *args, **kwargs) -> t.Any:
        """Create instance in storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, *args, **kwargs) -> t.Any | dict[str, t.Any] | None:
        """Get single instance from storage by it's id, other attrs or by more complicated filtration."""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, *args, **kwargs) -> None:
        """Delete one or multiple instances from storage."""
        raise NotImplementedError

    @abc.abstractmethod
    async def count(self, *args, **kwargs) -> int | t.NoReturn:
        """Calculate number of items in list."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_list(self, *args, **kwargs) -> list[dict[str, t.Any]] | list[t.Any]:
        """Get list of storage instances."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_paginated_list(
        self, *args, **kwargs
    ) -> tuple[list[dict[str, t.Any]] | list[t.Any], int, int]:
        """Get paginated list of storage instances."""
        raise NotImplementedError

    @abc.abstractmethod
    async def save(self, *args, **kwargs) -> None:
        """Save all changes to storage."""
        raise NotImplementedError
