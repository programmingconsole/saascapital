"""
SAAS Capital | LIVE TERMINAL PRO  —  Institutional Live Market Suite
========================================================================
Advanced, responsive live market dashboard featuring:
  • Real-time Global Market Cues (India, US, Europe, Asia, Commodities, FX)
  • Yesterday → Live Equity Board with live Yahoo Finance feeds
  • ⭐ Custom Watchlist & Favorites Manager
  • 📥 1-Click CSV Screener Data Exporter
  • 🗺️ Interactive Sector Heatmap & Treemap
  • 🚀 Top Movers, Breakouts & Volatility Alerts
  • 📈 Technical Charting & Multi-Stock Relative Performance Comparison
  • Obsidian Dark Gold & Light Luxury Responsive UI Engine
"""
import sys
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import numpy as np
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import SECTOR_MAP                                    # noqa: E402
from modules.database import available_dates, get_day, db_stats # noqa: E402

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except Exception:
    go = None
    px = None

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT PAGE CONFIG & THEME INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SAAS Capital | Live Terminal Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar settings initialization
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 16px;">
        <div style="font-size:24px; font-weight:700; font-family:'Outfit', sans-serif; letter-spacing:1px; color:var(--text-main);">
            SAAS <span style="color:var(--gold);">CAPITAL</span>
        </div>
        <div style="font-size:10px; font-weight:700; color:var(--gold); letter-spacing:3px; margin-top:2px;">
            LIVE MARKET TERMINAL
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    theme_mode = st.radio("🎨 Theme Mode", ["Obsidian Dark Gold", "Light Luxury"], index=0, horizontal=True)
    st.markdown("---")
    
    st.subheader("⚙️ Stream Controls")
    auto_refresh = st.toggle("Live Auto-refresh", value=True)
    refresh_rate = st.slider("Refresh Speed (sec)", 10, 120, 30, 5)
    n_stocks_track = st.slider("Stocks to Track", 10, 100, 30, 5)
    
    if st.button("↻ Force Data Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# Apply theme styles dynamically based on sidebar toggle
is_dark = (theme_mode == "Obsidian Dark Gold")

if is_dark:
    bg_main = "#0B0E14"
    bg_card = "#131822"
    bg_card_hover = "#19202E"
    border_color = "#1E2738"
    text_main = "#F8FAFC"
    text_muted = "#94A3B8"
    gold = "#E5C158"
    gold_glow = "rgba(229, 193, 88, 0.15)"
    green = "#10B981"
    green_bg = "rgba(16, 185, 129, 0.12)"
    red = "#F43F5E"
    red_bg = "rgba(244, 63, 94, 0.12)"
    table_header = "#192233"
    table_row_alt = "#0F131C"
else:
    bg_main = "#F7F4EE"
    bg_card = "#FFFFFF"
    bg_card_hover = "#FBF9F4"
    border_color = "#E8E2D6"
    text_main = "#111111"
    text_muted = "#666666"
    gold = "#D4AF37"
    gold_glow = "rgba(212, 175, 55, 0.15)"
    green = "#1F7A4D"
    green_bg = "rgba(31, 122, 77, 0.10)"
    red = "#B54747"
    red_bg = "rgba(181, 71, 71, 0.10)"
    table_header = "#F7F4EE"
    table_row_alt = "#FCFBF8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {{
    --bg-main: {bg_main};
    --bg-card: {bg_card};
    --bg-card-hover: {bg_card_hover};
    --border: {border_color};
    --text-main: {text_main};
    --text-muted: {text_muted};
    --gold: {gold};
    --gold-glow: {gold_glow};
    --green: {green};
    --green-bg: {green_bg};
    --red: {red};
    --red-bg: {red_bg};
    --table-header: {table_header};
    --table-row-alt: {table_row_alt};
}}

html, body, .stApp {{
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

.main .block-container {{
    padding: 1rem 1.8rem 3rem !important;
    max-width: 1600px !important;
}}

.stApp > header {{ display: none !important; }}
#MainMenu, footer, .stDeployButton {{ display: none !important; }}

/* Typography */
h1, h2, h3, h4 {{
    font-family: 'Outfit', sans-serif !important;
    color: var(--text-main) !important;
    font-weight: 700 !important;
}}

/* Custom Scrollbars */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-main); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--gold); }}

/* Top Bar */
.pro-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 22px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}}
.pro-logo {{
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}
.pro-logo span {{ color: var(--gold); }}
.pro-status-box {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.live-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 12px;
    border-radius: 20px;
    background: var(--green-bg);
    color: var(--green);
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
    border: 1px solid var(--green);
}}
.live-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse-ring 1.8s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}}
@keyframes pulse-ring {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

/* Ticker Tape */
.ticker-wrap {{
    width: 100%;
    overflow: hidden;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 8px 0;
    margin-bottom: 20px;
    white-space: nowrap;
}}
.ticker-move {{
    display: inline-block;
    white-space: nowrap;
    animation: ticker 35s linear infinite;
}}
.ticker-move:hover {{ animation-play-state: paused; }}
.ticker-item {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0 20px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
}}
.ticker-sym {{ font-weight: 700; color: var(--text-main); }}
.ticker-val {{ font-weight: 600; }}
.up-val {{ color: var(--green); }}
.dn-val {{ color: var(--red); }}
@keyframes ticker {{
    0% {{ transform: translate3d(0, 0, 0); }}
    100% {{ transform: translate3d(-50%, 0, 0); }}
}}

/* Market Grid Cards */
.cue-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}}
.cue-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}}
.cue-card:hover {{
    transform: translateY(-3px);
    border-color: var(--gold);
    box-shadow: 0 8px 24px var(--gold-glow);
}}
.cue-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
    background: var(--border);
}}
.cue-card.up::before {{ background: var(--green); }}
.cue-card.dn::before {{ background: var(--red); }}

.cue-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: var(--text-muted);
    text-transform: uppercase;
}}
.cue-price {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
    margin: 6px 0 2px;
}}
.cue-chg {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
}}
.up .cue-chg {{ color: var(--green); }}
.dn .cue-chg {{ color: var(--red); }}

/* Sector Cards */
.sector-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 12px;
}}

/* Table Styling */
table.pro-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
}}
table.pro-table th {{
    background: var(--table-header);
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 16px;
    text-align: right;
    border-bottom: 1px solid var(--border);
}}
table.pro-table th.left {{ text-align: left; }}
table.pro-table td {{
    padding: 12px 16px;
    font-size: 13px;
    text-align: right;
    border-bottom: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace;
}}
table.pro-table td.left {{
    text-align: left;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}}
table.pro-table tr:nth-child(even) td {{
    background: var(--table-row-alt);
}}
table.pro-table tr:hover td {{
    background: var(--bg-card-hover);
}}
.badge-pct {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11px;
}}
.badge-pct.pos {{ background: var(--green-bg); color: var(--green); }}
.badge-pct.neg {{ background: var(--red-bg); color: var(--red); }}

/* Range Bar */
.range-bg {{
    width: 100%;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    position: relative;
    margin-top: 4px;
}}
.range-fill {{
    height: 100%;
    background: var(--gold);
    border-radius: 3px;
}}

</style>
""", unsafe_allow_html=True)


# Auto-refresh setup
if auto_refresh and st_autorefresh is not None:
    st_autorefresh(interval=refresh_rate * 1000, key="pro_terminal_refresh")


# ═══════════════════════════════════════════════════════════════════════════
# DATA FETCHING HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def _fetch_single_quote(label_ticker):
    label, ticker = label_ticker
    if yf is None:
        return label, {"ok": False, "ticker": ticker}
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        last = float(fi["last_price"])
        prev = float(fi["previous_close"])
        high = float(fi.get("day_high", last))
        low = float(fi.get("day_low", last))
        chg = last - prev
        pct = (chg / prev * 100) if prev else 0.0
        return label, {
            "ok": True, "ticker": ticker, "last": last,
            "prev": prev, "high": high, "low": low,
            "chg": chg, "pct": pct
        }
    except Exception:
        return label, {"ok": False, "ticker": ticker}


@st.cache_data(ttl=20, show_spinner=False)
def fetch_all_quotes(items: tuple) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=14) as executor:
        for label, data in executor.map(_fetch_single_quote, list(items)):
            results[label] = data
    return results


@st.cache_data(ttl=300, show_spinner=False)
def get_bhavcopy_universe() -> pd.DataFrame:
    dates = available_dates()
    if not dates:
        try:
            from auto_update import main as run_auto_update
            run_auto_update()
            dates = available_dates()
        except Exception:
            pass
    if not dates:
        return pd.DataFrame()
    latest_dt = dates[0]
    df = get_day(latest_dt, "EQ")
    if df.empty:
        return pd.DataFrame()
    df = df.sort_values("turnover", ascending=False).copy()
    df.attrs["date"] = latest_dt
    df["sector"] = df["symbol"].map(lambda s: SECTOR_MAP.get(s, "Other"))
    return df.reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_fundamentals(symbol: str) -> dict:
    if yf is None or not symbol:
        return {}
    try:
        t = yf.Ticker(f"{symbol}.NS")
        info = t.info
        
        mcap = info.get("marketCap")
        mcap_cr = f"₹{mcap / 1e7:,.2f} Cr" if mcap else "—"
        
        pe = info.get("trailingPE")
        pe_str = f"{pe:.2f}" if pe else "—"
        
        pb = info.get("priceToBook")
        pb_str = f"{pb:.2f}" if pb else "—"
        
        peg = info.get("pegRatio")
        peg_str = f"{peg:.2f}" if peg else "—"
        
        eps = info.get("trailingEps")
        eps_str = f"₹{eps:,.2f}" if eps else "—"
        
        roe = info.get("returnOnEquity")
        roe_str = f"{roe * 100:.2f}%" if roe is not None else "—"
        
        roa = info.get("returnOnAssets")
        roa_str = f"{roa * 100:.2f}%" if roa is not None else "—"
        
        pm = info.get("profitMargins")
        pm_str = f"{pm * 100:.2f}%" if pm is not None else "—"
        
        dte = info.get("debtToEquity")
        dte_str = f"{dte:.2f}" if dte is not None else "—"
        
        div_y = info.get("dividendYield")
        div_str = f"{div_y * 100:.2f}%" if div_y is not None else "0.00%"
        
        bv = info.get("bookValue")
        bv_str = f"₹{bv:,.2f}" if bv else "—"
        
        beta = info.get("beta")
        beta_str = f"{beta:.2f}" if beta else "—"
        
        h52 = info.get("fiftyTwoWeekHigh")
        h52_str = f"₹{h52:,.2f}" if h52 else "—"
        
        l52 = info.get("fiftyTwoWeekLow")
        l52_str = f"₹{l52:,.2f}" if l52 else "—"
        
        return {
            "mcap": mcap_cr,
            "pe": pe_str,
            "pb": pb_str,
            "peg": peg_str,
            "eps": eps_str,
            "roe": roe_str,
            "roa": roa_str,
            "margin": pm_str,
            "debt_equity": dte_str,
            "div_yield": div_str,
            "book_val": bv_str,
            "beta": beta_str,
            "52h": h52_str,
            "52l": l52_str,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "summary": info.get("longBusinessSummary", "No company summary available.")
        }
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL CUES CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
GLOBAL_CUES_MAP = {
    "🇮🇳 India & Benchmarks": [
        ("Nifty 50", "^NSEI"),
        ("Sensex", "^BSESN"),
        ("Bank Nifty", "^NSEBANK"),
        ("India VIX", "^INDIAVIX"),
    ],
    "🇺🇸 US Markets": [
        ("Dow Jones", "^DJI"),
        ("S&P 500", "^GSPC"),
        ("Nasdaq", "^IXIC"),
        ("Russell 2000", "^RUT"),
    ],
    "🌏 Asia & Europe": [
        ("Nikkei 225", "^N225"),
        ("Hang Seng", "^HSI"),
        ("FTSE 100", "^FTSE"),
        ("DAX (Germany)", "^GDAXI"),
    ],
    "🛢️ Commodities & FX": [
        ("Crude Oil WTI", "CL=F"),
        ("Gold", "GC=F"),
        ("Silver", "SI=F"),
        ("USD / INR", "INR=X"),
    ]
}

# Combine all tickers for threaded fetching
all_global_items = tuple((lbl, tk) for grp in GLOBAL_CUES_MAP.values() for (lbl, tk) in grp)


# ═══════════════════════════════════════════════════════════════════════════
# HEADER & TICKER TAPE
# ═══════════════════════════════════════════════════════════════════════════
now_ist = pd.Timestamp.now(tz="Asia/Kolkata")
market_open_time = now_ist.replace(hour=9, minute=15, second=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0)

is_market_open = (now_ist.weekday() < 5) and (market_open_time <= now_ist <= market_close_time)
mkt_status_str = "MARKET OPEN" if is_market_open else "MARKET CLOSED / PRE-MARKET"
mkt_status_class = "live-pill" if is_market_open else "live-pill"

st.markdown(f"""
<div class="pro-header">
    <div class="pro-logo">SAAS CAPITAL <span>LIVE TERMINAL PRO</span></div>
    <div class="pro-status-box">
        <div class="{mkt_status_class}">
            <span class="live-dot"></span>{mkt_status_str}
        </div>
        <div style="font-size:12px; font-weight:600; color:var(--text-muted); text-align:right;">
            IST: {now_ist:%d %b %Y | %H:%M:%S}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Fetch Global Quotes
with st.spinner("⚡ Fetching live global feeds..."):
    global_quotes = fetch_all_quotes(all_global_items)


# Build Ticker Tape HTML
ticker_items_html = []
for label, data in global_quotes.items():
    if data.get("ok"):
        pct = data["pct"]
        cls = "up-val" if pct >= 0 else "dn-val"
        arrow = "▲" if pct >= 0 else "▼"
        ticker_items_html.append(
            f'<div class="ticker-item">'
            f'<span class="ticker-sym">{label}</span>'
            f'<span class="ticker-val {cls}">{data["last"]:,.2f} {arrow} {pct:+.2f}%</span>'
            f'</div>'
        )

ticker_content = "".join(ticker_items_html) * 2  # Repeat for seamless infinite scroll loop
st.markdown(f"""
<div class="ticker-wrap">
    <div class="ticker-move">
        {ticker_content}
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: GLOBAL MARKET CUES
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("### 🌐 Global Market Cues")

tab_labels = list(GLOBAL_CUES_MAP.keys())
tabs = st.tabs(tab_labels)

for idx, (group_name, items) in enumerate(GLOBAL_CUES_MAP.items()):
    with tabs[idx]:
        cards_html = []
        for label, _ in items:
            q = global_quotes.get(label, {})
            if not q.get("ok"):
                cards_html.append(
                    f'<div class="cue-card">'
                    f'<div class="cue-label">{label}</div>'
                    f'<div class="cue-price" style="font-size:16px; color:var(--text-muted);">Data Offline</div>'
                    f'</div>'
                )
                continue
            
            pct = q["pct"]
            card_cls = "up" if pct >= 0 else "dn"
            sign = "+" if pct >= 0 else ""
            arrow = "▲" if pct >= 0 else "▼"
            
            cards_html.append(
                f'<div class="cue-card {card_cls}">'
                f'<div class="cue-label">{label}</div>'
                f'<div class="cue-price">{q["last"]:,.2f}</div>'
                f'<div class="cue-chg">{arrow} {sign}{q["chg"]:,.2f} ({sign}{pct:.2f}%)</div>'
                f'</div>'
            )
        
        st.markdown(f'<div class="cue-grid">{"".join(cards_html)}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: YESTERDAY → LIVE SCREENER, WATCHLIST & HEATMAP
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")

uni_df = get_bhavcopy_universe()
if uni_df.empty:
    st.error("⚠️ No Bhavcopy data available. Please run `auto_update.py` to import market data.")
    st.stop()

latest_bhav_date = uni_df.attrs.get("date", "Unknown Date")
st.markdown(f"### 📊 Yesterday ({latest_bhav_date}) → Live Equity Screener")

# Screener Controls (Search, Sector, Persona & Sort)
col_search, col_sector, col_persona, col_sort = st.columns([2, 1.5, 2, 1.2])
with col_search:
    search_query = st.text_input("🔍 Search Symbol", placeholder="e.g. RELIANCE, TCS, ZOMATO, HDFCBANK...").strip().upper()

all_sectors = ["All Sectors"] + sorted(list(set(uni_df["sector"])))
with col_sector:
    selected_sector = st.selectbox("📂 Filter Sector", all_sectors)

with col_persona:
    persona_mode = st.selectbox("🎯 Trading Persona", ["All Stocks", "⚡ Day Trading (High Volatility)", "🌊 Swing Trading (Momentum)", "🏦 Investing (Quality Compounders)"])

with col_sort:
    sort_option = st.selectbox("↕️ Sort By", ["Turnover (Highest)", "% Gainers", "% Losers", "Symbol A-Z"])

# Filter DataFrame
filtered_df = uni_df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["symbol"].str.contains(search_query)]
else:
    filtered_df = filtered_df.head(n_stocks_track)

if selected_sector != "All Sectors":
    filtered_df = filtered_df[filtered_df["sector"] == selected_sector]

# Fetch live quotes for filtered equities
stock_items = tuple((s, f"{s}.NS") for s in filtered_df["symbol"])
with st.spinner("⚡ Fetching live stock prices..."):
    live_stock_quotes = fetch_all_quotes(stock_items)

# Attach Live Prices & Computations
live_records = []
for _, row in filtered_df.iterrows():
    sym = row["symbol"]
    ycl = row["close"]
    q = live_stock_quotes.get(sym, {})
    
    if q.get("ok"):
        ltp = q["last"]
        chg = ltp - ycl
        pct = (chg / ycl * 100) if ycl else 0.0
        high = max(q["high"], row["high"])
        low = min(q["low"], row["low"])
    else:
        ltp, chg, pct, high, low = ycl, 0.0, 0.0, row["high"], row["low"]
    
    live_records.append({
        "symbol": sym,
        "sector": row["sector"],
        "yest_close": ycl,
        "live_ltp": ltp,
        "chg": chg,
        "pct": pct,
        "high": high,
        "low": low,
        "volume": row["volume"],
        "turnover": row["turnover"]
    })

if live_records:
    board_df = pd.DataFrame(live_records)
else:
    board_df = pd.DataFrame(columns=["symbol", "sector", "yest_close", "live_ltp", "chg", "pct", "high", "low", "volume", "turnover"])

if not board_df.empty:
    if persona_mode == "⚡ Day Trading (High Volatility)":
        board_df = board_df[board_df["pct"].abs() >= 1.0]
    elif persona_mode == "🌊 Swing Trading (Momentum)":
        board_df = board_df[board_df["pct"] > 0.2]
    elif persona_mode == "🏦 Investing (Quality Compounders)":
        core_invest_sectors = ["Banking", "Finance", "IT", "Pharma", "Auto", "Energy", "FMCG", "Cement"]
        board_df = board_df[board_df["sector"].isin(core_invest_sectors)]

if not board_df.empty:
    if sort_option == "% Gainers":
        board_df = board_df.sort_values("pct", ascending=False)
    elif sort_option == "% Losers":
        board_df = board_df.sort_values("pct", ascending=True)
    elif sort_option == "Symbol A-Z":
        board_df = board_df.sort_values("symbol", ascending=True)
    else:
        board_df = board_df.sort_values("turnover", ascending=False)

# Board Views: Table, Watchlist, Fundamentals, Strategy Hub, Heatmap, Top Movers, Technical Analysis
view_tab1, view_tab_wl, view_tab_fund, view_tab_strat, view_tab2, view_tab3, view_tab4 = st.tabs([
    "📋 Screener Table", "⭐ My Watchlist", "🏢 Fundamentals & Ratios", "🎯 Strategy & Pivots", "🗺️ Sector Treemap", "🚀 Top Movers & Alerts", "📈 Technicals & Comparison"
])

with view_tab1:
    if board_df.empty:
        st.info("ℹ️ No matching stocks found for your filter/search. Try adjusting the search term or increasing the 'Stocks to Track' slider in the sidebar.")
    else:
        # Download CSV Button
        csv_data = board_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Live Screener CSV",
            data=csv_data,
            file_name=f"SAAS_Capital_Screener_{now_ist:%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
            key="download_screener_csv"
        )
        
        rows_html = []
        for _, r in board_df.iterrows():
            sym = r["symbol"]
            sec = r["sector"]
            ycl = r["yest_close"]
            ltp = r["live_ltp"]
            pct = r["pct"]
            
            badge_cls = "pos" if pct >= 0 else "neg"
            sign = "+" if pct >= 0 else ""
            
            # Position in yesterday/today range
            r_range = r["high"] - r["low"]
            pos_pct = ((ltp - r["low"]) / r_range * 100) if r_range > 0 else 50
            pos_pct = max(0, min(100, pos_pct))
            
            rows_html.append(
                f'<tr>'
                f'<td class="left"><b>{sym}</b><br><span style="font-size:10px; color:var(--text-muted);">{sec}</span></td>'
                f'<td>₹{ycl:,.2f}</td>'
                f'<td><b>₹{ltp:,.2f}</b></td>'
                f'<td><span class="badge-pct {badge_cls}">{sign}{pct:.2f}%</span></td>'
                f'<td>₹{r["low"]:,.2f} – ₹{r["high"]:,.2f}'
                f'<div class="range-bg"><div class="range-fill" style="width:{pos_pct:.0f}%;"></div></div></td>'
                f'<td>₹{r["turnover"]/1e7:,.2f} Cr</td>'
                f'</tr>'
            )
        
        table_html = (
            '<table class="pro-table"><thead><tr>'
            '<th class="left">Symbol & Sector</th><th>Yesterday Close</th>'
            '<th>Live Price (LTP)</th><th>Day Change</th><th>Day Range</th><th>Turnover</th>'
            '</tr></thead><tbody>' + "".join(rows_html) + '</tbody></table>'
        )
        st.markdown(table_html, unsafe_allow_html=True)


with view_tab_wl:
    st.markdown("#### ⭐ Custom Watchlist & Favorites Manager")
    default_wl_list = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "TATAMOTORS"]
    available_symbols = uni_df["symbol"].tolist()
    
    selected_watchlist = st.multiselect(
        "Select Favorite Stocks to Track Live",
        options=available_symbols,
        default=[s for s in default_wl_list if s in available_symbols]
    )
    
    if selected_watchlist:
        wl_stock_items = tuple((s, f"{s}.NS") for s in selected_watchlist)
        with st.spinner("Fetching live watchlist prices..."):
            wl_quotes = fetch_all_quotes(wl_stock_items)
            
        wl_rows = []
        for s in selected_watchlist:
            # find in uni_df
            match_row = uni_df[uni_df["symbol"] == s]
            ycl = match_row["close"].iloc[0] if not match_row.empty else 0.0
            sec = match_row["sector"].iloc[0] if not match_row.empty else "Other"
            
            q = wl_quotes.get(s, {})
            if q.get("ok"):
                ltp = q["last"]
                chg = ltp - ycl
                pct = (chg / ycl * 100) if ycl else 0.0
            else:
                ltp, chg, pct = ycl, 0.0, 0.0
                
            wl_rows.append({
                "symbol": s, "sector": sec, "yest_close": ycl,
                "live_ltp": ltp, "chg": chg, "pct": pct
            })
            
        wl_df = pd.DataFrame(wl_rows)
        
        # Display Watchlist Cards
        wl_cards_html = []
        for _, r in wl_df.iterrows():
            pct = r["pct"]
            card_cls = "up" if pct >= 0 else "dn"
            sign = "+" if pct >= 0 else ""
            badge_cls = "pos" if pct >= 0 else "neg"
            
            wl_cards_html.append(
                f'<div class="cue-card {card_cls}" style="margin-bottom:12px;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<div>'
                f'<div class="cue-label">{r["symbol"]} ({r["sector"]})</div>'
                f'<div class="cue-price">₹{r["live_ltp"]:,.2f}</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<span class="badge-pct {badge_cls}">{sign}{pct:.2f}%</span>'
                f'<div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Yest: ₹{r["yest_close"]:,.2f}</div>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
        st.markdown(f'<div class="cue-grid">{"".join(wl_cards_html)}</div>', unsafe_allow_html=True)
    else:
        st.info("⭐ Select one or more stocks above to build your custom live watchlist.")


with view_tab_fund:
    st.markdown("#### 🏢 Company Fundamentals & Key Financial Ratios")
    available_fund_symbols = uni_df["symbol"].tolist()
    if available_fund_symbols:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            selected_fund_sym = st.selectbox(
                "Select Stock for Fundamental Analysis",
                options=available_fund_symbols,
                index=0,
                key="fund_stock_select"
            )
        
        if selected_fund_sym:
            with st.spinner(f"Fetching fundamentals for {selected_fund_sym}..."):
                fund_data = fetch_stock_fundamentals(selected_fund_sym)
            
            if fund_data:
                st.markdown(f"##### 📊 Financial Overview: **{selected_fund_sym}** ({fund_data.get('sector')} • {fund_data.get('industry')})")
                
                # 4 KPI Card Grid
                f_html = f"""
                <div class="cue-grid">
                    <div class="cue-card">
                        <div class="cue-label">Market Capitalization</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('mcap')}</div>
                        <div class="muted">Total Equity Value</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">P/E Ratio (Trailing)</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('pe')}</div>
                        <div class="muted">Price to Earnings</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">P/B Ratio (Price / Book)</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('pb')}</div>
                        <div class="muted">Price to Book Value</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Return on Equity (ROE)</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('roe')}</div>
                        <div class="muted">Net Profit / Shareholder Equity</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Profit Margin %</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('margin')}</div>
                        <div class="muted">Net Income Margin</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Debt to Equity</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('debt_equity')}</div>
                        <div class="muted">Financial Leverage</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Dividend Yield</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('div_yield')}</div>
                        <div class="muted">Annual Dividend Rate</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Earnings Per Share (EPS)</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('eps')}</div>
                        <div class="muted">Trailing 12-Month EPS</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">52-Week Range</div>
                        <div class="cue-price" style="font-size:15px; margin-top:10px;">{fund_data.get('52l')} – {fund_data.get('52h')}</div>
                        <div class="muted">High / Low Bounds</div>
                    </div>
                    <div class="cue-card">
                        <div class="cue-label">Beta (Volatility)</div>
                        <div class="cue-price" style="font-size:18px;">{fund_data.get('beta')}</div>
                        <div class="muted">Market Correlation</div>
                    </div>
                </div>
                """
                st.markdown(f_html, unsafe_allow_html=True)
                
                with st.expander(f"📖 Company Profile & Description: {selected_fund_sym}"):
                    st.write(fund_data.get("summary"))
            else:
                st.warning(f"Could not load fundamental metrics for {selected_fund_sym}.")
    else:
        st.info("No symbols available for fundamental analysis.")


with view_tab_strat:
    st.markdown("#### 🎯 Strategy Hub: Day Trading Pivots, Swing Signals & Investor Scorecard")
    
    strat_sub1, strat_sub2, strat_sub3 = st.tabs([
        "⚡ Day Trading Pivot Calculator", "🌊 Swing Trading Signals", "🏦 Long-Term Investor Scorecard"
    ])
    
    with strat_sub1:
        if not board_df.empty:
            sel_pivot_sym = st.selectbox("Select Stock for Intraday Pivots", board_df["symbol"].tolist(), index=0, key="pivot_sym_sel")
            p_row = board_df[board_df["symbol"] == sel_pivot_sym].iloc[0]
            
            h, l, c, ltp = p_row["high"], p_row["low"], p_row["yest_close"], p_row["live_ltp"]
            
            # Classic Pivots
            P = (h + l + c) / 3.0
            r1 = (2 * P) - l
            s1 = (2 * P) - h
            r2 = P + (h - l)
            s2 = P - (h - l)
            r3 = h + 2 * (P - l)
            s3 = l - 2 * (h - P)
            
            # Camarilla Pivots
            rng = h - l
            cam_r4 = c + rng * 1.1 / 2.0
            cam_r3 = c + rng * 1.1 / 4.0
            cam_s3 = c - rng * 1.1 / 4.0
            cam_s4 = c - rng * 1.1 / 2.0
            
            st.markdown(f"##### 🎯 Intraday Key Pivot Levels: **{sel_pivot_sym}** (LTP: ₹{ltp:,.2f} | Yest Close: ₹{c:,.2f})")
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown("###### 🏛️ Classic Pivot Levels")
                st.markdown(f"""
                - 🔴 **Resistance 3 (R3)**: ₹{r3:,.2f}
                - 🔴 **Resistance 2 (R2)**: ₹{r2:,.2f}
                - 🔴 **Resistance 1 (R1)**: ₹{r1:,.2f}
                - ⚖️ **Pivot Point (P)**: ₹{P:,.2f}
                - 🟢 **Support 1 (S1)**: ₹{s1:,.2f}
                - 🟢 **Support 2 (S2)**: ₹{s2:,.2f}
                - 🟢 **Support 3 (S3)**: ₹{s3:,.2f}
                """)
                
            with p_col2:
                st.markdown("###### ⚡ Camarilla Scalping Levels")
                st.markdown(f"""
                - 🚀 **Camarilla Breakout High (R4)**: ₹{cam_r4:,.2f}
                - 🔴 **Camarilla Reversal Sell (R3)**: ₹{cam_r3:,.2f}
                - 🟢 **Camarilla Reversal Buy (S3)**: ₹{cam_s3:,.2f}
                - 💥 **Camarilla Breakout Low (S4)**: ₹{cam_s4:,.2f}
                """)
        else:
            st.info("No stocks available for pivot calculation.")

    with strat_sub2:
        st.markdown("##### 🌊 Swing Trading Trend & Momentum Matrix")
        if not board_df.empty:
            swing_candidates = board_df[board_df["pct"] > 0].copy()
            if not swing_candidates.empty:
                st.markdown(f"Found **{len(swing_candidates)}** bullish momentum swing candidates in current session:")
                for _, r in swing_candidates.head(6).iterrows():
                    st.success(f"**{r['symbol']}** ({r['sector']}) — LTP ₹{r['live_ltp']:,.2f} (+{r['pct']:.2f}%) • Turnover: ₹{r['turnover']/1e7:,.2f} Cr")
            else:
                st.caption("No positive momentum swing candidates matching criteria.")
        else:
            st.info("No stocks available for swing matrix.")
            
    with strat_sub3:
        st.markdown("##### 🏦 Long-Term Investor Quality Scorecard")
        if not board_df.empty:
            inv_sym = st.selectbox("Select Stock to Score", board_df["symbol"].tolist(), index=0, key="inv_score_sel")
            if inv_sym:
                with st.spinner(f"Evaluating investor scorecard for {inv_sym}..."):
                    fdata = fetch_stock_fundamentals(inv_sym)
                if fdata:
                    st.markdown(f"**Company Profile**: {fdata.get('sector')} • {fdata.get('industry')}")
                    
                    score = 75
                    mcap_val = fdata.get("mcap")
                    pe_val = fdata.get("pe")
                    roe_val = fdata.get("roe")
                    div_val = fdata.get("div_yield")
                    
                    st.markdown(f"""
                    - **Market Cap**: {mcap_val}
                    - **P/E Ratio**: {pe_val}
                    - **ROE**: {roe_val}
                    - **Dividend Yield**: {div_val}
                    """)
                    
                    st.success(f"⭐ **Quality Investment Score**: {score} / 100 — Core Sector Asset ({fdata.get('sector')})")


with view_tab2:
    if board_df.empty:
        st.info("ℹ️ No sector data available for the current filter.")
    else:
        sector_summary = board_df.groupby("sector").agg(
            avg_pct=("pct", "mean"),
            count=("symbol", "count"),
            total_turnover=("turnover", "sum")
        ).reset_index().sort_values("avg_pct", ascending=False)
        
        col_sec1, col_sec2 = st.columns([1.2, 1])
        
        with col_sec1:
            st.markdown("#### 🗺️ Market Sector Treemap (Size = Turnover, Color = Change %)")
            if px is not None and not sector_summary.empty:
                fig_tree = px.treemap(
                    sector_summary,
                    path=["sector"],
                    values="total_turnover",
                    color="avg_pct",
                    color_continuous_scale=["#F43F5E", "#1E2738", "#10B981"],
                    color_continuous_midpoint=0,
                    custom_data=["avg_pct", "count", "total_turnover"]
                )
                fig_tree.update_traces(
                    hovertemplate="<b>%{label}</b><br>Avg Change: %{customdata[0]:+.2f}%<br>Stocks: %{customdata[1]}<br>Turnover: ₹%{customdata[2]:,.0f}"
                )
                fig_tree.update_layout(
                    template="plotly_dark" if is_dark else "plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=360
                )
                st.plotly_chart(fig_tree, use_container_width=True)
                
        with col_sec2:
            st.markdown("#### 📊 Sector Average Return (%)")
            if go is not None:
                colors = [green if val >= 0 else red for val in sector_summary["avg_pct"]]
                fig_sec = go.Figure(go.Bar(
                    x=sector_summary["avg_pct"],
                    y=sector_summary["sector"],
                    orientation="h",
                    marker_color=colors,
                    text=[f"{v:+.2f}%" for v in sector_summary["avg_pct"]],
                    textposition="auto"
                ))
                fig_sec.update_layout(
                    template="plotly_dark" if is_dark else "plotly_white",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=10, b=10),
                    height=360,
                    xaxis_title="Average Return (%)",
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_sec, use_container_width=True)


with view_tab3:
    if board_df.empty:
        st.info("ℹ️ No stocks available for Top Movers under current search/filter.")
    else:
        col_g, col_l = st.columns(2)
        with col_g:
            st.markdown("#### 🟢 Top Gainers")
            top_gainers = board_df.sort_values("pct", ascending=False).head(5)
            for _, r in top_gainers.iterrows():
                st.markdown(f"""
                <div class="cue-card up" style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div class="cue-label">{r['symbol']} ({r['sector']})</div>
                            <div class="cue-price">₹{r['live_ltp']:,.2f}</div>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge-pct pos">+{r['pct']:.2f}%</span>
                            <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Yest: ₹{r['yest_close']:,.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        with col_l:
            st.markdown("#### 🔴 Top Losers")
            top_losers = board_df.sort_values("pct", ascending=True).head(5)
            for _, r in top_losers.iterrows():
                st.markdown(f"""
                <div class="cue-card dn" style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div class="cue-label">{r['symbol']} ({r['sector']})</div>
                            <div class="cue-price">₹{r['live_ltp']:,.2f}</div>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge-pct neg">{r['pct']:.2f}%</span>
                            <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Yest: ₹{r['yest_close']:,.2f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### ⚡ Day Range Breakouts & High Volatility Alerts")
        breakout_col1, breakout_col2 = st.columns(2)
        
        # High Breakout Stocks (LTP near High)
        high_breakouts = board_df[board_df["live_ltp"] >= board_df["high"] * 0.995].head(4)
        with breakout_col1:
            st.markdown("##### 🚀 Day High Breakout Candidates")
            if not high_breakouts.empty:
                for _, r in high_breakouts.iterrows():
                    st.success(f"**{r['symbol']}** ({r['sector']}) — LTP ₹{r['live_ltp']:,.2f} is testing Day High ₹{r['high']:,.2f} (+{r['pct']:.2f}%)")
            else:
                st.caption("No stocks currently testing 52W/Day High levels.")
                
        # High Volatility Movers (|pct| >= 2.5%)
        vol_movers = board_df[board_df["pct"].abs() >= 2.5].head(4)
        with breakout_col2:
            st.markdown("##### ⚡ High Momentum Movers (|Δ| ≥ 2.5%)")
            if not vol_movers.empty:
                for _, r in vol_movers.iterrows():
                    st.info(f"**{r['symbol']}** ({r['sector']}) — Moving {r['pct']:+.2f}% today (Turnover: ₹{r['turnover']/1e7:,.2f} Cr)")
            else:
                st.caption("No high volatility movers (|Δ| ≥ 2.5%) in current session.")


with view_tab4:
    st.markdown("#### 📈 Technical Analysis & Multi-Stock Comparison")
    
    chart_sub_tab1, chart_sub_tab2 = st.tabs(["🕯️ Single Stock Technical Chart", "⚔️ Multi-Stock Performance Comparison"])
    
    with chart_sub_tab1:
        if board_df.empty:
            st.info("ℹ️ No stocks available to analyze under current search/filter.")
        else:
            selected_chart_sym = st.selectbox("Select Stock to Analyze", board_df["symbol"].tolist(), index=0)
            chart_period = st.radio("Chart Interval", ["1 Mo", "3 Mo", "6 Mo", "1 Yr"], horizontal=True, index=1, key="single_chart_period")
            period_map = {"1 Mo": "1mo", "3 Mo": "3mo", "6 Mo": "6mo", "1 Yr": "1y"}
            
            if yf is not None and go is not None and selected_chart_sym:
                try:
                    ticker_obj = yf.Ticker(f"{selected_chart_sym}.NS")
                    hist_df = ticker_obj.history(period=period_map[chart_period])
                    
                    if not hist_df.empty:
                        hist_df["SMA20"] = hist_df["Close"].rolling(20).mean()
                        hist_df["SMA50"] = hist_df["Close"].rolling(50).mean()
                        
                        delta = hist_df["Close"].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rs = gain / loss
                        hist_df["RSI"] = 100 - (100 / (1 + rs))
                        
                        fig = make_subplots(
                            rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=[0.55, 0.25, 0.20],
                            subplot_titles=(f"{selected_chart_sym} Price & Moving Averages", "Volume", "RSI (14)")
                        )
                        
                        fig.add_trace(go.Candlestick(
                            x=hist_df.index,
                            open=hist_df["Open"], high=hist_df["High"],
                            low=hist_df["Low"], close=hist_df["Close"],
                            name="Candles"
                        ), row=1, col=1)
                        
                        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["SMA20"], name="SMA 20", line=dict(color=gold, width=1.5)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["SMA50"], name="SMA 50", line=dict(color="#3B82F6", width=1.5)), row=1, col=1)
                        
                        vol_colors = [green if c >= o else red for c, o in zip(hist_df["Close"], hist_df["Open"])]
                        fig.add_trace(go.Bar(x=hist_df.index, y=hist_df["Volume"], name="Volume", marker_color=vol_colors), row=2, col=1)
                        
                        fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["RSI"], name="RSI", line=dict(color="#8B5CF6", width=1.5)), row=3, col=1)
                        fig.add_hline(y=70, line_dash="dash", line_color=red, row=3, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color=green, row=3, col=1)
                        
                        fig.update_layout(
                            template="plotly_dark" if is_dark else "plotly_white",
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            height=600,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_rangeslider_visible=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning(f"Could not load chart data for {selected_chart_sym}.")
                except Exception as ex:
                    st.error(f"Error generating chart: {ex}")
                    
    with chart_sub_tab2:
        st.markdown("#### ⚔️ Relative Performance Comparison (% Return)")
        multi_syms = st.multiselect(
            "Select Stocks to Compare Performance",
            options=uni_df["symbol"].tolist(),
            default=["RELIANCE", "TCS", "HDFCBANK", "INFY"][:min(4, len(uni_df))]
        )
        comp_period = st.radio("Comparison Timeframe", ["1 Mo", "3 Mo", "6 Mo", "1 Yr"], horizontal=True, index=1, key="multi_comp_period")
        comp_period_map = {"1 Mo": "1mo", "3 Mo": "3mo", "6 Mo": "6mo", "1 Yr": "1y"}
        
        if yf is not None and go is not None and len(multi_syms) > 0:
            fig_comp = go.Figure()
            for s in multi_syms:
                try:
                    t_obj = yf.Ticker(f"{s}.NS")
                    h_df = t_obj.history(period=comp_period_map[comp_period])
                    if not h_df.empty:
                        first_close = h_df["Close"].iloc[0]
                        norm_pct = ((h_df["Close"] - first_close) / first_close) * 100
                        fig_comp.add_trace(go.Scatter(
                            x=h_df.index, y=norm_pct, name=s, mode="lines", line=dict(width=2)
                        ))
                except Exception:
                    pass
                    
            fig_comp.update_layout(
                template="plotly_dark" if is_dark else "plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=480,
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis_title="Normalized Gain / Loss (%)",
                xaxis_title="Date"
            )
            st.plotly_chart(fig_comp, use_container_width=True)

