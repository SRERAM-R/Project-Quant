"""
Project Quant - Stock Universe.

Defines the tradable stock universe, grouped by sector. Screening, backtesting, and live order placement modules all
import from here.

Author: Sreram R
"""

stocks_list_with_sectors = {

    "BANKING": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK",
        "INDUSINDBK", "BANKBARODA", "PNB", "CANBK", "UNIONBANK",
        "IDFCFIRSTB", "FEDERALBNK", "AUBANK", "BANDHANBNK",
        "RBLBANK"
    ],

    "FINANCIAL SERVICES": [
        "BAJFINANCE", "BAJAJFINSV", "CHOLAFIN", "MUTHOOTFIN",
        "SHRIRAMFIN", "RECLTD", "PFC", "IRFC", "JIOFIN",
        "SBICARD", "LICHSGFIN"
    ],

    "INSURANCE": [
        "HDFCLIFE", "SBILIFE", "ICICIPRULI", "ICICIGI", "LICI"
    ],

    "INFORMATION TECHNOLOGY": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM",
        "LTM", "PERSISTENT", "COFORGE",
        "MPHASIS", "OFSS"
    ],

    "AUTO & AUTO ANCILLARIES": [
        "MARUTI", "M&M", "TMPV", "BAJAJ-AUTO",
        "HEROMOTOCO", "EICHERMOT", "TVSMOTOR",
        "ASHOKLEY", "BHARATFORG", "MOTHERSON",
        "BOSCHLTD"
    ],

    "PHARMA & HEALTHCARE": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB",
        "LUPIN", "AUROPHARMA", "TORNTPHARM",
        "ALKEM", "GLENMARK", "ZYDUSLIFE",
        "BIOCON", "APOLLOHOSP"
    ],

    "OIL, GAS & ENERGY": [
        "RELIANCE", "ONGC", "IOC", "BPCL",
        "HINDPETRO", "GAIL", "OIL",
        "PETRONET"
    ],

    "POWER & UTILITIES": [
        "NTPC", "POWERGRID", "TATAPOWER",
        "ADANIENSOL", "ADANIPOWER", "JSWENERGY",
        "NHPC",
    ],

    "METALS & MINING": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO",
        "SAIL", "JINDALSTEL", "VEDL",
        "NMDC", "NATIONALUM",
    ],

    "CEMENT & BUILDING MATERIALS": [
        "ULTRACEMCO", "AMBUJACEM",
        "SHREECEM", "DALBHARAT"
    ],

    "FMCG": [
        "HINDUNILVR", "ITC", "NESTLEIND",
        "BRITANNIA", "DABUR", "MARICO",
        "GODREJCP", "COLPAL", "TATACONSUM"
    ],

    "CAPITAL GOODS & INDUSTRIALS": [
        "ABB", "SIEMENS", "BHEL", "CUMMINSIND",
        "LT", "CGPOWER", "POLYCAB", "HAVELLS",
        "KEI", "APLAPOLLO"
    ],

    "CHEMICALS": [
        "PIDILITIND", "UPL", "SRF"
    ],

    "REAL ESTATE": [
        "DLF", "LODHA", "GODREJPROP",
        "OBEROIRLTY", "PRESTIGE"
    ],

    "CONSUMER & RETAIL": [
        "ASIANPAINT", "TITAN", "TRENT",
        "DMART", "PAGEIND", "VBL"
    ],

    "DEFENCE": [
        "HAL", "BEL", "BDL", "MAZDOCK",
        "COCHINSHIP"
    ],

    "TELECOM": [
        "BHARTIARTL", "IDEA"
    ],

    "INFRASTRUCTURE": [
        "ADANIPORTS", "IRB", "NBCC",
        "RVNL", "IRCON", "NCC"
    ],

    "EXCHANGES & MARKET INFRASTRUCTURE": [
        "BSE", "MCX", "CDSL"
    ],

    "NEW AGE & INTERNET": [
        "ETERNAL", "NAUKRI", "PAYTM",
        "POLICYBZR"
    ],

    "MISCELLANEOUS": [
        "COALINDIA"
    ]
}

stocks_list = [
    stock
    for sector_stocks in stocks_list_with_sectors.values()
    for stock in sector_stocks
]