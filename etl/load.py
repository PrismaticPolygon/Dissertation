import os
import time

import pandas as pd
import numpy as np

root = "data"


def load():

    path = os.path.join(root, "dscm_w.csv")

    if os.path.exists(path):    # Delete if it exists

        os.remove(path)

    location = pd.read_csv(os.path.join("data", "location.csv"), index_col="tiploc", dtype={"src_id": int}, usecols=["tiploc", "stanox_area"])
    # weather = pd.read_csv(os.path.join("data", "weather.csv"), parse_dates=[1], dtype={"src_id": int})

    for file in os.listdir(os.path.join(root, "darwinII")):

        date = file[:10]

        start = time.time()

        print("Loading {}...".format(date), end="")

        movement = pd.read_csv(os.path.join(root, "darwin", file), index_col=["uid"])
        schedule = pd.read_csv(os.path.join(root, "schedule", file), index_col=["uid"], dtype={"headcode": str, "sleepers": str, "branding": str})

        groups = movement.groupby("uid")

        schedule["atd"] = 0     # Does THIS have a date? I don't fucking think so! Wait. Movement should be fine.
        schedule["ata"] = 0

        for uid in schedule.index.unique():  # Iterate through UIDs in schedule

            try:

                train = groups.get_group(uid)   # Get every Darwin train message for this UID
                meta = schedule.loc[uid]        # Get SCHEDULE metadata for this UID

                origin = train[train["tiploc"] == meta["origin"]]
                destination = train[train["tiploc"] == meta["destination"]]

                if len(origin) == 0 or len(destination) == 0:   # No matching origin or destination

                    raise ValueError("No origin or destination for UID {}".format(uid))

                schedule.loc[uid, "atd"] = origin.iloc[-1]["at"]
                schedule.loc[uid, "ata"] = destination.iloc[-1]["at"]

            except KeyError:    # Case where schedule UID not present in Darwin

                pass

            except ValueError as e:

                pass

        results = schedule[(schedule["ata"] != 0) & (schedule["atd"] != 0)]    # Only get those with ata and atd correctly set

        results = results.drop(["id", "transaction_type", "runs_from", "runs_to", "identity", "headcode", "service_code",
                                "stp_indicator", "branding", "timetable_code", "sleepers"], axis=1)

        # Create delay columns
        results["ata"] = pd.to_datetime(results["ata"])
        results["arrival_time"] = pd.to_datetime(results["arrival_time"])
        results["departure_time"] = pd.to_datetime(results["departure_time"])

        results["duration"] = (results["arrival_time"] - results["departure_time"]).map(lambda x: x.total_seconds()) / 60.0
        results["delay"] = (results["ata"] - results["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0
        results["delayed"] = (results["delay"] > 5).astype("uint8")  # Delays are legally only more than 5 minutes

        # Remove trains where the duration is less than the absolute delay. This deals with weird edge cases like
        # where a train sta = 2018-04-02 but ata = 2018-04-01 or a train with only 3 stops arrives before it departs
        results = results[results["duration"] > -1 * results["delay"]]

        # Hm. Many don't have equivalent stanoxes. Interesting.

        # Add origin stanox area
        results = results.join(location, on="origin", how="inner")
        results = results.rename({"stanox_area": "origin_stanox_area"}, axis=1)

        # Add destination stanox area
        results = results.join(location, on="destination", how="inner")
        results = results.rename({"stanox_area": "destination_stanox_area"}, axis=1)

        results = results.rename({"departure_time": "std", "arrival_time": "sta"}, axis=1)

        # And now, weather. I had hoped to do this more nicely, but alas.

        #
        # # Join origin weather
        # results["origin_hour"] = pd.to_datetime(results['atd'], format="%Y-%m-%d %H:%M:%S").dt.round('H')
        # results = results.merge(weather, left_on=["origin_src_id", "origin_hour"], right_on=["src_id", "ob_time"])
        # results = results.rename({col: col + "_origin" for col in weather.columns}, axis=1)
        #
        # # Join destination weather
        # results["destination_hour"] = pd.to_datetime(results['ata'], format="%Y-%m-%d %H:%M:%S").dt.round('H')
        # results = results.merge(weather, left_on=["destination_src_id", "destination_hour"], right_on=["src_id", "ob_time"])
        # results = results.rename({col: col + "_destination" for col in weather.columns}, axis=1)

        print("DONE ({:.2f}s)".format(time.time() - start))

        results.to_csv(path, mode="a", header=not os.path.exists(path))


if __name__ == "__main__":

    load()
