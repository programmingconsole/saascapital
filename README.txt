SAAS CAPITAL  -  LIVE MARKET PULSE  (Student Starter Kit)
=============================================================
This is the COMPLETE Live Terminal - the exact tool from Module 15.
Global cues (Nifty, Sensex, Dow, Nasdaq, Nikkei, Crude, Gold, USDINR...) plus a
"yesterday -> live" board for the most active stocks. Auto-refreshes every 30s.

Live prices come from Yahoo Finance (free, no login, no broker token).
The stock list for the board comes from one NSE bhavcopy day (also free).

--------------------------------------------------------------------
THE EASY WAY  (let Claude Code set it up)
--------------------------------------------------------------------
Open Claude Code IN THIS FOLDER and paste this:

    I unzipped a Streamlit live-market app in this folder. Please:
    1. Install everything in requirements.txt.
    2. Run auto_update.py once to download the latest NSE bhavcopy into the
       database (so the 'yesterday to live' board has stocks).
    3. Launch it with:  streamlit run live_terminal.py
    Explain each step in plain words as you go.

--------------------------------------------------------------------
THE MANUAL WAY  (PowerShell)
--------------------------------------------------------------------
  pip install -r requirements.txt
  python auto_update.py              # one bhavcopy day -> fills the stock board
  streamlit run live_terminal.py     # opens the live dashboard

Note: the Global Cues work immediately. The "yesterday -> live" stock board
appears once auto_update.py has imported at least one bhavcopy day.

Two engines, kept separate: this app only READS the bhavcopy database; it never
writes live prices into it.

Education only.  SAAS Capital
