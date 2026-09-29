import pandas as pd, numpy as np
from pathlib import Path
from config import COLUMN_MAP, RAW_DIR
from modules.database import init_db, upsert_safe

def _rename(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]
    # If 'date' already exists (added by download script), drop source BizDt to avoid dupe
    if "date" in df.columns and "BizDt" in df.columns:
        df = df.drop(columns=["BizDt"])
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    # Deduplicate columns (keep first)
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def _clean_equity(df: pd.DataFrame) -> pd.DataFrame:
    """Keep EQ series, drop bad rows, coerce types."""
    if "series" not in df.columns:
        return pd.DataFrame()
    df = df[df["series"] == "EQ"].copy()
    if df.empty:
        return df
    num = ["open","high","low","close","prev_close","volume","turnover","trades","oi","oi_change"]
    for c in num:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"].astype(str), errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["symbol","date","close"])
    df = df[df["close"] > 0]
    return df

def _add_change(df: pd.DataFrame) -> pd.DataFrame:
    if "close" in df.columns and "prev_close" in df.columns:
        df["change"]   = df["close"] - df["prev_close"]
        df["change_pct"] = ((df["change"] / df["prev_close"]) * 100).round(2)
    return df

def parse_file(path) -> pd.DataFrame:
    """Read one bhavcopy CSV and return clean equity DataFrame."""
    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()
    df = _rename(df)
    df = _clean_equity(df)
    df = _add_change(df)
    return df

def import_directory(directory: Path = RAW_DIR, progress_cb=None) -> dict:
    """Scan directory for NSE_BHAV_*.csv files and load into DB."""
    init_db()
    files  = sorted(Path(directory).glob("NSE_BHAV_2*.csv"))
    # exclude the combined file
    files  = [f for f in files if "LAST" not in f.name]
    total  = 0
    loaded = 0
    skipped= 0
    for i, fp in enumerate(files):
        if progress_cb:
            progress_cb(i, len(files), fp.name)
        df = parse_file(fp)
        if df.empty:
            skipped += 1
            continue
        n = upsert_safe(df)
        total  += n
        loaded += 1
    return {"files": len(files), "loaded": loaded,
            "skipped": skipped, "rows": total}

def import_uploaded(uploaded_file) -> dict:
    """Handle Streamlit uploaded file."""
    init_db()
    import io
    df = pd.read_csv(io.BytesIO(uploaded_file.read()), low_memory=False)
    df = _rename(df)
    df = _clean_equity(df)
    df = _add_change(df)
    if df.empty:
        return {"rows": 0, "date": None}
    n    = upsert_safe(df)
    date = df["date"].iloc[0] if "date" in df.columns else "?"
    return {"rows": n, "date": date}

def get_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert long multi-day DataFrame into wide format:
    symbol → columns for each date (close, volume, etc.)
    Used by scanners needing time-series per stock.
    """
    if df.empty:
        return pd.DataFrame()
    df = df.sort_values("date")
    return df

def build_matrix(df_long: pd.DataFrame, col: str) -> pd.DataFrame:
    """Pivot: rows=date, cols=symbol, values=col."""
    if df_long.empty or col not in df_long.columns:
        return pd.DataFrame()
    return df_long.pivot_table(index="date", columns="symbol",
                               values=col, aggfunc="last")
