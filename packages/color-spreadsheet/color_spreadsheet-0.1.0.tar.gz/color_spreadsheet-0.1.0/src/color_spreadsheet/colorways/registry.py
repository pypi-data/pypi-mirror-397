"""Colorway registry for managing available colorways."""
from typing import Dict, List, Type
from color_spreadsheet.colorways.base import Colorway
from color_spreadsheet.colorways.standard_financial import StandardFinancialColorway


# Registry mapping colorway names to their classes
COLORWAYS: Dict[str, Type[Colorway]] = {
    "standard-financial": StandardFinancialColorway,
}


def get_colorway(name: str) -> Colorway:
    """
    Get a colorway instance by name.

    Args:
        name: Name of the colorway (e.g., "standard-financial")

    Returns:
        An instance of the requested Colorway

    Raises:
        ValueError: If the colorway name is not found in the registry
    """
    if name not in COLORWAYS:
        available = ", ".join(list_colorways())
        raise ValueError(
            f"Unknown colorway '{name}'. Available colorways: {available}"
        )

    colorway_class = COLORWAYS[name]
    return colorway_class()


def list_colorways() -> List[str]:
    """
    Get a list of all available colorway names.

    Returns:
        List of colorway names as strings
    """
    return sorted(COLORWAYS.keys())
