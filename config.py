from pathlib import Path

BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
DB_PATH     = DATA_DIR / "bhavcopy.db"
RAW_DIR     = BASE_DIR / "raw" / "bhavcopy"   # relative - works on any PC

DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# NSE new-format column → internal name
COLUMN_MAP = {
    "TckrSymb": "symbol", "SctySrs": "series", "FinInstrmNm": "name",
    "ISIN": "isin", "BizDt": "date", "Sgmt": "segment",
    "OpnPric": "open", "HghPric": "high", "LwPric": "low",
    "ClsPric": "close", "LastPric": "last", "PrvsClsgPric": "prev_close",
    "TtlTradgVol": "volume", "TtlTrfVal": "turnover",
    "TtlNbOfTxsExctd": "trades", "OpnIntrst": "oi",
    "ChngInOpnIntrst": "oi_change", "StrkPric": "strike",
    "OptnTp": "option_type", "XpryDt": "expiry",
    # old-format fallbacks
    "SYMBOL": "symbol", "SERIES": "series", "OPEN": "open",
    "HIGH": "high", "LOW": "low", "CLOSE": "close",
    "PREVCLOSE": "prev_close", "TOTTRDQTY": "volume",
    "TOTTRDVAL": "turnover", "TOTALTRADES": "trades",
    "ISIN CODE": "isin",
}

SECTOR_MAP = {
    # Banking & Finance
    "HDFCBANK":"Banking","ICICIBANK":"Banking","SBIN":"Banking",
    "KOTAKBANK":"Banking","AXISBANK":"Banking","INDUSINDBK":"Banking",
    "BANDHANBNK":"Banking","IDFCFIRSTB":"Banking","FEDERALBNK":"Banking",
    "AUBANK":"Banking","CANBK":"Banking","BANKBARODA":"Banking",
    "PNB":"Banking","UNIONBANK":"Banking","RBLBANK":"Banking",
    "BAJFINANCE":"Finance","BAJAJFINSV":"Finance","HDFCLIFE":"Finance",
    "SBILIFE":"Finance","ICICIGI":"Finance","CHOLAFIN":"Finance",
    "MUTHOOTFIN":"Finance","MANAPPURAM":"Finance","LICHSGFIN":"Finance",
    # IT
    "TCS":"IT","INFY":"IT","WIPRO":"IT","HCLTECH":"IT","TECHM":"IT",
    "LTIM":"IT","PERSISTENT":"IT","COFORGE":"IT","MPHASIS":"IT",
    "OFSS":"IT","KPITTECH":"IT","TATAELXSI":"IT",
    # Pharma
    "SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma",
    "DIVISLAB":"Pharma","BIOCON":"Pharma","LUPIN":"Pharma",
    "AUROPHARMA":"Pharma","TORNTPHARM":"Pharma","ALKEM":"Pharma",
    "IPCALAB":"Pharma","ABBOTINDIA":"Pharma","SANOFI":"Pharma",
    # Auto
    "MARUTI":"Auto","TATAMOTORS":"Auto","M&M":"Auto","BAJAJ-AUTO":"Auto",
    "HEROMOTOCO":"Auto","EICHERMOT":"Auto","TVSMOTOR":"Auto",
    "ASHOKLEY":"Auto","BHARATFORG":"Auto","MOTHERSON":"Auto",
    "BOSCHLTD":"Auto","EXIDEIND":"Auto","MRF":"Auto",
    # Energy & Oil
    "RELIANCE":"Energy","ONGC":"Energy","BPCL":"Energy","IOC":"Energy",
    "NTPC":"Power","POWERGRID":"Power","ADANIGREEN":"Power",
    "TATAPOWER":"Power","TORNTPOWER":"Power","CESC":"Power",
    "COALINDIA":"Energy","GAIL":"Energy","PETRONET":"Energy",
    # Metal & Mining
    "TATASTEEL":"Metal","JSWSTEEL":"Metal","HINDALCO":"Metal",
    "VEDL":"Metal","SAIL":"Metal","NMDC":"Metal","JINDALSTEL":"Metal",
    "NATIONALUM":"Metal","HINDZINC":"Metal","WELCORP":"Metal",
    # FMCG
    "HINDUNILVR":"FMCG","ITC":"FMCG","NESTLEIND":"FMCG",
    "BRITANNIA":"FMCG","DABUR":"FMCG","MARICO":"FMCG",
    "COLPAL":"FMCG","GODREJCP":"FMCG","EMAMILTD":"FMCG",
    "TATACONSUM":"FMCG","VBL":"FMCG","UBL":"FMCG",
    # Infra & Cement
    "LT":"Infra","ADANIPORTS":"Infra","ADANIENT":"Infra",
    "ULTRACEMCO":"Cement","GRASIM":"Cement","AMBUJACEM":"Cement",
    "ACC":"Cement","SHREECEM":"Cement","RAMCOCEM":"Cement",
    # Telecom
    "BHARTIARTL":"Telecom","IDEA":"Telecom","TATACOMM":"Telecom",
    # Retail & Consumer
    "TITAN":"Consumer","DMART":"Retail","TRENT":"Retail",
    "NYKAA":"Consumer","ZOMATO":"Consumer","JUBLFOOD":"Consumer",
    # Real Estate
    "DLF":"RealEstate","GODREJPROP":"RealEstate","OBEROIRLTY":"RealEstate",
    "PRESTIGE":"RealEstate","PHOENIXLTD":"RealEstate",
    # Chemicals
    "PIDILITIND":"Chemicals","ATUL":"Chemicals","DEEPAKNTR":"Chemicals",
    "NAVINFLUOR":"Chemicals","FINPIPE":"Chemicals",
}

# ── SAAS Capital — Light Luxury Palette ──────────────────────────────────
GREEN  = "#1F7A4D"   # positive values
RED    = "#B54747"   # negative values
YELLOW = "#D4AF37"   # accent gold
BLUE   = "#3E5C76"   # muted slate (charts)
ORANGE = "#C08A2D"   # warm gold-bronze
GRAY   = "#666666"   # secondary text
BG     = "#FCFBF8"   # chart paper (secondary bg)
CARD   = "#FFFFFF"   # chart plot / card
BORDER = "#E8E2D6"   # thin borders / gridlines
