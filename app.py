# ==============================
# IMPORTS + PATH FIX
# ==============================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.graph_objects as go

from backend.data_loader import load_data
from backend.preprocessing import preprocess_data
from backend.calculations import calculate_metrics
from backend.forecast import generate_forecast
from backend.risk import calculate_burn_risk
from backend.health_score import calculate_health_score

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="CashCast Dashboard", layout="wide")

st.title("💰 CashCast - Smart Cash Flow Dashboard")

# ==============================
# SESSION STATE
# ==============================
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# ==============================
# SIDEBAR NAVIGATION
# ==============================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Overview", "Forecast", "Cash Burn"])

# ==============================
# SIDEBAR INPUTS
# ==============================
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if st.sidebar.button("🚀 Use Demo Data"):
    st.session_state.use_demo = True

initial_capital = st.sidebar.number_input("Initial Capital", min_value=1.0, value=50000.0)

# ==============================
# SCENARIO SIMULATION
# ==============================
st.sidebar.subheader("Scenario Simulation")
expense_change = st.sidebar.slider("Change Expense (%)", -50, 50, 0)
income_change = st.sidebar.slider("Change Income (%)", -50, 50, 0)

# ==============================
# LOAD DATA
# ==============================
df = None

if uploaded_file or st.session_state.use_demo:
    try:
        if st.session_state.use_demo:
            data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.csv")
            df = load_data(data_path)
            st.success("Demo data loaded!")
        else:
            df = load_data(uploaded_file)

        # ==============================
        # BACKEND PIPELINE
        # ==============================
        df = preprocess_data(df)
        df = calculate_metrics(df, initial_capital)

        df, forecast_df, method = generate_forecast(df)

        risk = calculate_burn_risk(df, forecast_df)
        health = calculate_health_score(df, risk)

        score = health["financial_health_score"]
        label = health["health_label"]
        components = health["components"]

        # ==============================
        # DATA QUALITY INDICATOR
        # ==============================
        if len(df) < 5:
            st.warning("Low data reliability: Predictions may be unstable")

        # ==============================
        # SCENARIO SIMULATION CALCULATION
        # ==============================
        df_sim = df.copy()
        df_sim["expense"] *= (1 + expense_change / 100)
        df_sim["income_post_tax"] *= (1 + income_change / 100)

        df_sim = calculate_metrics(df_sim, initial_capital)
        df_sim, forecast_sim, _ = generate_forecast(df_sim)

        risk_sim = calculate_burn_risk(df_sim, forecast_sim)
        health_sim = calculate_health_score(df_sim, risk_sim)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()
else:
    st.warning("Upload a file or use demo data")
    st.stop()

# ==============================
# PAGE 1: DATA OVERVIEW
# ==============================
if page == "Data Overview":

    # --- Income vs Expense Graph ---
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df["date"], y=df["income_post_tax"],
        mode='lines', name='Income',
        line=dict(color='green', width=3)
    ))
    fig1.add_trace(go.Scatter(
        x=df["date"], y=df["expense"],
        mode='lines', name='Expense',
        line=dict(color='red', width=3)
    ))
    st.plotly_chart(fig1, use_container_width=True)

    # --- Summary Stats ---
    avg_income = df["income_post_tax"].mean()
    avg_expense = df["expense"].mean()
    net_trend = df["net_cash_flow"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Income", round(avg_income, 2))
    col2.metric("Avg Expense", round(avg_expense, 2))
    col3.metric("Net Cash Trend", round(net_trend, 2))

    # --- Health Score Gauge ---
    st.subheader("Financial Health Score")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': label},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 55], 'color': "orange"},
                {'range': [55, 75], 'color': "yellow"},
                {'range': [75, 90], 'color': "lightgreen"},
                {'range': [90, 100], 'color': "green"}
            ],
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

    # --- Health Breakdown ---
    st.subheader("Health Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stability", components["stability"])
    c2.metric("Expense", components["expense_ratio"])
    c3.metric("Efficiency", components["efficiency"])
    c4.metric("Burn", components["burn"])

# ==============================
# PAGE 2: FORECAST
# ==============================
elif page == "Forecast":

    # --- Fallback Message ---
    if method == "fallback_mean":
        st.warning("Using fallback prediction due to limited data")

    # --- Graph ---
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["date"],
        y=df["net_cash_flow"],
        mode='lines',
        name='Net Cash',
        line=dict(color='cyan', width=3)
    ))

    fig2.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["predicted_cash_flow"],
        mode='lines',
        name='Forecast',
        line=dict(color='orange', dash='dash', width=3)
    ))

    st.plotly_chart(fig2, use_container_width=True)

    # --- Table ---
    st.subheader("Forecast Data")
    st.dataframe(forecast_df)

# ==============================
# PAGE 3: CASH BURN
# ==============================
elif page == "Cash Burn":

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=df["date"],
        y=df["cumulative_cash"],
        mode='lines',
        name='Cumulative Cash',
        line=dict(color='yellow', width=4)
    ))

    fig3.add_hline(y=0, line_dash="dash", line_color="red")

    # --- Risk Timeline Marker ---
    if risk["zero_hit_week"]:
        burn_date = forecast_df["date"].iloc[risk["zero_hit_week"] - 1]
        fig3.add_vline(x=burn_date, line_dash="dot", line_color="red")

    st.plotly_chart(fig3, use_container_width=True)

    # --- Burn Status ---
    if risk["status"] == "Cash already burnt":
        st.error("Cash already burnt")
    else:
        if risk["risk_level"] == "Low":
            color = "green"
        elif risk["risk_level"] == "Medium":
            color = "orange"
        else:
            color = "red"

        st.markdown(
            f"### Burn Status: <span style='color:{color}'>{risk['risk_level']}</span>",
            unsafe_allow_html=True
        )

        if risk["zero_hit_week"]:
            st.warning(f"Cash will run out in week {risk['zero_hit_week']}")

    # --- Weeks Remaining ---
    if risk["cash_burn_weeks_remaining"] == float("inf"):
        st.metric("Weeks Remaining", "Not Determined")
    else:
        st.metric("Weeks Remaining", round(risk["cash_burn_weeks_remaining"], 2))

# ==============================
# SIDEBAR SIMULATION RESULT
# ==============================
st.sidebar.subheader("Simulation Result")
st.sidebar.metric("Simulated Score", health_sim["financial_health_score"])