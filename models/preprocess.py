import os

import pandas as pd
import numpy as np

# Set dtypes for already encoded variables to save space

dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
         'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
         'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M', 'catering_R',
         'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight', 'bank_holiday_running', 'length',
         'speed'
]

dtype = {key: "uint8" for key in dtype}


path = os.path.join("data", "dscm.csv")

df = pd.read_csv(path, index_col=0, parse_dates=["departure_time", "arrival_time", "ata", "atd"], dtype=dtype)

df["origin_year"] = df["departure_time"].dt.year.astype("uint16")
df["origin_month"] = df["departure_time"].dt.month.astype("uint8")
df["origin_day"] = df["departure_time"].dt.day.astype("uint8")
df["origin_day_of_week"] = df["departure_time"].dt.dayofweek.astype("uint8")
df["origin_minutes"] = (df["departure_time"].dt.hour * 60 + df["departure_time"].dt.minute).astype("uint16")

df["destination_year"] = df["arrival_time"].dt.year.astype("uint16")
df["destination_month"] = df["arrival_time"].dt.month.astype("uint8")
df["destination_day"] = df["arrival_time"].dt.day.astype("uint8")
df["destination_day_of_week"] = df["arrival_time"].dt.dayofweek.astype("uint8")
df["destination_minutes"] = (df["arrival_time"].dt.hour * 60 + df["arrival_time"].dt.minute).astype("uint16")

# Most of these have tiny, tiny values.
# SO scheduled arrival time is itself the problem. Where does that come from?

df["delay"] = (df["ata"] - df["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0

# This is grotesquely wrong.

df[["ata", "arrival_time", "delay"]].to_csv("delay.csv")

# Curious that 'atd' is not found in axis. Particularly as it is the last column...

df = df.drop(["departure_time", "arrival_time", "ata"], axis=1)      # All useful data has been extracted.

# 10 MB. How can one-hot encoding make it so big? Sure, there's a lot of options...


#
# df = df.drop(["date", "origin_time", "destination_time"], axis=1)
#
# tiploc_map = {
#     "destination_tiploc": pd.Series(df["origin_tiploc"].values, index=df["origin_tiploc"].cat.codes).to_dict()
# }
#
# df["origin_tiploc"] = df["origin_tiploc"].cat.codes
# df["destination_tiploc"] = df.replace(tiploc_map)  # Takes way too long to work with.
#
# df = df.drop(["service_code", "headcode", "identity", "ATOC_code"], axis=1)
#
# df.columns = df.columns.str.lower()
#
# df["timetable_code"] = df["timetable_code"].cat.codes
#
# df["bank_holiday"] = df["bank_holiday"].fillna(False)
# df["bank_holiday"] = df["bank_holiday"].replace("X", True)
# df["bank_holiday"] = df["bank_holiday"].astype(bool)
#
df = df.drop(["id", "transaction_type", "runs_to", "runs_from", "identity", "headcode", "service_code", "stp_indicator",
              "timetable_code", "atd"], axis=1)

df = df.drop(["sleepers", "reservations", "branding"], axis=1)

# We may want to drop sleepers and reservations: not enough information.
# Seating, ATOC_code.

encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating"]

# We can do it for a bunch at the same time.

dummies = pd.get_dummies(df, prefix=encodes, columns=encodes)

df = df.drop(encodes, axis=1)
# df = df.join(dummies)

print(dummies.info())

print(dummies.columns)

dummies.to_csv("blah.csv")

# for e in encodes:
#
#     print("\n" + e + "\n")
#
#     # print(df[e].value_counts())
#
#     dummies = pd.get_dummies(df[e], prefix=e)
#
#     print(dummies.info())
#
#     df = df.drop(e, axis=1)
#     df = df.join(dummies)

# print(df["ATOC_code"].value_counts())
#
# # 2.6 MB... That's for every row, though! Hell, we might have to do this in load.
# # There's plenty there.
# # The array shape is ridiculous as well. There's a lot more entries. That's just the nature of the beast, though?
# # Not quite.
#
# # It gets pretty large pretty fast! 32 GB!. That's.... insane.
# # I'll have to buy some more RAM for my desktop.
# # It's not seating, that just pushes it over the edge. Right?
#
# print(df.info())
#
# # I can certainly optimise.
#
# print(df.columns)

# One-hot encode:
# status (P, 1)
# category (OO, XX, EE, OL, ES, XU, XZ)
# power_type (EMU, DMU, HST, E, D)
# timing load (S, E, A, 375, T, 323, N, 360, 333, 319, 313, 0, 410, 317, 257, 350, V, X, 365, 395, 69, 321, 385, 390...)
# seating (S, B)

# That's a lotta damage. Yeah. NO. I can always do that later.

# df["stp_indicator"] = df["stp_indicator"].cat.codes
# df["status"] = df["status"].cat.codes
# df["category"] = df["category"].cat.codes
# df["power_type"] = df["power_type"].cat.codes
# df["timing_load"] = df["timing_load"].cat.codes
# df["sleepers"] = df["sleepers"].cat.codes
# df["reservations"] = df["reservations"].cat.codes
# df["catering"] = df["catering"].cat.codes
# df["seating"] = df["seating"].cat.codes
#
# df.to_csv("out.csv")

