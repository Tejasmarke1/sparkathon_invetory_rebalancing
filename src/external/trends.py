from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import re

def fetch_google_trends(keywords, geo='IN'):
    pytrends = TrendReq(hl='en-US', tz=330)

    # Clean keywords
    keywords = [re.sub(r'\W+', '', kw) for kw in keywords if isinstance(kw, str)]
    keywords = [kw for kw in keywords if kw]  # remove empty strings

    # Batch keywords into chunks of 5
    all_trends = []
    for i in range(0, len(keywords), 5):
        chunk = keywords[i:i+5]
        try:
            pytrends.build_payload(chunk, timeframe='now 7-d', geo=geo)
            df = pytrends.interest_over_time()
            df.reset_index(inplace=True)
            df['Week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
            all_trends.append(df[['Week'] + chunk])
        except Exception as e:
            print(f"⚠️ Skipping keywords {chunk} due to error: {e}")

    if not all_trends:
        raise ValueError("❌ Google Trends fetch failed for all keyword batches.")

    # Merge all trend chunks
    trends = pd.concat(all_trends, axis=1)
    trends = trends.loc[:, ~trends.columns.duplicated()]
    return trends
