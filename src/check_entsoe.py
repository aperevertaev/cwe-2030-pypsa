import os
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

load_dotenv()
client = EntsoePandasClient(api_key=os.environ["ENTSOE_API_KEY"])

start = pd.Timestamp("2024-01-01", tz="Europe/Berlin")
end = pd.Timestamp("2024-01-08", tz="Europe/Berlin")
prices = client.query_day_ahead_prices("DE_LU", start=start, end=end)

print(prices.head())
print(prices.describe())