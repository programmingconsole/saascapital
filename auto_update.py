"""
auto_update.py
==============
Run daily at 4:00 PM IST (after NSE close at 3:30 PM).
Downloads today's NSE bhavcopy → imports into DB → logs result.

Usage:
  python auto_update.py              # download today
  python auto_update.py 2026-06-03   # download specific date
"""
import sys, datetime, requests, zipfile, io, logging
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
BASE   = Path(__file__).parent
sys.path.insert(0, str(BASE))
LOG_FILE = BASE / "data" / "auto_update.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

from config import RAW_DIR
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Referer":    "https://www.nseindia.com/",
    "Accept":     "*/*",
}

# ── URL builders ───────────────────────────────────────────────────────────
def urls_for(date: datetime.date) -> list:
    yyyy     = date.strftime("%Y")
    mon3     = date.strftime("%b").upper()
    dd       = date.strftime("%d")
    yyyymmdd = date.strftime("%Y%m%d")
    ddmonyyyy= f"{dd}{mon3}{yyyy}"
    return [
        # New NSE format (2024+)
        f"https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F_0000.csv.zip",
        # Legacy format
        f"https://archives.nseindia.com/content/historical/EQUITIES/{yyyy}/{mon3}/cm{ddmonyyyy}bhav.csv.zip",
    ]

# ── download one date ───────────────────────────────────────────────────────
def download_date(date: datetime.date, session: requests.Session) -> Path | None:
    save_path = RAW_DIR / f"NSE_BHAV_{date.strftime('%Y%m%d')}.csv"
    if save_path.exists():
        log.info(f"{date}  [CACHED] {save_path.name}")
        return save_path

    for url in urls_for(date):
        try:
            r = session.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and len(r.content) > 1000:
                zf  = zipfile.ZipFile(io.BytesIO(r.content))
                csv = zf.read(zf.namelist()[0])
                save_path.write_bytes(csv)
                log.info(f"{date}  [OK] {len(csv):,} bytes  {save_path.name}")
                return save_path
        except Exception as e:
            log.debug(f"  URL failed: {url}  ({e})")

    log.warning(f"{date}  [FAIL] No URL worked — may be holiday or data not yet available")
    return None

# ── import into DB ─────────────────────────────────────────────────────────
def import_file(path: Path) -> int:
    from modules.database import init_db, upsert_safe
    from modules.data_processor import parse_file
    init_db()
    df = parse_file(path)
    if df.empty:
        log.warning(f"  No EQ rows parsed from {path.name}")
        return 0
    n = upsert_safe(df)
    log.info(f"  Imported {n:,} rows into DB")
    return n

# ── desktop notification (Windows) ─────────────────────────────────────────
def notify(title: str, msg: str):
    try:
        import subprocess
        ps = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $n = New-Object System.Windows.Forms.NotifyIcon
        $n.Icon = [System.Drawing.SystemIcons]::Information
        $n.BalloonTipIcon  = "Info"
        $n.BalloonTipTitle = "{title}"
        $n.BalloonTipText  = "{msg}"
        $n.Visible = $true
        $n.ShowBalloonTip(4000)
        Start-Sleep -Milliseconds 5000
        $n.Dispose()
        '''
        subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps])
    except Exception:
        pass  # notification is optional

# ── skip weekends & known holidays ─────────────────────────────────────────
NSE_HOLIDAYS_2026 = {
    datetime.date(2026, 1, 26),   # Republic Day
    datetime.date(2026, 3, 17),   # Holi
    datetime.date(2026, 4, 2),    # Good Friday
    datetime.date(2026, 4, 14),   # Ambedkar Jayanti
    datetime.date(2026, 5, 1),    # Maharashtra Day
    datetime.date(2026, 8, 15),   # Independence Day
    datetime.date(2026, 10, 2),   # Gandhi Jayanti
    datetime.date(2026, 10, 22),  # Dussehra
    datetime.date(2026, 11, 11),  # Diwali
    datetime.date(2026, 11, 12),  # Diwali
    datetime.date(2026, 12, 25),  # Christmas
}

def is_trading_day(date: datetime.date) -> bool:
    if date.weekday() >= 5:
        return False
    if date in NSE_HOLIDAYS_2026:
        return False
    return True

# ── main ───────────────────────────────────────────────────────────────────
def main():
    # Determine target date
    if len(sys.argv) > 1:
        target = datetime.date.fromisoformat(sys.argv[1])
    else:
        target = datetime.date.today()

    log.info(f"{'='*55}")
    log.info(f"NSE Auto-Update  >>  {target}")

    if not is_trading_day(target):
        log.info(f"{target} is not a trading day. Nothing to download.")
        return

    session = requests.Session()
    # Warm up NSE session
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
    except Exception:
        pass

    path = download_date(target, session)
    if path:
        n = import_file(path)
        msg = f"{target}: {n:,} rows imported"
        log.info(f"DONE -- {msg}")
        notify("NSE Dashboard Updated", msg)
    else:
        log.warning(f"Download failed for {target}")
        notify("NSE Update Failed", f"Could not download bhavcopy for {target}")

    # Also download yesterday if missed (e.g. script ran over weekend)
    yesterday = target - datetime.timedelta(days=1)
    while not is_trading_day(yesterday) and (target - yesterday).days <= 5:
        yesterday -= datetime.timedelta(days=1)

    if yesterday != target:
        prev_path = RAW_DIR / f"NSE_BHAV_{yesterday.strftime('%Y%m%d')}.csv"
        if not prev_path.exists():
            log.info(f"Also catching up on {yesterday}...")
            p = download_date(yesterday, session)
            if p:
                import_file(p)

    log.info(f"{'='*55}\n")


if __name__ == "__main__":
    main()
