import streamlit as st
import pandas as pd
from utils.utils import load_model, batch_predict

st.title("📤 Batch Upload for CO₂ Emissions Prediction")

st.write("""
Upload a CSV file containing the required input features.  
The app will run batch predictions and display the results.
""")

# Example template download
with st.expander("ℹ️ Expected CSV Format"):
    st.write("The CSV should have columns like:")
    st.code("Population,GDP,Energy Use", language='csv')

# Upload file
uploaded_file = st.file_uploader("Upload your CSV file here", type=["csv"])

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading uploaded CSV: {e}")
        df = None

    if df is not None:
        st.write("### Uploaded Data")
        st.dataframe(df)
        try:
            model = load_model()
            results = batch_predict(model, df)
            st.write("### Batch Predictions")
            st.dataframe(results)
            # Download CSV
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="\U0001F4E5 Download Results as CSV",
                data=csv,
                file_name="batch_predictions.csv",
                mime='text/csv'
            )
        except Exception as e:
            st.error(f"Error during batch prediction: {e}")
else:
    st.info("Upload a CSV file to get started.")
