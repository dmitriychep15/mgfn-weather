"""Forecasts' xlsx generator."""

import asyncio

from xlsxwriter.worksheet import Worksheet

from src.models.schemas.forecasts import ForecastReportSchema
from src.models.schemas.weather_providers import ForecastData
from src.utils.file_generators.forecasts.abc import ForecastFileGenerator
from src.utils.file_generators.xlsx import AbstractXLSXFileGenerator


class ForecastXLSXFileGenerator(AbstractXLSXFileGenerator, ForecastFileGenerator):
    def _set_headers(self, worksheet: Worksheet, data: ForecastReportSchema):
        worksheet.merge_range(
            0,
            0,
            0,
            6,
            f"Прогноз погоды ({data.coordinates.lattitude}, {data.coordinates.longitude})",
            self.horizontal_top_header_format,
        )
        worksheet.merge_range(1, 0, 1, 6, data.location, self.horizontal_header_format)
        worksheet.merge_range(2, 0, 2, 2, "")

        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 10)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)

    def _generate(self, data: ForecastReportSchema) -> bytes:
        worksheet = self.workbook.add_worksheet("Прогноз погоды")
        self._set_headers(worksheet, data)
        i = 3
        for daily_forecast in data.forecasts:
            worksheet.merge_range(
                i,
                0,
                i,
                6,
                f"{daily_forecast.weekday} {daily_forecast.date_view} {daily_forecast.pressure_comment}",
                self.horizontal_left_header_format,
            )
            i += 1
            worksheet.merge_range(i, 0, i, 2, "")
            worksheet.write(i, 3, "ощущается\nкак", self.horizontal_header_format)
            worksheet.write(
                i, 4, "давление,\nмм рт. ст.", self.horizontal_header_format
            )
            worksheet.write(i, 5, "влажность", self.horizontal_header_format)
            worksheet.write(i, 6, "магнитное\nполе", self.horizontal_header_format)

            day_parts: dict[str, ForecastData] = {
                "ночь": daily_forecast.parts.night,
                "утро": daily_forecast.parts.morning,
                "день": daily_forecast.parts.day,
                "вечер": daily_forecast.parts.evening,
            }
            for day_part_name, day_part_data in day_parts.items():
                i += 1
                worksheet.write(i, 0, day_part_name, self.horizontal_row_format)
                worksheet.write(
                    i, 1, day_part_data.temp_avg_view, self.horizontal_row_format
                )
                worksheet.write(
                    i, 2, day_part_data.condition.name, self.horizontal_row_format
                )
                worksheet.write(
                    i, 3, day_part_data.feels_like_view, self.horizontal_row_format
                )
                worksheet.write(
                    i, 4, day_part_data.pressure_mm, self.horizontal_row_format
                )
                worksheet.write(
                    i, 5, day_part_data.humidity, self.horizontal_row_format
                )
                worksheet.write(
                    i,
                    6,
                    day_part_data.imfBt if day_part_data.imfBt else "-",
                    self.horizontal_row_format,
                )
            i += 2
        self._format_worksheet_for_print(worksheet)
        self.workbook.close()
        return self.output.getvalue()

    async def generate(self, data):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate, data)
