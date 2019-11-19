from locations.stanox import get_stanox_df
from locations.usage import get_usage_df
import pandas as pd

stanox_df = get_stanox_df() # 2571
usage_df = get_usage_df()   # 2563

df = pd.merge(stanox_df, usage_df, on=["3alpha", "nlc"], suffixes=("_stanox", "_usage"))    # 2549

df = df.drop(["description_stanox", "latitude_stanox", "longitude_stanox"], axis=1)   # Delete duplicates from stanox_df
df = df.rename({"description_usage": "description", "latitude_usage": "latitude", "longitude_usage": "longitude"}, axis=1)

df.to_csv("data/location.csv")

