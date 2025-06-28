import pandas as pd

def generate_features(data):
    sales_df = data['sales'].copy()
    trends_df = data['trends'].copy()
    holidays_df = data['holidays'].copy()

    # ✅ Detect and standardize the date column in sales
    for col in ['date', 'Date', 'Week', 'Timestamp']:
        if col in sales_df.columns:
            sales_df.rename(columns={col: 'Date'}, inplace=True)
            break
    else:
        raise ValueError("No valid date column found in sales data.")

    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df['Week'] = sales_df['Date'].dt.to_period('W').apply(lambda r: r.start_time)

    # ✅ Detect quantity column
    for col in ['quantity_sold', 'Quantity_Sold', 'Qty', 'Sales']:
        if col in sales_df.columns:
            quantity_col = col
            break
    else:
        raise ValueError("No valid quantity column found in sales data.")

    weekly_sales = sales_df.groupby(['SKU', 'Zone', 'Week'])[quantity_col].sum().reset_index()
    weekly_sales.rename(columns={quantity_col: 'Quantity_Sold'}, inplace=True)

    # ✅ Process Google Trends
    trends_df.rename(columns={'date': 'Date'}, inplace=True)
    trends_df['Date'] = pd.to_datetime(trends_df['Date'])
    trends_df['Week'] = trends_df['Date'].dt.to_period('W').apply(lambda r: r.start_time)

    # 🔍 Detect trend score column
    for col in ['trend_score', 'Trend_Score', 'score', 'trendscore']:
        if col in trends_df.columns:
            trends_df.rename(columns={col: 'Trend_Score'}, inplace=True)
            break
    else:
        raise ValueError("No valid trend score column found in trends data.")

    weekly_trends = trends_df.groupby(['SKU', 'Zone', 'Week'])['Trend_Score'].mean().reset_index()

    # ✅ Process Holidays
    holidays_df.rename(columns={'date': 'Date'}, inplace=True)
    holidays_df['Date'] = pd.to_datetime(holidays_df['Date'])
    holidays_df['Week'] = holidays_df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    holidays_df['Is_Holiday'] = 1
    holiday_flags = holidays_df.groupby(['Zone', 'Week'])['Is_Holiday'].max().reset_index()

    # 🔗 Merge all datasets
    df = pd.merge(weekly_sales, weekly_trends, on=['SKU', 'Zone', 'Week'], how='left')
    df = pd.merge(df, holiday_flags, on=['Zone', 'Week'], how='left')

    # 🧼 Fill missing values
    df['Trend_Score'] = df['Trend_Score'].fillna(0)
    df['Is_Holiday'] = df['Is_Holiday'].fillna(0).astype(int)

    # 🗓️ Time-based features
    df['Week_Number'] = df['Week'].dt.isocalendar().week
    df['Month'] = df['Week'].dt.month
    df['Is_Weekend'] = df['Week'].dt.weekday >= 5

    # 🔢 Categorical encodings
    df['SKU_Encoded'] = df['SKU'].astype('category').cat.codes
    df['Zone_Encoded'] = df['Zone'].astype('category').cat.codes

    # 🏷️ Promo flag
    df['On_Promo'] = 0

    return df
