"""Color-spreadsheet: Apply color coding to Excel cells based on content type."""
from color_spreadsheet.__version__ import __version__
from color_spreadsheet.core import process_workbook
from color_spreadsheet.colorways.base import Colorway

__all__ = ["__version__", "process_workbook", "Colorway"]
