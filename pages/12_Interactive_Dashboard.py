import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from utils.utils import load_model, forecast_emissions

st.set_page_config(layout="wide")
st.title("📊 Interactive Dashboard")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
forecast_df = st.session_state.get("forecast_df")
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page to use this dashboard.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page to use this dashboard.")
    st.stop()
if forecast_df is None or not hasattr(forecast_df, 'head'):
    st.warning("Please generate a forecast to use this dashboard.")
    st.stop()
df = pd.DataFrame(emission_sources)
has_emission_type = "emission" in df.columns and "type" in df.columns
if not has_emission_type:
    st.warning("No 'emission' or 'type' column found in emission sources. Please check your data input.")
    st.stop()

# --- Key Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Emissions (tons CO₂e)", f"{df['emission'].sum():,.0f}")
with col2:
    if forecast_df is not None and len(forecast_df) > 1:
        avg_change = (forecast_df["Emission"].values[1:] - forecast_df["Emission"].values[:-1]).mean()
        trend = "↓" if avg_change < 0 else "↑"
        st.metric("Annual Change", f"{avg_change:.2f} {trend}")
    else:
        st.metric("Annual Change", "N/A")
with col3:
    target = 1000
    target_year = None
    if forecast_df is not None:
        below_target = forecast_df[forecast_df["Emission"] <= target]
        if not below_target.empty:
            target_year = int(below_target.iloc[0]["Year"])
            st.metric("Target Year (≤1000)", f"{target_year}")
        else:
            st.metric("Target Year (≤1000)", "Not reached")
    else:
        st.metric("Target Year (≤1000)", "N/A")

st.divider()

# --- Interactive Emissions Forecast ---
st.subheader("Forecasted Emissions (Interactive)")
if forecast_df is not None:
    plotly_fig = go.Figure()
    plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name='Forecast'))
    plotly_fig.update_layout(title=f"Emission Forecast for {company_info['name']}", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
    st.plotly_chart(plotly_fig, use_container_width=True)
else:
    st.info("No forecast data available.")

# --- Interactive Emission Breakdown ---
st.subheader("Current Emissions by Source (Interactive)")
plotly_pie = go.Figure(data=[go.Pie(labels=df["type"], values=df["emission"], hole=0.3)])
plotly_pie.update_layout(title="Emission Breakdown by Source")
st.plotly_chart(plotly_pie, use_container_width=True)

plotly_bar = go.Figure(data=[go.Bar(x=df["type"], y=df["emission"])] )
plotly_bar.update_layout(title="Emission Bar Chart", xaxis_title="Source Type", yaxis_title="Annual Emissions (tons CO₂e)")
st.plotly_chart(plotly_bar, use_container_width=True)

# --- Scenario Comparison (if available) ---
if "scenario_library" in st.session_state and company_info["name"] in st.session_state["scenario_library"]:
    scenarios = list(st.session_state["scenario_library"][company_info["name"]].keys())
    if scenarios:
        st.subheader("Compare Scenarios (Interactive)")
        compare_list = st.multiselect("Select scenarios to compare", scenarios)
        if compare_list:
            model = load_model()
            years = 10
            plotly_fig = go.Figure()
            for sc in compare_list:
                sources = st.session_state["scenario_library"][company_info["name"]][sc]
                total_emission = sum([src["emission"] for src in sources])
                forecast_df = forecast_emissions(model, total_emission, years)
                plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name=sc))
            plotly_fig.update_layout(title=f"Scenario Comparison for {company_info['name']}", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
            st.plotly_chart(plotly_fig, use_container_width=True)

# --- Map Visualization (if location data present) ---
has_location = any('location' in src for src in emission_sources)
if has_location:
    import folium
    from streamlit_folium import st_folium
    st.subheader("Map of Emission Sources")
    m = folium.Map(location=[20, 78], zoom_start=4)
    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)
    for src in emission_sources:
        if 'location' in src:
            lat, lon = src['location']
            folium.CircleMarker(location=[lat, lon], radius=8, popup=f"{src['type']}: {src['emission']} tons", color='blue', fill=True).add_to(marker_cluster)
    st_folium(m, width=900, height=500) 