"""
Project Quant - Main Application Entry Point.

Streamlit multi-page router. Wires the sidebar navigation to each dashboard module and loads the global styling / Plotly theme once,
so every page inherits a consistent look.

Author: Sreram
"""

import streamlit as st

from backtest_engine import backtest
from crossover_tracker import crossover_tracker
from live_stock_scanner import live_scanner
from options_backtest_engine import options_backtest
from paper_trading_terminal import paper_trading_terminal
from styles import load_plotly_theme, load_styles

def main() -> None:

    st.set_page_config(
        page_title="Project Quant",
        page_icon="💹",
        layout="wide",
    )
    load_plotly_theme()
    load_styles()

    pages = {
        "Live Stock Scanner": live_scanner,
        "Crossover Tracker": crossover_tracker,
        "Paper Trading Terminal": paper_trading_terminal,
        "Backtest Engine (Stocks)": backtest,
        "Backtest Engine (Stocks + Options)": options_backtest,
    }

    st.sidebar.title("Project Quant")
    selected_page = st.sidebar.radio(label="Navigation", options=list(pages.keys()))
    try:
        pages[selected_page]()
    except Exception as e:
        st.exception(e)

if __name__ == "__main__":
    main()