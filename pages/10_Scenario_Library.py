import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils import load_model, forecast_emissions
import plotly.graph_objs as go

st.title("📚 Scenario Library")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
# Remove scenario_library session state check; always initialize below
company_name = company_info["name"]
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page before using the scenario library.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page before using the scenario library.")
    st.stop()

st.info("This page is optimized for mobile and desktop. For best experience on mobile, use landscape mode.")

# --- Scenario Library in Session State ---
if "scenario_library" not in st.session_state:
    st.session_state["scenario_library"] = {}
if company_name not in st.session_state["scenario_library"]:
    st.session_state["scenario_library"][company_name] = {}

# --- Save New Scenario ---
st.header("Save Current Scenario")
scenario_name = st.text_input("Scenario Name")
adjusted_sources = st.session_state.get("emission_sources", [])
if st.button("Save Scenario") and scenario_name:
    st.session_state["scenario_library"][company_name][scenario_name] = adjusted_sources.copy()
    st.success(f"Scenario '{scenario_name}' saved.")

# --- List and Load Scenarios ---
st.header("Saved Scenarios")
scenarios = list(st.session_state["scenario_library"][company_name].keys())
if scenarios:
    selected = st.selectbox("Select a scenario to load or compare", scenarios)
    if st.button("Load Scenario"):
        st.session_state["emission_sources"] = st.session_state["scenario_library"][company_name][selected].copy()
        st.success(f"Scenario '{selected}' loaded. Go to Dashboard or Scenario Simulation to view results.")
    if st.button("Delete Scenario"):
        del st.session_state["scenario_library"][company_name][selected]
        st.success(f"Scenario '{selected}' deleted.")
        st.experimental_rerun()
    # --- Compare Scenarios ---
    st.header("Compare Scenarios")
    compare_list = st.multiselect("Select scenarios to compare", scenarios)
    if compare_list:
        model = load_model()
        years = 10
        # --- Plotly Interactive Scenario Comparison ---
        plotly_fig = go.Figure()
        for sc in compare_list:
            sources = st.session_state["scenario_library"][company_name][sc]
            total_emission = sum([src["emission"] for src in sources])
            forecast_df = forecast_emissions(model, total_emission, years)
            plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name=sc))
        plotly_fig.update_layout(title=f"Interactive Scenario Comparison for {company_name}", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
        st.plotly_chart(plotly_fig, use_container_width=True)
        # --- Optional: Map Visualization if location data present ---
        has_location = any('location' in src for sc in compare_list for src in st.session_state["scenario_library"][company_name][sc])
        if has_location:
            import folium
            from streamlit_folium import st_folium
            st.header("Map of Emission Sources (first scenario)")
            first_scenario = st.session_state["scenario_library"][company_name][compare_list[0]]
            m = folium.Map(location=[20, 78], zoom_start=4)
            for src in first_scenario:
                if 'location' in src:
                    lat, lon = src['location']
                    folium.CircleMarker(location=[lat, lon], radius=8, popup=f"{src['type']}: {src['emission']} tons", color='blue', fill=True).add_to(m)
            st_folium(m, width=700, height=400)
else:
    st.info("No scenarios saved yet.") 