"""
CREATESONLINE Data I/O Operations

Pure Python data input/output operations.
CSV and JSON reading/writing functionality.
"""

import json
import csv
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from .dataframe import CreatesonlineDataFrame
from .excel import load_workbook, Workbook
from .excel_writer import save_workbook
from .excel import load_workbook, Workbook
from .excel_writer import save_workbook


def read_csv(
    filepath: Union[str, Path],
    sep: str = ',',
    header: Union[int, str, None] = 0,
    index_col: Optional[Union[int, str]] = None,
    usecols: Optional[List[Union[int, str]]] = None,
    skiprows: Optional[Union[int, List[int]]] = None,
    nrows: Optional[int] = None,
    encoding: str = 'utf-8'
) -> CreatesonlineDataFrame:
    """
    Read CSV file into CreatesonlineDataFrame
    
    Args:
        filepath: Path to CSV file
        sep: Field separator
        header: Row to use as column names (0 for first row, None for no header)
        index_col: Column to use as row index
        usecols: Columns to read
        skiprows: Rows to skip
        nrows: Number of rows to read
        encoding: File encoding
    
    Returns:
        CreatesonlineDataFrame with CSV data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding=encoding, newline='') as f:
        # Handle skiprows
        if skiprows:
            if isinstance(skiprows, int):
                for _ in range(skiprows):
                    next(f, None)
            else:
                lines_to_skip = set(skiprows)
                for i, line in enumerate(f):
                    if i not in lines_to_skip:
                        f.seek(0)
                        for _ in range(i):
                            next(f)
                        break
        
        reader = csv.reader(f, delimiter=sep)
        
        # Read all rows
        rows = []
        for i, row in enumerate(reader):
            rows.append(row)
            if nrows and i >= nrows - 1:
                break
        
        if not rows:
            return CreatesonlineDataFrame()
        
        # Handle header
        if header == 0 or header is True:
            columns = rows[0]
            data_rows = rows[1:]
        elif isinstance(header, int):
            columns = rows[header]
            data_rows = rows[header + 1:]
        elif header is None:
            columns = [f'col_{i}' for i in range(len(rows[0]))]
            data_rows = rows
        else:
            raise ValueError("Invalid header parameter")
        
        # Handle usecols
        if usecols:
            if all(isinstance(col, str) for col in usecols):
                # Column names
                col_indices = [columns.index(col) for col in usecols if col in columns]
                columns = [columns[i] for i in col_indices]
            else:
                # Column indices
                col_indices = [i for i in usecols if i < len(columns)]
                columns = [columns[i] for i in col_indices]
            
            data_rows = [[row[i] for i in col_indices] for row in data_rows]
        
        # Convert to appropriate types
        data = {}
        for i, col in enumerate(columns):
            col_data = []
            for row in data_rows:
                if i < len(row):
                    value = row[i].strip()
                    # Try to convert to number
                    if value == '':
                        col_data.append(None)
                    elif value.lower() in ('true', 'false'):
                        col_data.append(value.lower() == 'true')
                    else:
                        try:
                            if '.' in value:
                                col_data.append(float(value))
                            else:
                                col_data.append(int(value))
                        except ValueError:
                            col_data.append(value)
                else:
                    col_data.append(None)
            
            data[col] = col_data
        
        df = CreatesonlineDataFrame(data=data)
        
        # Handle index_col
        if index_col is not None:
            if isinstance(index_col, str):
                df = df.set_index(index_col)
            elif isinstance(index_col, int):
                col_name = columns[index_col]
                df = df.set_index(col_name)
        
        return df


def to_csv(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    sep: str = ',',
    index: bool = True,
    header: bool = True,
    encoding: str = 'utf-8'
) -> None:
    """
    Write CreatesonlineDataFrame to CSV file
    
    Args:
        df: DataFrame to write
        filepath: Output file path
        sep: Field separator
        index: Whether to write row index
        header: Whether to write column header
        encoding: File encoding
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f, delimiter=sep)
        
        # Write header
        if header:
            header_row = []
            if index:
                header_row.append('index')
            header_row.extend(df.columns)
            writer.writerow(header_row)
        
        # Write data rows
        for i in range(len(df.index)):
            row = []
            if index:
                row.append(df.index[i])
            
            for col in df.columns:
                value = df._data[col][i]
                row.append('' if value is None else str(value))
            
            writer.writerow(row)


def read_json(
    filepath: Union[str, Path],
    orient: str = 'records',
    encoding: str = 'utf-8'
) -> CreatesonlineDataFrame:
    """
    Read JSON file into CreatesonlineDataFrame
    
    Args:
        filepath: Path to JSON file
        orient: JSON orientation ('records', 'dict', 'list')
        encoding: File encoding
    
    Returns:
        CreatesonlineDataFrame with JSON data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding=encoding) as f:
        data = json.load(f)
    
    if orient == 'records':
        # List of {column: value} dicts
        return CreatesonlineDataFrame(data=data)
    elif orient == 'dict':
        # {column: [values]} dict
        return CreatesonlineDataFrame(data=data)
    elif orient == 'list':
        # {column: [values]} dict (same as dict)
        return CreatesonlineDataFrame(data=data)
    else:
        raise ValueError(f"Invalid orient: {orient}")


def to_json(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    orient: str = 'records',
    indent: Optional[int] = None,
    encoding: str = 'utf-8'
) -> None:
    """
    Write CreatesonlineDataFrame to JSON file
    
    Args:
        df: DataFrame to write
        filepath: Output file path
        orient: JSON orientation ('records', 'dict', 'list')
        indent: JSON indentation
        encoding: File encoding
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = df.to_dict(orient=orient)
    
    with open(filepath, 'w', encoding=encoding) as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)


def read_excel(
    filepath: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    header: Union[int, None] = 0,
    index_col: Optional[Union[int, str]] = None,
    usecols: Optional[List[Union[int, str]]] = None,
    skiprows: Optional[Union[int, List[int]]] = None,
    nrows: Optional[int] = None
) -> CreatesonlineDataFrame:
    """
    Read Excel file into CreatesonlineDataFrame
    
    Note: Uses the internal Workbook reader (no external deps). Styles/formulas remain
    in the Workbook; the DataFrame view focuses on values.
    
    Args:
        filepath: Path to Excel file
        sheet_name: Sheet name or index
        header: Row to use as column names
        index_col: Column to use as row index
        usecols: Columns to read
        skiprows: Rows to skip
        nrows: Number of rows to read
    
    Returns:
        CreatesonlineDataFrame with Excel data
    """
    import logging
    logger = logging.getLogger(__name__)
    filepath = Path(filepath)

    if filepath.suffix.lower() != ".xlsx":
        logger.warning("Excel reader only supports .xlsx. Falling back to CSV if available.")
        csv_path = filepath.with_suffix('.csv')
        if csv_path.exists():
            return read_csv(csv_path, header=header, index_col=index_col, usecols=usecols, skiprows=skiprows, nrows=nrows)
        raise ImportError("Unsupported Excel format (only .xlsx). Save as .xlsx or .csv.")

    # Use advanced workbook loader
    try:
        workbook = load_workbook(filepath)
    except Exception as exc:
        logger.error(f"Could not parse Excel file '{filepath}': {exc}")
        csv_path = filepath.with_suffix('.csv')
        if csv_path.exists():
            logger.info(f"Falling back to CSV: {csv_path}")
            return read_csv(csv_path, header=header, index_col=index_col, usecols=usecols, skiprows=skiprows, nrows=nrows)
        raise

    # Resolve worksheet
    if isinstance(sheet_name, int):
        ws = workbook.worksheets[sheet_name]
    else:
        ws = None
        for sh in workbook.worksheets:
            if sh.title == sheet_name:
                ws = sh
                break
        if ws is None:
            ws = workbook.active

    # Extract rows
    rows = []
    for r_idx, row_cells in enumerate(ws.iter_rows(values_only=True)):
        if nrows is not None and r_idx >= nrows:
            break
        rows.append(list(row_cells))

    if not rows:
        return CreatesonlineDataFrame()

    # Apply skiprows
    if skiprows:
        if isinstance(skiprows, int):
            rows = rows[skiprows:]
        else:
            rows = [r for idx, r in enumerate(rows) if idx not in set(skiprows)]

    # Apply usecols by index or name after header processed
    # Handle header
    if header == 0 or header is True:
        columns = rows[0]
        data_rows = rows[1:]
    elif isinstance(header, int):
        columns = rows[header]
        data_rows = rows[header + 1:]
    elif header is None:
        columns = [f'col_{i}' for i in range(len(rows[0]))]
        data_rows = rows
    else:
        raise ValueError("Invalid header parameter")

    # Normalize column count
    max_len = max(len(r) for r in data_rows) if data_rows else len(columns)
    columns = columns[:max_len]

    # Handle usecols
    if usecols:
        if all(isinstance(col, str) for col in usecols):
            col_indices = [columns.index(col) for col in usecols if col in columns]
            columns = [columns[i] for i in col_indices]
        else:
            col_indices = [i for i in usecols if i < len(columns)]
            columns = [columns[i] for i in col_indices]
        data_rows = [[row[i] if i < len(row) else None for i in col_indices] for row in data_rows]

    data = {col: [] for col in columns}
    for row in data_rows:
        for i, col in enumerate(columns):
            data[col].append(row[i] if i < len(row) else None)

    df = CreatesonlineDataFrame(data=data)

    if index_col is not None:
        if isinstance(index_col, str) and index_col in df.columns:
            df = df.set_index(index_col)
        elif isinstance(index_col, int) and index_col < len(columns):
            df = df.set_index(columns[index_col])

    return df


def to_excel(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    sheet_name: str = "Sheet1",
    index: bool = True,
    header: bool = True
) -> None:
    """
    Write CreatesonlineDataFrame to Excel file
    
    Note: Uses the internal Workbook writer (no external deps). Styles are not inferred
    from DataFrame; write-then-style via Workbook if needed.
    """
    filepath = Path(filepath)
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    cols = list(df.columns)
    if index:
        cols = ["index"] + cols

    if header:
        ws.append(cols)

    for i in range(len(df.index)):
        row = []
        if index:
            row.append(df.index[i])
        for col in df.columns:
            row.append(df._data[col][i])
        ws.append(row)

    save_workbook(wb, filepath)

# =====================================================================
# Minimal XLSX reader (no external dependencies)
# =====================================================================
import zipfile
import xml.etree.ElementTree as ET
import re


_CELL_REF_RE = re.compile(r"([A-Za-z]+)([0-9]+)")


def _col_letter_to_index(col: str) -> int:
    idx = 0
    for c in col:
        idx = idx * 26 + (ord(c.upper()) - ord('A') + 1)
    return idx - 1


def _load_shared_strings(zf: zipfile.ZipFile) -> list:
    try:
        with zf.open("xl/sharedStrings.xml") as f:
            tree = ET.parse(f)
        strings = []
        for si in tree.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
            text_parts = []
            for t in si.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"):
                text_parts.append(t.text or "")
            strings.append("".join(text_parts))
        return strings
    except KeyError:
        return []


def _sheet_path_for_name(zf: zipfile.ZipFile, sheet_name: Union[str, int]) -> str:
    # default sheet1
    workbook = ET.parse(zf.open("xl/workbook.xml"))
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets = workbook.findall(".//main:sheet", ns)
    if isinstance(sheet_name, int):
        target = sheets[sheet_name]
    else:
        target = next(s for s in sheets if s.get("name") == sheet_name)
    rid = target.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    rels = ET.parse(zf.open("xl/_rels/workbook.xml.rels"))
    nsr = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
    for rel in rels.findall(".//rel:Relationship", nsr):
        if rel.get("Id") == rid:
            return f"xl/{rel.get('Target')}"
    return "xl/worksheets/sheet1.xml"


def _read_xlsx_rows(filepath: Path, sheet_name: Union[str, int], max_rows: Optional[int]) -> list:
    rows = {}
    with zipfile.ZipFile(filepath, "r") as zf:
        shared = _load_shared_strings(zf)
        sheet_path = _sheet_path_for_name(zf, sheet_name)
        with zf.open(sheet_path) as f:
            tree = ET.parse(f)
        ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for row in tree.findall(".//main:sheetData/main:row", ns):
            r_index = int(row.get("r", "0")) - 1
            if max_rows is not None and r_index >= max_rows:
                break
            for c in row.findall("main:c", ns):
                ref = c.get("r", "")
                m = _CELL_REF_RE.match(ref)
                if not m:
                    continue
                col_idx = _col_letter_to_index(m.group(1))
                cell_type = c.get("t")
                v = c.find("main:v", ns)
                value = None
                if v is not None:
                    raw = v.text
                    if cell_type == "s":
                        try:
                            value = shared[int(raw)]
                        except Exception:
                            value = raw
                    else:
                        # Try numeric conversion
                        try:
                            value = float(raw) if "." in raw else int(raw)
                        except Exception:
                            value = raw
                rows.setdefault(r_index, {})[col_idx] = value

    # Normalize into list of lists
    if not rows:
        return []
    max_col = max(max(cols.keys()) for cols in rows.values()) if rows else -1
    max_row = max(rows.keys())
    matrix = []
    for r in range(max_row + 1):
        row_vals = []
        cols = rows.get(r, {})
        for c in range(max_col + 1):
            row_vals.append(cols.get(c))
        matrix.append(row_vals)
    return matrix


# Utility functions for data conversion
def from_dict(data: Dict[str, List[Any]]) -> CreatesonlineDataFrame:
    """Create DataFrame from dictionary"""
    return CreatesonlineDataFrame(data=data)


def from_records(records: List[Dict[str, Any]]) -> CreatesonlineDataFrame:
    """Create DataFrame from list of records"""
    return CreatesonlineDataFrame(data=records)


def concat(
    dataframes: List[CreatesonlineDataFrame],
    axis: int = 0,
    ignore_index: bool = False
) -> CreatesonlineDataFrame:
    """
    Concatenate multiple DataFrames
    
    Args:
        dataframes: List of DataFrames to concatenate
        axis: Axis to concatenate along (0=rows, 1=columns)
        ignore_index: Reset index in result
    
    Returns:
        Concatenated DataFrame
    """
    if not dataframes:
        return CreatesonlineDataFrame()
    
    result = dataframes[0].copy()
    
    for df in dataframes[1:]:
        result = result.concat(df, axis=axis)
    
    if ignore_index:
        result = result.reset_index(drop=True)
    
    return result


# Data validation utilities
def validate_dataframe(df: CreatesonlineDataFrame) -> Dict[str, Any]:
    """
    Validate DataFrame and return diagnostics
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Dictionary with validation results
    """
    return {
        'shape': df.shape,
        'columns': df.columns,
        'null_counts': {
            col: sum(1 for val in df._data[col] if val is None)
            for col in df.columns
        },
        'data_types': {
            col: type(df._data[col][0]).__name__ if df._data[col] else 'empty'
            for col in df.columns
        },
        'memory_usage_estimate': f"{df.size * 8} bytes",
        'duplicate_rows': 0,  # Would need to implement duplicate detection
        'is_valid': True
    }


def sample_data(df: CreatesonlineDataFrame, n: int = 5, random_state: Optional[int] = None) -> CreatesonlineDataFrame:
    """
    Sample n rows from DataFrame
    
    Args:
        df: DataFrame to sample from
        n: Number of rows to sample
        random_state: Random seed for reproducibility
    
    Returns:
        DataFrame with sampled rows
    """
    import random
    
    if random_state:
        random.seed(random_state)
    
    if n >= len(df):
        return df.copy()
    
    indices = random.sample(range(len(df)), n)
    indices.sort()
    
    new_data = {}
    for col in df.columns:
        new_data[col] = [df._data[col][i] for i in indices]
    
    new_index = [df.index[i] for i in indices]
    
    return CreatesonlineDataFrame(
        data=new_data,
        index=new_index
    )




