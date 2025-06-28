# src/data_loader.py

import pandas as pd
import os

# Define default data path
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

def load_trends(path=os.path.join(DATA_DIR, "trends.csv")):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def load_holidays(path=os.path.join(DATA_DIR, "holidays.csv")):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def load_all_data():
    return {
        "inventory": load_inventory(),
        "sales": load_sales(),
        "zones": load_zones(),
        "cost_matrix": load_cost_matrix(),
        "trends": load_trends(),
        "holidays": load_holidays()
    }

if __name__ == "__main__":
    data = load_all_data()
    for name, df in data.items():
        print(f"Loaded {name}: {df.shape[0]} rows")
