"""
Project Quant - Historical Data Downloader.

Downloads and caches minute-level historical OHLC data for the entire stock universe from Kite, chunked into API-safe date ranges,
and saves each symbol as both Parquet (for fast loading) and CSV (for inspection).

Author: Sreram R
"""

import os
import time
from datetime import datetime, timedelta

import pandas as pd
from pathlib import Path
from kiteconnect import KiteConnect

from stocks_list import stocks_list

home_directory = Path.home()

api_key=""
access_token=""
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

historical_data_folder = home_directory / "Downloads" / "Stock Market"/ "Historical Stock Data - Copy"
from_date = datetime.strptime("2021-01-01", "%Y-%m-%d")
to_date = datetime.strptime("2026-07-31", "%Y-%m-%d")
interval = "minute"

instruments = kite.instruments("NSE")
token_map = {i["tradingsymbol"]: i["instrument_token"] for i in instruments}

def get_chunks(from_date, to_date, chunk_days=60):
    chunks = []
    start_date = from_date
    while start_date <= to_date:
        end_date = min(start_date + timedelta(days=chunk_days), to_date)
        chunks.append((start_date, end_date))
        start_date = end_date + timedelta(days=1)
    return chunks

def download_historical_data(symbol):
    file_path = os.path.join(historical_data_folder, f"{symbol}.parquet")
    excel_file_path = os.path.join(historical_data_folder, f"{symbol}.csv")

    if os.path.exists(file_path):
        print(f"{symbol}: file already exists.")
        return

    token = token_map.get(symbol)
    if not token:
        print(f"{symbol}: not found in NSE. Skipping...")
        return

    print(f"{symbol}: Downloading...")
    chunks = get_chunks(from_date, to_date)
    all_data = []
    failed_chunks = []

    for i, (start, end) in enumerate(chunks, 1):
        try:
            raw = kite.historical_data(
                instrument_token=token,
                from_date=start.strftime("%Y-%m-%d"),
                to_date=end.strftime("%Y-%m-%d"),
                interval=interval,
                continuous=False,
            )
            if raw:
                all_data.append(pd.DataFrame(raw))
            time.sleep(0.3)
        except Exception as e:
            print(f"{symbol}: chunk {i} ({start.date()} to {end.date()}) failed - {e}")
            failed_chunks.append((start.date(), end.date()))
        time.sleep(2)

    if not all_data:
        print(f"{symbol}: no data found")
        return

    dataset = pd.concat(all_data, ignore_index=True)
    dataset = dataset.rename(columns={
        "date": "Datetime",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })
    dataset["Datetime"] = pd.to_datetime(dataset["Datetime"], errors="coerce")
    dataset.set_index("Datetime", inplace=True)
    dataset.sort_index(inplace=True)
    dataset = dataset[~dataset.index.duplicated(keep="first")]

    os.makedirs(historical_data_folder, exist_ok=True)
    dataset.to_parquet(file_path, engine="pyarrow", compression="snappy")
    dataset.to_csv(excel_file_path)

    if failed_chunks:
        print(f"{symbol}: saved {len(dataset)} candles, WARNING - {len(failed_chunks)} chunk(s) failed: {failed_chunks}")
    else:
        print(f"{symbol}: saved {len(dataset)} candles")

def download_all_data(stocks):
    total = len(stocks)
    for i, symbol in enumerate(stocks, 1):
        print(f"[{i}/{total}] ", end="")
        download_historical_data(symbol)
        time.sleep(0.5)
    print("Downloaded all stocks successfully.")

if __name__ == "__main__":
    print("Program has successfully begun...")
    download_all_data(stocks_list)
    print("Successfully downloaded data.")