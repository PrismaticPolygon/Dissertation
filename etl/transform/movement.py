import os
import time
import csv

import pandas as pd

from lxml import etree

def parse_time(string, date):
    """
    Convert a Darwin time to a datetime by adding the date the file was written and the

    :param string: a time. Either HH:MM or HH:MM:SS
    :param date: a d
    :return:
    """

    if len(string) == 5:    # HH:MM.

        string += ":00"

    return date + " " + string


def parse(ts, date):
    """
    Parse Darwin Forecast ElementTrees. Some TS elements contain multiple arr/dep/pass children, so return a list.

    :param ts: a Darwin Forecast ElementTree
    :param date: the date the message was sent
    :return: a movement dictionary
    """

    movements = []

    for child in ts:  # Either PlatformData, TSTimeData, or TSLocation

        if child.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}Location":  # If the CHILD tag has these things, then we're interested.

            for grandchild in child:

                if "at" in grandchild.attrib:

                    movement = {
                        "uid": ts.attrib["uid"],
                        "ssd": ts.attrib["ssd"],
                        "tiploc": child.attrib["tpl"],
                        "at": parse_time(grandchild.attrib["at"], date)
                    }

                    if grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}arr":

                        movement["type"] = "ARRIVAL"

                    elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}dep":

                        movement["type"] = "DEPARTURE"

                    elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}pass":

                        movement["type"] = "PASS"

                    movements.append(movement)

    if len(movements) == 0:

        raise ValueError("No movements")

    return ts.attrib["ssd"], movements

# Maybe I can't know for sure? No. That is simply unacceptable.

def transform(start="2018-04-01", end="2019-04-01"):
    """
    Convert each day's XML messages into a CSV. Disregard trains that started before start and after end.
    If a train runs between two days, the service start date (ssd) is the file to which it is saved.

    Include the start but exclude the end

    """

    in_dir = os.path.join("archive", "darwin")
    out_dir = os.path.join("data", "darwinII")

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    files = {"yesterday": None, "today": None}
    writers = {"yesterday": None, "today": None}

    for file in os.listdir(in_dir):

        date = file[:10]
        in_path = os.path.join(in_dir, file)
        out_path = os.path.join(out_dir, date) + ".csv"

        # if date < start or date > end or os.path.exists(out_path):
        #
        #     print("Skipping {}...".format(in_path))
        #
        #     continue

        # files["today"] = open(out_path, "w", newline="")
        #
        # writers["today"] = csv.DictWriter(files["today"], ["uid", "ssd", "tiploc", "at", "type"])
        # writers["today"].writeheader()

        days = {
            "yesterday": None,
            "today": []
        }

        # We shouldn't have that timestamp.

        cur = time.time()

        print("Parsing {} to {}...".format(in_path, out_path), end="")

        with open(in_path, "rb") as in_file:

            for line in in_file:

                try:

                    root = etree.fromstring(line)   # Read the XML into lxml

                    if "http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2" in root.nsmap.values():

                        ts = root.attrib['ts'][:10]

                        try:

                            ssd, movements = parse(root[0][0], date)

                            if start <= ssd < end:

                                if ssd < ts:  # the service started yesterday, after the start date

                                    print(ssd, ts, root.attrib["ts"], movements)

                                    days["yesterday"] += movements  # Shouldn't be possible on first iteration.

                                else:         # the service started before the end date

                                    days["today"] += movements

                            else:

                                pass

                        except ValueError:  #

                            pass

                except etree.XMLSyntaxError:  # Seem to be 'standalone' delay messages.

                    pass

        if days["yesterday"] is not None:

            print(len(days["yesterday"]))
            print(len(days["today"]))

            df = pd.DataFrame(days["yesterday"])
            df.to_csv("yesterday.csv")

            print(df.head())

            df = df.drop_duplicates(ignore_index=True)
            df = df.sort_values(["uid", "at"])

            for uid, train in df.groupby("uid"):

                print(train)

            df.to_csv("yesterday.csv")

        days["yesterday"] = days["today"].copy()

        print(" DONE ({:.2f}s)".format(time.time() - cur))


if __name__ == "__main__":

    transform()
