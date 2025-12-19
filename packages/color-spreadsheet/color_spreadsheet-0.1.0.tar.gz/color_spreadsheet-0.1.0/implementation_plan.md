# Implementation Plan: color-spreadsheet PyPI Package

## Overview
Refactor `apply_colors_generic.py` into a pip-installable package that applies color coding to Excel cells based on content type, with extensible architecture for multiple colorways.

## Package Location
Create new package at: `/Users/mshron/code/switchbox/color-spreadsheet/`

## Directory Structure
```
color-spreadsheet/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── color_spreadsheet/
│       ├── __init__.py
│       ├── __version__.py
│       ├── cli.py                    # CLI entry point
│       ├── core.py                   # Main processing logic
│       ├── classifier.py             # Cell type classification
│       ├── reporter.py               # Summary reporting
│       └── colorways/
│           ├── __init__.py
│           ├── base.py               # Abstract Colorway class
│           ├── standard_financial.py # Default colorway
│           └── registry.py           # Colorway registration
└── tests/
    ├── __init__.py
    └── test_classifier.py
```

## Implementation Steps

### 1. Initialize Package with uv
```bash
cd /Users/mshron/code/switchbox/
uv init color-spreadsheet --lib
cd color-spreadsheet
```

### 2. Configure pyproject.toml with uv
```bash
# Add dependencies
uv add openpyxl

# Add dev dependencies
uv add --dev pytest

# Manually update pyproject.toml to add:
# - authors = [{name = "Maxwell Shron", email = "max@shron.net"}]
# - description = "Apply color coding to Excel spreadsheet cells based on content type"
# - [project.scripts] section with: color-spreadsheet = "color_spreadsheet.cli:main"
```

### 3. Setup Directory Structure
- Ensure `src/color_spreadsheet/` exists (may be created by uv)
- Create `src/color_spreadsheet/colorways/` subdirectory
- Create `tests/` directory if not exists

### 4. Create LICENSE File
- Fetch MIT license text from https://license.md/wp-content/uploads/2022/06/mit.txt
- Replace placeholders: Year=2025, Copyright holder=Maxwell Shron
- Save to `LICENSE`

### 5. Implement Core Modules

#### `src/color_spreadsheet/__version__.py`
```python
__version__ = "0.1.0"
```

#### `src/color_spreadsheet/classifier.py`
Extract from `apply_colors_generic.py` (lines 30-36):
- `is_formula(value) -> bool`
- `has_cross_sheet_reference(formula) -> bool`
- Add `CellType` enum: EMPTY, TEXT, HARDCODED_VALUE, FORMULA_SAME_SHEET, FORMULA_CROSS_SHEET
- Add `classify_cell(cell) -> CellType`

#### `src/color_spreadsheet/colorways/base.py`
Abstract base class with methods:
- `get_font_for_hardcoded_value() -> Font`
- `get_font_for_same_sheet_formula() -> Font`
- `get_font_for_cross_sheet_formula() -> Font`
- `get_font_for_text() -> Optional[Font]`

#### `src/color_spreadsheet/colorways/standard_financial.py`
Implement StandardFinancialColorway:
- Blue (0000FF) for hardcoded values
- Black (000000) for same-sheet formulas
- Green (008000) for cross-sheet formulas
- None (unchanged) for text

#### `src/color_spreadsheet/colorways/registry.py`
- `COLORWAYS` dict mapping names to classes
- `get_colorway(name: str) -> Colorway`
- `list_colorways() -> List[str]`
- Register standard_financial by default

#### `src/color_spreadsheet/reporter.py`
Extract from `apply_colors_generic.py` (lines 92-125):
- `Statistics` dataclass with sheet-level and overall counts
- `generate_summary(statistics: Statistics) -> str`

#### `src/color_spreadsheet/core.py`
Main processing logic extracted from `apply_colors_generic.py` (lines 38-84):
- `process_workbook(input_path: str, output_path: str, colorway: Colorway) -> Statistics`
- Load workbook, iterate sheets/cells, classify and color, save, return stats

#### `src/color_spreadsheet/cli.py`
Command-line interface:
- Use argparse for `--input`, `--output`, `--colorway` (default: standard-financial)
- Add `--list-colorways` flag
- Add `--verbose`/`-v` and `--quiet`/`-q` flags
- Validate: input exists, output directory exists, input != output
- Call `process_workbook()` and display summary
- `def main()` as entry point

#### `src/color_spreadsheet/__init__.py`
```python
from color_spreadsheet.__version__ import __version__
from color_spreadsheet.core import process_workbook
from color_spreadsheet.colorways.base import Colorway

__all__ = ["__version__", "process_workbook", "Colorway"]
```

### 6. Create .gitignore
Standard Python .gitignore:
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.venv/
venv/
.pytest_cache/
```

### 7. Create README.md
Include:
- Project description
- Installation: `pip install color-spreadsheet`
- Usage: `color-spreadsheet --input="input.xlsx" --output="output.xlsx"`
- Color scheme explanation (blue/black/green)
- Future colorway support

### 8. Test Local Installation
Create a clean test environment and install locally:
```bash
# Build the package
cd /Users/mshron/code/switchbox/color-spreadsheet
uv build

# Test in a clean folder
mkdir -p /tmp/color-spreadsheet-test
cd /tmp/color-spreadsheet-test
python -m venv test-env
source test-env/bin/activate
pip install /Users/mshron/code/switchbox/color-spreadsheet/dist/*.whl

# Test the CLI
color-spreadsheet --help
color-spreadsheet --list-colorways
color-spreadsheet --input="/Users/mshron/code/switchbox/permit-power/Permit Power Calculations (Switchbox, forked from v1.2.3).xlsx" --output="test-output.xlsx"

# Verify output matches original script behavior
deactivate
```

Note: Cannot test `pip install color-spreadsheet` from PyPI until package is uploaded.

## Key Design Decisions

1. **Colorway Architecture**: Class-based plugin system for extensibility
2. **CLI Command**: `color-spreadsheet` (matches package name)
3. **Default Colorway**: standard-financial (current logic)
4. **Build Backend**: hatchling (modern, simple)
5. **Python Version**: >=3.9 (broad compatibility)

## Source Material
- Extract logic from: `/Users/mshron/code/switchbox/permit-power/apply_colors_generic.py`
- MIT License: https://license.md/wp-content/uploads/2022/06/mit.txt (Year: 2025, Copyright: Maxwell Shron)

## Success Criteria
- `pip install color-spreadsheet` works
- `color-spreadsheet --input="file.xlsx" --output="colored.xlsx"` produces identical output to original script
- Architecture allows adding new colorways with ~50 lines of code
- Ready for upload to PyPI via twine
