import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# -------------------------------
# Create Sample Dataset (replace with your real data)
# -------------------------------
def create_sample_data():
    np.random.seed(42)
    data = pd.DataFrame({
        'Population': np.random.uniform(50, 1500, 500),    # millions
        'GDP': np.random.uniform(200, 20000, 500),         # billion USD
        'Energy Use': np.random.uniform(100, 5000, 500),   # TWh
    })

    # Synthetic emissions: a combination of the above features
    data['Emissions'] = (
        data['Population'] * 2.5 +
        data['GDP'] * 0.8 +
        data['Energy Use'] * 1.2 +
        np.random.normal(0, 100, 500)   # adding some noise
    )

    return data

# -------------------------------
# Train the Model
# -------------------------------
def train_and_save_model():
    # Load / generate data
    df = pd.read_csv("data/your_real_data.csv")


    # Features and target
    X = df[['Population', 'GDP', 'Energy Use']]
    y = df['Emissions']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model training
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("Model Performance on Test Data:")
    print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

    # Save the model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/emission_model.pkl")
    print("\n✅ Model saved at: models/emission_model.pkl")

# -------------------------------
# Run the script
# -------------------------------
if __name__ == "__main__":
    train_and_save_model()
