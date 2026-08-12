"""
Project Quant - Backtest Engine (Stocks).

Backtests the selected strategy against historical stock data - runs the strategy over a selected stock's price
history and renders full performance analytics (P&L, win rate, Sharpe/Sortino, drawdown, equity curve, win/loss streaks, and
monthly/hourly breakdowns), with the complete trade log exportable to Excel.

Author: Sreram R
"""

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

from datetime import date
from stocks_list import stocks_list, stocks_list_with_sectors
from strategy import backtest_analysis, get_stock_data, list_of_strategies, run_strategy
from styles import color_pnl, metric_card

# ============================================================================================================================================
# FUNCTIONS
# ============================================================================================================================================

def backtest():
    st.subheader("PROJECT QUANT")
    st.title("🔍 Backtest Engine (Stock)")

    sector = st.selectbox(
        label="Sector", options=["ALL SECTORS"] + list(stocks_list_with_sectors.keys())
    )
    if sector == "ALL SECTORS":
        filtered_stocks_list = sorted(stocks_list)
    else:
        filtered_stocks_list = sorted(stocks_list_with_sectors[sector])
    stock = st.selectbox(label="Stock", options=filtered_stocks_list)
    strategy = st.selectbox(label="Strategy", options=list(list_of_strategies.keys()))
    date_range = st.date_input(
        label="Date Range",
        value=(date(2021, 1, 1), date(2026, 7, 31)),
        min_value=date(2021, 1, 1),
        max_value=date(2026, 7, 31),
    )
    if len(date_range) != 2:
        st.info("Select Start Date and End Date.")
        st.stop()
    start_date, end_date = date_range
    if start_date > end_date:
        st.info("End Date must be after Start Date.")
        st.stop()

    if "backtest_result" not in st.session_state:
        st.session_state.backtest_result = None

    run_backtest = st.button("▶ Run Backtest")
    if run_backtest:
        with st.spinner(f"Running backtest on {stock}"):
            stock_data = get_stock_data(stock)
            stock_data_with_required_indicators = run_strategy(stock, stock_data, start_date, end_date)
            trade_log = list_of_strategies[strategy](stock, stock_data_with_required_indicators)
            st.session_state.backtest_result = backtest_analysis(trade_log, "NA")
            st.session_state.backtest_stock = stock
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date

    if st.session_state.backtest_result is not None:
        st.info(f"Showing results for: **{st.session_state.backtest_stock}**")
    if st.session_state.backtest_result is None:
        st.info("Select a stock and click Run Backtest")
        st.stop()

    backtest_data = st.session_state.backtest_result
    net_profit_or_loss = backtest_data["Net Profit/Loss"]
    number_of_trades = backtest_data["Number Of Trades"]
    number_of_winning_trades = backtest_data["Number Of Winning Trades"]
    number_of_losing_trades = backtest_data["Number Of Losing Trades"]
    average_winning_trade = backtest_data["Average Winning Trade"]
    average_losing_trade = backtest_data["Average Losing Trade"]
    win_rate = number_of_winning_trades * 100.0 / number_of_trades if number_of_trades != 0 else 0
    expectancy = (win_rate * average_winning_trade - (100 - win_rate) * abs(average_losing_trade)) / 100.0
    gross_profit = backtest_data["Gross Profit"]
    gross_loss = backtest_data["Gross Loss"]
    max_profit = backtest_data["Maximum Profit"]
    max_loss = backtest_data["Maximum Loss"]
    average_holding_minutes = backtest_data["Average Holding Minutes"]
    profit_factor = gross_profit * 1.0 / abs(gross_loss) if gross_loss != 0 else "∞"
    risk_reward_ratio = (average_winning_trade * 1.0 / abs(average_losing_trade) if average_losing_trade != 0 else "∞")
    profit_factor_display = (round(profit_factor, 2) if isinstance(profit_factor, (int, float)) else profit_factor)
    risk_reward_ratio_display = (round(risk_reward_ratio, 2) if isinstance(risk_reward_ratio, (int, float)) else risk_reward_ratio)

    trade_log = backtest_data["Trade Log"].copy()

    if len(trade_log) == 0:
        st.info("Trade log is empty!")
        return

    trade_log["Exit Date"] = pd.to_datetime(trade_log["Exit Time"]).dt.date
    daily_pnl = trade_log.groupby("Exit Date")["Net Profit/Loss"].sum()
    equity_curve = trade_log["Net Profit/Loss"].cumsum()
    running_peak = equity_curve.cummax()
    drawdown = equity_curve - running_peak
    max_drawdown = drawdown.min()
    initial_capital = 25000
    days = (trade_log["Exit Time"].max() - trade_log["Entry Time"].min()).total_seconds() / 86400.0
    total_return = (initial_capital + equity_curve.iloc[-1]) / initial_capital
    cagr = (total_return ** (365.0 / days) - 1) * 100 if total_return > 0 and days != 0 else 0
    sharpe = ((daily_pnl.mean() / daily_pnl.std()) * np.sqrt(252) if not pd.isna(daily_pnl.std()) and daily_pnl.std() != 0 else 0)
    downside = daily_pnl[daily_pnl < 0]
    sortino = ((daily_pnl.mean() / downside.std()) * np.sqrt(252) if not pd.isna(downside.std()) and downside.std() != 0 else 0)
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    st.subheader("Backtest Results")
    (net_profit_or_loss_widget, number_of_trades_widget, win_rate_widget, expectancy_widget) = st.columns(4)
    with net_profit_or_loss_widget:
        metric_card(label="Net Profit/Loss", value=round(net_profit_or_loss, 2))
    with number_of_trades_widget:
        metric_card(label="Number Of Trades", value=number_of_trades)
    with win_rate_widget:
        metric_card(label="Win Rate", value=round(win_rate, 2))
    with expectancy_widget:
        metric_card(label="Expectancy", value=round(expectancy, 2))

    (profit_factor_widget, risk_reward_ratio_widget, average_winning_trade_widget, average_losing_trade_widget) = st.columns(4)
    with profit_factor_widget:
        metric_card(label="Profit Factor", value=profit_factor_display)
    with risk_reward_ratio_widget:
        metric_card(label="Risk/Reward", value=risk_reward_ratio_display)
    with average_winning_trade_widget:
        metric_card(label="Average Winning Trade", value=round(average_winning_trade, 2))
    with average_losing_trade_widget:
        metric_card(label="Average Losing Trade", value=round(average_losing_trade, 2))

    cagr_widget, sharpe_ratio_widget, sortino_widget, calmar_widget = st.columns(4)
    with cagr_widget:
        metric_card(label="CAGR %", value=round(cagr, 2))
    with sharpe_ratio_widget:
        metric_card(label="Sharpe Ratio", value=round(sharpe, 2))
    with sortino_widget:
        metric_card(label="Sortino", value=round(sortino, 2))
    with calmar_widget:
        metric_card(label="Calmar", value=round(calmar, 2))

    (max_drawdown_widget, max_winning_trade_widget, max_losing_trade_widget, average_holding_time_widget) = st.columns(4)
    with max_drawdown_widget:
        metric_card(label="Max Drawdown", value=round(max_drawdown, 2))
    with max_winning_trade_widget:
        metric_card(label="Maximum Winning Trade", value=round(max_profit, 2))
    with max_losing_trade_widget:
        metric_card(label="Maximum Losing Trade", value=round(max_loss, 2))
    with average_holding_time_widget:
        metric_card(label="Average Holding Time", value=round(average_holding_minutes, 2))

    (winning_trades_widget, losing_trades_widget, gross_profit_widget, gross_loss_widget) = st.columns(4)
    with winning_trades_widget:
        metric_card(label="Winning Trades", value=number_of_winning_trades)
    with losing_trades_widget:
        metric_card(label="Losing Trades", value=number_of_losing_trades, positive_is_good=False)
    with gross_profit_widget:
        metric_card(label="Gross Profit", value=round(gross_profit, 2))
    with gross_loss_widget:
        metric_card(label="Gross Loss", value=round(gross_loss, 2))

    st.write("### Monthly Statistics")
    trade_log_month_statistics = backtest_data["Trade Log Monthly Statistics"]
    st.dataframe(trade_log_month_statistics)

    st.write("### Day Statistics")
    trade_log_day_statistics = backtest_data["Trade Log Day Statistics"]
    st.dataframe(trade_log_day_statistics)

    st.write("### Hourly Statistics")
    trade_log_hourly_statistics = backtest_data["Trade Log Hourly Statistics"]
    st.dataframe(trade_log_hourly_statistics)

    st.write("### Equity Curve")
    equity_curve_values = np.concatenate([[0], equity_curve.values])
    fig_equity = go.Figure()
    fig_equity.add_trace(
        go.Scatter(
            x=list(range(0, len(equity_curve) + 1)),
            y=equity_curve_values,
            fill="tozeroy",
            fillcolor="rgba(22,163,74,0.10)",
            line=dict(color="black", width=1.5),
            name="Equity",
        )
    )
    fig_equity.update_layout(xaxis_title="Number of Trades", yaxis_title="Cumulative P&L")
    st.plotly_chart(fig_equity, use_container_width=True)

    st.write("### Drawdown Curve")
    fig_drawdown = go.Figure()
    fig_drawdown.add_trace(
        go.Scatter(
            x=list(range(1, len(drawdown) + 1)),
            y=drawdown.values,
            fill="tozeroy",
            fillcolor="rgba(220,38,38,0.15)",
            line=dict(color="#dc2626", width=1.5),
            name="Drawdown",
        )
    )
    fig_drawdown.update_layout(xaxis_title="Number of Trades", yaxis_title="Drawdown")
    st.plotly_chart(fig_drawdown, use_container_width=True)

    st.write("### Trade Histogram")
    fig_histogram = px.histogram(
        trade_log,
        x="Net Profit/Loss",
        nbins=10,
        color="Result",
        color_discrete_map={"Win": "#16a34a", "Loss": "#dc2626"},
        barmode="overlay",
        opacity=0.85,
        labels={"Net Profit/Loss": "Profit/Loss Per Trade", "count": "Number Of Trades"},
    )
    fig_histogram.add_vline(x=0, line_dash="dash", line_color="black", line_width=1.5)
    fig_histogram.add_vline(
        x=trade_log["Net Profit/Loss"].mean(),
        line_dash="dot",
        line_color="gray",
        annotation_text=f"Mean: {trade_log['Net Profit/Loss'].mean():.2f}",
        annotation_position="top right",
    )
    st.plotly_chart(fig_histogram, use_container_width=True)

    st.write("### Monthly Returns Heatmap")
    heatmap_pivot = backtest_data["Heatmap Pivot"]
    fig_heatmap = px.imshow(
        heatmap_pivot,
        color_continuous_scale=["#dc2626", "white", "#16a34a"],
        color_continuous_midpoint=0,
        text_auto=".1f",
        aspect="auto",
    )
    fig_heatmap.update_layout(
        xaxis_title="Month",
        yaxis_title="Year",
        coloraxis_showscale=False,
        yaxis=dict(
            tickmode="array",
            tickvals=list(heatmap_pivot.index),
            ticktext=[str(year) for year in heatmap_pivot.index],
        ),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.write("### Win/Loss Streaks")
    results = trade_log["Net Profit/Loss"].apply(lambda x: 1 if x > 0 else -1).tolist()
    streaks = []
    current = results[0]
    count = 1
    for result in results[1:]:
        if result == current:
            count += 1
        else:
            streaks.append(current * count)
            current, count = result, 1
    streaks.append(current * count)
    colors = ["green" if streak > 0 else "red" for streak in streaks]

    fig_streak = px.bar(x=list(range(1, len(streaks) + 1)), y=streaks)
    fig_streak.update_traces(marker_color=colors)
    fig_streak.update_layout(xaxis_title="Number of Trades", yaxis_title="Profit/Loss", showlegend=False)
    st.plotly_chart(fig_streak, use_container_width=True)

    max_win_streaks = max([streak for streak in streaks if streak > 0], default=0)
    max_loss_streaks = abs(min([streak for streak in streaks if streak < 0], default=0))
    max_consecutive_wins_widget, max_consecutive_losses_widget = st.columns(2)
    with max_consecutive_wins_widget:
        metric_card(label="Maximum Consecutive Wins", value=max_win_streaks)
    with max_consecutive_losses_widget:
        metric_card(label="Maximum Consecutive Losses", value=max_loss_streaks, positive_is_good=False)

    st.write("### Rolling Win Rate(20-Trade Window)")
    trade_log["Win"] = (trade_log["Net Profit/Loss"] > 0).astype(int)
    trade_log["Rolling Win Rate %"] = trade_log["Win"].rolling(20, min_periods=1).mean() * 100
    fig_rwr = go.Figure()
    fig_rwr.add_trace(go.Scatter(
        x=list(range(1, len(trade_log) + 1)),
        y=trade_log["Rolling Win Rate %"].values,
        line=dict(color="black", width=1.5)
    ))
    fig_rwr.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="50%")
    fig_rwr.add_hline(y=win_rate, line_dash="dash", line_color="lightgray", annotation_text=f"Average {win_rate:.1f}%")
    fig_rwr.update_layout(xaxis_title="Number of Trades", yaxis_title="Win Rate %")
    st.plotly_chart(fig_rwr, use_container_width=True)

    st.write("### Holding Time vs P&L")
    fig_holding_time = px.scatter(
        trade_log,
        x="Holding Minutes",
        y="Net Profit/Loss",
        color="Result",
        color_discrete_map={"Win": "green", "Loss": "red"},
        trendline="ols",
        trendline_scope="overall",
        labels={"Holding Minutes": "Hold Duration (in minutes)", "Net Profit/Loss": "P&L"},
    )
    fig_holding_time.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_holding_time, use_container_width=True)

    st.write("### Trade Log")
    styled_log = trade_log.style.map(color_pnl, subset=["Net Profit/Loss"]).format({"Net Profit/Loss": "{:.2f}"})
    st.dataframe(styled_log, use_container_width=True, hide_index=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        trade_log.to_excel(writer, sheet_name="Trade Log", index=False)
        trade_log_month_statistics.to_excel(writer, sheet_name="Monthly Statistics", index=False)
        trade_log_day_statistics.to_excel(writer, sheet_name="Day Statistics", index=False)
        trade_log_hourly_statistics.to_excel(writer, sheet_name="Hourly Statistics", index=False)

    st.write("### Download Data")
    st.download_button(
        label="⬇ Export Full Report",
        data=buffer.getvalue(),
        file_name=f"{stock} Backtest Data.xlsx",
    )







