import numpy as np
from utils.constants import (
    INCOME_POST,
    EXPENSE,
    NET_CASH_FLOW,
    HEALTH_SCORE,
    RISK_LEVEL
)

def calculate_health_score(df, risk_dict):
    # --- Stability ---
    std_dev = np.std(df[NET_CASH_FLOW])
    mean_cf = np.mean(df[NET_CASH_FLOW])

    if mean_cf == 0:
        stability = 10
    else:
        ratio = std_dev / abs(mean_cf)
        stability = 30 if ratio < 0.5 else 20 if ratio < 1 else 10

    # --- Expense Ratio ---
    total_income = df[INCOME_POST].sum()
    total_expense = df[EXPENSE].sum()

    if total_income == 0:
        expense_score = 5
    else:
        r = total_expense / total_income
        expense_score = 25 if r < 0.5 else 18 if r < 0.75 else 10 if r < 1 else 5

    # --- Efficiency ---
    avg_cf = np.mean(df[NET_CASH_FLOW])
    efficiency = 20 if avg_cf > 0 else 10 if avg_cf > -0.1 * total_income else 5

    # --- Burn ---
    risk = risk_dict[RISK_LEVEL]
    burn = 25 if risk == "Low" else 15 if risk == "Medium" else 5

    score = stability + expense_score + efficiency + burn

    # Label
    if score >= 90:
        label = "Very Stable"
    elif score >= 75:
        label = "Stable"
    elif score >= 55:
        label = "Moderate"
    elif score >= 40:
        label = "Risky"
    else:
        label = "Critical"

    return {
        HEALTH_SCORE: round(score, 2),
        "health_label": label,
        "components": {
            "stability": stability,
            "expense_ratio": expense_score,
            "efficiency": efficiency,
            "burn": burn
        }
    }