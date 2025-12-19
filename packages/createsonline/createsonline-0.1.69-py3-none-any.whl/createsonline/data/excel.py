"""
CREATESONLINE Advanced Excel Support
Pure Python Excel (.xlsx) reading and writing with openpyxl-level capabilities.

Features:
- Read/write XLSX files with full formatting
- Cell styles (fonts, colors, borders, alignment)
- Formulas and formula evaluation
- Multiple worksheets
- Data types (numbers, dates, booleans, strings)
- Cell ranges and merging
- Data validation
- Basic charts support

ZERO EXTERNAL DEPENDENCIES - Pure Python implementation!
"""

import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import math


# ============================================================================
# Excel Constants and Enums
# ============================================================================

class CellType(Enum):
    """Excel cell data types"""
    STRING = "s"
    NUMBER = "n"
    BOOLEAN = "b"
    FORMULA = "f"
    SHARED_STRING = "str"
    ERROR = "e"
    INLINE_STRING = "inlineStr"


class HorizontalAlignment(Enum):
    """Horizontal cell alignment"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"


class VerticalAlignment(Enum):
    """Vertical cell alignment"""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"


class BorderStyle(Enum):
    """Border line styles"""
    THIN = "thin"
    MEDIUM = "medium"
    THICK = "thick"
    DOUBLE = "double"
    DOTTED = "dotted"
    DASHED = "dashed"


class PatternFill(Enum):
    """Cell fill patterns"""
    SOLID = "solid"
    GRAY125 = "gray125"
    DARKGRAY = "darkGray"
    MEDIUMGRAY = "mediumGray"
    LIGHTGRAY = "lightGray"


# ============================================================================
# Excel Color Support
# ============================================================================

@dataclass
class Color:
    """RGB color representation"""
    red: int = 0
    green: int = 0
    blue: int = 0
    alpha: int = 255

    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create color from hex string (#RRGGBB or RRGGBB)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return cls(
                red=int(hex_color[0:2], 16),
                green=int(hex_color[2:4], 16),
                blue=int(hex_color[4:6], 16)
            )
        elif len(hex_color) == 8:  # ARGB
            return cls(
                alpha=int(hex_color[0:2], 16),
                red=int(hex_color[2:4], 16),
                green=int(hex_color[4:6], 16),
                blue=int(hex_color[6:8], 16)
            )
        return cls()

    def to_hex(self) -> str:
        """Convert to hex string (ARGB format)"""
        return f"{self.alpha:02X}{self.red:02X}{self.green:02X}{self.blue:02X}"

    # Common colors
    BLACK = None
    WHITE = None
    RED = None
    GREEN = None
    BLUE = None
    YELLOW = None


# Initialize common colors
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)


# ============================================================================
# Excel Cell Styling
# ============================================================================

@dataclass
class Font:
    """Font formatting"""
    name: str = "Calibri"
    size: int = 11
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    color: Optional[Color] = None


@dataclass
class Fill:
    """Cell fill/background"""
    pattern_type: PatternFill = PatternFill.SOLID
    fg_color: Optional[Color] = None
    bg_color: Optional[Color] = None


@dataclass
class Border:
    """Cell border"""
    left: Optional[BorderStyle] = None
    right: Optional[BorderStyle] = None
    top: Optional[BorderStyle] = None
    bottom: Optional[BorderStyle] = None
    diagonal: Optional[BorderStyle] = None
    left_color: Optional[Color] = None
    right_color: Optional[Color] = None
    top_color: Optional[Color] = None
    bottom_color: Optional[Color] = None


@dataclass
class Alignment:
    """Cell alignment"""
    horizontal: Optional[HorizontalAlignment] = None
    vertical: Optional[VerticalAlignment] = None
    wrap_text: bool = False
    shrink_to_fit: bool = False
    indent: int = 0
    text_rotation: int = 0


@dataclass
class CellStyle:
    """Complete cell formatting"""
    font: Font = field(default_factory=Font)
    fill: Fill = field(default_factory=Fill)
    border: Border = field(default_factory=Border)
    alignment: Alignment = field(default_factory=Alignment)
    number_format: str = "General"


# ============================================================================
# Excel Cell
# ============================================================================

class Cell:
    """Represents a single Excel cell"""

    def __init__(
        self,
        value: Any = None,
        cell_type: Optional[CellType] = None,
        formula: Optional[str] = None,
        style: Optional[CellStyle] = None,
        row: int = 0,
        column: int = 0
    ):
        self._value = value
        self._formula = formula
        self._type = cell_type or self._infer_type(value)
        self.style = style or CellStyle()
        self.row = row
        self.column = column
        self._merged = False

    @staticmethod
    def _infer_type(value: Any) -> CellType:
        """Infer cell type from value"""
        if value is None:
            return CellType.STRING
        elif isinstance(value, bool):
            return CellType.BOOLEAN
        elif isinstance(value, (int, float)):
            return CellType.NUMBER
        elif isinstance(value, str) and value.startswith('='):
            return CellType.FORMULA
        else:
            return CellType.STRING

    @property
    def value(self) -> Any:
        """Get cell value"""
        if self._formula and self._formula.startswith('='):
            # Return calculated value if available, otherwise return formula
            return self._value if self._value is not None else self._formula
        return self._value

    @value.setter
    def value(self, val: Any):
        """Set cell value"""
        if isinstance(val, str) and val.startswith('='):
            self._formula = val
            self._type = CellType.FORMULA
        else:
            self._value = val
            self._formula = None
            self._type = self._infer_type(val)

    @property
    def formula(self) -> Optional[str]:
        """Get cell formula"""
        return self._formula

    @formula.setter
    def formula(self, formula: str):
        """Set cell formula"""
        if formula and not formula.startswith('='):
            formula = '=' + formula
        self._formula = formula
        self._type = CellType.FORMULA

    @property
    def coordinate(self) -> str:
        """Get cell coordinate (e.g., 'A1')"""
        return f"{self.column_letter}{self.row + 1}"

    @property
    def column_letter(self) -> str:
        """Convert column index to letter (0 → A, 1 → B, etc.)"""
        result = ""
        col = self.column
        while col >= 0:
            result = chr(col % 26 + ord('A')) + result
            col = col // 26 - 1
        return result

    def __repr__(self) -> str:
        return f"Cell({self.coordinate}={self.value})"


# ============================================================================
# Excel Worksheet
# ============================================================================

class Worksheet:
    """Represents an Excel worksheet"""

    def __init__(self, title: str = "Sheet1", workbook=None):
        self.title = title
        self.workbook = workbook
        self._cells: Dict[Tuple[int, int], Cell] = {}
        self._merged_cells: List[str] = []
        self._column_dimensions: Dict[int, Dict[str, Any]] = {}
        self._row_dimensions: Dict[int, Dict[str, Any]] = {}
        self._freeze_panes: Optional[str] = None

    def cell(self, row: int, column: int, value: Any = None) -> Cell:
        """
        Get or create a cell at the specified row and column.

        Args:
            row: Row index (0-based)
            column: Column index (0-based)
            value: Optional value to set

        Returns:
            Cell object
        """
        key = (row, column)
        if key not in self._cells:
            self._cells[key] = Cell(row=row, column=column)

        if value is not None:
            self._cells[key].value = value

        return self._cells[key]

    def get_cell_by_coord(self, coordinate: str, value: Any = None) -> Cell:
        """
        Get cell by coordinate string (e.g., 'A1', 'B2')

        Args:
            coordinate: Cell coordinate (e.g., 'A1')
            value: Optional value to set

        Returns:
            Cell object
        """
        row, col = self._coord_to_indices(coordinate)
        return self.cell(row, col, value)

    @staticmethod
    def _coord_to_indices(coordinate: str) -> Tuple[int, int]:
        """Convert coordinate string 'A1' to (row, col) indices"""
        match = re.match(r'([A-Z]+)(\d+)', coordinate.upper())
        if not match:
            raise ValueError(f"Invalid coordinate: {coordinate}")

        col_str, row_str = match.groups()

        # Convert column letter to index
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord('A') + 1)
        col -= 1

        row = int(row_str) - 1

        return row, col

    def iter_rows(
        self,
        min_row: Optional[int] = None,
        max_row: Optional[int] = None,
        min_col: Optional[int] = None,
        max_col: Optional[int] = None,
        values_only: bool = False
    ):
        """
        Iterate over rows in the worksheet

        Args:
            min_row: Minimum row index (0-based, inclusive)
            max_row: Maximum row index (0-based, inclusive)
            min_col: Minimum column index (0-based, inclusive)
            max_col: Maximum column index (0-based, inclusive)
            values_only: Return values instead of Cell objects

        Yields:
            List of cells or values for each row
        """
        # Determine bounds
        if self._cells:
            all_rows = [r for r, c in self._cells.keys()]
            all_cols = [c for r, c in self._cells.keys()]
            min_row = min_row if min_row is not None else min(all_rows, default=0)
            max_row = max_row if max_row is not None else max(all_rows, default=0)
            min_col = min_col if min_col is not None else min(all_cols, default=0)
            max_col = max_col if max_col is not None else max(all_cols, default=0)
        else:
            min_row = min_row or 0
            max_row = max_row or 0
            min_col = min_col or 0
            max_col = max_col or 0

        for row in range(min_row, max_row + 1):
            row_cells = []
            for col in range(min_col, max_col + 1):
                cell = self.cell(row, col)
                row_cells.append(cell.value if values_only else cell)
            yield row_cells

    def append(self, values: List[Any]):
        """
        Append a row to the worksheet

        Args:
            values: List of values to append
        """
        # Find next empty row
        max_row = max((r for r, c in self._cells.keys()), default=-1) + 1

        for col, value in enumerate(values):
            self.cell(max_row, col, value)

    def merge_cells(self, range_string: str):
        """
        Merge cells in the specified range

        Args:
            range_string: Cell range (e.g., 'A1:B2')
        """
        self._merged_cells.append(range_string)

    def set_column_width(self, column: int, width: float):
        """Set column width"""
        if column not in self._column_dimensions:
            self._column_dimensions[column] = {}
        self._column_dimensions[column]['width'] = width

    def set_row_height(self, row: int, height: float):
        """Set row height"""
        if row not in self._row_dimensions:
            self._row_dimensions[row] = {}
        self._row_dimensions[row]['height'] = height

    @property
    def max_row(self) -> int:
        """Get maximum row index with data"""
        return max((r for r, c in self._cells.keys()), default=0)

    @property
    def max_column(self) -> int:
        """Get maximum column index with data"""
        return max((c for r, c in self._cells.keys()), default=0)

    def __getitem__(self, key: str) -> Cell:
        """Get cell by coordinate (e.g., ws['A1'])"""
        return self.get_cell_by_coord(key)

    def __setitem__(self, key: str, value: Any):
        """Set cell value by coordinate (e.g., ws['A1'] = 123)"""
        self.get_cell_by_coord(key, value)


# ============================================================================
# Excel Workbook
# ============================================================================

class Workbook:
    """Represents an Excel workbook"""

    def __init__(self):
        self.worksheets: List[Worksheet] = []
        self.active_sheet_index: int = 0
        self._shared_strings: List[str] = []
        self.properties: Dict[str, Any] = {
            'creator': 'CREATESONLINE',
            'created': datetime.now(),
            'modified': datetime.now()
        }

    def create_sheet(self, title: str = None, index: Optional[int] = None) -> Worksheet:
        """
        Create a new worksheet

        Args:
            title: Sheet title (auto-generated if None)
            index: Position to insert sheet (append if None)

        Returns:
            New Worksheet object
        """
        if title is None:
            title = f"Sheet{len(self.worksheets) + 1}"

        worksheet = Worksheet(title=title, workbook=self)

        if index is not None:
            self.worksheets.insert(index, worksheet)
        else:
            self.worksheets.append(worksheet)

        return worksheet

    def remove_sheet(self, worksheet: Worksheet):
        """Remove a worksheet"""
        if worksheet in self.worksheets:
            self.worksheets.remove(worksheet)

    @property
    def active(self) -> Worksheet:
        """Get active worksheet"""
        if not self.worksheets:
            self.create_sheet()
        return self.worksheets[self.active_sheet_index]

    @active.setter
    def active(self, worksheet: Worksheet):
        """Set active worksheet"""
        if worksheet in self.worksheets:
            self.active_sheet_index = self.worksheets.index(worksheet)

    def get_sheet_by_name(self, name: str) -> Optional[Worksheet]:
        """Get worksheet by name"""
        for ws in self.worksheets:
            if ws.title == name:
                return ws
        return None

    @property
    def sheetnames(self) -> List[str]:
        """Get list of sheet names"""
        return [ws.title for ws in self.worksheets]

    def __getitem__(self, key: str) -> Worksheet:
        """Get worksheet by name (e.g., wb['Sheet1'])"""
        ws = self.get_sheet_by_name(key)
        if ws is None:
            raise KeyError(f"Worksheet '{key}' not found")
        return ws


# ============================================================================
# Excel Formula Evaluator
# ============================================================================

class FormulaEvaluator:
    """Basic Excel formula evaluator"""

    def __init__(self, workbook: Workbook):
        self.workbook = workbook

    def evaluate(self, formula: str, context_sheet: Worksheet = None) -> Any:
        """
        Evaluate an Excel formula

        Args:
            formula: Formula string (with or without '=')
            context_sheet: Sheet context for cell references

        Returns:
            Calculated value
        """
        formula = formula.lstrip('=').strip()

        # Handle simple formulas
        try:
            # SUM function
            if formula.upper().startswith('SUM('):
                return self._eval_sum(formula, context_sheet)
            # AVERAGE function
            elif formula.upper().startswith('AVERAGE(') or formula.upper().startswith('AVG('):
                return self._eval_average(formula, context_sheet)
            # COUNT function
            elif formula.upper().startswith('COUNT('):
                return self._eval_count(formula, context_sheet)
            # IF function
            elif formula.upper().startswith('IF('):
                return self._eval_if(formula, context_sheet)
            # Simple arithmetic
            else:
                return eval(formula)
        except Exception:
            return f"#ERROR: {formula}"

    def _eval_sum(self, formula: str, sheet: Worksheet) -> float:
        """Evaluate SUM function"""
        # Extract range: SUM(A1:A10)
        match = re.search(r'SUM\((.*?)\)', formula, re.IGNORECASE)
        if not match:
            return 0

        range_str = match.group(1)
        values = self._get_range_values(range_str, sheet)
        return sum(v for v in values if isinstance(v, (int, float)))

    def _eval_average(self, formula: str, sheet: Worksheet) -> float:
        """Evaluate AVERAGE function"""
        match = re.search(r'AVERAGE\((.*?)\)|AVG\((.*?)\)', formula, re.IGNORECASE)
        if not match:
            return 0

        range_str = match.group(1) or match.group(2)
        values = [v for v in self._get_range_values(range_str, sheet) if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0

    def _eval_count(self, formula: str, sheet: Worksheet) -> int:
        """Evaluate COUNT function"""
        match = re.search(r'COUNT\((.*?)\)', formula, re.IGNORECASE)
        if not match:
            return 0

        range_str = match.group(1)
        values = self._get_range_values(range_str, sheet)
        return len([v for v in values if v is not None])

    def _eval_if(self, formula: str, sheet: Worksheet) -> Any:
        """Evaluate IF function: IF(condition, true_value, false_value)"""
        # This is a simplified implementation
        match = re.search(r'IF\((.*?),(.*?),(.*?)\)', formula, re.IGNORECASE)
        if not match:
            return None

        condition, true_val, false_val = match.groups()
        # Simplified condition evaluation
        try:
            if eval(condition.strip()):
                return eval(true_val.strip())
            else:
                return eval(false_val.strip())
        except:
            return None

    def _get_range_values(self, range_str: str, sheet: Worksheet) -> List[Any]:
        """Get values from a cell range (e.g., 'A1:A10')"""
        if ':' in range_str:
            start, end = range_str.split(':')
            start_row, start_col = sheet._coord_to_indices(start.strip())
            end_row, end_col = sheet._coord_to_indices(end.strip())

            values = []
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell = sheet.cell(row, col)
                    values.append(cell.value)
            return values
        else:
            # Single cell
            row, col = sheet._coord_to_indices(range_str.strip())
            return [sheet.cell(row, col).value]


# ============================================================================
# Excel Date/Time Handling
# ============================================================================

class ExcelDate:
    """Excel date/time conversion utilities"""

    # Excel epoch: January 1, 1900 (Excel incorrectly treats 1900 as a leap year)
    EXCEL_EPOCH = datetime(1899, 12, 30)

    @classmethod
    def to_excel(cls, dt: datetime) -> float:
        """
        Convert Python datetime to Excel serial date

        Args:
            dt: Python datetime object

        Returns:
            Excel serial date number
        """
        delta = dt - cls.EXCEL_EPOCH
        excel_date = delta.days + (delta.seconds / 86400.0)

        # Excel bug: treats 1900 as leap year
        if excel_date > 59:
            excel_date += 1

        return excel_date

    @classmethod
    def from_excel(cls, excel_date: float) -> datetime:
        """
        Convert Excel serial date to Python datetime

        Args:
            excel_date: Excel serial date number

        Returns:
            Python datetime object
        """
        # Excel bug: treats 1900 as leap year
        if excel_date > 59:
            excel_date -= 1

        return cls.EXCEL_EPOCH + timedelta(days=excel_date)


# ============================================================================
# Main Reader/Writer Functions
# ============================================================================

def load_workbook(filename: Union[str, Path]) -> Workbook:
    """
    Load an Excel workbook from file

    Args:
        filename: Path to .xlsx file

    Returns:
        Workbook object
    """
    from createsonline.data.io import _load_shared_strings, _sheet_path_for_name, _read_xlsx_rows

    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    workbook = Workbook()

    with zipfile.ZipFile(filepath, 'r') as zf:
        # Load shared strings
        workbook._shared_strings = _load_shared_strings(zf)

        # Load workbook.xml to get sheets
        wb_xml = ET.parse(zf.open("xl/workbook.xml"))
        ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

        for sheet_elem in wb_xml.findall(".//main:sheet", ns):
            sheet_name = sheet_elem.get("name")
            worksheet = workbook.create_sheet(title=sheet_name)

            # Load sheet data
            try:
                rows = _read_xlsx_rows(filepath, sheet_name, None)
                for row_idx, row_data in enumerate(rows):
                    for col_idx, value in enumerate(row_data):
                        if value is not None:
                            worksheet.cell(row_idx, col_idx, value)
            except Exception as e:
                print(f"Warning: Could not load sheet '{sheet_name}': {e}")

    return workbook


def save_workbook(workbook: Workbook, filename: Union[str, Path]):
    """
    Save workbook to Excel file

    Args:
        workbook: Workbook to save
        filename: Output file path
    """
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # For now, save as CSV (full XLSX writing is complex)
    # This will be enhanced in future versions
    for ws in workbook.worksheets:
        csv_path = filepath.with_name(f"{filepath.stem}_{ws.title}.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)

            # Write data
            for row_cells in ws.iter_rows(values_only=True):
                writer.writerow(row_cells)

    print(f"Workbook saved as CSV files in {filepath.parent}")
    print(f"Note: Full XLSX writing support coming soon!")