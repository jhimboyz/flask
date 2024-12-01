import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import matplotlib.pyplot as plt

# Load the CSV data into a DataFrame
df = pd.read_csv(r'C:\DEMO PYTHON STRUCTURE\FLASK LOGIN PAGE SAMPLE3 - FORECASTING - Responsive - kapoy\data\data.csv')

# Convert 'status' to numerical values
df['status'] = df['status'].replace({'Full': 2, 'Moderate': 1, 'Low': 0})

# Convert 'datetime' to UNIX timestamp
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
df['datetime'] = df['datetime'].astype(np.int64) // 10**9  # Convert to UNIX timestamp

# Convert 'duration' to minutes
df['duration'] = df['duration'] / 60

# Feature matrix X and target vector y
X = df[['status', 'datetime', 'duration']]
y = df['fuel_consumed']

# Pipeline: Scaling -> Gradient Boosting Regressor (No winsorization step)  
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('regressor', GradientBoostingRegressor())
])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'regressor__n_estimators': [100, 200],
    'regressor__learning_rate': [0.01, 0.1],
    'regressor__max_depth': [3, 5]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=10, scoring='neg_mean_squared_error')
grid_search.fit(X_train, y_train)

# Best model from GridSearchCV
best_pipeline = grid_search.best_estimator_

# Save the trained model pipeline
joblib.dump(best_pipeline, 'gradient_boosting_pipeline.pkl')

# Predict on the test set
y_pred = best_pipeline.predict(X_test)

# Evaluation metrics
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Gradient Boosting - MSE: {mse}, MAE: {mae}, R^2: {r2}")

# Visualization: Actual vs Predicted Fuel Consumption
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='green', label='Predicted vs Actual')
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Perfect Prediction (y=x)')
plt.xlabel('Actual Fuel Consumption')
plt.ylabel('Predicted Fuel Consumption')
plt.title('Actual vs Predicted Fuel Consumption (Gradient Boosting Regression)')
plt.legend()
plt.grid(True)
plt.show()
