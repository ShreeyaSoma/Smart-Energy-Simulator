import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ===============================
# CONFIGURATION
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "synthetic_energy_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "energy_model.pkl")

RATE_PER_KWH = 6  # cost per unit

# Appliance wattages (W)
appliances_watts = {
    "Fan1": 70, "Fan2": 70,
    "Light1": 20, "Light2": 20,
    "AC": 1500, "Fridge": 150,
    "WashingMachine": 500, "TV": 120
}

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=["Day", "Total_kWh"])
y = df["Total_kWh"]

# ===============================
# TRAIN MODEL
# ===============================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"✅ Model trained | R² Score: {round(score,3)}")

joblib.dump(model, MODEL_PATH)
print(f"✅ Model saved at {MODEL_PATH}")

# ===============================
# PREDICTION UTILITIES
# ===============================
def predict_next_day(latest_data: pd.DataFrame) -> float:
    pred = model.predict(latest_data)
    return round(pred[0], 2)

def predict_next_week(latest_data: pd.DataFrame) -> float:
    return round(predict_next_day(latest_data) * 7, 2)

def predict_next_month(latest_data: pd.DataFrame) -> float:
    return round(predict_next_week(latest_data) * 4, 2)

def calculate_cost(kwh: float) -> float:
    return round(kwh * RATE_PER_KWH, 2)

def top_consuming_appliances(latest_usage: dict, top_n=2):
    consumption = {a: latest_usage[a]*appliances_watts[a]/1000 for a in appliances_watts}
    sorted_appl = sorted(consumption.items(), key=lambda x: x[1], reverse=True)
    return sorted_appl[:top_n]

# ===============================
# Q&A SUGGESTIONS ENGINE
# ===============================
def suggestion_reduce_top2(latest_usage: dict):
    top2 = top_consuming_appliances(latest_usage, top_n=2)
    return f"Consider reducing {top2[0][0]} and {top2[1][0]} usage tomorrow. They consumed {round(top2[0][1]+top2[1][1],2)} kWh today."

def suggestion_ac_savings(latest_usage: dict):
    ac_hours = latest_usage["AC"]
    ac_saving = (ac_hours * 0.5 * appliances_watts["AC"]) / 1000
    weekly_saving = round(ac_saving * 7, 2)
    return f"Reducing AC by 50% could save ~{weekly_saving} kWh (~₹{calculate_cost(weekly_saving)}) per week."

def suggestion_fridge_compare(latest_usage: dict):
    fridge_kwh = (latest_usage["Fridge"] * appliances_watts["Fridge"]) / 1000
    other_kwh = sum(latest_usage[a]*appliances_watts[a]/1000 for a in appliances_watts if a!="Fridge")
    percent = round((fridge_kwh/(fridge_kwh+other_kwh))*100, 1)
    return f"Your fridge alone used {percent}% of total consumption today."

def suggestion_expensive_days(df):
    week_data = df.tail(7)
    top2_days = week_data.sort_values(by="Total_kWh", ascending=False).head(2)
    days = list(top2_days["Day"])
    return f"Your most expensive days this week were Day {days[0]} and Day {days[1]}."

def suggestion_monthly_projection(latest_data: pd.DataFrame):
    month_kwh = predict_next_month(latest_data)
    return f"If you continue with today’s pattern, expect a monthly bill of ₹{calculate_cost(month_kwh)}."

# ===============================
# TEST RUN
# ===============================
if __name__ == "__main__":
    latest_day = df.tail(1).drop(columns=["Day", "Total_kWh"])
    latest_usage_dict = latest_day.to_dict(orient="records")[0]

    print("\n🔹 Latest Usage (Hours):")
    print(latest_usage_dict)

    # Predictions
    tomorrow = predict_next_day(latest_day)
    week = predict_next_week(latest_day)
    month = predict_next_month(latest_day)

    print(f"\n🔮 Tomorrow: {tomorrow} kWh (₹{calculate_cost(tomorrow)})")
    print(f"📅 Week: {week} kWh (₹{calculate_cost(week)})")
    print(f"🗓️ Month: {month} kWh (₹{calculate_cost(month)})")

    # Top appliances
    print("\n🔥 Top 2 Appliances Today:")
    for app, cons in top_consuming_appliances(latest_usage_dict, 2):
        print(f"- {app}: {round(cons,2)} kWh")

    # Suggestions
    print("\n💡 Suggestions:")
    print("1.", suggestion_reduce_top2(latest_usage_dict))
    print("2.", suggestion_ac_savings(latest_usage_dict))
    print("3.", suggestion_fridge_compare(latest_usage_dict))
    print("4.", suggestion_expensive_days(df))
    print("5.", suggestion_monthly_projection(latest_day))
