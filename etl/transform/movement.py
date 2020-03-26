import os
import time
from lxml import etree
import csv


class MovementError(Exception):

    pass


def field(obj, key):

    if key in obj:

        return obj[key]

    return None


def parse_time(obj, key, date):

    if key in obj:

        _ = obj[key]

        if len(_) == 5:

            return date + " " + _ + ":00"

        else:

            return date + " " + _

    return None


class Movement:

    def __init__(self, ts, start, end, date):

        self.ssd = ts.attrib["ssd"]  # Service start date

        if self.ssd < start or self.ssd > end:

            raise MovementError("Not {} <= x <= {}".format(start, end))

        self.rid = ts.attrib["rid"]     # RTTI unique train ID
        self.uid = ts.attrib["uid"]     # Train UID
        # self.isReverseFormation = ts.attrib["isReverseFormation"] if "isReverseFormation" in ts.attrib else False

        # self.length = None      # The number of carriages in the train
        # self.lateReason = None  # The reason the train is late

        self.isMovement = False

        for child in ts:    # Either PlatformData, TSTimeData, or TSLocation

            # if child.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}LateReason":  # Always last if present
            #
            #     self.lateReason = child.text

            if child.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}Location":  # If the CHILD tag has these things, then we're interested.

                for grandchild in child:

                    if "at" in grandchild.attrib:   # Should always be the first one. But subsequent grandchild

                        self.isMovement = True
                        self.tiploc = child.attrib["tpl"]
                        # self.src = grandchild.attrib["src"]

                        # self.wta = parse_time(child.attrib, "wta", date)   # Working time of arrival
                        # self.wtd = parse_time(child.attrib, "wtd", date)   # Working time of departure
                        # self.pta = parse_time(child.attrib, "pta", date)   # Public time of arrival
                        # self.ptd = parse_time(child.attrib, "ptd", date)   # Public time of departure
                        # self.eta = parse_time(child.attrib, "eta", date)   # Estimated time of arrival
                        # self.etd = parse_time(child.attrib, "etd", date)   # Estimated time of departure
                        # self.wtp = parse_time(child.attrib, "wtp", date)   # Working time of pass
                        # self.delayed = child.attrib["delayed"] if "delayed" in child.attrib else False

                        # self.ata = None     # Actual time of arrival
                        # self.atd = None     # Actual time of departure
                        # self.atp = None     # Actual time of pass

                        # self.platSource = "P"       # Defaults to "P" (planned)
                        # self.platUp = False         # Defaults to False
                        # self.plat = None            # Platform number
                        # self.platConfirmed = False  # Whether the platform number is confirmed. Defaults to False
                        # self.suppressed = False     # Whether the service is suppressed for this location. Defaults to False
                        # self.detachFront = False    # Indicates from which end of the train stock will be detached. Defaults to False

                        if grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}arr":

                            self.type = "ARRIVAL"

                        elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}dep":

                            self.type = "DEPARTURE"

                        elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}pass":

                            self.type = "PASS"

                        self.at = parse_time(grandchild.attrib, "at", date)

                    # if self.isMovement is True:
                    #
                    #     if grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}length":
                    #
                    #         self.length = int(grandchild.text)
                    #
                    #     elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}plat":
                    #
                    #         self.platSource = field(grandchild.attrib, "platsrc")
                    #         self.platUp = field(grandchild.attrib, "platsup") == "true"
                    #         self.platConfirmed = field(grandchild.attrib, "conf") == "true"
                    #         self.plat = grandchild.text
                    #
                    #     elif grandchild.tag == "{http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2}suppr":
                    #
                    #         self.suppressed = grandchild.text == "true"

            if self.isMovement is True:

                break

        if self.isMovement is False:    # This means that we've never found a grandchild with an 'at' attribute.

            raise MovementError("Not a movement")

        del self.isMovement

    def __str__(self):

        return "Movement <{}>".format(self.uid)


def transform(start, end):
    """

    Convert each day's XML messages into a CSV. Disregard trains that started before start and after end.
    If a train runs between two days, the day it started is the file to which it is saved.

    At the start, a writer for 'today' is opened. For each new file, 'yesterday' is set to today, and 'today' is reset.
    In this way two writers are always open simultaneously. This ensures that data for trains that run overnight are
    captured in the correct file.

    :param start:
    :param end:
    :return:
    """

    in_dir = os.path.join("archive", "darwin")
    out_dir = os.path.join("data", "darwin")

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    yesterday = None
    yesterday_writer = None

    for file in os.listdir(in_dir):

        date = file[:10]
        in_path = os.path.join(in_dir, file)
        out_path = os.path.join(out_dir, date) + ".csv"

        if date < start or date > end or os.path.exists(in_path):

            print("Skipping {}...".format(in_path))

            continue

        today = open(out_path, "w", newline="")
        today_writer = csv.DictWriter(today, None)

        cur = time.time()

        print("Parsing {} to {}...".format(in_path, out_path), end="")

        with open(in_path, "rb") as in_file:

            for line in in_file:

                try:

                    root = etree.fromstring(line)   # Read the XML into lxml

                    for value in root.nsmap.values():   # Iterate through the namespace to find forecasts

                        if value == "http://www.thalesgroup.com/rtti/PushPort/Forecasts/v2":

                            try:

                                movement = Movement(root[0][0], start, end, date)

                                if movement.ssd < date:  # I.e. the service started yesterday

                                    if yesterday_writer.fieldnames is None:

                                        yesterday_writer.fieldnames = movement.__dict__.keys()
                                        yesterday_writer.writeheader()

                                    yesterday_writer.writerow(movement.__dict__)

                                else:

                                    if today_writer.fieldnames is None:

                                        today_writer.fieldnames = movement.__dict__.keys()
                                        today_writer.writeheader()

                                    today_writer.writerow(movement.__dict__)

                            except MovementError as e:

                                pass

                except etree.XMLSyntaxError as e:  # Seem to be 'standalone' delay messages.

                    pass

        print(" DONE ({:.2f}s)".format(time.time() - cur))

        if yesterday is not None:

            yesterday.close()

        yesterday = today
        yesterday_writer = today_writer
