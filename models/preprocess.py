import os

import pandas as pd


def preprocess():

    # Set dtypes for already encoded variables to save space
    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R',
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

    df["delay"] = (df["ata"] - df["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0

    df = df.drop(["departure_time", "arrival_time", "ata", "origin", "destination"],
                 axis=1)  # All useful data has been extracted.

    #
    df = df.drop(
        ["id", "transaction_type", "runs_to", "runs_from", "identity", "headcode", "service_code", "stp_indicator",
         "timetable_code", "atd"], axis=1)

    df = df.drop(["sleepers", "reservations", "branding"], axis=1)

    encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating"]

    df = pd.get_dummies(df, prefix=encodes, columns=encodes)
    df["delayed"] = df["delay"] > 5     # Delays are legally only more than 5 minutes

    df = df[df["delay"] > -120]         # Filter out ridiculous values caused by day mismatch (yet to be debugged)

    return df