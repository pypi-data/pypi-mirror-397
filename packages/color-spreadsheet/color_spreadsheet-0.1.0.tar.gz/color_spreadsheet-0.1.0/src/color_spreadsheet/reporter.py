"""Summary reporting for color-coding operations."""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class SheetStatistics:
    """Statistics for a single sheet."""
    blue: int = 0
    black: int = 0
    green: int = 0
    text_skipped: int = 0

    @property
    def total_colored(self) -> int:
        """Total cells that were colored (excludes text)."""
        return self.blue + self.black + self.green

    @property
    def total_processed(self) -> int:
        """Total cells processed including text."""
        return self.blue + self.black + self.green + self.text_skipped


@dataclass
class Statistics:
    """Statistics for the entire workbook."""
    sheets: Dict[str, SheetStatistics] = field(default_factory=dict)
    total_cells_processed: int = 0

    def get_overall_totals(self) -> SheetStatistics:
        """Calculate overall totals across all sheets."""
        totals = SheetStatistics()
        for sheet_stats in self.sheets.values():
            totals.blue += sheet_stats.blue
            totals.black += sheet_stats.black
            totals.green += sheet_stats.green
            totals.text_skipped += sheet_stats.text_skipped
        return totals


def generate_summary(statistics: Statistics) -> str:
    """
    Generate a formatted summary report of color-coding statistics.

    Args:
        statistics: Statistics object containing all processing results

    Returns:
        Formatted string containing the summary report
    """
    lines = []
    lines.append("=" * 70)
    lines.append("COLOR APPLICATION SUMMARY")
    lines.append("=" * 70)

    # Print per-sheet statistics
    for sheet_name, counts in statistics.sheets.items():
        # Only show sheets where we colored something
        if counts.total_colored > 0:
            lines.append(f"\n{sheet_name}:")
            lines.append(f"  Blue (hardcoded numbers):    {counts.blue:5d} cells")
            lines.append(f"  Black (same-sheet formulas): {counts.black:5d} cells")
            lines.append(f"  Green (cross-sheet refs):    {counts.green:5d} cells")
            lines.append(f"  Text (unchanged):            {counts.text_skipped:5d} cells")

    # Print overall totals
    totals = statistics.get_overall_totals()
    lines.append("\n" + "=" * 70)
    lines.append("OVERALL TOTAL:")
    lines.append(f"  Blue (hardcoded numbers):    {totals.blue:5d} cells")
    lines.append(f"  Black (same-sheet formulas): {totals.black:5d} cells")
    lines.append(f"  Green (cross-sheet refs):    {totals.green:5d} cells")
    lines.append(f"  Text (unchanged):            {totals.text_skipped:5d} cells")
    lines.append(f"  Total processed:             {statistics.total_cells_processed:5d} cells")
    lines.append("=" * 70)

    return "\n".join(lines)
