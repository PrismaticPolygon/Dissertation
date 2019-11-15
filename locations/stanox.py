import pandas as pd
import os
import pyproj

def stanox_areas():

    path = os.path.join("stanox", "stanox_areas.csv")

    df = pd.read_csv(path)

    df = df.rename({"STANOX Code": "stanox_area", "BR Region": "br_region", "Main Locations": "locations"}, axis=1)

    df["stanox_area"] = df["stanox_area"].map(lambda x: x[:2])

    df = df[df["stanox_area"] != "00"]  # Mainland Europe

    return df

def ordw():

    path = os.path.join("stanox", "ORDW.csv")

    df = pd.read_csv(path)
    df = df.rename({
        "NAME": "description",
        "TIPLOC": "tiploc",
        "EASTING": "easting",
        "NORTHING": "northing"}, axis=1)

    return df

def corpus():

    # path = os.path.join("stanox", "stanox", "CORPUS.csv")
    path = os.path.join("stanox", "CORPUS.csv")

    df = pd.read_csv(path, na_values=" ")
    df = df.drop("UIC", axis=1) # It's not clear what UIC is
    df = df.drop("NLCDESC16", axis=1) # There are no null NLCDESC, and longer the description, the better

    df["stanox_area"] = df["STANOX"].astype(str).map(lambda x: x[:2])

    df.columns = map(str.lower, df.columns)

    return df

def foi():

    # Contains lots of placeholder values as per https://groups.google.com/forum/#!topic/openrailstanox-talk/kJAsHSGvP3o
    path = os.path.join("stanox", "FOI.csv")

    df = pd.read_csv(path)
    df = df.rename({
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "CODE": "tiploc",
        "DESCRIPTION": "description"}, axis=1)

    return df

def naptan():

    # path = os.path.join("stanox", "stanox", "NAPTAN.csv")
    path = os.path.join("stanox", "NAPTAN.csv")

    df = pd.read_csv(os.path.abspath(path))

    df = df.drop(["RevisionNumber", "Modification", "CreationDateTime", "ModificationDateTime", "StationNameLang", "GridType"], axis=1) # Get rid of metastanox
    df = df.rename({
        "AtcoCode": "atco",
        "TiplocCode": "tiploc",
        "CrsCode": "3alpha",
        "StationName": "description",
        "Easting": "easting",
        "Northing": "northing"}, axis=1)

    return df

def get_stanox_df():

    df = pd.merge(naptan(), corpus(), on=["tiploc", "3alpha"])
    df = pd.merge(df, stanox_areas(), on="stanox_area")
    df = df[pd.notnull(df["stanox"])]

    df["stanox"] = df["stanox"].astype("uint32")
    df["nlc"] = df["nlc"].astype("str")

    # # To use all the stanoxsets (more merging work required)
    # dfs = [naptan(), foi(), corpus(), ordw()]
    # df = reduce(lambda left, right: pd.merge(left, right, on=['tiploc']), dfs)

    # Convert easting and northing to longitude and latitude
    bng = pyproj.Proj(init='epsg:27700')
    wgs84 = pyproj.Proj(init='epsg:4326')

    df["longitude"], df["latitude"] = pyproj.transform(bng, wgs84, df["easting"].values, df['northing'].values)
    df = df.drop(["easting", "northing"], axis=1)

    return df

# The resulting stanoxset contains 2550 stanoxes. There are 2563 train stations un the UK, excluding stations
# on the London Underground and the 181 heritage railways.
