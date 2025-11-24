"""Common for all system pydantic schemas."""

from datetime import date, datetime
from enum import Enum, StrEnum

import pytz
from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict


class DateFormatEnum(str, Enum):
    """
    Possible date formats to use for formatting datetime objects. Examples:
    - `FULL_DATE` - "02.09.2016";
    - `FULL_DATETIME` - "02.09.2016 14:15:32";
    """

    FULL_DATE = "FULL_DATE"
    FULL_DATETIME = "FULL_DATETIME"

    @classmethod
    def str_formats(cls) -> dict["DateFormatEnum", str]:
        return {
            cls.FULL_DATE: "%d.%m.%Y",
            cls.FULL_DATETIME: "%d.%m.%Y %H:%M:%S",
        }


weekdays_ru_aliases = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}


class FileFormatEnum(StrEnum):
    """Possible file formats."""

    XLSX = "XLSX"

    @classmethod
    def filename_endings(cls) -> dict["FileFormatEnum", str]:
        """
        Returns file endings according to formats.
        Use it to add to the end of file's name.
        """
        return {
            cls.XLSX: ".xlsx",
        }


class CustomBaseModel(BaseModel):
    """Redefined pydantic's `BaseModel` with custom methods and settings."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @staticmethod
    def get_date_view(date_value: date) -> str:
        """Returns date field's string representation for view."""

        str_format = "%d.%m.%Y"
        return date_value.strftime(str_format)

    @staticmethod
    def get_datetime_view(
        some_datetime: datetime,
        format: DateFormatEnum = DateFormatEnum.FULL_DATE,
        tz: str = "Europe/Moscow",
    ) -> str:
        """Returns datetime field's string representation for view."""
        str_formats = DateFormatEnum.str_formats()
        str_format = str_formats.get(format, "%d.%m.%Y")
        return (
            some_datetime.replace(tzinfo=pytz.utc)
            .astimezone(pytz.timezone(tz))
            .strftime(str_format)
        )

    @staticmethod
    def get_temp_view(temp: float) -> str:
        """Returns temperature field's string representation for view."""
        temp_str = str(int(temp))
        prefix = ""
        if temp > 0:
            prefix = "+"
        return f"{prefix}{temp_str}°C"


class ListQueryParams(CustomBaseModel):
    """
    Common query params to get db instances list.
    Redefine `ordering` in child Schema with specific ordering enum
    annotation and default value.
    """

    ordering: Enum = Field(Query(...))
    search: None | str = Field(Query(None))


class PaginatedListQueryParams(ListQueryParams):
    """
    Common query params to get db instances paginated list.
    Redefine `ordering` in child Schema with specific ordering enum
    annotation and default value.
    """

    page_number: int = Field(Query(1, ge=1, description="Page number."))
    page_size: int = Field(Query(20, ge=1, description="Records per page."))


class PaginatedList(CustomBaseModel):
    """Common schema for paginated entities list."""

    content: list
    total_items: int
    total_pages: int
