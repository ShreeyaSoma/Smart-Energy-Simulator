# ⚡ Smart Energy Consumption Simulator

A **Streamlit-powered interactive simulator** to model and analyze daily household energy consumption.  
Built to help users **understand appliance usage patterns, forecast consumption, and receive actionable suggestions** to reduce energy bills — all within a simple, interactive dashboard.

---

### 🌍 Why This Project?

Most households receive an electricity bill **after usage**, leaving no room for proactive control.  
Traditional energy analysis tools often rely on **static displays from existing datasets**, showing what has already happened — not what could happen.  

This project goes a step further. It doesn’t just analyze past records; it **lets you actively create and simulate your own energy data** through real-time appliance toggles and dynamic predictions.  

With this interactive approach, you can:  
- 🔌 Identify your **top energy-consuming appliances**  
- 📊 Forecast **daily, weekly, and monthly consumption**  
- 💰 Compare **cost savings from usage adjustments**  
- 💡 Get **personalized suggestions** to stay within a daily limit  

> In other words, instead of being a passive observer, you become an **active decision-maker** in managing your household energy.

---

## 🚀 Key Functionalities

- **🔌 Appliance Control Panel**
  - Toggle appliances ON/OFF in real-time
  - Fridge is always ON (baseline load)
  
- **📊 Live Energy Metrics**
  - Daily consumption and cost
  - Alerts when daily limits are exceeded
  - Visual breakdown of appliance usage
  
- **📈 Trend Visualizations**
  - Daily and weekly consumption trend graphs
  - Appliance-wise usage comparison charts

- **💡 Intelligent Suggestions**
  - Find top appliances to cut down tomorrow
  - Explore savings by reducing AC usage
  - See fridge contribution to total usage

- **ℹ️ Transparent Calculation Metrics**
  - Rate: ₹6 per kWh
  - Assumed usage hours for appliances
  - Hybrid model approach with a pre-trained Random Forest

---

## ⚙️ Tech Behind the Scenes

- **Frontend**: [Streamlit](https://streamlit.io)  
- **Backend Logic**: Pre-trained Random Forest Model (`energy_model.pkl`)  
- **Visualization**: Plotly Express  
- **Dataset**: Synthetic household appliance energy consumption data  
- **Deployment**: Hugging Face Spaces (Dockerized with Streamlit entrypoint)

---

## 🏗️ Deployment Notes

The project was successfully deployed to **Hugging Face Spaces** with a few streamlined changes:

1. **Pre-trained Model**  
   - Instead of retraining, the app loads a `energy_model.pkl` file directly for instant predictions.

2. **Simplified File Structure**  
   - Kept all necessary files (`app.py`, `synthetic_energy_data.csv`, `energy_model.pkl`) inside the `src` folder for easy deployment.  
   - Removed training scripts not required in production (`train_and_prepare_model.py`).

3. **Dockerfile Update**  
   - Entrypoint set to launch the Streamlit app from the `src` directory.  
   - Exposed port `8501` for Hugging Face hosting.

4. **Session Handling**  
   - Used Streamlit session state to simulate day progression, weekly tracking, and history-based insights.

---

## 📌 How to Run Locally

```bash
git clone https://github.com/YourUsername/SmartEnergySimulator.git
cd SmartEnergySimulator
pip install -r requirements.txt
streamlit run src/streamlit_app.py
