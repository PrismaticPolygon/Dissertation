import os
import time
import csv

from lxml import etree

from etl.extract import dates

def parse_time(string, ssd, date):
    """
    Convert a Darwin time to a datetime by adding the date the file was written and the.

    It is never possible that we receive a message before the actual event. But Darwin messages can be delayed.

    We don't have to consider the case that ssd == timestamp BUT it should be that timestamp = ssd + 1.

    :param string: a time. Either HH:MM or HH:MM:SS
    :param date: a d
    :return:
    """

    if len(string) == 5:    # String is HH:MM format

        string += ":00"

    if ssd == date:     # Timestamp and SSD match up

        return ssd + " " + string

    if ssd < date:      # Timestamp is a day ahead

        if string > "12:00:00":  # It's late. Assume there's been an error. Use the SSD

            return ssd + " " + string

        else:                    # It's early morning, and so likely the day after

            return date + " " + string

def parse(ts, date):
    """
    Parse Darwin Forecast ElementTrees. Some TS elements contain multiple arr/dep/pass children, so return a list.

    :param ts: a Darwin Forecast ElementTree
    :param date: the date the message was sent
    :return: a movement dictionary
    """

    uid = ts.attrib["uid"]
    ssd = ts.attrib["ssd"]
    movements = []

    for child in ts:  # Either PlatformData, TSTimeData, or TSLocation

        if child.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}Location":  # If the CHILD tag has this, we're interested.

            for grandchild in child:

                if "at" in grandchild.attrib:

                    movement = {
                        "uid": uid,
                        "ssd": ssd,
                        "tiploc": child.attrib["tpl"],
                        "at": parse_time(grandchild.attrib["at"], ssd, date)
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

    return ssd, movements

def transform(start="2018-04-01", end="2019-04-01"):
    """
    Convert each day's XML messages into a CSV. Disregard trains that started before start and after end.
    If a train runs between two days, the service start date (ssd) is the file to which it is saved.

    Include the start but exclude the end.

    """

    in_dir = os.path.join("archive", "darwin")
    out_dir = os.path.join("data", "darwin")

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    files = dict()
    writers = dict()

    for file in os.listdir(in_dir):

        date = file[:10]
        in_path = os.path.join(in_dir, file)
        out_path = os.path.join(out_dir, date + ".csv")

        if date < start or date > end:

            print("Skipping {}...".format(in_path))

            continue

        cur = time.time()

        print("Parsing {} to {}...".format(in_path, out_path), end="")

        with open(in_path, "rb") as in_file:

            for line in in_file:

                try:

                    root = etree.fromstring(line)   # Read the XML into lxml

                    if "http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2" in root.nsmap.values():

                        ts = root.attrib['ts'][:10]

                        try:

                            ssd, movements = parse(root[0][0], ts)

                            if start <= ssd < end:  # The ssd is in range

                                if ssd not in files:

                                    files[ssd] = open(os.path.join(out_dir, ssd + ".csv"), "w", newline="")

                                    writers[ssd] = csv.DictWriter(files[ssd], ["uid", "ssd", "tiploc", "at", "type"])
                                    writers[ssd].writeheader()

                                writers[ssd].writerows(movements)

                            else:

                                pass

                        except ValueError as e:  # Why aren't there any key errors?

                            if str(e) != "No movements":

                                print(e)

                            pass

                except etree.XMLSyntaxError:  # Seem to be 'standalone' delay messages.

                    pass

        print(" DONE ({:.2f}s)".format(time.time() - cur))

    for file in files.values():

        file.close()

if __name__ == "__main__":

    transform()
