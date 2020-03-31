import os
import time

import numpy as np
import pandas as pd


def datetime(df, key):

    prefix = "origin" if key == "departure_time" else "destination"

    def cyclical(column, f, period):

        denom = {
            "month": 12,
            "day": 31,
            "day_of_week": 7,
            "minutes": 1440
        }

        f = np.sin if f == "sin" else np.cos

        return f(2 * np.pi * column / denom[period])

    df[prefix + "_year"] = df[key].dt.year.astype("uint16")

    df[prefix + "_month_sin"] = cyclical(df[key].dt.month, "sin", "month")
    df[prefix + "_month_cos"] = cyclical(df[key].dt.month, "cos", "month")

    df[prefix + "_day_sin"] = cyclical(df[key].dt.day, "sin", "day")
    df[prefix + "_day_cos"] = cyclical(df[key].dt.day, "cos", "day")

    df[prefix + "_day_of_week_sin"] = cyclical(df[key].dt.day, "sin", "day_of_week")
    df[prefix + "_day_of_week_cos"] = cyclical(df[key].dt.day, "cos", "day_of_week")

    df[prefix + "_minutes_sin"] = cyclical(df[key].dt.hour * 60 + df[key].dt.minute, "sin", "minutes")
    df[prefix + "_minutes_cos"] = cyclical(df[key].dt.hour * 60 + df[key].dt.minute, "cos", "minutes")


def preprocess():

    # Set dtypes for already encoded variables to save space
    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed']

    dtype = {key: "uint8" for key in dtype}

    path = os.path.join("D:", "data", "dscm.csv")

    df = pd.read_csv(path, index_col=0, parse_dates=["departure_time", "arrival_time", "ata", "atd"], dtype=dtype)

    # Create origin time columns
    datetime(df, "departure_time")

    # Create departure time columns
    datetime(df, "departure_time")

    # Create delay variables
    df["delay"] = (df["ata"] - df["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0
    df["delayed"] = df["delay"] > 5  # Delays are legally only more than 5 minutes
    df = df[df["delay"] > -120]  # Filter out ridiculous values caused by day mismatch (yet to be debugged)

    df = df.drop(["departure_time", "arrival_time", "ata"], axis=1)  # All useful data has been extracted.

    # Useless fields
    df = df.drop(
        ["id", "transaction_type", "runs_to", "runs_from", "identity", "headcode", "service_code", "stp_indicator",
         "timetable_code", "atd"], axis=1)

    print(df["stp_indicator"].value_counts())   # Might be worth one-hot. Are alterations more likely to be bad?

    df = df.drop(["sleepers", "reservations", "branding"], axis=1)

    encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating", "origin_stanox_area",
               "destination_stanox_area"]

    df = pd.get_dummies(df, prefix=encodes, columns=encodes)
    df["delayed"] = df["delay"] > 5     # Delays are legally only more than 5 minutes

    df = df[df["delay"] > -120]         # Filter out ridiculous values caused by day mismatch (yet to be debugged)

    return df


if __name__ == "__main__":

    start = time.time()

    print("Preprocessing DataFrame...", end="")

    x = preprocess()

    print(" DONE ({.:2f}s)".format(time.time() - start), end="\n\n")

    print(x.head())