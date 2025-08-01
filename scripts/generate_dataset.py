import pandas as pd
import random
import os

# Get current script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure data folder exists
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Appliance wattages
appliances = {
    "Fan1": 70, "Fan2": 70,
    "Light1": 20, "Light2": 20,
    "AC": 1500, "Fridge": 150,
    "WashingMachine": 500, "TV": 120
}

def random_hours(appliance):
    if appliance == "Fan1": return random.randint(4, 8)
    if appliance == "Fan2": return random.randint(2, 6)
    if appliance == "Light1": return random.randint(4, 7)
    if appliance == "Light2": return random.randint(3, 6)
    if appliance == "AC": return random.choice([0,1,2,3,4,5,6])
    if appliance == "Fridge": return 24
    if appliance == "WashingMachine": return random.choice([0,0,0,1])
    if appliance == "TV": return random.randint(1, 5)
    return 0

rows = []
for day in range(1, 31):
    usage = {appl: random_hours(appl) for appl in appliances}
    total_kwh = sum(usage[a] * appliances[a] for a in appliances) / 1000
    usage["Day"] = day
    usage["Total_kWh"] = round(total_kwh, 2)
    rows.append(usage)

df = pd.DataFrame(rows)
df = df[["Day"] + list(appliances.keys()) + ["Total_kWh"]]

# Save dataset reliably
save_path = os.path.join(DATA_DIR, "synthetic_energy_data.csv")
df.to_csv(save_path, index=False)

print(f"✅ Synthetic dataset saved at {save_path}")
print(df.head())
