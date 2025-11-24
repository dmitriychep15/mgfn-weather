"""File generators for forecasts."""

import abc
import typing as t

from src.models.schemas.forecasts import (
    ForecastReportSchema,
)


class ForecastFileGenerator(abc.ABC):
    """Abstract file generator. Works as a context manager."""

    @abc.abstractmethod
    def __enter__(self) -> t.Self:
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abc.abstractmethod
    async def generate(self, data: ForecastReportSchema) -> bytes:
        """Generates the file with forecast."""
        raise NotImplementedError
