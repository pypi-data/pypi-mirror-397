"""Command-line interface for color-spreadsheet."""
import argparse
import os
import sys
from pathlib import Path

from color_spreadsheet.colorways.registry import get_colorway, list_colorways
from color_spreadsheet.core import process_workbook
from color_spreadsheet.reporter import generate_summary


def main() -> None:
    """Main entry point for the color-spreadsheet CLI."""
    parser = argparse.ArgumentParser(
        description="Apply color coding to Excel spreadsheet cells based on content type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  color-spreadsheet --input="data.xlsx" --output="data-colored.xlsx"
  color-spreadsheet -i input.xlsx -o output.xlsx --colorway=standard-financial
  color-spreadsheet --list-colorways
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to input Excel file"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Path to output Excel file"
    )

    parser.add_argument(
        "--colorway",
        type=str,
        default="standard-financial",
        help="Colorway to use (default: standard-financial)"
    )

    parser.add_argument(
        "--list-colorways",
        action="store_true",
        help="List available colorways and exit"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )

    args = parser.parse_args()

    # Handle --list-colorways
    if args.list_colorways:
        print("Available colorways:")
        for colorway_name in list_colorways():
            print(f"  - {colorway_name}")
        sys.exit(0)

    # Validate required arguments
    if not args.input or not args.output:
        parser.error("--input and --output are required (unless using --list-colorways)")

    input_path = args.input
    output_path = args.output

    # Validate input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Validate input is a file
    if not os.path.isfile(input_path):
        print(f"Error: Input path is not a file: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Validate output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: Output directory does not exist: {output_dir}", file=sys.stderr)
        sys.exit(1)

    # Validate input != output
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        print("Error: Input and output paths must be different", file=sys.stderr)
        sys.exit(1)

    # Get colorway
    try:
        colorway = get_colorway(args.colorway)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Process workbook
    if not args.quiet:
        print(f"Loading workbook: {input_path}")
        if args.verbose:
            print(f"Using colorway: {args.colorway}")

    try:
        stats = process_workbook(input_path, output_path, colorway)
    except Exception as e:
        print(f"Error processing workbook: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"Saved colored workbook to: {output_path}")
        print()
        print(generate_summary(stats))
        print("\nDone!")


if __name__ == "__main__":
    main()
