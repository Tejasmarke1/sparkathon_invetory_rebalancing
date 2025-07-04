from src.external.weather import fetch_weather_data
from src.external.trends import fetch_google_trends
from src.external.holidays import fetch_holidays
from datetime import datetime
import pandas as pd

def generate_features(sales_df):
    sales_df = sales_df.copy()
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df['Week'] = sales_df['Date'].dt.to_period('W').apply(lambda r: r.start_time)

    # Aggregate weekly sales
    weekly_sales = sales_df.groupby(['SKU', 'Zone', 'Week'])['Quantity_Sold'].sum().reset_index()

    # 🔁 Google Trends
    keywords = sales_df['SKU'].unique().tolist()
    try:
        trends_df = fetch_google_trends(keywords)
    except Exception as e:
        print(f"⚠️ Failed to fetch trends: {e}")
        trends_df = pd.DataFrame({'keyword': keywords, 'trend': [0] * len(keywords)})

    # 📅 Holidays
    year = datetime.now().year
    holidays_df = fetch_holidays(year)

    # 🌤 Weather for each zone
    WEATHER_API_KEY = "51c7714767dc30514f7c07ca28db716a"  # Replace with your key
    zones = weekly_sales['Zone'].unique().tolist()
    weather_data = pd.concat([fetch_weather_data(zone, WEATHER_API_KEY) for zone in zones], ignore_index=True)
    
    print(trends_df.head())

    # 🔁 Merge Trends
   # If trends_df doesn't have Week, fallback
    if 'Week' not in trends_df.columns or trends_df.empty:
        print("⚠️ Google Trends data unavailable, generating fallback data...")
        weeks = weekly_sales['Week'].unique()
        skus = weekly_sales['SKU'].unique()
        trends_df = pd.DataFrame([
        {'Week': week, 'SKU': sku, 'Trend_Score': 0}
        for week in weeks for sku in skus
        ])
    else:
        trends_df = trends_df.rename(columns={'keyword': 'SKU', 'trend': 'Trend_Score'})
        
    
    
    print("Trends columns:", trends_df.columns)
    print("Weekly Sales columns:", weekly_sales.columns)
    
    if 'Trend_Score' in trends_df.columns:
        trends_df = trends_df.drop(columns=['Trend_Score'])

    trends_df = trends_df.melt(id_vars=['Week'], var_name='SKU', value_name='Trend_Score')
    trends_df['Trend_Score'] = pd.to_numeric(trends_df['Trend_Score'], errors='coerce')
    trends_df = trends_df.dropna(subset=['Trend_Score'])


        
    
    merged = pd.merge(weekly_sales, trends_df, on=['SKU', 'Week'], how='left')



    # 📅 Merge Holidays
    holidays_df['Is_Holiday'] = 1
    holidays_df['Week'] = pd.to_datetime(holidays_df['Week'])
    holiday_flags = holidays_df.groupby(['Zone', 'Week'])['Is_Holiday'].max().reset_index()
    merged = pd.merge(merged, holiday_flags, on=['Zone', 'Week'], how='left')
    merged['Is_Holiday'] = merged['Is_Holiday'].fillna(0).astype(int)

    # 🌤 Merge Weather
    merged = pd.merge(merged, weather_data[['Zone', 'Week', 'Temperature', 'Humidity']], 
                      on=['Zone', 'Week'], how='left')
    merged[['Temperature', 'Humidity']] = merged[['Temperature', 'Humidity']].fillna(method='ffill')

    # 🧠 Time & Encoding
    merged['Week_Number'] = merged['Week'].dt.isocalendar().week
    merged['Month'] = merged['Week'].dt.month
    merged['SKU_Encoded'] = merged['SKU'].astype('category').cat.codes
    merged['Zone_Encoded'] = merged['Zone'].astype('category').cat.codes
    merged['On_Promo'] = 0

    return merged
