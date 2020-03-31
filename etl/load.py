import os
import time
import pandas as pd

root = "D:data"


def load():

    path = os.path.join(root, "dscm.csv")

    if os.path.exists(path):    # Delete if it exists

        os.remove(path)

    location = pd.read_csv(os.path.join(root, "location.csv"), dtype={"src_id": int}, usecols=["tiploc", "stanox_area"])
    # weather = pd.read_csv(os.path.join(root, "weather.csv"), parse_dates=[1], dtype={"src_id": int})

    for file in os.listdir(os.path.join(root, "darwin")):

        date = file[:10]

        start = time.time()

        print("Loading {}...".format(date), end="")

        movement = pd.read_csv(os.path.join(root, "darwin", file), index_col=["uid"])
        schedule = pd.read_csv(os.path.join(root, "schedule", file), index_col=["uid"])

        groups = movement.groupby("uid")

        schedule["atd"] = 0     # Does THIS have a date? I don't fucking think so! Wait. Movement should be fine.
        schedule["ata"] = 0

        for uid in movement.index.unique():  # There's likely to be UIDs in movement not in schedule (from STP and VSTP)

            try:

                train = groups.get_group(uid)   # Get every Darwin train message for this UID
                meta = schedule.loc[uid]        # Get SCHEDULE metadata for this UID

                origin = train[train["tiploc"] == meta["origin"]]
                destination = train[train["tiploc"] == meta["destination"]]

                if len(origin) == 0 or len(destination) == 0:   # No matching origin or destination

                    raise ValueError("No origin or destination for UID {}".format(uid))

                schedule.loc[uid, "atd"] = origin.iloc[0]["at"]
                schedule.loc[uid, "ata"] = destination.iloc[0]["at"]

            except KeyError:    # Case where schedule UID not present in Darwin

                pass
                # print("UID {} not in SCHEDULE".format(uid))

            except ValueError as e:

                pass
                # print(e)

        results = schedule[(schedule["ata"] != 0) & (schedule["atd"] != 0)]    # Only get those with ata correctly set

        # Add origin stanox area
        results = results.merge(location, left_on="origin", right_on="tiploc")
        results = results.rename({"stanox_area": "origin_stanox_area"}, axis=1)

        # Add destination stanox area
        results = results.merge(location, left_on="destination", right_on="tiploc")
        results = results.rename({"stanox_area": "destination_stanox_area"}, axis=1)

        print("DONE ({:.2f}s)".format(time.time() - start))

        results.to_csv(path, mode="a", header=not os.path.exists(path))


if __name__ == "__main__":

    load()
