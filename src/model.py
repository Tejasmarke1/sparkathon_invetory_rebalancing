import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
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

    for (sku, zone), group in features_df.groupby(['SKU', 'Zone']):
        group = group.sort_values('Week')

        if len(group) < 5:
            continue
        
        
        print(f"Processing {sku}-{zone} | Records: {len(group)}")
        

        le_zone = LabelEncoder()
        group['Zone_Encoded'] = le_zone.fit_transform(group['Zone'])

        numerical_cols = ['Trend_Score', 'Is_Holiday', 'Week_Number', 'On_Promo', 'lag_1', 'lag_2', 'lag_3', 'rolling_avg_3']
        X = group[numerical_cols]
        y = group['Quantity_Sold']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

        xgb = XGBRegressor(objective='reg:squarederror', random_state=42)
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [3, 5],
            'learning_rate': [0.05, 0.1]
        }
        grid = GridSearchCV(xgb, param_grid, scoring='neg_mean_absolute_error', cv=3)
        grid.fit(X_train, y_train)

        model = grid.best_estimator_

        y_pred = model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_pred)
        print(f"[{sku}-{zone}] MAE on test set: {test_mae:.2f}")

        last_row = X.iloc[[-1]]
        X_future = scaler.transform(last_row)
        forecast = model.predict(X_future)[0]

        predictions.append({
            'SKU': sku,
            'Zone': zone,
            'Predicted_Week': next_week.date(),
            'Forecast_Quantity': round(forecast)
        })

    return pd.DataFrame(predictions, columns=["SKU", "Zone", "Predicted_Week", "Forecast_Quantity"])




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
            print("⚠️ No overlap between forecast and historical data. Skipping evaluation.")
            return None

        mae = mean_absolute_error(merged['Quantity_Sold'], merged['Forecast_Quantity'])
        return mae

    except Exception as e:
        print("⚠️ Evaluation failed:", e)
        return None
