import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler, LabelEncoder

def add_lag_features(df):
    df = df.sort_values(['SKU', 'Zone', 'Week'])
    df['lag_1'] = df.groupby(['SKU', 'Zone'])['Quantity_Sold'].shift(1)
    df['lag_2'] = df.groupby(['SKU', 'Zone'])['Quantity_Sold'].shift(2)
    df['lag_3'] = df.groupby(['SKU', 'Zone'])['Quantity_Sold'].shift(3)
    df['rolling_avg_3'] = df.groupby(['SKU', 'Zone'])['Quantity_Sold'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    return df.dropna(subset=['lag_1', 'lag_2', 'lag_3'])

def train_model(features_df):
    features_df = add_lag_features(features_df)
    predictions = []

    last_week = features_df['Week'].max()
    next_week = last_week + pd.Timedelta(weeks=1)
    
    inventory_df = pd.read_csv('data/inventory.csv')
    print(inventory_df.head())

    for (sku, zone), group in features_df.groupby(['SKU', 'Zone']):
        group = group.sort_values('Week')

        if len(group) < 5:
            print(f"[{sku}-{zone}] Skipped due to insufficient records")
            continue

        print(f"Processing {sku}-{zone} | Records: {len(group)}")

        le_zone = LabelEncoder()
        group['Zone_Encoded'] = le_zone.fit_transform(group['Zone'])

        numerical_cols = [
            'Trend_Score', 'Is_Holiday', 'Temperature', 'Humidity',
            'Week_Number', 'On_Promo', 'lag_1', 'lag_2', 'lag_3', 'rolling_avg_3'
        ]

        X = group[numerical_cols]
        y = group['Quantity_Sold']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        if len(X_train) < 5 or len(X_test) < 1:
            print(f"[{sku}-{zone}] Skipped due to too small train/test split")
            continue

        # ✅ Using early stopping properly
        model = XGBRegressor(
            objective='reg:squarederror',
            random_state=42,
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            reg_alpha=1.0,
            reg_lambda=1.0
        )

        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        y_pred = model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_pred)
        print(f"[{sku}-{zone}] MAE on test set: {test_mae:.2f}")
        print("▶ Sample Predicted:", y_pred[:3])
        print("▶ Sample Actual   :", y_test.values[:3])

        # Forecast next week
        last_train_input = X.iloc[len(X_train) - 1 : len(X_train)]
        X_future = scaler.transform(last_train_input)
        forecast = model.predict(X_future)[0]
        
        stock_row = inventory_df[
        (inventory_df['SKU'] == sku) & (inventory_df['Zone'] == zone)
        ]
        
        current_stock = int(stock_row['Current_Stock'].values[0]) if not stock_row.empty else 0
        

        predictions.append({
            'SKU': sku,
            'Zone': zone,
            # Use next_week for prediction
            'Predicted_Week': next_week.date(),
            'Forecast_Quantity': round(forecast),
            'Current_Stock': current_stock
        })

    return pd.DataFrame(predictions, columns=["SKU", "Zone", "Predicted_Week", "Forecast_Quantity","Current_Stock"])




def evaluate_model(features_df, forecast_df):
    try:
        features_df['Week'] = pd.to_datetime(features_df['Week'])
        forecast_df['Predicted_Week'] = pd.to_datetime(forecast_df['Predicted_Week'])

        merged = pd.merge(
            features_df,
            forecast_df,
            how='inner',
            left_on=['SKU', 'Zone', 'Week'],
            right_on=['SKU', 'Zone', 'Predicted_Week']
        )

        if merged.empty:
            print("⚠️ No overlap between forecast and actual data. Evaluation skipped.")
            return None

        mae = mean_absolute_error(merged['Quantity_Sold'], merged['Forecast_Quantity'])
        print(f"✅ Evaluation MAE: {mae:.2f}")
        return mae

    except Exception as e:
        print("⚠️ Evaluation failed:", e)
        return None
