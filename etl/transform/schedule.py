import os
import time
import csv

import pandas as pd

# See Appendix A of CIF USER SPEC v29 FINAL.
activities = [
    "A", "AE", "AX", "BL", "C", "D", "-D", "E", "G", "H", "HH", "K", "KC", "KE", "KF", "KS", "L", "N", "OP", "OR", "PR",
    "R", "RM", "RR", "S", "T", "-T", "TB", "TF", "TS", "TW", "U", "-U", "W", "X"
]


def parse_days_run(string):
    """
    Parse days_run. It is 7-character string. Each binary digit indicates whether the train runs on that day or not.

    :param string:
    :return:
    """
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    value = {
        "mon": 0,
        "tue": 0,
        "wed": 0,
        "thu": 0,
        "fri": 0,
        "sat": 0,
        "sun": 0
    }

    for i, digit in enumerate(string):

        if digit == "1":

            value[days[i]] = 1

    return value


def parse_characteristics(string):
    """
    Parse characteristics.

    See pg.40 of CIF USER SPEC v29 FINAL.

    :param string:
    :return:
    """

    characteristics = {
        "B": 0,     # Vacuum braked
        "C": 0,     # Timed at 100 m.p.h
        "D": 0,     # DOO (coaching stock trains)
        "E": 0,     # Conveys Mark 4 coaches
        "G": 0,     # Trainman (guard) requiored
        "M": 0,     # Timed at 110 m.p.h
        "P": 0,     # Push / pull train
        "Q": 0,     # Runs as required
        "R": 0,     # Air conditioned with PA system
        "S": 0,     # Steam heated
        "Y": 0,     # Runs to terminal / yards as required
        "Z": 0      # May convey traffic to SB1C gauge. Not to be diverted from booked route without authority.
    }

    for char in string:

        if char != " ":

            characteristics[char] = 1

    return {"characteristic_" + k: v for k, v in characteristics.items()}


def date(string):

    if string is None or string.strip() == '':

        return None

    else:

        year = int(string[0:2])

        if year > 59:

            year += 1900

        else:

            year += 2000

        return str(year) + "-" + string[2:4] + "-" + string[4:6]


def sleepers(char):
    """
    Permissible values are B (both), F (first class only), and S (standard class only). An empty string means no
    sleepers are available.

    :param char:
    :return: "B", "F", "S", or ""
    """

    return char.strip()


def bank_holiday(char):

    return 0 if char.strip() == "" else 1


def reservations(char):
    """
    Parse reservations. Permissible values are A (compulsory), E (essential for bikes), R (recommended), and S
    (possible from any station).
    :param char:
    :return: "A", "E", "R", "S", ""
    """

    return char.strip()


def headcode(string):

    return string.strip()


def identity(string):

    return string.strip()


def category(string):

    return string.strip()


def timing_load(string):
    """
    Parse timing load. Permissible values are numerous: 69, A, E, N, S, T, V, X, D1, D2, D3, AT, E, 0 - 999, 0, 506,
    1 - 9999, 325 (E).

    :param string:
    :return:
    """

    return string.strip()


def parse_catering(string):
    """
    Parse catering code. 4 characters. Two permissible. See pg. 39.
    :param string:
    :return:
    """

    codes = {
        "C": 0,     # Buffet service
        "F": 0,     # Restaurant service available for first class passengers
        "H": 0,     # Service of hot food available
        "M": 0,     # Meal included for first class passengers
        "R": 0,     # Restaurant
        "T": 0      # Trolley service
    }

    for char in string:

        if char != " ":

            codes[char] = 1

    return {"catering_" + k: v for k, v in codes.items()}


def branding(string):
    """
    Parse service branding. E if Eurostar, else blank.
    :param string:
    :return:
    """

    return string.strip()


def seating(char):
    """
    Parse seating class. Blank or B is first and standard. S is standard class only.
    :param char:
    :return: B (both) or S (standard)
    """

    return "B" if char.strip() == "" or char == "B" else "S"


def status(char):
    """
    See pg.41. Permissible values are B, F, P, S, T, 1, 2, 3.
    :param char:
    :return:
    """

    return char.strip()


def power_type(string):

    return string.strip()


def service_code(string):

    return string.strip()


def speed(string):

    if string.strip() == "":

        return ""

    return int(string)


def parse_bs(line):  # Basic schedule
    """
    Parse a basic schedule record. See pg.17 of CIF USER SPEC v29 FINAL.
    :param line:
    :return:
    """

    bs = {
        # "record_type": line[0:2],
        "transaction_type": line[2],
        "uid": line[3:9],
        "runs_from": date(line[9:15]),
        "runs_to": date(line[15:21]),
        # "days_run": line[21:28],
        "bank_holiday": bank_holiday(line[28]),
        "status": status(line[29]),
        "category": category(line[30:32]),
        "identity": identity(line[32:36]),
        "headcode": headcode(line[36:40]),
        # "course_indicator": line[40],                     # Not used to convey data, but 1 always populated
        "service_code": service_code(line[41:49]),
        # "portion_id": line[49],                           # Always blank
        "power_type": power_type(line[50:53]),
        "timing_load": timing_load(line[53:57]),
        "speed": speed(line[57:60]),
        # "characteristics": line[60:66],
        "seating": seating(line[66]),
        "sleepers": sleepers(line[67]),
        "reservations": reservations(line[68]),
        # "connection_indicator": line[69],                   # Not used
        # "catering": line[70:74],
        "branding": branding(line[74:78]),                    #
        "stp_indicator": line[79]
    }

    bs.update(parse_characteristics(line[60:66]))
    bs.update(parse_days_run(line[21:28]))
    bs.update(parse_catering(line[70:74]))

    bs["freight"] = 1 if bs["identity"] == "" else 0

    return bs


def parse_bx(line):     # Basic schedule extended

    return {
        # "record_type": line[:2],
        # "traction_class": line[2:6],    # Not used
        # "UIC_code": line[6:11],         # Used for services to/from Europe
        "ATOC_code": line[11:13],       # TOC codes (https://wiki.openraildata.com//index.php?title=TOC_Codes)
        "timetable_code": line[13]      # Y = subject to performance monitoring; N = not subject
    }



def full(date, filename):

    path = os.path.join("data", "schedule", date)

    if os.path.exists(path):

        # os.mkdir(path)

        print("Parsing " + filename + " to " + path + "...", end="")

        fields = {
            "metadata": [],
            "routes": []
        }

        start = time.time()

        files = {key: open(os.path.join(path, key + ".csv"), "w", newline="") for key in fields.keys()}
        writers = {key: csv.DictWriter(files[key], None) for key in fields.keys()}

        with open(filename) as file:

            bs = None

            for line in file:

                record_type = line[:2]

                if record_type == "BS":     # Basic schedule.

                    if bs is not None:  # Write to csv. This way both BS and BSX are written.

                        if writers["metadata"].fieldnames is None:

                            writers["metadata"].fieldnames = bs.keys()
                            writers["metadata"].writeheader()

                        writers["metadata"].writerow(bs)

                    bs = parse_bs(line)

                if record_type == "BX":     # Basic schedule extended.

                    bx = parse_bx(line)
                    bs.update(bx)

        for file in files.values():

            file.close()

        print(" DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}...".format(filename))

def transform():

    full("2018-03-30", "archive/schedule/2018-03-30-full.schedule")

    # for file in os.listdir(os.path.join("archive", "schedule")):
    #
    #     if file[11] == "f":



    # pass