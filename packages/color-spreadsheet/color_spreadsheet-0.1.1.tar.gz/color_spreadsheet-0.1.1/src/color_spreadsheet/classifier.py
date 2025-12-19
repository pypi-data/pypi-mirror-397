"""Cell type classification for Excel spreadsheet cells."""
from datetime import datetime
from enum import Enum, auto
from typing import Any
from openpyxl.cell.cell import Cell


class CellType(Enum):
    """Types of cells in a spreadsheet."""
    EMPTY = auto()
    TEXT = auto()
    HARDCODED_VALUE = auto()
    FORMULA_SAME_SHEET = auto()
    FORMULA_CROSS_SHEET = auto()


def is_formula(value: Any) -> bool:
    """Check if value is a formula."""
    return value is not None and isinstance(value, str) and value.startswith('=')


def has_cross_sheet_reference(formula: str) -> bool:
    """Check if formula references other sheets (contains '!' operator)."""
    return '!' in formula


def classify_cell(cell: Cell) -> CellType:
    """
    Classify a cell based on its content type.

    Args:
        cell: An openpyxl Cell object

    Returns:
        CellType indicating the type of content in the cell
    """
    value = cell.value

    # Empty cells
    if value is None:
        return CellType.EMPTY

    # Check if it's a formula
    if is_formula(value):
        if has_cross_sheet_reference(value):
            return CellType.FORMULA_CROSS_SHEET
        else:
            return CellType.FORMULA_SAME_SHEET

    # Check if it's a number, date, or boolean (hardcoded value)
    if isinstance(value, (int, float, bool, datetime)):
        return CellType.HARDCODED_VALUE

    # Otherwise it's text/label
    if isinstance(value, str):
        return CellType.TEXT

    # Default fallback (shouldn't normally reach here)
    return CellType.TEXT
