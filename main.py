import os
import pandas as pd

from src.data_loader import load_all_data
from src.feature_engineering import generate_features
from src.model import train_model, evaluate_model
from src.rebalancer import generate_transfer_plan

# Step 1: Load datasets
print("🔄 Loading datasets...")
data = load_all_data()

# Step 2: Feature Engineering (includes external sources)
print("🛠️ Performing feature engineering (real-time external signals)...")
try:
    features_df = generate_features(data['sales'])
except Exception as e:
    print("❌ Feature generation failed:", e)
    exit()

# Step 3: Train & Forecast
print("📈 Training model & forecasting next week's demand...")
forecast_df = train_model(features_df)

print("\n🔍 Forecast Preview:")
print(forecast_df.head())

# Step 4: Evaluate
print("\n📊 Evaluating model performance...")
mae = evaluate_model(features_df, forecast_df)
if mae is not None:
    print(f"✅ Model evaluation completed. MAE: {mae:.2f}")
else:
    print("⚠️ Skipping MAE evaluation due to lack of overlap.")

# Step 5: Save forecast
os.makedirs('outputs', exist_ok=True)
forecast_path = 'outputs/forecasts.csv'
forecast_df.to_csv(forecast_path, index=False)
print(f"✅ Forecast saved to: {forecast_path}")

# Step 6: Load inventory and cost data
inventory_df = data['inventory']
cost_df = data['cost_matrix']

# Step 7: Rebalancing
print("\n♻️ Generating inventory transfer plan...")
transfer_plan = generate_transfer_plan(forecast_df, inventory_df, cost_df)

# Step 8: Save transfer suggestions
transfer_path = 'outputs/transfer_plan.json'
pd.DataFrame(transfer_plan).to_json(transfer_path, orient='records', indent=2)
print(f"✅ Transfer plan saved to: {transfer_path}")
