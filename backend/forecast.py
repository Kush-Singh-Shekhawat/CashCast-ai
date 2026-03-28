import pandas as pd
from utils.constants import *

FORECAST_HORIZON = 8
WINDOW_SIZE = 3

def generate_forecast(df):
    df = df.copy()

    # Moving average
    df[MOVING_AVG] = df[NET_CASH_FLOW].rolling(window=WINDOW_SIZE).mean()

    valid_ma = df[MOVING_AVG].dropna()

    # --- Fallback ---
    if not valid_ma.empty:
        last_avg = valid_ma.iloc[-1]
        method = "moving_average"
    else:
        last_avg = df[NET_CASH_FLOW].mean()
        method = "fallback_mean"

    # --- Trend Detection ---
    trend = df[NET_CASH_FLOW].diff().mean()
    if pd.isna(trend):
        trend = 0

    last_date = df[DATE].iloc[-1]
    last_cash = df[CUMULATIVE_CASH].iloc[-1]

    forecast_rows = []

    for i in range(1, FORECAST_HORIZON + 1):
        next_date = last_date + pd.Timedelta(weeks=i)

        predicted_cash_flow = last_avg + trend
        last_cash += predicted_cash_flow

        forecast_rows.append({
            DATE: next_date,
            PREDICTED_CASH_FLOW: predicted_cash_flow,
            PREDICTED_CUMULATIVE: last_cash
        })

    forecast_df = pd.DataFrame(forecast_rows)

    return df, forecast_df, method