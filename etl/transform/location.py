import os
import pyproj

import pandas as pd
import numpy as np


def transform():

    # Read and clean NaPTAN. 2632 records.
    naptan = pd.read_csv(os.path.join("archive", "naptan.csv"))
    naptan = naptan.drop(["RevisionNumber", "Modification", "CreationDateTime", "ModificationDateTime",
                          "StationNameLang", "GridType"], axis=1)  # Get rid of metadata
    naptan = naptan.rename({
        "AtcoCode": "atco",
        "TiplocCode": "tiploc",
        "CrsCode": "3alpha",
        "StationName": "description",
        "Easting": "easting",
        "Northing": "northing"
    }, axis=1)

    # Read and clean CORPUS. 55060 records.
    corpus = pd.read_csv(os.path.join("archive", "corpus.csv"), na_values=" ")
    corpus = corpus.drop(["UIC", "NLCDESC16"], axis=1)
    corpus["stanox_area"] = corpus["STANOX"].astype(str).map(lambda x: x[:2])
    corpus.columns = map(str.lower, corpus.columns)

    # Merge dataframes and drop records without a stanox (the least permissive)
    df = pd.merge(naptan, corpus, on=["tiploc", "3alpha"])
    df = df[df["stanox"].notna()]

    df[["stanox", "stanox_area"]] = df[["stanox", "stanox_area"]].astype(int)

    # Convert easting and northing to longitude and latitude
    bng = pyproj.Proj('epsg:27700')
    wgs84 = pyproj.Proj('epsg:4326')

    df["latitude"], df["longitude"] = pyproj.transform(bng, wgs84, df["easting"].values, df['northing'].values)
    df = df.drop(["easting", "northing"], axis=1)

    # Load midas stations. 29840 records.
    midas = pd.read_csv(os.path.join("archive", "midas.csv"))
    midas = midas[midas["end_date"] == "Current"]
    midas = midas.set_index("src_id")
    midas = midas.sort_index()

    # Create map columns
    df["src_id"] = 0
    df["distance"] = -1

    geod = pyproj.Geod(ellps='WGS84')

    # Calculate the closest MIDAS station each train station
    def closest(row):

        lat0, lon0 = np.full(len(midas), row["latitude"]), np.full(len(midas), row["longitude"])
        lat1, lon1 = midas["latitude"].values, midas["longitude"].values

        azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
        distance /= 1000  # Convert from metres to kilometres

        min_distance = np.nanmin(distance)              # Get the smallest distance, ignoring nans
        station = midas.iloc[np.nanargmin(distance)]    # Get the row at which the closest distance occurs

        return station.name, min_distance

    df[["src_id", "distance"]] = df[["latitude", "longitude"]].apply(closest, axis=1, result_type="expand")

    df.to_csv(os.path.join("data", "location.csv"), index=False)


if __name__ == "__main__":

    transform()
