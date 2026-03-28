# 💰 CashCast AI

AI-powered cash flow forecasting and financial health dashboard for small businesses.

## 🚀 Features
- Weekly cash flow analysis from CSV
- 8-week trend-based forecasting
- Cash burn risk detection
- Financial health score (with breakdown)
- Scenario simulation (income/expense changes)
- Data reliability indicator

## 🧠 Tech Stack
- Python
- Pandas, NumPy
- Streamlit
- Plotly

## 📂 Project Structure
backend/
utils/
data/
app.py

## ⚙️ How to Run
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

## 📊 Input Format (CSV)
Required columns:
- date
- income_pre_tax
- income_post_tax
- expense

## 🎯 Use Case
Helps small businesses:
- Predict cash shortages
- Understand financial health
- Make better decisions quickly

## 🏁 Hackathon Goal
Focus on clarity, usability, and decision-making over complexity.