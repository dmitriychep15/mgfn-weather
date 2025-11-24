"""Dataclasses/structures for construnting DB SQL queries using repositories' methods."""

import typing as t
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy.sql.elements import UnaryExpression


@dataclass
class SQLAlchemyQueryEssentials:
    """
    Essential params for constructing SQL DB query through repositories:
    - `ordering` - ordering Enum value (optional);
    - `order_expressions` - dict with all possible orderings for list, where:
        - keys: all possible orderings as related Enum codes,
        - values: lists of target instance models attributes UnaryExpressions
        (.asc()/.desc()) for this ordering.
        For example:
          {OrderingEnum.name_asc: [InstanceModel.name.asc()],
           OrderingEnum.number_desc: [InstanceModel.number.desc()]};
    - `orderings` - list of specific order expressions ([InstanceModel.number.desc(), InstanceModel.created_at.desc()]);
    - `columns` - if you need to query not the model, but specific attributes, pass them here as a list, for example:
        `columns=[
            InstanceModel.name.label("name"),
            InstanceModel.number.label("instance_number"),
            func.count(InstanceModel.id).label("instances_count")
        ]`;
    - `load_options` - list of load options to load related entities, for example:
        `load_options = [
            selectinload(InstanceModel.instance2).selectinload(InstanceModel2.fields),
            selectinload(InstanceModel.additional_fields)
        ]`;
    - `search` - string value for search (optional);
    - `search_attrs` - list of InstanceModel's attributes for searching in list query;
    - `custom_filters` - pass here list of any filters, that are possible to use in .filter() method. Specific filters for some common cases are described below;
    - `page_number`, `page_size` - use these atributes in case you need paginated list;
    """

    ordering: Enum | None = None
    order_expressions: dict[Enum, list[UnaryExpression]] | None = None
    orderings: list[UnaryExpression] | None = None
    columns: list[InstrumentedAttribute | t.Any] | None = None
    load_options: list[_AbstractLoad] | None = None
    search: str | None = None
    search_attrs: list[InstrumentedAttribute] | None = None
    custom_filters: list[bool | t.Any] | None = None
    page_number: int | None = None
    page_size: int | None = None
