"""
Project Quant - Crossover Tracker.

Scans live intraday price data for the selected screener's entry signals across the stocks.

Author: Sreram R
"""

import pandas as pd
import streamlit as st
from datetime import time
from streamlit_autorefresh import st_autorefresh

from strategy import get_cached_indicator_data, download_initial_stock_data, refresh_stock_data
from stocks_list import stocks_list

sustain_recent_window = 10
sustain_recent_min = 7
sustain_prior_window = 20
sustain_prior_min = 15

rejection_trend_window = 20
rejection_trend_min = 15
rejection_spike_window = 5
rejection_spike_min = 1
rejection_confirmation_window = 20
rejection_confirmation_min = 15
sustained_exit_window = 5
rejection_exit_window = 5

volume_window = 20
volume_multiplier = 10
breakout_time_difference_in_minutes = 15

autorefresh_interval = 300000

def is_sustained_crossover(indicator_data, direction):
    total_candled_needed = sustain_prior_window + sustain_recent_window
    if len(indicator_data) < total_candled_needed:
        return False

    recent = indicator_data.tail(sustain_recent_window)
    prior = indicator_data.iloc[-total_candled_needed : -sustain_recent_window]

    if direction == "bullish":
        recent_condition = ((recent["Close"] > recent["VWAP"]) &
                            (recent["EMA21"] > recent["VWAP"]) &
                            (recent["EMA9"] > recent["EMA21"]) &
                            (recent["EMA21_Angle"] > 0) &
                            (recent["VWAP_Angle"] > 0)
                            )
        prior_condition = ((prior["Close"] <= prior["VWAP"]) &
                            (prior["EMA21"] < prior["VWAP"]) &
                            (prior["EMA9"] < prior["VWAP"])
                            )
    else:
        recent_condition = ((recent["Close"] < recent["VWAP"]) &
                            (recent["EMA21"] < recent["VWAP"]) &
                            (recent["EMA9"] < recent["EMA21"]) &
                            (recent["EMA21_Angle"] < 0) &
                            (recent["VWAP_Angle"] < 0)
                            )
        prior_condition = ((prior["Close"] >= prior["VWAP"]) &
                            (prior["EMA21"] > prior["VWAP"]) &
                            (prior["EMA9"] > prior["VWAP"])
                            )

    return recent_condition.sum() >= sustain_recent_min and prior_condition.sum() >= sustain_prior_min

def is_rejection(indicator_data, direction):
    total_needed = rejection_trend_window + rejection_spike_window +  rejection_confirmation_window
    if len(indicator_data) < total_needed:
        return False

    window = indicator_data.tail(total_needed)
    trend = window.iloc[:rejection_trend_window]
    spike = window.iloc[rejection_trend_window : rejection_trend_window+rejection_spike_window]
    confirm = window.iloc[rejection_trend_window+rejection_spike_window:]
    if direction == "bullish_rejection":
        trend_condtion = ((trend["Close"] < trend["VWAP"]) &
                           (trend["EMA21"] < trend["VWAP"]) &
                          (trend["EMA9"] < trend["VWAP"])
                            ).sum() >= rejection_trend_min
        spike_condtion = ((spike["Close"] > spike["VWAP"])
                            ).sum() >= rejection_spike_min
        confirm_condtion =((confirm["Close"] < confirm["VWAP"]) &
                           (confirm["EMA21"] < confirm["VWAP"]) &
                          (confirm["EMA9"] < confirm["VWAP"])
                            ).sum() >= rejection_confirmation_min
    else:
        trend_condtion = ((trend["Close"] > trend["VWAP"]) &
                           (trend["EMA21"] > trend["VWAP"]) &
                          (trend["EMA9"] > trend["VWAP"])
                            ).sum() >= rejection_trend_min
        spike_condtion = ((spike["Close"] < spike["VWAP"])
                            ).sum() >= rejection_spike_min
        confirm_condtion =((confirm["Close"] > confirm["VWAP"]) &
                           (confirm["EMA21"] > confirm["VWAP"]) &
                          (confirm["EMA9"] > confirm["VWAP"])
                            ).sum() >= rejection_confirmation_min
    return trend_condtion and spike_condtion and confirm_condtion

def bullish_sustained_exit_condition(indicator_data):
    window = indicator_data.tail(sustained_exit_window)
    condition = ((window["Close"] < window["VWAP"]) &
                 (window["EMA21"] < window["VWAP"]) &
                 (window["EMA9"] < window["VWAP"])
                )
    return len(window) == sustained_exit_window and condition.all()

def bearish_sustained_exit_condition(indicator_data):
    window = indicator_data.tail(sustained_exit_window)
    condition = ((window["Close"] > window["VWAP"]) &
                 (window["EMA21"] > window["VWAP"]) &
                 (window["EMA9"] > window["VWAP"])
                )
    return len(window) == sustained_exit_window and condition.all()

def bullish_rejection_exit_condition(indicator_data):
    window = indicator_data.tail(rejection_exit_window)
    condition = ((window["Close"] < window["VWAP"]) &
            (window["EMA21"] < window["VWAP"]) &
            (window["EMA9"] < window["EMA21"]) &
            (window["EMA21_Angle"] < 0) &
            (window["VWAP_Angle"] < 0)
            )
    return len(window) == sustained_exit_window and condition.all()

def bearish_rejection_exit_condition(indicator_data):
    window = indicator_data.tail(rejection_exit_window)
    condition = ((window["Close"] > window["VWAP"]) &
            (window["EMA21"] > window["VWAP"]) &
            (window["EMA9"] > window["EMA21"]) &
            (window["EMA21_Angle"] > 0) &
            (window["VWAP_Angle"] > 0)
            )
    return len(window) == sustained_exit_window and condition.all()

def is_abnormal_volume(indicator_data):
    if len(indicator_data) < volume_window + 1:
        return False

    volume_data = indicator_data["Volume"]
    average_volume = volume_data[-(volume_window + 1):-1].mean()
    if average_volume <= 0:
        return False
    return volume_data.iloc[-1] >= volume_multiplier*average_volume

def is_day_breakout(indicator_data, bullish=True):
    datetimes = pd.to_datetime(indicator_data["Datetime"])
    current_date = datetimes.iloc[-1].date()
    indicator_data_today = indicator_data[datetimes.dt.date == current_date]
    if len(indicator_data_today) < 15:
        return False
    previous_candle = indicator_data_today.iloc[-2]
    last_candle = indicator_data_today.iloc[-1]
    prior_candles = indicator_data_today.iloc[:-2]
    if prior_candles.empty:
        return False
    if bullish:
        if not (previous_candle["Close"] > previous_candle["Open"] and last_candle["Close"] > last_candle["Open"]):
            return False
        prior_extreme_per_candle = prior_candles[["Open", "Close"]].max(axis=1)
        prior_extreme_candle_index = prior_extreme_per_candle.idxmax()
        prior_extreme_close = prior_extreme_candle_index.loc[prior_extreme_candle_index, "Close"]
    else:
        if not (previous_candle["Close"] < previous_candle["Open"] and last_candle["Close"] < last_candle["Open"]):
            return False
        prior_extreme_per_candle = prior_candles[["Open", "Close"]].min(axis=1)
        prior_extreme_candle_index = prior_extreme_per_candle.idxmin()
        prior_extreme_close = indicator_data_today.loc[prior_extreme_candle_index, "Close"]

    prior_extreme_time = pd.to_datetime(indicator_data_today.loc[prior_extreme_candle_index, "Datetime"])

    if bullish:
        crossed = previous_candle["Close"] > prior_extreme_close and last_candle["Close"] > prior_extreme_close
    else:
        crossed = previous_candle["Close"] < prior_extreme_close and last_candle["Close"] < prior_extreme_close
        
    if not crossed:
        return False

    time_difference = (pd.to_datetime(previous_candle["Datetime"])- prior_extreme_time).total_seconds()/60
    return time_difference > breakout_time_difference_in_minutes

def is_day_high_breakout(indicator_data):
    return is_day_breakout(indicator_data, bullish=True)

def is_day_low_breakdown(indicator_data):
    return is_day_breakout(indicator_data, bullish=False)

def add_to_tracked_dict(tracked_dict, stock, condition_met, latest_candle):
    if condition_met:
        tracked_dict[stock] = {
            "Stock" : stock,
            "Confirmed_At": latest_candle["Datetime"],
            "Close": latest_candle["Close"],
            "EMA9": latest_candle["EMA9"],
            "EMA21": latest_candle["EMA21"],
            "VWAP": latest_candle["VWAP"]
        }

def update_tracked_dict(tracked_dict, stock, condition_met, exit_condition_met, latest_candle):
    if condition_met:
        if stock in tracked_dict:
            return
        tracked_dict[stock] = {
            "Stock" : stock,
            "Confirmed_At": latest_candle["Datetime"],
            "Close": latest_candle["Close"],
            "EMA9": latest_candle["EMA9"],
            "EMA21": latest_candle["EMA21"],
            "VWAP": latest_candle["VWAP"]
        }
    elif stock in tracked_dict and exit_condition_met:
        del tracked_dict[stock]

def render_table(title, tracked_dict):
    st.subheader(f"{title}")
    if not tracked_dict:
        st.info("No active entries")
        return
    table = pd.DataFrame(tracked_dict.values())
    table = table.sort_values("Confirmed_At", ascending=False).reset_index(drop=True)
    st.dataframe(table, use_container_width=True)

def crossover_tracker():
    st.subheader("PROJECT QUANT")
    st.title("📡 Crossover Tracker")
    st.caption("Tracks sustained crossovers and false-breakout rejections")

    for key in ["bullish_sustained", "bearish_sustained","bullish_rejection", "bearish_rejection", "volume_spike", "day_high_breakout", "day_low_breakdown"]:
        session_key = f"crossover_tracker_{key}"
        if session_key not in st.session_state:
            st.session_state[session_key] = {}
    st_autorefresh(interval=autorefresh_interval, key="crossover_tracker_refresh")

    if "stock_cache_data" not in st.session_state:
        st.session_state.stock_cache_data = download_initial_stock_data()
    st.session_state.stock_cache_data = refresh_stock_data(st.session_state.stock_cache_data)
    stock_cache_data = st.session_state.stock_cache_data

    for stock in stocks_list:
        if stock not in stock_cache_data:
            continue
        indicator_data = get_cached_indicator_data(stock, stock_cache_data)
        if indicator_data.empty:
            continue
        latest_candle = indicator_data.iloc[-1]
        update_tracked_dict(st.session_state.crossover_tracker_bullish_sustained, stock, is_sustained_crossover(indicator_data, "bullish"), bullish_sustained_exit_condition(indicator_data), latest_candle)
        update_tracked_dict(st.session_state.crossover_tracker_bearish_sustained, stock, is_sustained_crossover(indicator_data, "bearish"), bearish_sustained_exit_condition(indicator_data), latest_candle)
        update_tracked_dict(st.session_state.crossover_tracker_bullish_rejection, stock, is_rejection(indicator_data, "bullish_rejection"), bullish_rejection_exit_condition(indicator_data), latest_candle)
        update_tracked_dict(st.session_state.crossover_tracker_bearish_rejection, stock, is_rejection(indicator_data, "bearish_rejection"), bearish_rejection_exit_condition(indicator_data), latest_candle)
        add_to_tracked_dict(st.session_state.crossover_tracker_volume_spike, stock, is_abnormal_volume(indicator_data), latest_candle)
        add_to_tracked_dict(st.session_state.crossover_tracker_day_high_breakout, stock, is_day_high_breakout(indicator_data), latest_candle)
        add_to_tracked_dict(st.session_state.crossover_tracker_day_low_breakdown, stock, is_day_low_breakdown(indicator_data), latest_candle)

    render_table("Bullish Sustained Crossover", st.session_state.crossover_tracker_bullish_sustained)
    render_table("Bearish Sustained Crossover", st.session_state.crossover_tracker_bearish_sustained)
    render_table("Bullish Rejection", st.session_state.crossover_tracker_bullish_rejection)
    render_table("Bearish Rejection", st.session_state.crossover_tracker_bearish_rejection)
    render_table("Volume Spike", st.session_state.crossover_tracker_volume_spike)
    render_table("Day High Breakout", st.session_state.crossover_tracker_day_high_breakout)
    render_table("Day Low Breakdown", st.session_state.crossover_tracker_day_low_breakdown)






