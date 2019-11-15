import pandas as pd
from weather.download import download
from weather.stations import get_stations_df
from weather.weather import get_weather_df

download()

stations_df = get_stations_df()
weather_df = get_weather_df()

merged = pd.merge(weather_df, stations_df, on="src_id")

merged.to_csv("data/weather.csv")
