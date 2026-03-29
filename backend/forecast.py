from prophet import Prophet
import pandas as pd
from utils.constants import *

FORECAST_HORIZON = 8

def generate_forecast(df):
    df = df.copy()

    prophet_df = df[[DATE, NET_CASH_FLOW]].rename(columns={
        DATE: "ds",
        NET_CASH_FLOW: "y"
    })

    model = Prophet()
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=FORECAST_HORIZON, freq='W')
    forecast = model.predict(future)

    forecast = forecast.tail(FORECAST_HORIZON)

    last_cash = df[CUMULATIVE_CASH].iloc[-1]
    rows = []

    for i, row in forecast.iterrows():
        pred = row["yhat"]
        last_cash += pred

        rows.append({
            DATE: row["ds"],
            PREDICTED_CASH_FLOW: pred,
            PREDICTED_CUMULATIVE: last_cash
        })

    return df, pd.DataFrame(rows), "prophet"