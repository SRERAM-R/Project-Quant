"""
Project Quant - Live Stock Scanner.

Scans live intraday price data for the selected screener's entry signals across the stocks.

Author: Sreram R
"""

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from strategy import (bullish_ema_acceleration_scanner, bearish_ema_acceleration_scanner,
                      bearish_stock_scanner, bullish_stock_scanner,
                      opening_range_resistance_hold, opening_range_support_hold,
                      download_initial_stock_data, refresh_stock_data)

def live_scanner():
    st.subheader("PROJECT QUANT")
    st.title("📡 Live Stock Scanner")
    st.caption("Real-time momentum & breakout screener")

    results = []
    list_of_strategies = ["Bullish EMA Acceleration Scanner",
                          "Bearish EMA Acceleration Scanner",
                          "Bullish Stock Screener",
                          "Bearish Stock Screener",
                          "Opening Range Support Hold",
                          "Opening Range Resistance Hold"
    ]

    if "stock_cache_data" not in st.session_state:
        with st.spinner("Loading initial stock data..."):
            st.session_state.stock_cache_data = download_initial_stock_data()
        st.session_state.last_refresh_time = pd.Timestamp.now()

    st_autorefresh(interval=300000, key="live_scanner_refresh")
    refresh_cooldown_seconds = 300
    seconds_since_refresh = (pd.Timestamp.now() - st.session_state.last_refresh_time).total_seconds()
    if seconds_since_refresh >= refresh_cooldown_seconds:
        with st.spinner("Refreshing latest candles..."):
            st.session_state.stock_cache_data = refresh_stock_data(st.session_state.stock_cache_data)
        st.session_state.last_refresh_time = pd.Timestamp.now()

    st.caption(f"Last updated : {st.session_state.last_refresh_time.strftime('%H:%M:%S')}")

    strategy = st.selectbox(label="Strategy", options=list_of_strategies)
    stock_data = st.session_state.stock_cache_data
    run_scan = st.button("Run Scan")

    if run_scan:
        with st.spinner("Running scan"):
            if strategy == "Bullish Stock Screener":
                results = bullish_stock_scanner(stock_data)
            elif strategy == "Bearish Stock Screener":
                results = bearish_stock_scanner(stock_data)
            elif strategy == "Opening Range Support Hold":
                results = opening_range_support_hold(stock_data)
            elif strategy == "Opening Range Resistance Hold":
                results = opening_range_resistance_hold(stock_data)
            elif strategy == "Bullish EMA Acceleration Scanner":
                results = bullish_ema_acceleration_scanner(stock_data)
            elif strategy == "Bearish EMA Acceleration Scanner":
                results = bearish_ema_acceleration_scanner(stock_data)
        results = pd.DataFrame(results)
        if results.empty:
            st.info("No stocks found!!!")
        else:
            results.drop_duplicates(keep="first", inplace=True)
            results["% Change"] = round((results["Close"] - results["First Candle Open"]) * 100.0 / results["First Candle Open"], 2)
            if (strategy == "Opening Range Support Hold" or
                strategy == "Bullish Stock Screener" or
                strategy == "Bullish EMA Acceleration Scanner"):
                results = results[results["% Change"] > 0]
                results.sort_values(by="VWAP_Angle", ascending=False, inplace=True)
            elif (strategy == "Opening Range Resistance Hold" or
                  strategy == "Bearish Stock Screener" or
                  strategy == "Bearish EMA Acceleration Scanner"):
                results = results[results["% Change"] < 0]
                results.sort_values(by="VWAP_Angle", inplace=True)
            results.reset_index(drop=True, inplace=True)
            st.write("Number Of Stocks:", len(results))
            st.dataframe(results[["Datetime", "Stock", "VWAP_Angle", "% Change"]])
            with st.expander("Show Complete Data"):
                st.dataframe(results)





