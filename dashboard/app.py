# dashboard/app.py

from fastapi import FastAPI
from fastapi import HTTPException   
from src.data_loader import load_all_data
from src.feature_engineering import generate_features
from src.model import train_model, evaluate_model
from src.rebalancer import generate_transfer_plan
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app = FastAPI()

# Allow frontend to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Use your frontend domain in prod.
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Inventory Rebalancing API is live!"}


@app.get("/forecast")
def forecast():
    data = load_all_data()
    features_df = generate_features(data['sales'])
    forecast_df = train_model(features_df)
    forecast_df.to_csv("outputs/forecasts.csv", index=False)
    return forecast_df.to_dict(orient='records')


@app.get("/transfer-plan")
def get_transfer_plan():
    try:
        print("🔄 Reading forecast...")
        forecast_df = pd.read_csv('outputs/forecasts.csv')
        print(forecast_df.head())

        print("📦 Reading inventory...")
        inventory_df = pd.read_csv('data/inventory.csv')
        print(inventory_df.head())

        print("💰 Reading cost matrix...")
        cost_df = pd.read_csv('data/cost_matrix.csv')
        print(cost_df.head())

        suggestions = generate_transfer_plan(forecast_df, inventory_df, cost_df)

        if not suggestions:
            return {"message": "No transfer suggestions generated."}

        return suggestions

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating transfer plan: {str(e)}")

