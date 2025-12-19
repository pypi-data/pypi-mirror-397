"""Standard financial colorway implementation."""
from typing import Optional
from openpyxl.styles import Font
from color_spreadsheet.colorways.base import Colorway


class StandardFinancialColorway(Colorway):
    """
    Standard financial colorway for Excel spreadsheets.

    Color Logic:
    - Blue (0000FF): Hardcoded inputs (numbers, dates, booleans)
    - Black (000000): Same-sheet formulas
    - Green (008000): Cross-sheet formulas
    - Text/Labels: No change (left as is)
    """

    def get_font_for_hardcoded_value(self) -> Font:
        """Blue for hardcoded values (inputs)."""
        return Font(color="0000FF")

    def get_font_for_same_sheet_formula(self) -> Font:
        """Black for same-sheet formulas."""
        return Font(color="000000")

    def get_font_for_cross_sheet_formula(self) -> Font:
        """Green for cross-sheet formulas."""
        return Font(color="008000")

    def get_font_for_text(self) -> Optional[Font]:
        """No change for text cells."""
        return None
