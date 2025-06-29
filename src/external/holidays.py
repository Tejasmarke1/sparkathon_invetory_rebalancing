import requests
import pandas as pd
from datetime import datetime

CALENDARIFIC_API_KEY = "edvu97u1iiktrF7s71Z7uhmbwaMLxAWL"  # Replace with your actual key

def fetch_holidays(year, country='IN', region='Maharashtra'):
    url = "https://calendarific.com/api/v2/holidays"
    params = {
        "api_key": CALENDARIFIC_API_KEY,
        "country": country,
        "year": year,
        "location": region
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200 or 'response' not in data:
        raise Exception("Failed to fetch holidays:", data)

    holidays = data['response']['holidays']
    records = []

    for h in holidays:
        date = pd.to_datetime(h['date']['iso'])
        week = date.to_period('W').start_time
        records.append({
            "Date": date,
            "Week": week,
            "Holiday_Name": h['name'],
            "Zone": region,
            "Is_Holiday": 1
        })

    df = pd.DataFrame(records)
    return df[['Zone', 'Week', 'Holiday_Name', 'Is_Holiday']]

# Example usage
if __name__ == "__main__":
    state_zone_mapping = {
        'Maharashtra': 'Pune',
        'Delhi': 'Delhi',
        'Tamil Nadu': 'Chennai',
        'Uttar Pradesh': 'Lucknow'
    }

    year = datetime.now().year
    all_holidays = pd.DataFrame()

    for state, zone in state_zone_mapping.items():
        state_holidays = fetch_holidays(year, region=state)
        state_holidays['Zone'] = zone  # Ensure matches your model zones
        all_holidays = pd.concat([all_holidays, state_holidays], ignore_index=True)

    all_holidays.to_csv('data/holidays.csv', index=False)
    print("✅ Holidays saved to data/holidays.csv")
