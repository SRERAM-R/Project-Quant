"""
Project Quant - Download Options Data.

Fetches and saves historical intraday options data (nearest-expiry CE/PE contracts) per trading day, used by the Backtest
Engine (Stocks + Options) page for options-based backtesting.

Author: Sreram R
"""

import pandas as pd
import os
import time

from kiteconnect import KiteConnect
from pathlib import Path
from stocks_list import  stocks_list

api_key=""
access_token=""
kite=KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

current_date=pd.to_datetime("2026-06-01").date()
print("\n📥Downloading data for : ",current_date)

stock_options_data_folder_location= Path.home() / "Downloads" / "Stock Market" / "Historical Options Data"
os.makedirs(stock_options_data_folder_location,exist_ok=True)

instruments=pd.DataFrame(kite.instruments("NFO"))

merged_options_data=[]

print("\nTotal stocks : ",len(stocks_list),"\n")

start_time=time.time()

for stock in stocks_list:
    print(f"✅ Processing {stock}")
    options_contracts=instruments[(instruments["name"]==stock) & (instruments["instrument_type"].isin(["CE","PE"]))]
    if len(options_contracts)==0:
        print(f"❌ No contracts found for {stock}")
        continue
    nearest_expiry=sorted(options_contracts["expiry"].unique())[0]
    options_contracts=options_contracts[options_contracts["expiry"]==nearest_expiry]

    for _,row in options_contracts.iterrows():
        token=row["instrument_token"]
        symbol=row["tradingsymbol"]
        strike=row["strike"]
        option_type=row["instrument_type"]

        try:
            options_data=kite.historical_data(instrument_token=token,from_date=f"{current_date} 09:15:00",to_date=f"{current_date} 15:30:00",interval="minute")
            if len(options_data)==0:
                continue
            temporary_options_data=pd.DataFrame(options_data)
            temporary_options_data["Stock"]=stock
            temporary_options_data["Strike"] = strike
            temporary_options_data["Option Type"] = option_type
            temporary_options_data["Symbol"] = symbol
            temporary_options_data["Expiry"] = nearest_expiry

            merged_options_data.append(temporary_options_data)
            time.sleep(0.5)

        except Exception as e:
            print(e)

if len(merged_options_data)>0:
    final_merged_options_data=pd.concat(merged_options_data,ignore_index=True)
    file_path=os.path.join(stock_options_data_folder_location,f"{current_date}.parquet")
    final_merged_options_data.to_parquet(file_path,index=False)
    print(f"\n{current_date} - Saved {len(final_merged_options_data)} rows.")

print("\n🎉 Download complete.")

end_time=time.time()

print("Time taken : ",round((end_time-start_time)/60,1)," minutes.")

