from utils.constants import *

def generate_insights(df, forecast_df, risk, health):
    insights = []

    avg_cf = df[NET_CASH_FLOW].mean()
    current_cash = df[CUMULATIVE_CASH].iloc[-1]

    # --- Cash Flow Insight ---
    if avg_cf > 0:
        insights.append("✅ Positive cash flow indicates healthy operations.")
    else:
        insights.append("⚠️ Negative cash flow detected. Expenses may be too high.")

    # --- Risk Insight ---
    if risk[RISK_LEVEL] == "High":
        insights.append("🚨 High burn risk: Cash may run out soon.")
    elif risk[RISK_LEVEL] == "Medium":
        insights.append("⚠️ Moderate burn risk: Monitor spending closely.")
    else:
        insights.append("✅ Low burn risk: Financial position is stable.")

    # --- Runway Insight ---
    if risk["cash_burn_weeks_remaining"] != float("inf"):
        insights.append(f"📉 Estimated runway: {round(risk['cash_burn_weeks_remaining'], 1)} weeks remaining.")

    # --- Forecast Trend Insight ---
    future_trend = forecast_df[PREDICTED_CASH_FLOW].mean()
    if future_trend > 0:
        insights.append("📈 Forecast shows improving cash flow trend.")
    else:
        insights.append("📉 Forecast indicates potential decline in cash flow.")

    # --- Health Score Insight ---
    score = health[HEALTH_SCORE]
    label = health["health_label"]

    insights.append(f"💡 Financial Health Score: {score} ({label})")

    # --- Simple Recommendation ---
    if avg_cf < 0:
        insights.append("👉 Consider reducing expenses or increasing revenue streams.")
    elif risk[RISK_LEVEL] != "Low":
        insights.append("👉 Stabilize cash flow to reduce future risk.")
    else:
        insights.append("👉 Maintain current strategy and monitor growth opportunities.")

    return insights