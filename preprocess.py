import pandas as pd
import numpy as np

dtype = {
    "origin_tiploc": "category",
    "destination_tiploc": "category",
    "timetable_code": "category",
    "stp_indicator": "category",
    "status": "category",
    "category": "category",
    "power_type": "category",
    "timing_load": "category",
    "sleepers": "category",
    "reservations": "category",
    "catering": "category",
    "seating": "category",
}

# Ah. I have to encode both.

df = pd.read_csv("records.csv", index_col="id", parse_dates=["origin_time", "destination_time"], dtype=dtype)

df["origin_year"] = df["origin_time"].dt.year
df["origin_month"] = df["origin_time"].dt.month
df["origin_day"] = df["origin_time"].dt.day
df["origin_day_of_week"] = df["origin_time"].dt.dayofweek

df["origin_minutes"] = df["origin_time"].dt.hour * 60 + df["origin_time"].dt.minute

df["destination_year"] = df["destination_time"].dt.year
df["destination_month"] = df["destination_time"].dt.month
df["destination_day"] = df["destination_time"].dt.day
df["destination_day_of_week"] = df["destination_time"].dt.dayofweek

df["destination_minutes"] = df["destination_time"].dt.hour * 60 + df["destination_time"].dt.minute

df = df.drop(["date", "origin_time", "destination_time"], axis=1)

tiploc_map = {
    "destination_tiploc": pd.Series(df["origin_tiploc"].values, index=df["origin_tiploc"].cat.codes).to_dict()
}

df["origin_tiploc"] = df["origin_tiploc"].cat.codes
df["destination_tiploc"] = df.replace(tiploc_map)  # Takes way too long to work with.

df = df.drop(["service_code", "headcode", "identity", "ATOC_code"], axis=1)

df.columns = df.columns.str.lower()

df["timetable_code"] = df["timetable_code"].cat.codes

df["bank_holiday"] = df["bank_holiday"].fillna(False)
df["bank_holiday"] = df["bank_holiday"].replace("X", True)
df["bank_holiday"] = df["bank_holiday"].astype(bool)

df = df.drop(["runs_to", "runs_from"], axis=1)

df["stp_indicator"] = df["stp_indicator"].cat.codes
df["status"] = df["status"].cat.codes
df["category"] = df["category"].cat.codes
df["power_type"] = df["power_type"].cat.codes
df["timing_load"] = df["timing_load"].cat.codes
df["sleepers"] = df["sleepers"].cat.codes
df["reservations"] = df["reservations"].cat.codes
df["catering"] = df["catering"].cat.codes
df["seating"] = df["seating"].cat.codes

# characteristics = ["B", "C", "D", "E", "G", "M", "P", "Q", "R", "S", "Y", "Z"]

df = df.drop(["characteristics"], axis=1)

df.to_csv("out.csv")

