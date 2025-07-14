import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils import load_model, forecast_emissions

st.title("🗓️ Year-by-Year Action Planning")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
# Robust initialization for action_plan
if "action_plan" not in st.session_state or not isinstance(st.session_state["action_plan"], dict):
    st.session_state["action_plan"] = {}
action_plan = st.session_state["action_plan"]
original_forecast = st.session_state.get("forecast_df")

if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page before using action planning.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page before using action planning.")
    st.stop()
# Only stop if action_plan is not a dict (allow empty dict)
if not isinstance(action_plan, dict):
    st.warning("Action plan is missing or invalid. Please initialize action plan.")
    st.stop()

st.write(f"Action planning for **{company_info['name']}**")
df = pd.DataFrame(emission_sources)

years = st.slider("Plan for how many years?", min_value=1, max_value=30, value=10)

# --- Action Planning Table ---
st.write("### Specify Planned Reductions (%) for Each Source and Year")
reduction_plan = {}
for idx, row in df.iterrows():
    source = row['type']
    reduction_plan[source] = []
    for year in range(years):
        col = st.number_input(f"{source} - Year {year+1} reduction (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"{source}_{year}")
        reduction_plan[source].append(col)

# --- Calculate Action Plan Emissions ---
base_emissions = {row['type']: row['emission'] for _, row in df.iterrows()}
action_emissions = []
for year in range(years):
    total = 0
    for source in base_emissions:
        reduction = reduction_plan[source][year]
        reduced = base_emissions[source] * (1 - reduction/100)
        total += reduced
    action_emissions.append(total)

# --- Forecast with Action Plan ---
model = load_model()
action_forecast = forecast_emissions(model, action_emissions[0], years)
action_forecast['Emission'] = action_emissions  # override with planned values

# --- Plot Comparison ---
st.write("### Forecast Comparison: Baseline vs. Action Plan")
fig, ax = plt.subplots()
if original_forecast is not None and len(original_forecast) >= years:
    ax.plot(original_forecast['Year'][:years], original_forecast['Emission'][:years], label='Baseline', marker='o')
ax.plot(action_forecast['Year'], action_forecast['Emission'], label='Action Plan', marker='o')
ax.set_xlabel("Year")
ax.set_ylabel("CO₂ Emissions (tons)")
ax.set_title(f"Emission Forecast Comparison for {company_info['name']}")
ax.legend()
st.pyplot(fig, use_container_width=True)

st.write("### Action Plan Data")
st.dataframe(action_forecast, use_container_width=True) 