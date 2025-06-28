import requests
import pandas as pd
from datetime import datetime

def fetch_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    res = requests.get(url).json()

    records = []
    for entry in res['list']:
        dt = datetime.fromtimestamp(entry['dt'])
        temp = entry['main']['temp']
        humidity = entry['main']['humidity']
        rain = entry.get('rain', {}).get('3h', 0)

        records.append({
            'City': city,
            'Datetime': dt,
            'Temperature': temp,
            'Humidity': humidity,
            'Rainfall': rain,
            'Week': dt.to_period('W').start_time
        })

    df = pd.DataFrame(records)
    weekly_df = df.groupby(['City', 'Week']).agg({
        'Temperature': 'mean',
        'Humidity': 'mean',
        'Rainfall': 'sum'
    }).reset_index()

    return weekly_df

# Usage:
# df = fetch_weather('Pune', 'YOUR_API_KEY')
# df.to_csv('data/weather.csv', index=False)
