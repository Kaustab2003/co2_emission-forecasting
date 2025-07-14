import streamlit as st
from utils.utils import load_model, forecast_emissions
import matplotlib.pyplot as plt
import pandas as pd

st.title("📈 Forecast CO₂ Emissions")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

def get_total_emissions():
    sources = st.session_state.get("emission_sources", [])
    if not sources or not isinstance(sources, list) or not all(isinstance(x, dict) for x in sources):
        return 0
    df = pd.DataFrame(sources)
    if "emission" not in df.columns:
        st.warning("No 'emission' column found in emission sources. Please check your data input.")
        return 0
    return df["emission"].sum()

# Check for company info and emission sources
company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page before forecasting.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page before forecasting.")
    st.stop()

try:
    name = company_info.get('name', 'Unknown')
    sector = company_info.get('sector', 'Unknown')
    size = company_info.get('size', 'Unknown')
    st.write(f"Forecasting CO₂ emissions for **{name}** ({sector}, {size})")
except Exception as e:
    st.warning(f"Error reading company info: {e}")
    st.stop()

years = st.slider("Forecast for next N years:", min_value=1, max_value=30, value=20)
total_emissions = get_total_emissions()
st.write(f"Starting with total annual emissions: **{total_emissions} tons CO₂e**")

if st.button("Generate Forecast"):
    try:
        forecast_df = forecast_emissions(model, total_emissions, years)
        st.session_state["forecast_df"] = forecast_df  # Save for dashboard
    except Exception as e:
        st.error(f"Error generating forecast: {e}")
        forecast_df = None

    forecast_df = st.session_state.get("forecast_df")
    if forecast_df is not None and hasattr(forecast_df, 'head'):
        try:
            st.write("### Emissions Forecast Data")
            st.dataframe(forecast_df, use_container_width=True)

            st.write("### Forecast Graph")
            fig, ax = plt.subplots()
            if 'Year' in forecast_df.columns and 'Emission' in forecast_df.columns:
                ax.plot(forecast_df['Year'], forecast_df['Emission'], marker='o')
                ax.set_xlabel("Year")
                ax.set_ylabel("CO₂ Emissions (tons)")
                ax.set_title(f"Emission Forecast for {name}")
                st.pyplot(fig, use_container_width=True)
            else:
                st.warning("Forecast data missing 'Year' or 'Emission' columns.")
        except Exception as e:
            st.error(f"Error displaying forecast: {e}")
    else:
        st.info("No forecast data available. Please generate a forecast on the 'Forecast' page.")
