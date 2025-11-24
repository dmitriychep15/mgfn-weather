"""Abstract XLSX files generator."""

import abc
from io import BytesIO

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet


class AbstractXLSXFileGenerator(abc.ABC):
    """Abstract .xlsx file generator. Works as a context manager."""

    def __enter__(self):
        self.output = BytesIO()
        self.workbook = Workbook(self.output, {"in_memory": True})

        self.horizontal_top_header_format = self.workbook.add_format(
            {
                "border": 1,
                "text_wrap": True,
                "valign": "vcenter",
                "align": "center",
                "bold": True,
            }
        )
        self.horizontal_top_header_format.set_font_name("Helvetica")
        self.horizontal_top_header_format.set_font_size(14)

        self.horizontal_header_format = self.workbook.add_format(
            {
                "border": 1,
                "text_wrap": True,
                "valign": "vcenter",
                "align": "center",
                "bold": True,
            }
        )
        self.horizontal_header_format.set_font_name("Helvetica")
        self.horizontal_header_format.set_font_size(12)

        self.horizontal_left_header_format = self.workbook.add_format(
            {
                "border": 1,
                "text_wrap": True,
                "valign": "vcenter",
                "align": "left",
                "bold": True,
            }
        )
        self.horizontal_left_header_format.set_font_name("Helvetica")
        self.horizontal_left_header_format.set_font_size(12)

        self.horizontal_row_format = self.workbook.add_format(
            {"border": 1, "text_wrap": True, "valign": "vcenter", "align": "center"}
        )
        self.horizontal_row_format.set_font_name("Helvetica")
        self.horizontal_row_format.set_font_size(10)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.workbook.close()

    def _format_worksheet_for_print(self, worksheet: Worksheet) -> None:
        """Formats the worksheet for printing.
        Call this method after finishing generating the worksheet.
        """
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.hide_gridlines(0)
        worksheet.set_margins(left=0.3, right=0.3, top=0.3, bottom=0.3)

    @abc.abstractmethod
    def _set_headers(self, worksheet: Worksheet, *args, **kwargs) -> None:
        """Sets the worksheet's headers."""
        raise NotImplementedError

    @abc.abstractmethod
    async def generate(self, *args, **kwarrgs) -> bytes:
        """Generates the `.xlsx` file."""
        raise NotImplementedError
