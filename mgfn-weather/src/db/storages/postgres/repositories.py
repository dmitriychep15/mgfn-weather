"""Postgres repositories for handling DB operations with entities."""

import logging
import typing as tp
from enum import Enum
from math import ceil
from uuid import UUID

import asyncpg
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select, delete, Select, func, or_
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.exc import InterfaceError, IntegrityError, InternalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    InstrumentedAttribute,
)
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import UnaryExpression

from src.db.storages.abstract_repository import AbstractRepository
from src.db.storages.postgres.query_models import (
    SQLAlchemyQueryEssentials,
)

from src.models.db_entities.forecasts import Forecast
from src.models.db_entities.files import File


logger = logging.getLogger(__name__)


class SQLAlchemyRepository(AbstractRepository):
    """Interface for working with PostgreSQL DB via SQLAlchemy."""

    DBModel: tp.Type[DeclarativeBase]
    pk_attr: str = "id"
    soft_deletable: bool = False

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **attrs):
        try:
            instance: DeclarativeBase = self.DBModel(**attrs)
            self.session.add(instance)
            await self.session.flush()
            return instance
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            IntegrityError,
        ) as e:
            await self._handle_error(e)

    async def get(
        self,
        instance_id: UUID | str | None = None,
        load_options: list[_AbstractLoad] | None = None,
        essentials: SQLAlchemyQueryEssentials | None = None,
        **attrs,
    ) -> DeclarativeBase | dict[str, tp.Any] | None:
        """Returns exactly one DB instance or None if such one was not found.
        In case you pass `essentials` attribute's value, other method's attibutes will be ignored
        (use it when you need more complicated filtration, than just passing instance attributes' values and load_options).
        """
        try:
            if not any((instance_id, attrs, essentials)):
                raise ValueError(
                    f"No attributes was passed to get an instance of {self.DBModel}"
                )
            if essentials:
                instance_query_stmt = self._get_list_query_stmt(essentials)
                instance_query: ChunkedIteratorResult = await self.session.execute(
                    instance_query_stmt
                )
                if essentials.columns:
                    instance = instance_query.fetchone()
                    if instance is None:
                        return
                    return instance._asdict()
                return instance_query.scalars().first()
            if instance_id is not None:
                attrs[self.pk_attr] = instance_id
            instance_query_stmt = select(self.DBModel).filter_by(**attrs)
            if load_options:
                for load_option in load_options:
                    instance_query_stmt = instance_query_stmt.options(load_option)
            instance_query: ChunkedIteratorResult = await self.session.execute(
                instance_query_stmt
            )
            return instance_query.scalars().first()
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            InternalError,
        ) as e:
            await self._handle_error(e)

    async def delete(
        self,
        instance_id: UUID | str | None = None,
        filters: list[bool | tp.Any] | None = None,
    ):
        try:
            delete_query_stmt = delete(self.DBModel)
            if filters:
                for query_filter in filters:
                    delete_query_stmt = delete_query_stmt.filter(query_filter)
            elif instance_id:
                query_filter = {self.pk_attr: instance_id}
                delete_query_stmt = delete_query_stmt.filter_by(**query_filter)
            else:
                raise ValueError(
                    f"No query filters was passed to delete an instance/instances of {self.DBModel}"
                )
            await self.session.execute(delete_query_stmt)
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            InternalError,
        ) as e:
            await self._handle_error(e)

    def _order_list(
        self,
        list_query_stmt: Select,
        ordering: Enum,
        order_expressions: dict[Enum, list[UnaryExpression]],
    ) -> Select:
        """Orders storage instances' list."""
        for order_expression in order_expressions[ordering]:
            list_query_stmt = list_query_stmt.order_by(order_expression)
        return list_query_stmt

    def _filter(
        self,
        list_query_stmt: Select,
        custom_filters: list[bool | tp.Any],
    ) -> Select:
        """Filters query by any passed filter expressions."""
        for query_filter in custom_filters:
            list_query_stmt = list_query_stmt.filter(query_filter)
        return list_query_stmt

    def _search(
        self,
        list_query_stmt: Select,
        search_str: str,
        search_attrs: list[InstrumentedAttribute],
    ) -> Select:
        """Search filtration by matching `search_str` to instance's `search_attrs`."""
        tmp_subquery = []
        replaceable_chars = ["%", "_"]
        for word in search_str.split():
            for replaceable_char in replaceable_chars:
                word = word.lower().replace(replaceable_char, f"\{replaceable_char}")
            for attr in search_attrs:
                tmp_subquery.append(func.lower(attr).contains(f"{word.lower()}"))
        return list_query_stmt.filter(or_(*tmp_subquery))

    def _get_base_list_query_stmt(
        self, essentials: SQLAlchemyQueryEssentials
    ) -> Select:
        """Returns base list query statement for further filtration, searching, grouping by etc."""
        if essentials.columns:
            query_stmt = select(*essentials.columns)
        else:
            query_stmt = select(self.DBModel)
        return query_stmt

    def _get_list_query_stmt(
        self,
        essentials: SQLAlchemyQueryEssentials,
    ) -> Select:
        """
        Returns stmt for getting required list.
        Use the result to get raw list of dicts of db instances, or paginated one.
        """
        list_query_stmt: Select = self._get_base_list_query_stmt(essentials)
        if essentials.load_options:
            for load_option in essentials.load_options:
                list_query_stmt = list_query_stmt.options(load_option)
        if essentials.orderings:
            for order_expression in essentials.orderings:
                list_query_stmt = list_query_stmt.order_by(order_expression)
        elif essentials.ordering and essentials.order_expressions:
            list_query_stmt = self._order_list(
                list_query_stmt, essentials.ordering, essentials.order_expressions
            )
        if essentials.search and essentials.search_attrs:
            list_query_stmt = self._search(
                list_query_stmt, essentials.search, essentials.search_attrs
            )
        if essentials.custom_filters:
            list_query_stmt = self._filter(list_query_stmt, essentials.custom_filters)
        return list_query_stmt

    def _extract_list_records(
        self,
        query: ChunkedIteratorResult,
        as_dict: bool = False,
    ) -> list[DeclarativeBase] | list[dict[str, tp.Any]]:
        """Extracts records from list query and returns them either as DBModel entities or as dicts."""
        if as_dict:
            return [item._asdict() for item in query.fetchall()]
        return query.scalars().all()

    async def get_list(
        self,
        essentials: SQLAlchemyQueryEssentials,
    ) -> list[DeclarativeBase] | list[dict[str, tp.Any]]:
        try:
            list_query_stmt: Select = self._get_list_query_stmt(essentials)
            list_query: ChunkedIteratorResult = await self.session.execute(
                list_query_stmt
            )
            return self._extract_list_records(list_query, bool(essentials.columns))
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            InternalError,
        ) as e:
            await self._handle_error(e)

    async def count(
        self,
        essentials: SQLAlchemyQueryEssentials,
    ) -> int:
        try:
            all_items_query_stmt: Select = self._get_list_query_stmt(essentials)
            all_items_query_result: ChunkedIteratorResult = await self.session.execute(
                select(func.count(1)).select_from(all_items_query_stmt)
            )
            return all_items_query_result.scalar_one()
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            InternalError,
        ) as e:
            await self._handle_error(e)

    async def get_paginated_list(
        self,
        essentials: SQLAlchemyQueryEssentials,
    ) -> tuple[list[DeclarativeBase] | list[dict[str, tp.Any]], int, int]:
        try:
            list_query_stmt: Select = self._get_list_query_stmt(essentials)
            total_items = await self.count(essentials)
            total_pages: int = ceil(total_items / essentials.page_size)
            list_query_stmt = list_query_stmt.offset(
                (essentials.page_number - 1) * essentials.page_size
            ).limit(essentials.page_size)
            list_query = await self.session.execute(list_query_stmt)
            list_content = self._extract_list_records(
                list_query, bool(essentials.columns)
            )
            return list_content, total_pages, total_items
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            InternalError,
        ) as e:
            await self._handle_error(e)

    async def _handle_error(
        self,
        error: (
            ConnectionError
            | asyncpg.PostgresError
            | InterfaceError
            | IntegrityError
            | InternalError
        ),
    ):
        """
        Handles errors:
        - rollbacks session,
        - logs the error,
        - raises HTTPException.
        """
        log_msg = f"ERROR connecting to database: {error}"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        response_detail = "База данных недоступна, повторите запрос позже."
        if isinstance(error, (asyncpg.PostgresError, InternalError)):
            log_msg = f"ERROR handling database: {error}"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_detail = "Ошибка работы с БД."
        elif isinstance(error, IntegrityError):
            try:
                comment = error.orig.args[0].split("DETAIL: ")[1]
            except Exception:
                comment = error
            log_msg = f"Error inserting values to {self.DBModel.__tablename__} or another table: {comment}"
            status_code = status.HTTP_400_BAD_REQUEST
            response_detail = "Ошибка сохранения записи в БД. Попробуйте снова"

        await self.session.rollback()
        logger.error(log_msg)
        raise HTTPException(status_code, response_detail)

    async def save(
        self, instance_to_refresh: DeclarativeBase | None = None, flush: bool = False
    ) -> None:
        """Saves changes.
        - `flush` - if True - saves only in session, not in DB,
        - `instance_to_refresh` - send an instance here to refresh
        all it's attributes after committing transaction.
        """
        try:
            if flush:
                await self.session.flush()
                return
            await self.session.commit()
            if instance_to_refresh:
                await self.session.refresh(instance_to_refresh)
        except (
            ConnectionError,
            InterfaceError,
            asyncpg.PostgresError,
            IntegrityError,
        ) as e:
            await self._handle_error(e)


class ForecastSQLAlchemyRepository(SQLAlchemyRepository):
    """Interface for handling DB operations with forecasts."""

    DBModel = Forecast


class FileSQLAlchemyRepository(SQLAlchemyRepository):
    """Interface for handling db operations with files via postgresql."""

    DBModel = File
