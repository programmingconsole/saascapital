"""
SAAS Capital | LIVE TERMINAL PRO  —  Institutional Live Market Suite
========================================================================
Advanced, responsive live market dashboard featuring:
  • Real-time Global Market Cues (India, US, Europe, Asia, Commodities, FX)
  • Yesterday → Live Equity Board with live Yahoo Finance feeds
  • Real-time Sector Breakdown & Performance Heatmap
  • Interactive Stock Screener with Search & Multi-sector filtering
  • Technical Charting & Analysis Modal (Candlesticks, Volume, RSI, Moving Averages)
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
    from plotly.subplots import make_subplots
except Exception:
    go = None

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
    initial_sidebar_state="expanded"
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
# SECTION 2: YESTERDAY → LIVE SCREENER & HEATMAP
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")

uni_df = get_bhavcopy_universe()
if uni_df.empty:
    st.error("⚠️ No Bhavcopy data available. Please run `auto_update.py` to import market data.")
    st.stop()

latest_bhav_date = uni_df.attrs.get("date", "Unknown Date")
st.markdown(f"### 📊 Yesterday ({latest_bhav_date}) → Live Equity Screener")

# Screener Controls (Search & Sector Filter)
col_search, col_sector, col_sort = st.columns([2, 2, 1.5])
with col_search:
    search_query = st.text_input("🔍 Search Symbol", placeholder="e.g. RELIANCE, TCS, ZOMATO, HDFCBANK...").strip().upper()

all_sectors = ["All Sectors"] + sorted(list(set(uni_df["sector"])))
with col_sector:
    selected_sector = st.selectbox("📂 Filter Sector", all_sectors)

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
if search_query:
    filtered_df = filtered_df[filtered_df["symbol"].str.contains(search_query)]
if selected_sector != "All Sectors":
    filtered_df = filtered_df[filtered_df["sector"] == selected_sector]

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
    if sort_option == "% Gainers":
        board_df = board_df.sort_values("pct", ascending=False)
    elif sort_option == "% Losers":
        board_df = board_df.sort_values("pct", ascending=True)
    elif sort_option == "Symbol A-Z":
        board_df = board_df.sort_values("symbol", ascending=True)
    else:
        board_df = board_df.sort_values("turnover", ascending=False)

# Board Views: Table, Heatmap, Gainers/Losers, Technical Chart
view_tab1, view_tab2, view_tab3, view_tab4 = st.tabs([
    "📋 Screener Table", "🔥 Sector Heatmap", "🚀 Top Movers", "📈 Technical Chart & Insights"
])

with view_tab1:
    if board_df.empty:
        st.info("ℹ️ No matching stocks found for your filter/search. Try adjusting the search term or increasing the 'Stocks to Track' slider in the sidebar.")
    else:
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


with view_tab2:
    if board_df.empty:
        st.info("ℹ️ No sector data available for the current filter.")
    else:
        sector_summary = board_df.groupby("sector").agg(
            avg_pct=("pct", "mean"),
            count=("symbol", "count"),
            total_turnover=("turnover", "sum")
        ).reset_index().sort_values("avg_pct", ascending=False)
        
        st.markdown("#### Sector Returns Overview")
        
        if go is not None:
            colors = [green if val >= 0 else red for val in sector_summary["avg_pct"]]
            fig_sec = go.Figure(go.Bar(
                x=sector_summary["sector"],
                y=sector_summary["avg_pct"],
                marker_color=colors,
                text=[f"{v:+.2f}%" for v in sector_summary["avg_pct"]],
                textposition="auto"
            ))
            fig_sec.update_layout(
                template="plotly_dark" if is_dark else "plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=40),
                height=340,
                yaxis_title="Average Change (%)",
                xaxis_title="Sector"
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


with view_tab4:
    st.markdown("#### 📈 Interactive Technical Analysis")
    if board_df.empty:
        st.info("ℹ️ No stocks available to analyze under current search/filter.")
    else:
        selected_chart_sym = st.selectbox("Select Stock to Analyze", board_df["symbol"].tolist(), index=0)
    
    chart_period = st.radio("Chart Interval", ["1 Mo", "3 Mo", "6 Mo", "1 Yr"], horizontal=True, index=1)
    period_map = {"1 Mo": "1mo", "3 Mo": "3mo", "6 Mo": "6mo", "1 Yr": "1y"}
    
    if yf is not None and go is not None and selected_chart_sym:
        try:
            ticker_obj = yf.Ticker(f"{selected_chart_sym}.NS")
            hist_df = ticker_obj.history(period=period_map[chart_period])
            
            if not hist_df.empty:
                # Calculate Technical Indicators
                hist_df["SMA20"] = hist_df["Close"].rolling(20).mean()
                hist_df["SMA50"] = hist_df["Close"].rolling(50).mean()
                
                # RSI 14
                delta = hist_df["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                hist_df["RSI"] = 100 - (100 / (1 + rs))
                
                # Plotly Candlestick + Volume + RSI
                fig = make_subplots(
                    rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.03, row_heights=[0.55, 0.25, 0.20],
                    subplot_titles=(f"{selected_chart_sym} Price & Moving Averages", "Volume", "RSI (14)")
                )
                
                # Candlesticks
                fig.add_trace(go.Candlestick(
                    x=hist_df.index,
                    open=hist_df["Open"], high=hist_df["High"],
                    low=hist_df["Low"], close=hist_df["Close"],
                    name="Candles"
                ), row=1, col=1)
                
                # SMAs
                fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["SMA20"], name="SMA 20", line=dict(color=gold, width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df["SMA50"], name="SMA 50", line=dict(color="#3B82F6", width=1.5)), row=1, col=1)
                
                # Volume
                vol_colors = [green if c >= o else red for c, o in zip(hist_df["Close"], hist_df["Open"])]
                fig.add_trace(go.Bar(x=hist_df.index, y=hist_df["Volume"], name="Volume", marker_color=vol_colors), row=2, col=1)
                
                # RSI
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

