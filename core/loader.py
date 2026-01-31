import pandas as pd

INTERN_COLUMNS = [
    'Name', 'Sex', 'Qualification', 'University',
    'Year of Completion', 'National Identification Number', 'Nationality'
]

QUALIFICATION_COLUMNS = ['MBChB', 'BDS', 'B.PHARM', 'BSN', 'BSM']


def _read_excel_auto_header(path: str, key_columns: list[str], max_scan: int = 20) -> pd.DataFrame:
    """Read an Excel file, auto-detecting the header row by scanning for key columns."""
    # Try row 0 first (most common)
    for header_row in range(max_scan):
        try:
            df = pd.read_excel(path, header=header_row)
            df.columns = df.columns.astype(str).str.strip()
            if any(col in df.columns for col in key_columns):
                return df
        except Exception:
            continue

    raise ValueError(
        f"Could not find expected columns in first {max_scan} rows. "
        f"Looking for any of: {', '.join(key_columns)}"
    )


def load_interns(path: str) -> pd.DataFrame:
    df = _read_excel_auto_header(path, INTERN_COLUMNS)
    missing = [c for c in INTERN_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Interns file missing columns: {', '.join(missing)}")
    return df[INTERN_COLUMNS].copy()


def load_facilities(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (unpivoted facilities DataFrame, raw facilities DataFrame)."""
    key_cols = ['Internship Training Centre'] + QUALIFICATION_COLUMNS
    df = _read_excel_auto_header(path, key_cols)

    if 'Internship Training Centre' not in df.columns:
        raise ValueError("Facilities file missing 'Internship Training Centre' column.")

    present_quals = [q for q in QUALIFICATION_COLUMNS if q in df.columns]
    if not present_quals:
        raise ValueError(
            f"Facilities file has no qualification columns. Expected any of: {', '.join(QUALIFICATION_COLUMNS)}"
        )

    raw = df[['Internship Training Centre'] + present_quals].copy()

    unpivoted = df.melt(
        id_vars=['Internship Training Centre'],
        value_vars=present_quals,
        var_name='Qualification',
        value_name='Available Positions'
    )
    unpivoted = unpivoted[unpivoted['Available Positions'] > 0].reset_index(drop=True)
    return unpivoted, raw
