"""
CREATESONLINE Internal Data Structures Module

Pure Python data manipulation library with zero external dependencies.
Lightweight replacement for Pandas with AI-native features.

NEW: Advanced Excel Support!
- Full .xlsx reading and writing
- Cell formatting (fonts, colors, borders, alignment)
- Formula support and evaluation
- Multiple worksheets
- Date/time handling
- Cell merging and styling

All with ZERO external dependencies - no openpyxl or pandas needed!
"""

from .dataframe import CreatesonlineDataFrame
from .series import CreatesonlineSeries
from .io import read_csv, read_json, to_csv, to_json, read_excel, to_excel

# Advanced Excel support
from .excel import (
    Workbook,
    Worksheet,
    Cell,
    CellStyle,
    Font,
    Fill,
    Border,
    Alignment,
    Color,
    FormulaEvaluator,
    ExcelDate,
    load_workbook,
    HorizontalAlignment,
    VerticalAlignment,
    BorderStyle,
    PatternFill
)
from .excel_writer import save_workbook

__all__ = [
    # DataFrames and Series
    'CreatesonlineDataFrame',
    'CreatesonlineSeries',

    # CSV and JSON I/O
    'read_csv',
    'read_json',
    'to_csv',
    'to_json',

    # Excel I/O
    'read_excel',
    'to_excel',

    # Advanced Excel Classes
    'Workbook',
    'Worksheet',
    'Cell',
    'CellStyle',
    'Font',
    'Fill',
    'Border',
    'Alignment',
    'Color',
    'FormulaEvaluator',
    'ExcelDate',
    'load_workbook',
    'save_workbook',

    # Excel Enums
    'HorizontalAlignment',
    'VerticalAlignment',
    'BorderStyle',
    'PatternFill',
]

# Convenience aliases
DataFrame = CreatesonlineDataFrame
Series = CreatesonlineSeries