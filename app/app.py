import sys
import os
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# ===============================
# PATH FIX
# ===============================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.train_and_prepare_model import (
    predict_next_day, predict_next_week, predict_next_month,
    calculate_cost, top_consuming_appliances,
    suggestion_reduce_top2, suggestion_ac_savings,
    suggestion_fridge_compare, suggestion_expensive_days,
    suggestion_monthly_projection, appliances_watts
)

# ===============================
# LOAD DATA & MODEL
# ===============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "synthetic_energy_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "energy_model.pkl")

df = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

# ===============================
# SESSION STATE INIT
# ===============================
if "appliance_state" not in st.session_state:
    st.session_state.appliance_state = {appl: False for appl in appliances_watts}
    st.session_state.appliance_state["Fridge"] = True  # fridge always ON
if "day_counter" not in st.session_state:
    st.session_state.day_counter = 1
if "history" not in st.session_state:
    st.session_state.history = []  # track daily results

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Smart Energy Simulator", layout="wide")

st.title("⚡ Smart Energy Consumption Dashboard")
st.caption("Individual Household Energy Simulation | Click 'Next Day' to simulate")

# ===============================
# SIDEBAR - Appliance Control
# ===============================
st.sidebar.header("🔌 Appliance Control")
st.sidebar.write("Toggle appliances ON/OFF for today's simulation.")

for appl in appliances_watts:
    if appl == "Fridge":
        st.sidebar.checkbox(appl, value=True, disabled=True)
    else:
        st.session_state.appliance_state[appl] = st.sidebar.checkbox(appl, value=False)

daily_limit = st.sidebar.number_input("Set Daily Limit (kWh)", value=15.0, min_value=5.0, step=0.5)

# ===============================
# SIMULATION LOGIC
# ===============================
# More realistic usage mapping
usage_mapping = {
    "Fan1": 4, "Fan2": 4,
    "Light1": 5, "Light2": 5,
    "AC": 6,
    "Fridge": 24,
    "WashingMachine": 1.5,
    "TV": 4
}

usage_hours = {}
for appl, state in st.session_state.appliance_state.items():
    if appl == "Fridge":
        usage_hours[appl] = 24
    else:
        usage_hours[appl] = usage_mapping[appl] if state else 0

today_df = pd.DataFrame([usage_hours])
today_kwh = predict_next_day(today_df)

# ===============================
# HYBRID PREDICTIONS
# ===============================
# Model-based
model_week_kwh = predict_next_week(today_df)
model_month_kwh = predict_next_month(today_df)

# History-based
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    avg_daily = hist_df["kWh"].mean()
    real_week_kwh = round(avg_daily * 7, 2)
    real_month_kwh = round(avg_daily * 30, 2)
else:
    real_week_kwh = model_week_kwh
    real_month_kwh = model_month_kwh

# ===============================
# DAY COUNTER DISPLAY (Week/Month)
# ===============================
day_num = st.session_state.day_counter
week_num = ((day_num - 1) // 7) + 1
day_in_week = ((day_num - 1) % 7) + 1
month_num = ((week_num - 1) // 4) + 1
st.markdown(f"### 📅 Simulation Day: Month {month_num}, Week {week_num}, Day {day_in_week}")

# ===============================
# BUTTON - NEXT DAY
# ===============================
if st.button("🌞 End Day & Go to Next"):
    st.session_state.history.append({
        "Day": st.session_state.day_counter,
        "Usage": usage_hours.copy(),
        "kWh": today_kwh,
        "Cost": calculate_cost(today_kwh)
    })
    st.success(f"✅ Day {day_num} recorded with {today_kwh} kWh")
    st.session_state.day_counter += 1

# ===============================
# METRIC CARDS
# ===============================
st.subheader("📊 Energy Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Today's Consumption", f"{today_kwh} kWh", f"₹{calculate_cost(today_kwh)}")
col2.metric("Weekly Projection",
            f"{model_week_kwh} kWh (Model)",
            f"{real_week_kwh} kWh (Your Trend)")
col3.metric("Monthly Projection",
            f"{model_month_kwh} kWh (Model)",
            f"{real_month_kwh} kWh (Your Trend)")

if today_kwh > daily_limit:
    st.error(f"⚠️ Daily limit exceeded! Limit: {daily_limit} kWh")
else:
    st.success("✅ You are within the daily limit.")

# ===============================
# TOP CONSUMING APPLIANCES
# ===============================
st.subheader("🔥 Top Consuming Appliances Today")
top2 = top_consuming_appliances(usage_hours, 2)
for app, cons in top2:
    st.write(f"- {app}: {round(cons,2)} kWh")

# ===============================
# USAGE GRAPH
# ===============================
st.subheader("📈 Appliance Usage Breakdown")
usage_data = pd.DataFrame({
    "Appliance": list(usage_hours.keys()),
    "kWh": [usage_hours[a]*appliances_watts[a]/1000 for a in usage_hours]
})
fig = px.bar(
    usage_data,
    x="Appliance", y="kWh", color="Appliance",
    title="Today's Usage", hover_data=["kWh"]
)
st.plotly_chart(fig, use_container_width=True)

# ===============================
# WEEKLY TREND
# ===============================
if st.session_state.history:
    st.subheader("📈 Weekly Trend (So Far)")
    hist_df = pd.DataFrame(st.session_state.history)
    fig_line = px.line(hist_df, x="Day", y="kWh", markers=True, title="Daily Consumption Trend")
    st.plotly_chart(fig_line, use_container_width=True)

# ===============================
# Q&A SUGGESTIONS
# ===============================
st.subheader("💡 Suggestions for You")

questions = [
    "Which 2 appliances should I reduce tomorrow?",
    "What if I reduce AC usage by 50%?",
    "How much does my fridge contribute?",
    "Which were the 2 most expensive days this week?",
    "What’s my monthly bill projection if I continue like today?"
]

selected_q = st.selectbox("Choose a question:", questions)

if selected_q == questions[0]:
    st.info(suggestion_reduce_top2(usage_hours))
elif selected_q == questions[1]:
    st.info(suggestion_ac_savings(usage_hours))
elif selected_q == questions[2]:
    st.info(suggestion_fridge_compare(usage_hours))
elif selected_q == questions[3]:
    st.info(suggestion_expensive_days(df))
elif selected_q == questions[4]:
    st.info(suggestion_monthly_projection(today_df))

# ===============================
# METRIC NOTES
# ===============================
st.subheader("ℹ️ Calculation Metrics")
st.markdown("""
- **Rate Used:** ₹6 per kWh  
- **Fridge:** Always ON (24 hours)  
- **Fans/Lights/TV:** 4–5 hours if ON  
- **AC:** 6 hours if ON  
- **Washing Machine:** 1.5 hours if ON  
- **Daily Limit:** User-defined, default 15 kWh  
- **Predictions:** Random Forest Model trained on synthetic 30-day dataset  
- **Hybrid Approach:**  
   - *Model Projection:* assumes today's pattern repeats  
   - *Your Trend:* based on average of your simulated days  
- **Simulation:** Click 'Next Day' → adds to weekly history  
""")
