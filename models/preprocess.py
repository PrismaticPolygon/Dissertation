import os
import time

import numpy as np
import pandas as pd

from sklearn.preprocessing import scale
from imblearn.over_sampling import SMOTE

class Args:

    def __init__(self):

        self.properties = {
            "onehot": True,
            "cyclical": True,
            "gaussian": False,
            "smote": False,
            "weather": False
        }

    def __str__(self):

        if not any(self.properties.values()):

            return "default"

        else:

            return "_".join([k for k, v in self.properties.items() if v])

args = {
    "onehot": True,
    "cyclical": False,
    "gaussian": False,
    "smote": False,
    "weather": False
}

args["default"] = not any(args.values())


def arg():

    return "_".join([k for k, v in args.items() if v])


def datetime(df, key):

    prefix = "origin" if key == "departure_time" else "destination"

    def cyclical(column, f, period):

        denom = {
            "month": 12,
            "day": 31,
            "day_of_week": 7,
            "hour": 24,
            "minute": 60,
            "day_minute": 1440
        }

        f = np.sin if f == "sin" else np.cos

        return f(2 * np.pi * column / denom[period])

    df[prefix + "_year"] = df[key].dt.year.astype("uint16")

    if args["cyclical"]:

        for f in ["sin", "cos"]:

            df[prefix + "_month_" + f] = cyclical(df[key].dt.month, f, "month")
            df[prefix + "_day_" + f] = cyclical(df[key].dt.day, f, "day")
            df[prefix + "_day_of_week_" + f] = cyclical(df[key].dt.dayofweek, f, "day_of_week")
            df[prefix + "_hour_" + f] = cyclical(df[key].dt.hour, f, "hour")
            df[prefix + "_minutes_" + f] = cyclical(df[key].dt.minutes, f, "minute")
            # df[prefix + "_minutes_" + f] = cyclical(df[key].dt.hour * 60 + df[key].dt.minute, f, "day_minute")

    else:

        df[prefix + "_month"] = df[key].dt.month.astype("uint8")
        df[prefix + "_day"] = df[key].dt.day.astype("uint8")
        df[prefix + "_day_of_week"] = df[key].dt.dayofweek.astype("uint8")
        df[prefix + "_hour"] = df[key].dt.hour.astype("uint8")
        df[prefix + "_minutes"] = df[key].dt.minute.astype("uint8")
        # df[prefix + "_minutes"] = df[key].dt.hour * 60 + df[key].dt.minute


def onehot():

    pass


def gaussian():

    pass

def preprocess():

    start = time.time()

    path = os.path.join("data", "preprocessed", "{}.csv".format(arg()))

    if os.path.exists(path):

        print("Loading {}...".format(path), end="")

        df =  pd.read_csv(path)

        print(" DONE ({:.2f}s)".format(time.time() - start))

        return df

    print("Preprocessing to {}...".format(path), end="")

    # Set dtypes for already encoded variables to save space
    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed']

    dtype = {key: "uint8" for key in dtype}

    # Handle mixed DtypeWarning
    dtype["headcode"] = str
    dtype["sleepers"] = str
    dtype["branding"] = str

    df = pd.read_csv(os.path.join("data", "dscm.csv"), index_col=0, parse_dates=["departure_time", "arrival_time", "ata", "atd"], dtype=dtype)

    # Drop useless fields
    df = df.drop(["id", "transaction_type", "runs_to", "runs_from", "identity", "headcode", "service_code",
                  "stp_indicator", "timetable_code", "atd", "sleepers", "reservations", "branding", "origin",
                  "destination", "tiploc_x", "tiploc_y"], axis=1)

    # Create origin and destination time columns
    datetime(df, "departure_time")
    datetime(df, "arrival_time")

    # Create delay variables
    df["delay"] = (df["ata"] - df["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0
    df["delayed"] = df["delay"] > 5  # Delays are legally only more than 5 minutes
    df = df[df["delay"] > -120]  # Filter out ridiculous values caused by day mismatch (yet to be debugged)

    df = df.drop(["departure_time", "arrival_time", "ata"], axis=1)  # All useful data has been extracted.

    # This should really be all objects.

    encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating", "origin_stanox_area",
               "destination_stanox_area"]

    if args["onehot"]: # One-hot encode categorical variables

        df = pd.get_dummies(df, prefix=encodes, columns=encodes)

    else:   # Still need to convert strings to categorical

        for e in encodes:

            df[e] = df[e].astype("category").cat.codes

    if args["gaussian"]: # Convert all features to Gaussian: zero mean and unit variance.

        df = pd.DataFrame(scale(df), columns=df.columns)


    df.to_csv(path, index=False)

    print(" DONE ({:.2f}s)".format(time.time() - start))

    return df

if __name__ == "__main__":

    x = preprocess()

    print(x.head())

    print(x.info())