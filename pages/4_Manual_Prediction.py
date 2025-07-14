import streamlit as st
from utils.utils import load_model, manual_predict

st.title("🛠️ Manual Prediction")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

model = load_model()

# Example input fields (adjust based on your model)
population = st.number_input("Population (Millions)", value=100.0)
gdp = st.number_input("GDP (Billion USD)", value=500.0)
energy_use = st.number_input("Energy Use (TWh)", value=200.0)

if st.button("Predict Emissions"):
    input_features = {
        "Population": population,
        "GDP": gdp,
        "Energy Use": energy_use
    }
    try:
        prediction = manual_predict(model, input_features)
        st.success(f"Predicted CO₂ Emission: {prediction:.2f} Mt")
    except Exception as e:
        st.error(f"Error during prediction: {e}")
