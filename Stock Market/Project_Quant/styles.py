"""
Project Quant - Stock Universe.

Single source of truth for the dashboard's look and feel — fonts, metric card styling, and the shared Plotly theme. Every 
page calls `load_styles()` + `load_plotly_theme()  once at the top so the whole app stays visually consistent without 
repeating CSS across files.

Author: Sreram R
"""

import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

# -----------------------------------------------------------------------------------------------------------------------------------------------------
# Brand palette
# -----------------------------------------------------------------------------------------------------------------------------------------------------
# Kept as constants so every P&L colour decision (Python or CSS) traces back to one place.
# Note: the CSS block below hardcodes these same hex values since inline <style> strings can't reference Python variables —
# if you change a colour here, update the matching value in the CSS too.
# -----------------------------------------------------------------------------------------------------------------------------------------------------
COLOR_POSITIVE = "#16a34a"   # green  — gains / good outcomes
COLOR_NEGATIVE = "#dc2626"   # red    — losses / bad outcomes
COLOR_NEUTRAL  = "#1f2937"   # slate  — non-numeric / fallback text
COLOR_BORDER   = "#d1d5db"   # light grey — card & metric borders
COLOR_MUTED    = "#6b7280"   # grey   — secondary labels

FONT_FAMILY = "Poppins"

def load_styles() -> None:

    """
    Inject global CSS: layout spacing, font, metric-card, and widget styling. Call once per page, near the top, before any `st.metric`
    or layout calls.
    """

    st.markdown(
        f"""
        <style>
        /* Tighter top/left padding than Streamlit's default */
        .block-container {{
            padding-top: 3rem;
            padding-left: 1rem;
        }}

        /* Google Font */
        @import url('https://fonts.googleapis.com/css2?family={FONT_FAMILY}:wght@400;500;600;700&display=swap');

        /* Apply font app-wide */
        html, body, [class*="css"],
        h1, h2, h3, h4, h5, h6, p, label, div {{
            font-family: '{FONT_FAMILY}', sans-serif !important;
        }}

        /* Metric card container */
        div[data-testid="stMetric"] {{
            border: 2px solid {COLOR_BORDER};
            border-radius: 12px;
            padding: 30px 15px;
            background-color: white;
        }}

        /* Metric label — centered, bold */
        div[data-testid="stMetricLabel"] {{
            width: 100%;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        div[data-testid="stMetricLabel"] > div {{
            width: 100%;
            text-align: center !important;
            font-family: '{FONT_FAMILY}', sans-serif !important;
            font-size: 20px !important;
            font-weight: 700 !important;
        }}

        /* Metric value — centered, large */
        div[data-testid="stMetricValue"] {{
            width: 100%;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        div[data-testid="stMetricValue"] > div {{
            width: 100%;
            text-align: center !important;
            font-family: '{FONT_FAMILY}', sans-serif !important;
            font-size: 50px !important;
            font-weight: 700 !important;
        }}

        /* Selectbox text */
        div[data-baseweb="select"] * {{
            font-family: '{FONT_FAMILY}', sans-serif !important;
            font-weight: 600 !important;
        }}

        /* Sidebar text */
        section[data-testid="stSidebar"] * {{
            font-family: '{FONT_FAMILY}', sans-serif !important;
        }}

        /* Hide the default delta arrow — we colour-code values ourselves */
        div[data-testid="stMetricDelta"] {{
            display: none;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_plotly_theme() -> None:

    """
    Register and activate a shared Plotly template matching the app's palette.Call once at app startup. Every `go.Figure` / `px.*`
    chart created afterward will automatically use this template.
    """

    pio.templates["quant"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family=FONT_FAMILY, size=12, color=COLOR_NEUTRAL),
            paper_bgcolor="white",
            plot_bgcolor="white",
            colorway=[COLOR_POSITIVE, COLOR_NEGATIVE, "#2563eb", "#d97706"],
            xaxis=dict(showgrid=True, gridcolor="#f3f4f6", linecolor=COLOR_BORDER),
            yaxis=dict(showgrid=True, gridcolor="#f3f4f6", linecolor=COLOR_BORDER),
            margin=dict(t=40, b=40, l=40, r=20),
            hoverlabel=dict(bgcolor="white", font_size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
    )
    pio.templates.default = "quant"

def metric_card(label: str, value, positive_is_good: bool = True) -> None:

    """
    Render a custom HTML metric card with sign-aware colour coding. Used instead of `st.metric` when the delta arrow isn't wanted,
    or when the "good" direction is inverted (e.g. drawdown, where lower is better).

    Args:
        label: Card title shown above the value (e.g. "Net P&L").
        value: Value to display — numeric or pre-formatted string.
        positive_is_good: If False, flips the colour logic (useful for
            metrics like drawdown or risk exposure where a positive
            number is actually a bad outcome).
    """

    try:
        numeric_value = float(str(value).replace(",", ""))
        is_good = numeric_value >= 0 if positive_is_good else numeric_value < 0
        color = COLOR_POSITIVE if is_good else COLOR_NEGATIVE
    except (TypeError, ValueError):
        color = COLOR_NEUTRAL

    st.markdown(
        f"""
        <div style="border:2px solid {COLOR_BORDER}; border-radius:12px;
                    padding:20px 15px; text-align:center; background:white;
                    margin-bottom:1rem;">
            <div style="font-size:14px; font-weight:700;
                        color:{COLOR_MUTED}; margin-bottom:8px;">{label}</div>
            <div style="font-size:28px; font-weight:700; color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def color_pnl(val: float) -> str:

    """Pandas Styler helper — colours a numeric cell green/red by sign.

    Usage:
        df.style.map(color_pnl, subset=["P&L"])

    Args:
        val: Numeric cell value being styled.

    Returns:
        A CSS declaration string for pandas' Styler API.
    """

    color = COLOR_POSITIVE if val >= 0 else COLOR_NEGATIVE
    return f"color: {color}; font-weight: 600"
