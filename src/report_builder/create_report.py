import os, io
import re
import sys
import importlib
from pathlib import Path
import pandas as pd
import toml
from xlsxwriter.utility import xl_cell_to_rowcol
from xlsxwriter.utility import xl_rowcol_to_cell

# -----------------------------
# Data loading helpers
# -----------------------------

def load_toml(path):
    return toml.load(path)

def load_image(source: dict,
                   base_dir: Path | None = None,
                   func_registry: dict[str, callable] | None = None) -> pd.DataFrame:
    """
    Load an image from a source dict.
    Supports: function.
    """
    stype = source.get("type")

    base_dir = Path(base_dir) if base_dir else Path.cwd()

    if stype in ["gif", "jpg", "png", "tif"]:
        path = os.path.expandvars(source["path"])
        path = (base_dir / path).resolve() if not os.path.isabs(path) else Path(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"The file '{path}' was not found.")

        with open(path, 'rb') as f:
            img = io.BytesIO(f.read())

        return img

    elif stype in {"function", "callable", "python"}:
        # Priority 1: registry name
        if "registry" in source and func_registry:
            reg_name = source["registry"]
            if reg_name not in func_registry:
                raise KeyError(f"Function '{reg_name}' not found in func_registry.")
            func = func_registry[reg_name]
        # Priority 2: dotted path like "pkg.module:function" or "pkg.module.func"
        elif "dotted" in source:
            dotted = source["dotted"]

            func = resolve_callable(dotted, base_dir=base_dir)
        else:
            # Optional legacy: module + function
            if "module" in source and "function" in source:
                dotted = f"{source['module']}.{source['function']}"
                func = resolve_callable(dotted, base_dir=base_dir)
            else:
                raise ValueError("Function source requires 'registry' or 'dotted' (or 'module'+'function').")

        kwargs = source.get("kwargs", {}) or {}
        result = func(**kwargs)

    return result
        
def load_dataframe(source: dict,
                   base_dir: Path | None = None,
                   func_registry: dict[str, callable] | None = None) -> pd.DataFrame:
    """
    Load a DataFrame from a source dict.
    Supports: csv, excel, function.
    """
    stype = source.get("type")

    base_dir = Path(base_dir) if base_dir else Path.cwd()

    if stype == "csv":
        path = os.path.expandvars(source["path"])
        path = (base_dir / path).resolve() if not os.path.isabs(path) else Path(path)
        return pd.read_csv(path)

    elif stype == "excel":
        path = os.path.expandvars(source["path"])
        path = (base_dir / path).resolve() if not os.path.isabs(path) else Path(path)
        sheet = source.get("sheet")
        return pd.read_excel(path, sheet_name=sheet)

    elif stype in {"function", "callable", "python"}:
        # Priority 1: registry name
        if "registry" in source and func_registry:
            reg_name = source["registry"]
            if reg_name not in func_registry:
                raise KeyError(f"Function '{reg_name}' not found in func_registry.")
            func = func_registry[reg_name]
        # Priority 2: dotted path like "pkg.module:function" or "pkg.module.func"
        elif "dotted" in source:
            dotted = source["dotted"]

            func = resolve_callable(dotted, base_dir=base_dir)
        else:
            # Optional legacy: module + function
            if "module" in source and "function" in source:
                dotted = f"{source['module']}.{source['function']}"
                func = resolve_callable(dotted, base_dir=base_dir)
            else:
                raise ValueError("Function source requires 'registry' or 'dotted' (or 'module'+'function').")

        kwargs = source.get("kwargs", {}) or {}
        result = func(**kwargs)

        # Accept a DataFrame or a dict[str, DataFrame]
        if isinstance(result, pd.DataFrame):
            return result
        if isinstance(result, dict):
            key = source.get("key")
            if key is None:
                raise TypeError("Function returned a dict; please specify source.key in TOML.")
            df = result.get(key)
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Function returned dict but value for key '{key}' is not a DataFrame.")
            return df

        raise TypeError(f"Function '{func.__name__}' did not return a pandas DataFrame.")

    else:
        raise ValueError(f"Unsupported source.type='{stype}'.")

def resolve_callable(dotted: str, base_dir: Path | None = None):
    """
    Resolve a dotted path to a callable.
    Supports 'pkg.mod:func' or 'pkg.mod.func'.
    """
    dotted = dotted.replace(":", ".")
    if "." not in dotted:
        raise ValueError(f"Invalid dotted path '{dotted}'. Expected 'package.module:function'.")

    module_path, func_name = dotted.rsplit(".", 1)

    # Allow TOML to extend sys.path for local packages
    # (We'll add to sys.path in build_from_toml)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    if not callable(func):
        raise AttributeError(f"'{dotted}' is not a callable.")
    return func

# -----------------------------
# Formatting helpers
# -----------------------------
def infer_format_name(col_name: str, matchers: list[tuple[re.Pattern, str]], default_name: str | None) -> str | None:
    """Return the first matching format name for a column using regex matchers."""
    for pattern, fmt_name in matchers:
        if pattern.search(col_name):
            return fmt_name
    return default_name

def build_format(workbook, spec: dict):
    """Create (and return) a XlsxWriter format from a spec dict (e.g., {'num_format': '£#,##0'})."""
    fmt_args = {}
    if spec.get("num_format"):
        fmt_args["num_format"] = spec["num_format"]
        
    # you can add more properties here if you like, e.g. align, bold, font_color, etc.

    return workbook.add_format(fmt_args)

def autosize_width(series: pd.Series, min_w=10, max_w=40) -> int:
    """Crude auto width based on header and a sample of values."""
    header = str(series.name) if series.name is not None else ""
    max_len = len(header)
    # Sample values to avoid massive loops on big data
    sample = series.dropna().astype(str).head(200)
    for val in sample:
        max_len = max(max_len, len(val))
    # Heuristic: Excel character width is not exact; add a little padding
    width = min(max_w, max(min_w, max_len + 2))
    return width

# -----------------------------
# Excel writing helpers (XlsxWriter)
# -----------------------------
def write_title(worksheet, row, col, text, fmt):
    worksheet.write(row, col, text, fmt)
    return row + 2  # one line for title + one blank line

def dataframe_to_table_data(df: pd.DataFrame):
    """Convert DataFrame to list-of-lists with Python scalars, with NaNs -> None."""
    clean = df.copy()
    # Replace NaN/NA with None so cells are blank, not 'nan'
    clean = clean.where(pd.notnull(clean), None)
    # Ensure Python native types (especially for numpy types)
    data = clean.values.tolist()
    return data

def add_excel_table(worksheet, df: pd.DataFrame, start_row: int, start_col: int, table_style: str):
    """
    Add a native Excel Table with header and data.
    Returns (end_row, end_col), inclusive 0-based positions of the table body.
    """
    nrows, ncols = df.shape
    data = dataframe_to_table_data(df)
    columns = [{"header": str(c)} for c in df.columns]

    first_row = start_row
    first_col = start_col
    last_row = first_row + nrows  # includes header row + data rows
    last_col = first_col + ncols - 1

    worksheet.add_table(
        first_row, first_col, last_row, last_col,
        {
            "data": data,
            "columns": columns,
            "style": table_style,
            "banded_rows": True
        }
    )
    return last_row, last_col

def set_column_formats_and_widths(worksheet, df: pd.DataFrame, start_row: int, start_col: int,
                                  workbook, cfg_formats: dict, table_cfg: dict):
    """
    Apply column formats and widths:
      - Use matchers to pick named format → num_format and default width
      - Allow per-table overrides with 'column_widths'
      - Fallback to defaults
    """
    default_spec   = cfg_formats.get("default", {"num_format": "", "width": 14})
    named          = cfg_formats.get("named", {})
    matcher_specs  = cfg_formats.get("matchers", {})

    # Compile matchers in insertion order
    matchers = []
    for pattern, fmt_name in matcher_specs.items():
        matchers.append((re.compile(pattern), fmt_name))

    # Cache XlsxWriter format objects by name
    fmt_cache = {}

    def get_format_obj(fmt_name: str | None):
        if not fmt_name:
            key = "__default__"
            if key not in fmt_cache:
                fmt_cache[key] = build_format(workbook, default_spec)
            return fmt_cache[key]
        if fmt_name not in fmt_cache:
            spec = named.get(fmt_name, default_spec)
            fmt_cache[fmt_name] = build_format(workbook, spec)
        return fmt_cache[fmt_name]

    # Set column widths
    col_width_overrides = table_cfg.get("column_widths", {}) or {}
        
    for j, col in enumerate(df.columns):
        # Pick a format name using matchers
        fmt_name = infer_format_name(str(col), matchers, default_name=None)
        fmt_obj  = get_format_obj(fmt_name)

        # Width: override > named width > default width > autosize
        width = None
        if str(col) in col_width_overrides:
            width = col_width_overrides[str(col)]
        elif fmt_name and fmt_name in named and "width" in named[fmt_name]:
            width = named[fmt_name]["width"]
        elif "width" in default_spec:
            width = default_spec["width"]
        else:
            width = autosize_width(df[col])

        worksheet.set_column(start_col + j, start_col + j, width)

    # Set cell formatting
    rows, cols = df.shape
    for r in range(rows):      
        for c, col in enumerate(df.columns):
            # Pick a format name using matchers
            fmt_name = infer_format_name(str(col), matchers, default_name=None)
            fmt_obj  = get_format_obj(fmt_name)
        
            worksheet.write(start_row + 1 + r, start_col + c, df.iat[r, c], fmt_obj)

# -----------------------------
# Main build function
# -----------------------------
def build_from_toml(config_path: str,
                    func_registry: dict[str, callable] | None = None,
                    base_dir: str | Path | None = None):

    cfg = load_toml(config_path)
    base_dir = Path(base_dir) if base_dir else Path(config_path).resolve().parent

    # Allow TOML to inject pythonpath entries, relative to base_dir
    for p in (cfg.get("imports", {}).get("pythonpath", []) or []):
        p_abs = (base_dir / p).resolve()
        if str(p_abs) not in sys.path:
            sys.path.insert(0, str(p_abs))

    output = cfg["workbook"]["output"]
    defaults = cfg.get("defaults", {})
    cfg_formats = cfg.get("formats", {})
    sheets = cfg.get("sheets", [])

    # Setup workbook
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        title_fmt    = workbook.add_format({"bold": True, "font_size": defaults.get("title_font_size", 14)})
        subtitle_fmt = workbook.add_format({"bold": True, "font_size": defaults.get("subtitle_font_size", 12), "font_color": "#000000"})
        footnote_fmt = workbook.add_format({"italic": True, "font_size": defaults.get("footnote_font_size", 9), "font_color": "#555555"})
        protective_marking_fmt = workbook.add_format({"align": "center_across", "bold": True, "font_size": 18, "font_color": "#FF0000"})
        tbl_hdr = workbook.add_format({'bold': True, 'bg_color': '#000000', 'border': 1, 'align': 'center'})

        default_table_style = defaults.get("table_style", "Table Style Light 1")
        spacing_rows = int(defaults.get("spacing_rows", 2))

        # Iterate through sheets
        for sheet_cfg in sheets:
            # Add sheet
            sheet_name = sheet_cfg["name"]
            worksheet = workbook.add_worksheet(sheet_name)
            writer.sheets[sheet_name] = worksheet

            if sheet_cfg.get("header"):
                worksheet.set_header(sheet_cfg["header"]) 

            if sheet_cfg.get("footer"):
                worksheet.set_footer(sheet_cfg["footer"])

            current_row = 0
            current_col = 0

            # Add protective marking
            if sheet_cfg.get("protective_marking"):
                if sheet_cfg.get("protective_marking_span"):  
                    span = sheet_cfg["protective_marking_span"]
                else:
                    span = 10
                    
                for col in range(0, span):
                    worksheet.write_blank(0, col, None, protective_marking_fmt)
                    worksheet.write(current_row, current_col, sheet_cfg["protective_marking"], protective_marking_fmt)
                    worksheet.set_row(0, 24)

                current_row += 2
                    
            if sheet_cfg.get("title"):
                worksheet.write(current_row, current_col, sheet_cfg["title"], title_fmt)
                current_row += 2

            # Iterate through tables
            for t_cfg in sheet_cfg.get("tables", []):

                start_row = current_row
                start_col = current_col
                if t_cfg.get("start_cell"):
                    r, c = xl_cell_to_rowcol(t_cfg["start_cell"])
                    start_row, start_col = r, c

                df = load_dataframe(t_cfg["source"][0], base_dir=base_dir, func_registry=func_registry)

                # Add table and title
                if df is None or df.empty:
                    if t_cfg.get("title"):
                        worksheet.write(start_row, start_col, t_cfg["title"], subtitle_fmt)
                        start_row += 1
                    worksheet.write(start_row, start_col, "(no data)")
                    current_row = start_row + spacing_rows + 1
                    continue
                if t_cfg.get("title"):
                    worksheet.write(start_row, start_col, t_cfg["title"], subtitle_fmt)
                    print(t_cfg["title"])
                    start_row += 1

                end_row, end_col = add_excel_table(worksheet, df, start_row, start_col,
                                                   t_cfg.get("style", default_table_style))

                set_column_formats_and_widths(worksheet, df, start_row, start_col, workbook, cfg_formats, t_cfg)
                
                # Apply table header format
                for col, name in enumerate(df.columns):
                    worksheet.write(start_row, start_col + col, name, tbl_hdr)

                current_row = end_row + 1

                # Add table notes
                if t_cfg.get("table_notes"):
                    for line in t_cfg["table_notes"]:
                        worksheet.write(current_row, start_col, line, footnote_fmt)
                        current_row += 1

                current_row = current_row + 1 + spacing_rows
                current_col = 0

            # Add charts
            for t_cfg in sheet_cfg.get("charts", []):
                start_row = current_row
                start_col = current_col
                if t_cfg.get("start_cell"):
                    r, c = xl_cell_to_rowcol(t_cfg["start_cell"])
                    start_row, start_col = r, c

                if t_cfg.get("title"):
                    worksheet.write(start_row, start_col, t_cfg["title"], subtitle_fmt)
                    start_row += 1

                if t_cfg.get("x_scale"):
                    x_scale = t_cfg["x_scale"]
                else:
                    x_scale = 1.0

                if t_cfg.get("y_scale"):
                    y_scale = t_cfg["y_scale"]
                else:
                    y_scale = 1.0                
                
                # Insert the image
                img = load_image(t_cfg["source"][0], base_dir=base_dir, func_registry=func_registry)                
                worksheet.insert_image(xl_rowcol_to_cell(start_row, start_col), 'chart.png', {'image_data': img, 'x_scale': x_scale, 'y_scale': y_scale})

                # Add chart notes
                if t_cfg.get("chart_notes"):
                    r, c = xl_cell_to_rowcol(t_cfg["chart_notes_start_cell"])
                    current_row, start_col = r, c
                    for line in t_cfg["chart_notes"]:                        
                        worksheet.write(current_row, start_col, line, footnote_fmt)
                        current_row += 1

                current_row = current_row + 1 + spacing_rows
                current_col = 0

            # Add sheet footnotes
            if sheet_cfg.get("footnotes"):
                for line in sheet_cfg["footnotes"]:
                    worksheet.write(current_row, 0, line, footnote_fmt)
                    current_row += 1
                    
            current_row = current_row + 1 + spacing_rows
            current_col = 0

    print(f"Workbook written: {output}")

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    # Example: python create_report.py
    # Ensure 'report_config.toml' is in the same folder, or pass an absolute path.
    build_from_toml("report_config.toml")
