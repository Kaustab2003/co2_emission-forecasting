import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils import load_model, forecast_emissions

st.title("🔄 Scenario Simulation")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
# Robust initialization for scenario_data
if "scenario_data" not in st.session_state or not isinstance(st.session_state["scenario_data"], dict):
    st.session_state["scenario_data"] = {"original_forecast": None}
scenario_data = st.session_state["scenario_data"]
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page before using scenario simulation.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page before using scenario simulation.")
    st.stop()
if not scenario_data or not isinstance(scenario_data, dict):
    st.warning("Scenario data is missing or invalid. Please initialize scenario data.")
    st.stop()

st.write(f"Scenario simulation for **{company_info['name']}**")
df = pd.DataFrame(emission_sources)

st.write("### Adjust Emission Sources")
adjusted_emissions = []
for idx, row in df.iterrows():
    new_value = st.slider(
        f"{row['type']} (current: {row['emission']} tons CO₂e)",
        min_value=0.0,
        max_value=float(row['emission']),
        value=float(row['emission']),
        step=0.01
    )
    adjusted_emissions.append(new_value)

df["adjusted_emission"] = adjusted_emissions
new_total_emissions = df["adjusted_emission"].sum()
st.write(f"**New total annual emissions:** {new_total_emissions} tons CO₂e")

years = st.slider("Forecast for next N years:", min_value=1, max_value=30, value=20)

if st.button("Simulate Scenario"):
    model = load_model()
    scenario_forecast = forecast_emissions(model, new_total_emissions, years)
    st.write("### Scenario Forecast Data")
    st.dataframe(scenario_forecast, use_container_width=True)

    st.write("### Forecast Comparison")
    fig, ax = plt.subplots()
    if scenario_data.get("original_forecast") is not None:
        ax.plot(scenario_data["original_forecast"]['Year'], scenario_data["original_forecast"]['Emission'], label='Original', marker='o')
    ax.plot(scenario_forecast['Year'], scenario_forecast['Emission'], label='Scenario', marker='o')
    ax.set_xlabel("Year")
    ax.set_ylabel("CO₂ Emissions (tons)")
    ax.set_title(f"Emission Forecast Comparison for {company_info['name']}")
    ax.legend()
    st.pyplot(fig, use_container_width=True)

# --- Recommendations Section ---
st.write("### Recommendations & Best Practices")

recommendations = []
for idx, row in df.sort_values("adjusted_emission", ascending=False).iterrows():
    if row["type"] == "Electricity":
        rec = f"Consider switching a portion of your electricity use to renewables. Reducing electricity emissions by 20% could save {row['adjusted_emission']*0.2:.1f} tons CO₂e per year. [Learn more](https://www.epa.gov/greenpower/green-power-partnership-basics)"
    elif row["type"] == "Transport":
        rec = f"Transitioning company vehicles to electric or hybrid could reduce transport emissions. Cutting transport emissions by 10% saves {row['adjusted_emission']*0.1:.1f} tons CO₂e. [Best practices](https://www.epa.gov/greenvehicles)"
    elif row["type"] == "Supply Chain":
        rec = f"Work with suppliers who prioritize sustainability. A 5% reduction in supply chain emissions saves {row['adjusted_emission']*0.05:.1f} tons CO₂e. [Supply chain tips](https://www.cdp.net/en/supply-chain)"
    else:
        rec = f"Review and optimize this source. Even a small reduction (5%) saves {row['adjusted_emission']*0.05:.1f} tons CO₂e."
    recommendations.append(rec)

for rec in recommendations:
    st.markdown(f"- {rec}")

# --- Export Section ---
st.write("### Export Data")
import io
if st.button("Export Adjusted Emission Sources as CSV"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Adjusted Emission Sources CSV", data=csv, file_name="adjusted_emission_sources.csv", mime="text/csv")

if 'scenario_forecast' in locals():
    csv_scenario = scenario_forecast.to_csv(index=False).encode('utf-8')
    st.download_button("Download Scenario Forecast CSV", data=csv_scenario, file_name="scenario_forecast.csv", mime="text/csv")

st.info("This page is optimized for mobile and desktop. For best experience on mobile, use landscape mode.")

def get_sector_benchmarks(sector):
    benchmarks = {
        "Manufacturing": {"average": 5000, "best": 2000},
        "Energy": {"average": 20000, "best": 8000},
        "Transport": {"average": 8000, "best": 3000},
        "IT": {"average": 1000, "best": 400},
        "Other": {"average": 3000, "best": 1000},
    }
    return benchmarks.get(sector, {"average": 3000, "best": 1000})

# Data validation and anomaly detection
if company_info and not df.empty:
    sector = company_info["sector"]
    benchmarks = get_sector_benchmarks(sector)
    total_emissions = df["adjusted_emission"].sum()
    issues = []
    for idx, row in df.iterrows():
        if row["adjusted_emission"] < 0:
            issues.append(f"Negative value for {row['type']}.")
        if row["adjusted_emission"] > 2 * benchmarks["average"]:
            issues.append(f"Unusually high value for {row['type']} (>{2*benchmarks['average']} tons CO₂e).")
    if total_emissions > 2 * benchmarks["average"]:
        issues.append(f"Total emissions are much higher than sector average ({benchmarks['average']} tons CO₂e).")
    if issues:
        st.warning("Data validation issues detected:")
        for issue in issues:
            st.write(f"- {issue}") 