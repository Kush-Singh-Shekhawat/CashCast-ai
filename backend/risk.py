from utils.constants import (
    NET_CASH_FLOW,
    CUMULATIVE_CASH,
    BURN_RATE,
    BURN_WEEKS,
    RISK_LEVEL,
    PREDICTED_CUMULATIVE
)

def calculate_burn_risk(df, forecast_df):
    avg_cash_flow = df[NET_CASH_FLOW].mean()
    current_cash = df[CUMULATIVE_CASH].iloc[-1]

    burn_rate = 0
    burn_weeks = float('inf')
    risk_level = "Low"
    zero_hit_week = None

    # --- Burn calculation ---
    if avg_cash_flow < 0:
        burn_rate = abs(avg_cash_flow)
        burn_weeks = current_cash / burn_rate if burn_rate != 0 else float('inf')

    # --- Forecast zero detection ---
    for i, val in enumerate(forecast_df[PREDICTED_CUMULATIVE]):
        if val <= 0:
            zero_hit_week = i + 1
            break

    # --- Already burnt ---
    if current_cash <= 0:
        return {
            BURN_RATE: burn_rate,
            BURN_WEEKS: 0,
            RISK_LEVEL: "High",
            "zero_hit_week": 0,
            "status": "Cash already burnt"
        }

    # --- Risk classification ---
    if avg_cash_flow >= 0:
        risk_level = "Low"
    else:
        if zero_hit_week is not None:
            if zero_hit_week <= 4:
                risk_level = "High"
            elif zero_hit_week <= 8:
                risk_level = "Medium"
            else:
                risk_level = "Low"
        else:
            if burn_weeks < 4:
                risk_level = "High"
            elif burn_weeks < 8:
                risk_level = "Medium"
            else:
                risk_level = "Low"

    return {
        BURN_RATE: burn_rate,
        BURN_WEEKS: burn_weeks,
        RISK_LEVEL: risk_level,
        "zero_hit_week": zero_hit_week,
        "status": "Active"
    }