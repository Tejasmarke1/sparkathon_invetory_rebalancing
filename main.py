import os
import pandas as pd

from src.data_loader import load_all_data
from src.feature_engineering import generate_features
from src.model import train_model
from src.model import evaluate_model
from src.rebalancer import generate_transfer_plan

# Step 1: Load all datasets
print("🔄 Loading datasets...")
data = load_all_data()

# Step 2: Generate ML-ready features
print("🛠️ Performing feature engineering...")
features_df = generate_features(data)

# Step 3: Train model and forecast next week
print("📈 Training model & forecasting demand...")
forecast_df = train_model(features_df)

print("Forecast DataFrame Columns:", forecast_df.columns)
print(forecast_df.head())


# Evaluate model performance
print("📊 Evaluating model performance...")
mae = evaluate_model(features_df, forecast_df)
if mae is not None:
    print(f"✅ Model evaluation completed with MAE: {mae:.2f}")
 

# Step 4: Save forecast output
os.makedirs('outputs', exist_ok=True)
forecast_path = 'outputs/forecasts.csv'
forecast_df.to_csv(forecast_path, index=False)
print(f"✅ Forecast saved to: {forecast_path}")

# Step 5: Load inventory and cost data
inventory_df = data['inventory']
cost_df = data['cost_matrix']

# Step 6: Generate rebalancing plan
print("♻️ Generating transfer suggestions...")
transfer_plan = generate_transfer_plan(forecast_df, inventory_df, cost_df)

# Step 7: Save transfer output
transfer_path = 'outputs/transfer_plan.json'
pd.DataFrame(transfer_plan).to_json(transfer_path, orient='records', indent=2)
print(f"✅ Transfer plan saved to: {transfer_path}")
