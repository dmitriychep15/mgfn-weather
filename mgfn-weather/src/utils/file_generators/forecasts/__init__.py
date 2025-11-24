"""Forecast file generators."""

import typing as t

from src.models.schemas.common import FileFormatEnum
from src.utils.file_generators.forecasts.abc import ForecastFileGenerator
from src.utils.file_generators.forecasts.xlsx import ForecastXLSXFileGenerator


generators_by_format: dict[FileFormatEnum, t.Type[ForecastFileGenerator]] = {
    FileFormatEnum.XLSX: ForecastXLSXFileGenerator,
}
