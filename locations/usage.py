import pandas as pd
import math
import os
import pyproj

def clean(entries_and_exits):

    if isinstance(entries_and_exits, str):

        entries_and_exits = entries_and_exits.strip()

        if entries_and_exits == "-" or entries_and_exits == ":":

            return math.nan

        return float(entries_and_exits.replace(",", ""))

    elif math.isnan(entries_and_exits):

        return entries_and_exits

def get_usage_df():

    path = os.path.join("usage", "estimates-of-station-usage-2017-18.csv")

    df = pd.read_csv(path, encoding="latin-1")

    df = df.drop(['1718 Entries & Exits - GB rank', '1617 Entries & Exits - GB rank', 'Large station change flag',
                  'Small station change flag', '% Change', 'Explanation of large change 1718',
                  'Source for explanation of large change 1718', '1617 Entries & Exits', 'Station Group',
                  'PTE Urban Area Station', 'London Travelcard Area', 'SRS Code', 'SRS Description', 'NR Route',
                  'CRP Line Designation', "Entries & Exits_Full", "Entries & Exits_Reduced", "Entries & Exits_Season"], axis=1)

    df = df.rename({
        "NLC": "nlc",
        "TLC": "3alpha",
        "Station Name": "description",
        "Region": "region",
        "Local Authority": "local_authority",
        "Constituency": "constituency",
        "OS Grid Easting": "easting",
        "OS Grid Northing": "northing",
        "Station Facility Owner": "toc",
    }, axis=1)

    df["nlc"] = df["nlc"].astype("str").map(lambda x: x + "00")

    df["1718 Entries & Exits"] = df["1718 Entries & Exits"].map(clean)
    df["1718 Interchanges"] = df["1718 Interchanges"].map(clean)

    df["1718 Entries & Exits"] = df["1718 Entries & Exits"].fillna(df["1718 Entries & Exits"].mean()).astype("uint32")
    df["1718 Interchanges"] = df["1718 Interchanges"].fillna(df["1718 Interchanges"].mean()).astype("uint32")

    df["traffic"] = df["1718 Entries & Exits"] + df["1718 Interchanges"]
    df = df.drop(["1718 Entries & Exits", "1718 Interchanges"], axis=1)

    bng = pyproj.Proj(init='epsg:27700')
    wgs84 = pyproj.Proj(init='epsg:4326')

    df["longitude"], df["latitude"] = pyproj.transform(bng, wgs84, df["easting"].values, df['northing'].values)
    df = df.drop(["easting", "northing"], axis=1)

    return df