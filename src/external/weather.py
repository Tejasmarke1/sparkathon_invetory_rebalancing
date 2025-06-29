import requests
import pandas as pd
from datetime import datetime

def fetch_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        res = response.json()

        records = []
        for entry in res['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            temp = entry['main']['temp']
            humidity = entry['main']['humidity']
            rain = entry.get('rain', {}).get('3h', 0)

            records.append({
                'Zone': city,
                'Date': dt.date(),  # just the date part
                'Temperature': temp,
                'Humidity': humidity,
                'Rainfall': rain
            })

        df = pd.DataFrame(records)

        # Add 'Week' column as datetime
        df['Date'] = pd.to_datetime(df['Date'])
        df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)

        # Group by Zone and Week
        weekly_df = df.groupby(['Zone', 'Week']).agg({
            'Temperature': 'mean',
            'Humidity': 'mean',
            'Rainfall': 'sum'
        }).reset_index()

        return weekly_df

    except Exception as e:
        print(f"❌ Failed to fetch weather for {city}: {e}")
        return pd.DataFrame()

# ✅ Example usage
if __name__ == "__main__":
    api_key = "51c7714767dc30514f7c07ca28db716a"
    cities = ['Pune', 'Delhi', 'Nagpur', 'Lucknow', 'Chennai']

    all_weather = pd.DataFrame()

    for city in cities:
        city_weather = fetch_weather_data(city, api_key)
        all_weather = pd.concat([all_weather, city_weather], ignore_index=True)

    all_weather.to_csv('data/weather.csv', index=False)
    print("✅ Weather data saved to data/weather.csv")
