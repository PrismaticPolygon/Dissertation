import os
import pyproj

import pandas as pd


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

    df["longitude"], df["latitude"] = pyproj.transform(bng, wgs84, df["easting"].values, df['northing'].values)
    df = df.drop(["easting", "northing"], axis=1)

    # Load midas stations. 29840 records.
    midas = pd.read_csv(os.path.join("archive", "midas.csv"))
    midas = midas[midas["end_date"] == "Current"]

    # midas = midas.drop(["area", "start_date", "end_date", "postcode"], axis=1)
    midas = midas.set_index("src_id")
    midas = midas.sort_index()

    # Create map columns
    df["src_id"] = None
    df["distance"] = -1

    geod = pyproj.Geod(ellps='WGS84')

    # To slow. How would I parallelise it?
    # It's all numpy arrays under the hood. It is essentially the dot product.

    for _, row in df.iterrows():

        for src_id, midas_row in midas.iterrows():

            lat0, lon0 = row["latitude"], row["longitude"]
            lat1, lon1 = midas_row["latitude"], midas_row["longitude"]

            azimuth1, azimuth2, distance = geod.inv(lon0, lat0, lon1, lat1)
            distance /= 1000

            if row["src_id"] is None or row["distance"] > distance:

                row["src_id"] = src_id
                row["distance"] = distance

        print(row)

transform()