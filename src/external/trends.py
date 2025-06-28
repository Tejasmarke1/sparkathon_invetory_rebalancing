from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

def fetch_google_trends(keywords, geo='IN'):
    pytrends = TrendReq(hl='en-US', tz=330)
    pytrends.build_payload(kw_list=keywords, timeframe='now 7-d', geo=geo)
    trends = pytrends.interest_over_time()
    trends.reset_index(inplace=True)
    trends['Week'] = trends['date'].dt.to_period('W').apply(lambda r: r.start_time)
    return trends[['Week'] + keywords]

# Example usage:
# df = fetch_google_trends(['Biscuits', 'Chips'])
# df.to_csv('data/trends.csv', index=False)
