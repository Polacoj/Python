from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook


@dataclass(frozen=True)
class SheetInfo:
    name: str
    headers: list[str]


@dataclass(frozen=True)
class WorkbookInfo:
    file_name: str
    sheets: list[SheetInfo]


def read_workbook_info(file_path: str) -> WorkbookInfo:
    """Obtiene los nombres de hojas y los valores de su primera fila."""
    workbook = load_workbook(file_path, read_only=True, data_only=True)
    try:
        sheets = []
        for worksheet in workbook.worksheets:
            first_row = next(worksheet.iter_rows(values_only=True), ())
            headers = [
                str(value).strip() if value is not None and str(value).strip() else "(vacío)"
                for value in first_row
            ]
            sheets.append(SheetInfo(name=worksheet.title, headers=headers))
        return WorkbookInfo(file_name=Path(file_path).name, sheets=sheets)
    finally:
        workbook.close()
