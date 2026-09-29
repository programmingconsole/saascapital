import sqlite3, pandas as pd
from pathlib import Path
from config import DB_PATH

DDL = """
CREATE TABLE IF NOT EXISTS daily_prices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    series      TEXT,
    name        TEXT,
    isin        TEXT,
    open        REAL, high REAL, low REAL, close REAL,
    prev_close  REAL, volume INTEGER, turnover REAL,
    trades      INTEGER, oi REAL, oi_change REAL,
    delivery_qty INTEGER, delivery_pct REAL,
    UNIQUE(date, symbol, series)
);
CREATE INDEX IF NOT EXISTS idx_date   ON daily_prices(date);
CREATE INDEX IF NOT EXISTS idx_symbol ON daily_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_ds     ON daily_prices(date, symbol);
"""

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

def init_db():
    with get_conn() as c:
        for stmt in DDL.strip().split(";"):
            if stmt.strip():
                c.execute(stmt)

def upsert(df: pd.DataFrame) -> int:
    """Insert rows; ignore duplicates. Returns count inserted."""
    init_db()
    if df.empty:
        return 0
    cols = ["date","symbol","series","name","isin","open","high","low","close",
            "prev_close","volume","turnover","trades","oi","oi_change",
            "delivery_qty","delivery_pct"]
    keep = [c for c in cols if c in df.columns]
    df2  = df[keep].copy()
    for c in cols:
        if c not in df2.columns:
            df2[c] = None
    with get_conn() as conn:
        df2.to_sql("daily_prices", conn, if_exists="append", index=False,
                   method="multi", chunksize=500)
    return len(df2)

def upsert_safe(df: pd.DataFrame) -> int:
    init_db()
    if df.empty:
        return 0
    cols = ["date","symbol","series","name","isin","open","high","low","close",
            "prev_close","volume","turnover","trades","oi","oi_change",
            "delivery_qty","delivery_pct"]
    keep = [c for c in cols if c in df.columns]
    df2  = df[keep].copy()
    for c in cols:
        if c not in df2.columns:
            df2[c] = None
    rows = df2.to_dict("records")
    sql  = f"""INSERT OR IGNORE INTO daily_prices
               ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})"""
    vals = [[r.get(c) for c in cols] for r in rows]
    with get_conn() as conn:
        conn.executemany(sql, vals)
    return len(vals)

def query(sql: str, params=()) -> pd.DataFrame:
    init_db()
    with get_conn() as c:
        return pd.read_sql_query(sql, c, params=params)

def available_dates() -> list:
    init_db()
    try:
        df = query("SELECT DISTINCT date FROM daily_prices ORDER BY date DESC")
        return df["date"].tolist() if "date" in df.columns else []
    except Exception:
        return []

def latest_date() -> str:
    init_db()
    try:
        df = query("SELECT MAX(date) as d FROM daily_prices")
        return df["d"].iloc[0] if not df.empty else None
    except Exception:
        return None

def get_history(symbol: str, n_days: int = 260) -> pd.DataFrame:
    init_db()
    try:
        return query(
            "SELECT * FROM daily_prices WHERE symbol=? AND series='EQ' "
            "ORDER BY date DESC LIMIT ?", (symbol, n_days))
    except Exception:
        return pd.DataFrame()

def get_day(date: str, series: str = "EQ") -> pd.DataFrame:
    init_db()
    try:
        return query(
            "SELECT * FROM daily_prices WHERE date=? AND series=?",
            (date, series))
    except Exception:
        return pd.DataFrame()

def get_multi_day(n: int = 60, series: str = "EQ") -> pd.DataFrame:
    """Get last n dates for all symbols — used for scanner calculations."""
    dates = available_dates()[:n]
    if not dates:
        return pd.DataFrame()
    ph = ",".join(["?"]*len(dates))
    try:
        return query(
            f"SELECT * FROM daily_prices WHERE date IN ({ph}) AND series=?",
            dates + [series])
    except Exception:
        return pd.DataFrame()

def db_stats() -> dict:
    init_db()
    try:
        r = query("SELECT COUNT(*) as rows, COUNT(DISTINCT date) as days, "
                  "COUNT(DISTINCT symbol) as symbols, MIN(date) as first, "
                  "MAX(date) as last FROM daily_prices WHERE series='EQ'")
        if not r.empty:
            return r.iloc[0].to_dict()
    except Exception:
        pass
    return {"rows": 0, "days": 0, "symbols": 0, "first": None, "last": None}
