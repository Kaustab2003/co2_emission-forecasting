import joblib
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import requests
from sklearn.ensemble import IsolationForest
import importlib.util
import os
import sys

# 🔑 Path to the trained model
MODEL_PATH = "models/emission_model.pkl"

# --------------------------------
# Model Loading
# --------------------------------
def load_model():
    return joblib.load(MODEL_PATH)

# --------------------------------
# Country Forecasting (Placeholder Example)
# --------------------------------
def forecast_emissions(model, country, years):
    base_emission = {
        "USA": 5000,
        "China": 10000,
        "India": 2500,
        "Germany": 800,
        "UK": 600,
        "Brazil": 500,
        "Canada": 700
    }.get(country, 1000)

    # Simple growth factor (replace with model-based forecasting)
    forecast_data = pd.DataFrame({
        "Year": list(range(2025, 2025 + years)),
        "Emission": [base_emission * (1 + 0.02) ** i for i in range(years)]
    })

    return forecast_data

# --------------------------------
# Dashboard Data & Visualizations
# --------------------------------
def get_dashboard_data():
    years = list(range(2000, 2025))
    emissions = np.random.normal(loc=5000, scale=500, size=len(years))
    gdp = np.random.normal(loc=60000, scale=5000, size=len(years))
    data = pd.DataFrame({
        "Year": years,
        "Emissions": emissions,
        "GDP": gdp
    })
    return data

def plot_trends(data):
    fig, ax = plt.subplots()
    ax.plot(data["Year"], data["Emissions"], label="Emissions")
    ax.plot(data["Year"], data["GDP"], label="GDP")
    ax.set_xlabel("Year")
    ax.set_ylabel("Value")
    ax.set_title("Emissions and GDP Trend")
    ax.legend()
    st.pyplot(fig)

def plot_correlation(data):
    corr = data.drop("Year", axis=1).corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# --------------------------------
# Manual Input Prediction
# --------------------------------
def manual_predict(model, input_features):
    df = pd.DataFrame([input_features])
    return model.predict(df)[0]

# --------------------------------
# Batch CSV Prediction
# --------------------------------
def batch_predict(model, input_df):
    predictions = model.predict(input_df)
    input_df['Predicted Emissions'] = predictions
    return input_df

def fetch_external_emission_data(company_name):
    # Simulate fetching from an external API (replace with real API call as needed)
    # Example: response = requests.get(f'https://external.api/emissions?company={company_name}')
    # For demo, return mock data
    mock_data = [
        {"type": "Electricity", "emission": 1200},
        {"type": "Transport", "emission": 800},
        {"type": "Supply Chain", "emission": 1500},
    ]
    return mock_data

def ai_anomaly_detection(df):
    # Only use numeric columns for anomaly detection
    if df.empty or 'emission' not in df.columns:
        return []
    X = df[['emission']].values
    clf = IsolationForest(contamination=0.15, random_state=42)
    preds = clf.fit_predict(X)
    # -1 means anomaly
    anomalies = df.index[preds == -1].tolist()
    return anomalies

def test_all_sectors():
    sectors = ["Manufacturing", "Energy", "Transport", "IT", "Other"]
    errors = []
    for sector in sectors:
        try:
            spec = importlib.util.spec_from_file_location("company_profile", "pages/0_Company_Profile.py")
            company_profile = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(company_profile)
            get_sector_benchmarks = company_profile.get_sector_benchmarks
            result = get_sector_benchmarks(sector)
            print(f"Sector: {sector}, Benchmarks: {result}")
        except Exception as e:
            print(f"Error for sector {sector}: {e}")
            errors.append((sector, str(e)))
    if errors:
        print("\nErrors found:")
        for sector, err in errors:
            print(f"{sector}: {err}")
    else:
        print("All sector tests passed.")

def test_model_predictions():
    print("\nTesting model predictions...")
    try:
        model = load_model()
        # Manual prediction test
        input_features = {"Population": 100, "GDP": 500, "Energy Use": 200}
        pred = manual_predict(model, input_features)
        print(f"Manual prediction output: {pred}")
        # Batch prediction test
        df = pd.DataFrame([
            {"Population": 100, "GDP": 500, "Energy Use": 200},
            {"Population": 200, "GDP": 1000, "Energy Use": 400}
        ])
        batch = batch_predict(model, df.copy())
        print(f"Batch prediction output:\n{batch}")
    except Exception as e:
        print(f"Error in model predictions: {e}")

def test_dashboard_data():
    print("\nTesting dashboard data...")
    try:
        data = get_dashboard_data()
        assert not data.empty, "Dashboard data is empty!"
        print(f"Dashboard data sample:\n{data.head()}")
    except Exception as e:
        print(f"Error in dashboard data: {e}")

def test_anomaly_detection():
    print("\nTesting anomaly detection...")
    try:
        df = pd.DataFrame([
            {"emission": 100}, {"emission": 200}, {"emission": 3000}, {"emission": 400}, {"emission": 5000}
        ])
        anomalies = ai_anomaly_detection(df)
        print(f"Anomaly indices: {anomalies}")
    except Exception as e:
        print(f"Error in anomaly detection: {e}")

def smoke_test_all_pages():
    print("\nRunning smoke test for all Streamlit pages...")
    pages_dir = "pages"
    errors = []
    for fname in os.listdir(pages_dir):
        if fname.endswith(".py") and not fname.startswith("__"):
            page_path = os.path.join(pages_dir, fname)
            print(f"Testing page: {fname}")
            try:
                spec = importlib.util.spec_from_file_location(fname[:-3], page_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[fname[:-3]] = module
                spec.loader.exec_module(module)
                # Try to call main() if it exists
                if hasattr(module, "main"):
                    module.main()
                print(f"  ✅ {fname} loaded successfully.")
            except Exception as e:
                print(f"  ❌ Error in {fname}: {e}")
                errors.append((fname, str(e)))
    if errors:
        print("\nErrors found in pages:")
        for fname, err in errors:
            print(f"{fname}: {err}")
    else:
        print("All Streamlit pages loaded without import/runtime errors.")

def run_all_automated_tests():
    test_all_sectors()
    test_model_predictions()
    test_dashboard_data()
    test_anomaly_detection()
    print("\nAll automated feature tests completed.")

def run_all_automated_tests_and_pages():
    run_all_automated_tests()
    smoke_test_all_pages()
    print("\nAll automated and page smoke tests completed.")
