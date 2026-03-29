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
from backend.rule_based_insights import generate_insights

st.markdown("""
<style>


section.main > div {
    padding-top: 0rem !important;
}

/* Buttons */
.stButton>button {
    background-color: transparent;
    border: 2px solid #00CFFF;
    color: white;
    border-radius: 10px;
    padding: 8px 16px;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #00CFFF;
    color: black;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0e1117;
}

/* Cards feel */
.block-container {
    padding-top: 2rem;
}

/* Smooth fade */
.css-1d391kg {
    animation: fadeIn 0.6s ease-in;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
            
[data-testid="stNumberInput"] input {
    background-color: #111827;
    color: white;
    border-radius: 8px;
}            

/* MAIN PAGE BACKGROUND */
[data-testid="stAppViewContainer"] {
    background-color: #0b0f19;
}

/* IMPROVED SIDEBAR (contrast + border) */
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #00CFFF;
}

/* TEXT COLOR CONSISTENCY */
h1, h2, h3, h4, h5, h6, p, span {
    color: #e5e7eb;
}

/* METRIC CARDS (clean look) */
[data-testid="metric-container"] {
    background-color: #1f2937;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #374151;
}

/* HOVER EFFECT FOR METRICS */
[data-testid="metric-container"]:hover {
    border: 1px solid #00CFFF;
}

/* FIX GAUGE SHIFT (important) */
.js-plotly-plot {
    margin: auto;
}            
        
</style>
""", unsafe_allow_html=True)

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="CashCast Dashboard", layout="wide")

st.markdown("""
<div style="
    background-color:#111827;
    padding:20px 25px;
    border-bottom:1px solid #00CFFF;
    display:flex;
    justify-content:space-between;
    align-items:center;
">
    <div style="font-size:22px; font-weight:600; color:#00CFFF;">
        💰 CashCast
    </div>
    <div style="color:#9ca3af; font-size:14px;">
        AI Cash Flow Dashboard
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

# ==============================
# SIDEBAR NAVIGATION
# ==============================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Overview", "Forecast", "Cash Burn", "Simulation"])

# ==============================
# SIDEBAR INPUTS
# ==============================
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if st.sidebar.button("🚀 Use Demo Data"):
    st.session_state.use_demo = True

st.sidebar.markdown("""
<div style="
    background-color:#1f2937;
    padding:15px;
    border-radius:10px;
    border:1px solid #00CFFF;
    margin-bottom:10px;
">
    <h4 style="color:#00CFFF; margin-bottom:10px;">💰 Initial Capital</h4>
</div>
""", unsafe_allow_html=True)

initial_capital = st.sidebar.number_input(
    "Enter amount",
    min_value=1.0,
    value=50000.0,
    label_visibility="collapsed"
)

# ==============================
# LOAD DATA
# ==============================
df = None

if uploaded_file:
    st.session_state.use_demo = False

if uploaded_file or st.session_state.use_demo:
    try:
        if uploaded_file:
            df = load_data(uploaded_file)
            st.success("Uploaded file loaded!")
        else:
            data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.csv")
            df = load_data(data_path)
            st.success("Demo data loaded!")

        # ==============================
        # BACKEND PIPELINE
        # ==============================
        df = preprocess_data(df)
        df = calculate_metrics(df, initial_capital)

        df, forecast_df, method = generate_forecast(df)

        risk = calculate_burn_risk(df, forecast_df)
        health = calculate_health_score(df, risk)
        insights = generate_insights(df, forecast_df, risk, health)

        score = health["financial_health_score"]
        label = health["health_label"]
        components = health["components"]

        # ==============================
        # DATA QUALITY INDICATOR
        # ==============================
        if len(df) < 5:
            st.warning("Low data reliability: Predictions may be unstable")

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

    st.markdown("### ")

    # --- Income vs Expense Graph ---
    fig1 = go.Figure()
    fig1.update_layout(
        transition=dict(duration=800, easing='cubic-in-out')
    )
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
        number={'font': {'size': 32}},
        title={'text': label, 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00CFFF"},
            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 55], 'color': "orange"},
                {'range': [55, 75], 'color': "yellow"},
                {'range': [75, 90], 'color': "lightgreen"},
                {'range': [90, 100], 'color': "green"}
            ],
        }
    ))

    gauge.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=60, b=20),
    )

    with st.container():
        st.plotly_chart(gauge, use_container_width=False)

    # --- Health Breakdown ---
    st.subheader("Health Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stability", components["stability"])
    c2.metric("Expense", components["expense_ratio"])
    c3.metric("Efficiency", components["efficiency"])
    c4.metric("Burn", components["burn"])


    st.subheader("💡 Insights & Recommendations")

    for i in insights:
        st.write(i)

# ==============================
# PAGE 2: FORECAST
# ==============================
elif page == "Forecast":

    st.markdown("### ")

    # --- Fallback Message ---
    if method != "prophet":
        st.warning("Using fallback prediction due to limited data")

    # --- Graph ---
    fig2 = go.Figure()
    fig2.update_layout(
        transition=dict(duration=800, easing='cubic-in-out')
    )
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
        mode='lines+markers',
        name='AI Forecast',
        line=dict(color='orange', width=4)
    ))

    st.plotly_chart(fig2, use_container_width=True)

    # --- Table ---
    st.subheader("Forecast Data")
    st.dataframe(forecast_df)

    st.subheader("💡 Insights & Recommendations")

    for i in insights:
        st.write(i)

# ==============================
# PAGE 3: CASH BURN
# ==============================
elif page == "Cash Burn":

    st.markdown("### ")

    fig3 = go.Figure()
    fig3.update_layout(
        transition=dict(duration=800, easing='cubic-in-out')
    )
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

    st.subheader("💡 Insights & Recommendations")

    for i in insights:
        st.write(i)

# ==============================
# PAGE 3: SIMULATION GRAPHS
# ==============================

elif page == "Simulation":

    st.subheader("Adjust Scenario")

    col1, col2 = st.columns(2)
    with col1:
        expense_change = st.slider("Change Expense (%)", -50, 50, 0)
    with col2:
        income_change = st.slider("Change Income (%)", -50, 50, 0)

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

    st.markdown("### ")

    st.title("🧪 Scenario Simulation")

    fig_sim = go.Figure()
    fig_sim.update_layout(
        transition=dict(duration=800, easing='cubic-in-out')
    )

    fig_sim.add_trace(go.Scatter(
        x=df_sim["date"],
        y=df_sim["net_cash_flow"],
        mode='lines',
        name='Simulated Net Cash',
        line=dict(color='blue', width=3)
    ))

    fig_sim.add_trace(go.Scatter(
        x=forecast_sim["date"],
        y=forecast_sim["predicted_cash_flow"],
        mode='lines+markers',
        name='Simulated Forecast',
        line=dict(color='orange', width=4)
    ))

    st.plotly_chart(fig_sim, use_container_width=True)

    st.subheader("Simulated Health Score")
    st.metric("Simulated Score", health_sim["financial_health_score"])
