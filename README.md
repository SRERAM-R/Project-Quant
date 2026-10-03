# 📊 Project Quant

**A quantitative trading analytics platform for Indian equities — built with Streamlit, pandas, and the Zerodha Kite Connect API.**

Project Quant unifies historical backtesting, live intraday signal scanning, technical crossover tracking, and options-aware paper trading within a single, cohesive dashboard. It is engineered to feel like an internal tool at a proprietary trading desk — fast, data-dense, and grounded in real market mechanics rather than simplified, illustrative examples.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [1. Live Stock Scanner](#1-live-stock-scanner)
  - [2. Crossover Tracker](#2-crossover-tracker)
  - [3. Paper Trading Terminal](#3-paper-trading-terminal)
  - [4. Backtest Engine (Stocks)](#4-backtest-engine-stocks)
  - [5. Backtest Engine (Stocks + Options)](#5-backtest-engine-stocks--options)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Repository Scope](#repository-scope)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Data Requirements & Coverage](#data-requirements--coverage)
- [Terminology & Glossary](#terminology--glossary)
- [Important Operational Notes](#important-operational-notes)
- [Known Limitations & Design Decisions](#known-limitations--design-decisions)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

Project Quant is a **Streamlit-based, multi-page analytics dashboard** that lets a trader do four things end-to-end, all backed by the same underlying stock universe, indicator engine, and Zerodha Kite Connect data feed:

1. **Scan** the market live for intraday setups across a curated universe of ~150 NSE stocks, using six distinct screener strategies.
2. **Track** sustained EMA/VWAP crossovers and false-breakout rejections across the entire universe in real time.
3. **Backtest** strategies over multiple years of historical minute-level data, with institutional-grade performance analytics (Sharpe, Sortino, Calmar, drawdown, equity curves, monthly heatmaps, and more) — for both the underlying stock and its mapped options contract.
4. **Paper trade** F&O option contracts in real time against live Kite market data, with full position tracking, unrealized P&L, and a persistent trade log.

The project is organized around a shared analytical core (`strategy.py`) so that the same indicator calculations, stock universe, and performance-metrics logic power every page — there is one source of truth for what "EMA9," "VWAP," or "Sharpe Ratio" means across the entire application. *(Note: `strategy.py` and `paper_trading_terminal.py` are excluded from this public repository — see [Repository Scope](#repository-scope) for what that means for running the project as published.)*

---

## Features

### 1. Live Stock Scanner

Scans the entire stock universe for entry signals across **six strategies**, refreshed automatically every 5 minutes (and on demand):

| Strategy | Bias |
|---|---|
| Bullish / Bearish Stock Screener | Trend + VWAP + ADX confirmation |
| Bullish / Bearish EMA Acceleration Scanner | EMA slope-angle acceleration, sustained over a rolling candle window |
| Opening Range Support Hold | Price holding above the first 5-minute range low |
| Opening Range Resistance Hold | Price holding below the first 5-minute range high |

Results are ranked by `% Change` from the day's open and presented in a live-updating table.

### 2. Crossover Tracker

Continuously scans every stock in the universe across **seven** live technical signals, updating every 5 minutes:

- **Sustained Crossovers** — EMA9 / EMA21 / VWAP alignment holding consistently over a rolling window (bullish and bearish). Each direction has an independently configurable entry window and a separate, independently configurable exit window, so how quickly a stock is added versus how quickly it's removed can be tuned separately.
- **Rejections** — a brief opposite-direction spike that gets rejected back into the prevailing trend, split into a trend phase, a spike phase, and a confirmation phase (bullish and bearish), with the same independently configurable exit logic as above.
- **Abnormal Volume** — flags a candle whose volume spikes to several times the average of the preceding candles, a classic early signal of institutional participation or a breaking news event.
- **Day High Breakout / Day Low Breakdown** — flags a stock closing decisively beyond its own intraday high or low on two consecutive candles, with a minimum time gap enforced from when that extreme was set (filtering out breakouts that are really just noise immediately following the extreme).

Sustained Crossover and Rejection entries persist in their table until their dedicated exit condition is met — not simply the moment the original entry condition weakens — giving a stable, at-a-glance view of confirmed technical states. Abnormal Volume and breakout events are logged as a running record of the session's occurrences for that stock, since they represent discrete events rather than a persisting state.

### 3. Paper Trading Terminal

A fully interactive, single-position options paper-trading simulator:

- Select a sector, stock, option type (CE/PE), and contract from the live NFO instrument chain.
- Place a **pending order** at a target premium; the terminal polls live prices every 2 seconds and fills once the market reaches your target.
- Once filled, track **unrealized P&L, max favorable/adverse excursion, and time in trade** in real time.
- Exit manually — every closed trade is appended to a running trade log and persisted to a CSV file for later review.

*By design, only one position can be open at a time — this keeps the simulator's state model simple and mirrors a disciplined, one-trade-at-a-time trading approach rather than a portfolio-level system.*

### 4. Backtest Engine (Stocks)

Runs a selected strategy across a chosen stock's historical price history and produces a full analytics suite:

- **Headline metrics:** Net P&L, win rate, expectancy, profit factor, risk/reward, CAGR, Sharpe, Sortino, Calmar, max drawdown
- **Visual analytics:** equity curve, drawdown curve, trade P&L histogram, monthly returns heatmap, win/loss streak chart, rolling 20-trade win rate, holding-time-vs-P&L regression
- **Tabular breakdowns:** performance by month, by day of week, and by intraday session
- **Full trade log**, colour-coded by outcome, exportable to a multi-sheet Excel workbook

All return-based metrics (CAGR, Calmar) assume a fixed notional starting capital of **₹25,000** — this is a simplifying assumption for annualized-return calculations, not a constraint on position sizing.

> 📖 Every metric shown on this page (Sharpe, Sortino, Calmar, expectancy, profit factor, drawdown, and more) is defined in detail in the **[Project Quant Terminology Glossary](./Project%20Quant%20Terminology%20Glossary.pdf)** included with this project.

### 5. Backtest Engine (Stocks + Options)

Identical analytics suite to the Stocks backtest engine, but every signal generated on the underlying is mapped to the **nearest-expiry, at-the-money (ATM) option contract** at the time of entry, and P&L is computed on actual historical option-premium movement rather than the underlying's price movement — giving a realistic view of how a strategy would have performed if traded via options rather than the stock itself.

**Notes on options mechanics modeled here:**
- Only the **at-the-money strike** is considered by default — the engine does not currently backtest OTM or ITM strike selection.
- In reality, F&O stock options are restricted from taking fresh positions in the **nearest-weekly/monthly expiry for the final 2 trading days before expiry**, due to SEBI's compulsory physical delivery norms for stock derivatives. This engine does not currently model that restriction — a live/production version of this strategy would need to account for it when close to expiry.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI / App Framework | [Streamlit](https://streamlit.io/) |
| Data Manipulation | [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Technical Indicators | [pandas-ta](https://github.com/twopirllc/pandas-ta), [ta](https://github.com/bukosabino/ta) (ADX) |
| Charting | [Plotly](https://plotly.com/python/) (Graph Objects + Express) |
| Market Data & Execution | [Zerodha Kite Connect API](https://kite.trade/) |
| Live Auto-Refresh | [streamlit-autorefresh](https://pypi.org/project/streamlit-autorefresh/) |
| File I/O | [XlsxWriter](https://xlsxwriter.readthedocs.io/) (Excel export), [PyArrow](https://arrow.apache.org/docs/python/) (Parquet) |

---

## Project Structure

```
project-quant/
├── main.py                       # Streamlit entry point — sidebar navigation & global theming
├── styles.py                     # Shared CSS/HTML styling and Plotly theme (single source of visual truth)
├── stocks_list.py                # Tradable stock universe, grouped by sector
├── strategy.py                   # ⛔ NOT included in this repository — see "Repository Scope" below
├── live_stock_scanner.py         # Live Stock Scanner page
├── crossover_tracker.py          # Crossover Tracker page
├── paper_trading_terminal.py     # ⛔ NOT included in this repository — see "Repository Scope" below
├── backtest_engine.py            # Backtest Engine (Stocks) page
├── options_backtest_engine.py    # Backtest Engine (Stocks + Options) page
├── generate_access_token.py      # One-off CLI script to generate a Kite Connect access token
├── get_historical_data.py        # One-off utility to bulk-download historical OHLC data (stocks)
├── download_options_data.py      # Daily utility to download historical intraday options data
├── sample_data/                  # Sample historical data for a small set of stocks (see below)
├── requirements.txt              # Python dependencies
└── README.md
```

### ⚠️ Repository Scope

This public repository intentionally **excludes two files: `strategy.py` and `paper_trading_terminal.py`.**

Because `strategy.py` is the shared analytical core imported by every other page — indicators, scanners, backtest logic, and options-data mapping all live there — **this repository, as published, will not run end-to-end out of the box.** This is a deliberate scope decision for this public copy, not an oversight, and it isn't intended to misrepresent the project as immediately runnable by a stranger cloning it.

To still allow meaningful exploration of the codebase and its output:

- **Sample historical equity data** for three stocks — **HDFC Bank, Reliance Industries, and TCS** — is bundled directly in this repository, so the data structures, formats, and the general shape of the pipeline can be inspected without a live Kite Connect subscription.
- **Sample historical options data for 5 trading days (01–05 June 2026)** is bundled as well, covering the same three stocks, so the options-backtest data flow can be reviewed similarly.
- The full, functional codebase — including `strategy.py` and `paper_trading_terminal.py` — is available on request, and I'm glad to walk through it directly (including a live demo) in an interview setting.

---

## Prerequisites

- **Python 3.10+**
- **A Zerodha trading account with an active Kite Connect API subscription.**
  Kite Connect is a **paid, subscription-based API** — as of writing it costs **₹500/month**, billed directly by Zerodha. Without an active subscription, none of the live-data-dependent pages (Live Stock Scanner, Crossover Tracker, Paper Trading Terminal, and the historical/options data downloaders) will function, since every data pull in this project — historical or live — is sourced through Kite Connect. You can subscribe at [kite.trade](https://kite.trade/).
- **Project dependencies** — install each of the following before running the app:
  ```bash
  pip install streamlit
  pip install pandas
  pip install numpy
  pip install plotly
  pip install kiteconnect
  pip install streamlit-autorefresh
  pip install pandas-ta
  pip install ta
  pip install statsmodels
  pip install xlsxwriter
  pip install pyarrow
  ```
  | Package | Used for |
  |---|---|
  | `streamlit` | App framework / UI |
  | `pandas` | Data manipulation across every page |
  | `numpy` | Numerical calculations (CAGR, Sharpe/Sortino, slope-angle math) |
  | `plotly` | All charts — equity curve, drawdown, histograms, heatmaps |
  | `kiteconnect` | Zerodha Kite Connect API client — all live and historical market data |
  | `streamlit-autorefresh` | Auto-refreshing pages (Live Stock Scanner, Crossover Tracker, Paper Trading Terminal) |
  | `pandas-ta` | Technical indicators — EMA, VWAP, DPO |
  | `ta` | ADX indicator specifically |
  | `statsmodels` | Required by Plotly's OLS trendline on the Holding Time vs. P&L chart |
  | `xlsxwriter` | Excel export in both Backtest Engines |
  | `pyarrow` | Parquet read/write for historical stock and options data |

---

## Configuration

### Generating and setting your Kite Connect access token

Kite Connect access tokens are valid for a **single trading day** and must be regenerated every morning before use.

1. Fill in your `api_key` and `api_secret` in **`generate_access_token.py`**.
2. Run the script:
   ```bash
   python generate_access_token.py
   ```
3. Open the printed login URL in your browser, log in, and copy the `request_token` from the redirected URL back into the terminal prompt.
4. The script will print a fresh **`access_token`**.

### ⚠️ Applying the access token across the project

This project does not currently centralize Kite credentials in one place. **You must manually paste the same `api_key` and `access_token` into every file that initializes a `KiteConnect` client**, specifically:

- `live_stock_scanner.py` *(via `strategy.py`)*
- `crossover_tracker.py` *(via `strategy.py`)*
- `paper_trading_terminal.py`
- `strategy.py`
- `get_historical_data.py` (only needed if re-downloading historical stock data)
- `download_options_data.py` (only needed if downloading options data)

Since the access token expires daily, **this needs to be repeated every trading day** before using any live-data page. This is a deliberate simplification for a single-user, local-first project — see [Known Limitations & Design Decisions](#known-limitations--design-decisions).

> Note: `strategy.py` and `paper_trading_terminal.py` are excluded from this public repository — see [Repository Scope](#repository-scope). The list above reflects where credentials are configured in the full, private version of the codebase.

---

## Running the App

1. Open a terminal.
2. Copy the full file path of `main.py` on your machine.
3. Run:
   ```bash
   streamlit run "<full path to main.py>"
   ```
   For example, on Windows:
   ```bash
   streamlit run "C:\Users\<you>\Downloads\Stock Market\Project Quant\main.py"
   ```

Navigate between pages using the sidebar.

> **Note:** pages are *not* fully independent. The Live Stock Scanner and Crossover Tracker share a single cached copy of stock data behind the scenes for efficiency. Visiting Crossover Tracker before Live Stock Scanner in a session can, in rare cases, cause the Scanner page to briefly error on first load — simply reselect the page and it will recover. See [Known Limitations](#known-limitations--design-decisions) for details.

---

## Data Requirements & Coverage

This project does not ship with the full historical dataset. Run **`get_historical_data.py`** to populate your local data folder before using the stock backtest engine:

```bash
python get_historical_data.py
```

This downloads minute-level OHLC data for the entire stock universe (`stocks_list.py`) via Kite Connect, chunked into API-safe date ranges, and saves each symbol as both Parquet and CSV.

For the options backtest engine, run **`download_options_data.py`** once per trading day you want covered. This script has no command-line arguments by design — simply:

1. Open `download_options_data.py`.
2. Change the `current_date` variable near the top of the file to the trading day you want to download.
3. Run:
   ```bash
   python download_options_data.py
   ```
4. Repeat for every additional trading day you want available for options backtesting.

This is intentionally a **manual, single-day-per-run** utility rather than a bulk/range downloader — see [Known Limitations & Design Decisions](#known-limitations--design-decisions).

### Expected folder structure

Both downloader scripts, and the backtest engines that read their output, expect the following folder layout under your user home directory:

```
Downloads/
└── Stock Market/
    ├── Project Quant/              # this repository (cloned/extracted here)
    ├── Historical Stock Data/      # {stock}.csv / {stock}.parquet — from get_historical_data.py
    └── Historical Options Data/    # {date}.parquet — from download_options_data.py
```

**Historical data coverage differs by page:**

| Page | Data Availability |
|---|---|
| **Backtest Engine (Stocks)** | Historical data from **01 January 2021** to **31 July 2026**. |
| **Backtest Engine (Stocks + Options)** | Historical options data from **01 June 2026** onward, and only for the specific trading days you've individually downloaded via `download_options_data.py`. |

Selecting a date range outside these windows, or for a day you haven't downloaded options data for, will return incomplete or empty results with an on-screen message rather than a crash.

**For quick exploration without a Kite Connect subscription or the full data pipeline**, the `sample_data/` folder bundled with this repository includes:
- Historical equity data for **HDFC Bank, Reliance Industries, and TCS**
- Historical options data for these same three stocks, covering **01–05 June 2026**

This sample set is enough to inspect the data formats and pipeline structure, though running the backtest engines against it still requires `strategy.py` — see [Repository Scope](#repository-scope).

---

## Terminology & Glossary

The **Backtest Engine (Stocks)** and **Backtest Engine (Stocks + Options)** pages surface a large number of trading- and statistics-specific terms — VWAP, Sharpe Ratio, Sortino Ratio, Calmar Ratio, drawdown, expectancy, profit factor, ADX, DPO, and others.

**A complete glossary explaining every one of these terms, specifically as used on both backtest pages, is provided as a PDF** - [Project Quant Terminology Glossary](./Project%20Quant%20Terminology%20Glossary.pdf) - included in this repository. Refer to that document for definitions and the reasoning behind each metric rather than external sources, since a few conventions here (e.g., how breakeven trades are classified, or how "First Candle" fields are defined) are specific to this project's implementation.

---

## Important Operational Notes

A few behaviors are intentional design decisions or current constraints of the project, not bugs — worth knowing before you use it:

- **The Live Stock Scanner and Crossover Tracker cache stock data once per session** and refresh it automatically on a timer (5 minutes). Restarting the Streamlit server clears this cache and triggers a fresh download on next load.
- **Live Stock Scanner results reflect the exact moment "Run Scan" is clicked** — results are intentionally not persisted across the page's autorefresh cycle, so every scan always reflects the latest available candle data rather than a stale snapshot.
- **Paper Trading Terminal auto-refreshes every 2 seconds** while open, to keep live prices current during an active or pending trade.
- **Access tokens expire daily** — see [Configuration](#configuration).
- **Only one paper trade can be open at a time.**

---

## Known Limitations & Design Decisions

In the interest of transparency, this section documents constraints and tradeoffs that were made deliberately during development, rather than leaving them undocumented:

**Architecture & credentials**
- Kite Connect credentials are hardcoded per-file rather than centralized into a shared client or environment variables — a deliberate simplification for a single-user, local-first tool.
- `backtest_engine.py` and `options_backtest_engine.py` share a large amount of rendering/analytics code by design, kept as two separate files rather than refactored into a shared module, to keep each backtest engine self-contained and independently readable.
- Live-page indicator calculations (`strategy.py`) and backtest-page indicator calculations are computed via two separate code paths rather than one shared function — a known duplication, accepted for this version.

**Live Stock Scanner & Crossover Tracker**
- These two pages share a single cached copy of underlying stock data (`session_state.stock_cache_data`) for efficiency. Visiting Crossover Tracker before Live Stock Scanner in the same session can occasionally surface a one-time error on the Scanner page's first load; reselecting the page resolves it.
- Crossover Tracker refreshes its data on every autorefresh tick (~3 minutes) without an additional cooldown gate, unlike the Live Scanner's throttled refresh.
- Live Stock Scanner results intentionally reset on every rerun rather than persisting, so results always reflect the most current candle data.

**Backtesting methodology**
- Both backtest engines assume a fixed notional starting capital of ₹25,000 for CAGR/Calmar calculations; this is not currently configurable via the UI.
- Trades entered between 9:15–9:30 AM (the opening 15 minutes of the session) are intentionally excluded from the Hourly Statistics breakdown.
- Trades held longer than ~6 hours (370 minutes) are excluded from backtest results as a data-quality filter.
- A trade with exactly ₹0 net P&L is classified as a loss for win/loss streak purposes.
- Sortino Ratio uses a simplified downside-deviation calculation (based on losing days only) rather than the full textbook definition across all periods.
- The options backtest displays CAGR/Calmar in scientific notation (rather than a rounded decimal, as in the stocks-only engine) since leveraged options P&L can produce very large magnitudes that are more readable this way.
- The options backtest engine's bullish/bearish EMA-acceleration confirmation windows use different rolling-window lengths for bullish vs. bearish signals — a deliberate, independently-tuned choice rather than a symmetric default.

**Options data pipeline**
- Only the at-the-money (ATM) strike is considered by default when mapping a signal to an option contract; OTM/ITM strike selection is not currently modeled.
- The 2-day pre-expiry restriction on fresh stock-option positions (SEBI's compulsory physical delivery rule) is not currently modeled in the backtest engine.
- `download_options_data.py` is a manual, single-trading-day-per-run utility with no built-in backfill/date-range mode, and does not check for or skip already-downloaded dates — re-running it for a date you've already fetched will silently overwrite that file.

**Historical data pipeline**
- `get_historical_data.py` treats a stock's data file as "complete" once it exists locally, even if some chunks failed to download partway through a prior run. Gaps from partial failures are not automatically detected or retried — verify coverage manually if a backtest looks off for a specific stock.

---

## Roadmap

- [ ] Centralize Kite credentials into a single shared client / environment-variable configuration
- [ ] Configurable initial capital and position sizing in the Backtest Engine
- [ ] OTM/ITM strike selection in the options backtest engine
- [ ] Model the pre-expiry physical-delivery trading restriction in the options backtest
- [ ] Date-range/backfill support for the options data downloader
- [ ] Additional backtest strategies beyond momentum breakout

---

## Author

**Sreram R**
Built as an end-to-end exploration of quantitative trading infrastructure — from raw market data, through signal generation and backtesting, to simulated live execution — using tools a real trading desk would recognize.
