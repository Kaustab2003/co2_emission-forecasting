# model_prediction.py
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFECV
from sklearn.metrics import r2_score, mean_squared_error

RANDOM_STATE = 42

# -------------------- Load & Preprocess Data --------------------
data = pd.read_csv('data_cleaned.csv')
data = data[data['country'] != 'ARE']  # Remove outlier

# Define features & label
FEATURE_COLS = ['cereal_yield', 'fdi_perc_gdp', 'gni_per_cap', 'en_per_cap',
                'pop_urb_aggl_perc', 'prot_area_perc', 'pop_growth_perc', 'urb_pop_growth_perc']
LABEL_COL = 'co2_per_cap'

X = data[FEATURE_COLS].values
y = data[LABEL_COL].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

# -------------------- Feature Selection --------------------
rf = RandomForestRegressor(random_state=RANDOM_STATE)
selector = RFECV(estimator=rf, cv=KFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE), scoring='r2', n_jobs=-1)
selector.fit(X_train, y_train)

# Keep only selected features
selected_features = [f for f, keep in zip(FEATURE_COLS, selector.support_) if keep]
print(f"🔥 Selected features: {selected_features}")

# Transform train/test data
X_train_sel = selector.transform(X_train)
X_test_sel = selector.transform(X_test)

# -------------------- Random Forest Hyperparameter Tuning --------------------
param_grid = {
    'n_estimators': np.linspace(200, 2000, 10, dtype=int).tolist(),
    'max_features': ['sqrt', 'log2', None],
    'max_depth': [*np.linspace(10, 110, 11, dtype=int), None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_model = RandomizedSearchCV(
    RandomForestRegressor(random_state=RANDOM_STATE),
    param_distributions=param_grid,
    n_iter=20,
    cv=KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
    scoring='r2',
    n_jobs=-1,
    random_state=RANDOM_STATE,
    refit=True
)

rf_model.fit(X_train_sel, y_train)
print("✅ Best parameters:", rf_model.best_params_)
best_rf = rf_model.best_estimator_

# -------------------- Save Model & Features --------------------
save_dict = {
    'model': best_rf,
    'selected_features': selected_features
}
joblib.dump(save_dict, 'co2_forecast_model.pkl')
print("\n✅ Model and selected features saved to 'co2_forecast_model.pkl'.")

# -------------------- Evaluate --------------------
y_pred = best_rf.predict(X_test_sel)
print(f"\n📊 Test R2: {r2_score(y_test, y_pred):.3f}")
print(f"📊 RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")

# -------------------- Plot --------------------
plt.figure(figsize=(8, 6))
sns.regplot(x=y_pred, y=y_test, scatter_kws={'alpha': 0.6})
plt.xlabel('Predicted CO₂ per Capita')
plt.ylabel('Actual CO₂ per Capita')
plt.title(f'Prediction vs Actual | R = {np.corrcoef(y_pred, y_test)[0, 1]:.2f}')
plt.grid(True)
plt.tight_layout()
plt.show()
