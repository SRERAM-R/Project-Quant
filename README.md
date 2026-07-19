# 📊 Project Quant

**A full-stack quantitative trading analytics platform for Indian equities and F&O — built with Streamlit, pandas, and the Zerodha Kite Connect API.**

Project Quant brings together historical backtesting, live intraday signal scanning, and options-aware paper trading into a single, cohesive dashboard. It is designed to feel like an internal tool at a proprietary trading desk: fast, data-dense, and built around real market mechanics rather than toy examples.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [1. Live Signal Engine](#1-live-signal-engine)
  - [2. Paper Trading Terminal](#2-paper-trading-terminal)
  - [3. Backtest Engine (Stocks)](#3-backtest-engine-stocks)
  - [4. Backtest Engine (Stocks + Options)](#4-backtest-engine-stocks--options)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Data Requirements & Coverage](#data-requirements--coverage)
- [Terminology & Glossary](#terminology--glossary)
- [Important Operational Notes](#important-operational-notes)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

Project Quant is a **Streamlit-based, multi-page analytics dashboard** that lets a trader do three things end-to-end, all backed by the same underlying stock universe, indicator engine, and Zerodha Kite Connect data feed:

1. **Scan** the market live for intraday setups across a curated universe of ~150 NSE stocks, using eight distinct screener strategies.
2. **Backtest** those same strategies — and dedicated momentum-breakout strategies — over multiple years of historical minute-level data, with institutional-grade performance analytics (Sharpe, Sortino, Calmar, drawdown, equity curves, monthly heatmaps, and more).
3. **Paper trade** F&O option contracts in real time against live Kite market data, with full position tracking, unrealized P&L, and a persistent trade log.

The project is organized around a shared analytical core (`strategy.py`) so that the same indicator calculations, stock universe, and performance-metrics logic power every page — there is one source of truth for what "EMA9," "VWAP," or "Sharpe Ratio" means across the entire application.

---

## Features

### 1. Live Signal Engine

Scans the entire stock universe for entry signals across **eight strategies**, refreshed on demand:

| Strategy | Bias |
|---|---|
| Bullish / Bearish Stock Screener | Trend + VWAP + ADX confirmation |
| Bullish / Bearish Test Indicator | Opening-window (09:30–09:45) trend alignment across EMA9/21/50 and VWAP |
| Bullish / Bearish EMA Acceleration Scanner | EMA slope-angle acceleration, sustained over a rolling candle window |
| Opening Range Support Hold | Price holding above the first 5-minute range low |
| Opening Range Resistance Hold | Price holding below the first 5-minute range high |

Results are ranked by `% Change` from the day's open and presented in a live-updating table.

### 2. Paper Trading Terminal

A fully interactive options paper-trading simulator:

- Select a sector, stock, option type (CE/PE), and contract from the live NFO instrument chain.
- Place a **pending order** at a target premium; the terminal polls live prices every 2 seconds and fills automatically once the market reaches your target.
- Once filled, track **unrealized P&L, max favorable/adverse excursion, and time in trade** in real time.
- Exit manually — every closed trade is appended to a running trade log and persisted to a CSV file for later review.

### 3. Backtest Engine (Stocks)

Runs a selected strategy across a chosen stock's historical price history and produces a full analytics suite:

- **Headline metrics:** Net P&L, win rate, expectancy, profit factor, risk/reward, CAGR, Sharpe, Sortino, Calmar, max drawdown
- **Visual analytics:** equity curve, drawdown curve, trade P&L histogram, monthly returns heatmap, win/loss streak chart, rolling 20-trade win rate, holding-time-vs-P&L regression
- **Tabular breakdowns:** performance by month, by day of week, and by intraday session
- **Full trade log**, colour-coded by outcome, exportable to a multi-sheet Excel workbook

### 4. Backtest Engine (Stocks + Options)

Identical analytics suite to the Stocks backtest engine, but every signal generated on the underlying is mapped to the **nearest at/near-the-money option contract** at the time of entry, and P&L is computed on actual option premium movement (using real historical option-chain data) rather than the underlying's price movement — giving a realistic view of how a strategy would have performed if traded via options rather than the stock itself.

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
├── app.py                        # Streamlit entry point — sidebar navigation & global theming
├── styles.py                     # Shared CSS/HTML styling and Plotly theme (single source of visual truth)
├── stocks_list.py                # Tradable stock universe, grouped by sector
├── strategy.py                   # Core analytical engine — indicators, scanners, backtest strategies,
│                                  # options-data mapping, and performance-analytics functions
├── live_signal_engine.py         # Live Signal Engine page
├── paper_trading_terminal.py     # Paper Trading Terminal page
├── backtest_engine.py            # Backtest Engine (Stocks) page
├── options_backtest_engine.py    # Backtest Engine (Stocks + Options) page
├── api_configurations.py         # One-off CLI script to generate a Kite Connect access token
├── historical_data_downloader.py # One-off utility to bulk-download historical OHLC data
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Prerequisites

- **Python 3.10+**
- **A Zerodha trading account with an active Kite Connect API subscription.**
  Kite Connect is a **paid, subscription-based API** — as of writing it costs **₹500/month**, billed directly by Zerodha. Without an active subscription, none of the live-data-dependent pages (Live Signal Engine, Paper Trading Terminal, both Backtest Engines' data downloads) will function, since every data pull in this project — historical or live — is sourced through Kite Connect. You can subscribe at [kite.trade](https://kite.trade/).

---

## Configuration

### Generating and setting your Kite Connect access token

Kite Connect access tokens are valid for a **single trading day** and must be regenerated every morning before use.

1. Fill in your `api_key` and `api_secret` in **`api_configurations.py`**.
2. Run the script:
   ```bash
   python api_configurations.py
   ```
3. Open the printed login URL in your browser, log in, and copy the `request_token` from the redirected URL back into the terminal prompt.
4. The script will print a fresh **`access_token`**.

### ⚠️ Applying the access token across the project

This project does not currently centralize Kite credentials in one place. **You must manually paste the same `api_key` and `access_token` into every file that initializes a `KiteConnect` client**, specifically:

- `live_signal_engine.py`
- `paper_trading_terminal.py`
- `strategy.py`
- `historical_data_downloader.py` (only needed if re-downloading historical data)

Since the access token expires daily, **this needs to be repeated every trading day** before using any live-data page. A future improvement would be to centralize this into a single config module or environment variable — see [Roadmap](#roadmap).

---

## Running the App

```bash
streamlit run app.py
```

Navigate between pages using the sidebar. Each page is independent — you do not need to visit them in any particular order, though the **Live Signal Engine and Paper Trading Terminal require a valid, same-day access token** to function (see [Configuration](#configuration)).

---

## Data Requirements & Coverage

This project does not ship with historical data. Run **`historical_data_downloader.py`** to populate your local data folder before using the backtest engines:

```bash
python historical_data_downloader.py
```

This downloads minute-level OHLC data for the entire stock universe (`stocks_list.py`) via Kite Connect, chunked into API-safe date ranges, and saves each symbol as both Parquet and CSV.

**Historical data coverage differs by page:**

| Page | Data Availability |
|---|---|
| **Backtest Engine (Stocks)** | All stocks have historical data from **01 January 2021** onward. |
| **Backtest Engine (Stocks + Options)** | All stocks have historical options data from **01 June 2026** onward. |

Selecting a date range outside these windows will return incomplete or empty results.

---

## Terminology & Glossary

This dashboard uses a number of trading- and statistics-specific terms (VWAP, Sharpe Ratio, Calmar Ratio, drawdown, expectancy, ADX, DPO, and others) throughout its metrics and charts. **A complete glossary explaining every term used across the dashboard is provided separately as a PDF** (`docs/Project Quant - Terminology Glossary.pdf`) included in this repository. Refer to that document for definitions and the reasoning behind each metric rather than external sources, since a few conventions here (e.g., how breakeven trades are classified, or how "First Candle" fields are defined) are specific to this project's implementation.

---

## Important Operational Notes

A few behaviors are intentional design decisions or current constraints of the project, not bugs — worth knowing before you use it:

- **The Live Signal Engine caches stock data once per session.** Every time you refresh the browser tab (or restart the Streamlit server), that cached data is cleared and re-downloaded from scratch on the next run. If you're in the middle of a scanning session, **avoid refreshing the page** unless you intend to pull fresh data — you'll lose your current session's cache and have to wait for it to redownload.
- **The Live Signal Engine must be manually refreshed each time you want to use it** — it does not auto-poll for new candles in the background. Reload the page (or restart the app) to pull the latest market data before scanning.
- **Paper Trading Terminal auto-refreshes every 2 seconds** while open, to keep live prices current during an active or pending trade.
- **Access tokens expire daily** — see [Configuration](#configuration).

---

## Known Limitations

In the interest of transparency, this project has a few known constraints as of this release:

- Kite Connect credentials are hardcoded per-file rather than centralized in environment variables.
- The options data backtest currently requires manually pre-downloaded option-chain Parquet files for each trading day in the selected range; there is no automated bulk-downloader for options data yet (unlike the stock-only historical downloader).
- The Live Signal Engine's underlying data cache is session-scoped and does not auto-refresh on a timer (see [Important Operational Notes](#important-operational-notes)).

---

## Roadmap

- [ ] Scheduled auto-refresh for the Live Signal Engine's data cache
- [ ] Configurable initial capital and position sizing in the Backtest Engine
- [ ] Additional backtest strategies beyond momentum breakout

---

## Author

**Sreram R**
Built as an end-to-end exploration of quantitative trading infrastructure — from raw market data, through signal generation and backtesting, to simulated live execution — using tools a real trading desk would recognize.
