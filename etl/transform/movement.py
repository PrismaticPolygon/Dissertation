import os
import time
from lxml import etree
import csv


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

# Some have both arrival and departure times. Arrival would always come before departure.
# So we might actually have a problem.
# There's an idea: break it into two separate movements.


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

def transform(start="2018-04-01", end="2019-03-31"):
    """
    Convert each day's XML messages into a CSV. Disregard trains that started before start and after end.
    If a train runs between two days, the service start date (ssd) is the file to which it is saved.
    """

    in_dir = os.path.join("E:", "archive", "darwin")
    out_dir = os.path.join("E:", "data", "darwinII")

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    files = {"yesterday": None, "today": None}
    writers = {"yesterday": None, "today": None}

    for file in os.listdir(in_dir):

        date = file[:10]
        in_path = os.path.join(in_dir, file)
        out_path = os.path.join(out_dir, date) + ".csv"

        if date < start or date > end or os.path.exists(out_path):

            print("Skipping {}...".format(in_path))

            continue

        files["today"] = open(out_path, "w", newline="")

        writers["today"] = csv.DictWriter(files["today"], ["uid", "ssd", "tiploc", "at", "type"])
        writers["today"].writeheader()

        cur = time.time()

        print("Parsing {} to {}...".format(in_path, out_path), end="")

        with open(in_path, "rb") as in_file:

            for line in in_file:

                try:

                    root = etree.fromstring(line)   # Read the XML into lxml

                    if "http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2" in root.nsmap.values():

                        ts = root.attrib['ts'][:10]

                        print(ts)

                        try:

                            ssd, movements = parse(root[0][0], ts)

                            if start < ssd < date:  # the service started yesterday, after the start date

                                writers["yesterday"].writerows(movements)

                            elif ssd < end:         # the service started before the end date

                                writers["today"].writerows(movements)

                        except ValueError:  #

                            pass

                except etree.XMLSyntaxError:  # Seem to be 'standalone' delay messages.

                    pass

        if files["yesterday"] is not None:

            files["yesterday"].close()

        files["yesterday"] = writers["today"]
        writers["yesterday"] = writers["today"]

        print(" DONE ({:.2f}s)".format(time.time() - cur))

    files["yesterday"].close()


if __name__ == "__main__":

    transform()
