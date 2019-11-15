import pandas as pd
import os

def get_stations_df():

    path = os.path.join("stations", "excel_list_station_details.csv")

    df = pd.read_csv(path, index_col="src_id")

    df = df[df["Station end date"] == "Current "]
    df = df[df["Area type"] == "COUNTY "]

    df = df.drop(["Station end date", "Station start date", "Area type"], axis=1)

    df["Name"] = df["Name"].map(str.rstrip)
    df["Area"] = df["Area"].map(str.rstrip)

    df = df.sort_index()
    df.columns = map(str.lower, df.columns)

    return df


def build_ID_string():

    station_IDs = set()
    root = os.path.join("..", "data")

    for file in os.listdir(root):

        series = pd.read_csv(os.path.join(root, file), usecols=["src_id"], squeeze=True)

        station_IDs |= set([str(x) for x in series.values])

    return ",".join(station_IDs)