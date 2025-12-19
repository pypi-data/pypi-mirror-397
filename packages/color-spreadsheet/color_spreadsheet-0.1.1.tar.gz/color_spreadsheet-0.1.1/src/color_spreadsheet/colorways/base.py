"""Abstract base class for colorway implementations."""
from abc import ABC, abstractmethod
from typing import Optional
from openpyxl.styles import Font


class Colorway(ABC):
    """
    Abstract base class for colorway implementations.

    A colorway defines the color scheme to apply to different cell types
    in an Excel spreadsheet.
    """

    @abstractmethod
    def get_font_for_hardcoded_value(self) -> Font:
        """
        Get the font style for hardcoded values (numbers, dates, booleans).

        Returns:
            Font object with the appropriate color
        """
        pass

    @abstractmethod
    def get_font_for_same_sheet_formula(self) -> Font:
        """
        Get the font style for formulas that reference the same sheet.

        Returns:
            Font object with the appropriate color
        """
        pass

    @abstractmethod
    def get_font_for_cross_sheet_formula(self) -> Font:
        """
        Get the font style for formulas that reference other sheets.

        Returns:
            Font object with the appropriate color
        """
        pass

    @abstractmethod
    def get_font_for_text(self) -> Optional[Font]:
        """
        Get the font style for text cells.

        Returns:
            Font object with the appropriate color, or None to leave unchanged
        """
        pass
