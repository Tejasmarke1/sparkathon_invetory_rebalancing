# src/data_loader.py

import pandas as pd
import os

from src.external.trends import fetch_google_trends
from src.external.weather import fetch_weather_data
from src.external.holidays import fetch_holidays
DATA_DIR = "data/"

def load_inventory(path=os.path.join(DATA_DIR, "inventory.csv")):
    return pd.read_csv(path)

def load_sales(path=os.path.join(DATA_DIR, "sales.csv")):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def load_zones(path=os.path.join(DATA_DIR, "zones.csv")):
    return pd.read_csv(path)

def load_cost_matrix(path=os.path.join(DATA_DIR, "cost_matrix.csv")):
    return pd.read_csv(path)

# ⏱️ Real-time Google Trends
def load_trends():
    keywords = ['Biscuits', 'Chips', 'Juice', 'Milk', 'Oil', 'Rice', 'Shampoo', 'Soap', 'Toothpaste', 'Water Bottle']
    return fetch_google_trends(keywords)

# 📆 Real-time Holidays
def load_holidays():
    return fetch_holidays()

# 🌦️ Real-time Weather
def load_weather():
    return fetch_weather_data()

# 🔄 Combined loader
def load_all_data():
    return {
        "inventory": load_inventory(),
        "sales": load_sales(),
        "zones": load_zones(),
        "cost_matrix": load_cost_matrix()
        # trends, holidays, weather are loaded dynamically in feature_engineering.py
    }

if __name__ == "__main__":
    data = load_all_data()
    for name, df in data.items():
        print(f"✅ Loaded {name}: {df.shape[0]} rows")
