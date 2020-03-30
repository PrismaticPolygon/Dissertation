import os
import time
import csv

import pandas as pd

from datetime import datetime, timedelta


def one_hot(name, string):
    """
    One-hot encode selected fields: activity, catering, and characteristic. These fields contain several values that
    must be split.

    :param name: the name of the field
    :param string: the string to encode
    :return: a one-hot dictionary
    """

    if name == "activity":

        length = 2
        count = 12
        code = {
            "A": 0,  # Stops or shunts for other trains to pass
            "AE": 0,  # Attach / detach assisting locomotive
            "AX": 0,  # Shows as 'X' on arrival
            "BL": 0,  # Stops for banking locomotive
            "C": 0,  # Stops to change trainmen
            "D": 0,  # Stops to set down passengers
            "-D": 0,  # Stops to detach vehicles
            "E": 0,  # Stops for examination
            "G": 0,  # National Rail Timetable data to add
            "H": 0,  # Notional activity to prevent WTT timing columns merge
            "HH": 0,  # As H, where a third column is involved
            "K": 0,  # Passenger count point
            "KC": 0,  # Ticket collection and examination point
            "KE": 0,  # Ticket examination point
            "KF": 0,  # Ticket examination point, 1st class only
            "KS": 0,  # Selective ticket examination point
            "L": 0,  # Stops to change locomotives
            "N": 0,  # Stops not advertised
            "OP": 0,  # Stops for other operating reasons
            "OR": 0,  # Train locomotive on rear
            "PR": 0,  # Propelling between points shown
            "R": 0,  # Stops when required
            "RM": 0,  # Reversing movement, or driver changes ends
            "RR": 0,  # Stops for locomotive to run around train
            "S": 0,  # Stops for railway personnel only
            "T": 0,  # Stops to take up and set down passengers
            "-T": 0,  # Stops to attach and detach vehicles
            "TB": 0,  # Train begins (origin)
            "TF": 0,  # Train finishes (destination)
            "TS": 0,  # Detail consist for TOPS direct
            "TW": 0,  # Stops (or at pass) for tablet, staff, or token
            "U": 0,  # Stops to take up passengers
            "-U": 0,  # Stops to attach vehicles
            "W": 0,  # Stops for watering of coaches
            "X": 0  # Passes another train at crossing point on single line
        }

    elif name == "catering":

        length = 1
        count = 4
        code = {
            "C": 0,  # Buffet service
            "F": 0,  # Restaurant service available for first class passengers
            "H": 0,  # Service of hot food available
            "M": 0,  # Meal included for first class passengers
            "R": 0,  # Restaurant
            "T": 0  # Trolley service
        }

    elif name == "characteristic":

        length = 1
        count = 6
        code = {
            "B": 0,  # Vacuum braked
            "C": 0,  # Timed at 100 m.p.h
            "D": 0,  # DOO (coaching stock trains)
            "E": 0,  # Conveys Mark 4 coaches
            "G": 0,  # Trainman (guard) required
            "M": 0,  # Timed at 110 m.p.h
            "P": 0,  # Push / pull train
            "Q": 0,  # Runs as required
            "R": 0,  # Air conditioned with PA system
            "S": 0,  # Steam heated
            "Y": 0,  # Runs to terminal / yards as required
            "Z": 0   # May convey traffic to SB1C gauge. Not to be diverted from booked route without authority.
        }

    else:

        raise ValueError("Unrecognised field {} for value {}".format(name, string))

    for i in range(0, count, length):

        chars = string[i:i + length]

        if chars in code:

            code[chars] = 1

    return {name + "_" + k: v for k, v in code.items()}


def parse_days_run(string):
    """
    Parse days_run. 7 characters. Each binary digit indicates whether the train runs on that day or not, with Monday at
    i = 0. See pg.18.

    :param string: the raw SCHEDULE characters
    :return: a Boolean dictionary.
    """
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    return {days[i]: int(digit) for i, digit in enumerate(string)}


def parse_allowance(string):
    """
    Parse allowance (engineering, pathing, or performance) in minutes. Two characters. Permissible values (MM:SS) are:

        H (00:30)
        1, 1H ... 9, 9H (01:00, 01:30 ... 09:00, 09:30)
        10, 11 ... 58, 59 (10:00, 11:00 ... 58:00, 59:00)

    See https://wiki.openraildata.com//index.php?title=Schedule_Records#Location_Records and pg. 40.

    :param string: raw SCHEDULE characters
    :return: float
    """

    if string is None or string.strip() == "":

        return None

    else:

        string = string.strip()

        if len(string) == 1:

            return 0.5 if string[0] == "H" else float(string[0])

        else:

            return float(string[0]) + 0.5 if string[1] == "H" else float(string)


def parse_date(string):
    """
    Parse date (date runs to, date runs from). 6 characters. YYMMDD. If YY > 59, the date refers to 19YY; otherwise, it
    refers to 20YY. See pg.17.

    :param string: raw SCHEDULE characters
    :return: YYYY-MM-DD
    """

    if string is None or string.strip() == '':

        return None

    else:

        year = ("19" if int(string[0:2]) > 59 else "20") + string[0:2]

        return year + "-" + string[2:4] + "-" + string[4:6]

# How can I know when it rolls over?
# Not very easily, I'll bet. Nope.
# It'll have to be manual.

def parse_time(string, date):
    """
    Parse time (scheduled departures, arrivals, and passes). 5 characters. HHMM with an optional 'H' for half-minute.

    :param string: raw SCHEDULE characters
    :return: HH:MM:SS
    """

    if string is None or string.strip() == '':

        return None

    else:

        hours = string[0:2]
        minutes = string[2:4]
        seconds = "00" if len(string) == 4 else "30"

        return hours + ":" + minutes + ":" + seconds


def suffix(char):
    """
    Parse TIPLOC suffix. The number of times that a TIPLOC appears in a schedule.
    :param char: raw SCHEDULE character
    :return: int
    """

    return 0 if char == " " else int(char)


def parse_lo(line, bs, date):
    """
    Parse an origin location (LO). See pg. 20. LOs have no sta or stp. A LO always has an activity code of TB
    (train begins), and possibly more.

    :param line: raw SCHEDULE characters
    :param line: the BS record containing metadata
    :return: dict
    """

    lo = {
        "type": "LO",
        "location": line[2:9].strip(),
        "suffix": suffix(line[9]),
        "sta": None,
        "std": parse_time(line[10:15], date),
        "stp": None,
        "pta": None,
        "pass": 0,
        "ptd": parse_time(line[15:19], date),
        "platform": line[19:22].strip(),
        "line": line[22:25].strip(),
        "path": None,
        "engineering_allowance": parse_allowance(line[25:27]),
        "pathing_allowance": parse_allowance(line[27:29]),
        "performance_allowance": parse_allowance(line[41:43])
    }

    lo.update(one_hot("activity", line[29:41]))

    lo["id"] = bs["id"]
    lo["runs_to"] = bs["runs_to"]

    bs["length"] += 1
    bs["origin"] = lo["location"]
    bs["departure_time"] = lo["std"]

    return lo


def parse_li(line, bs, date):
    """
    Parse an intermediate location (LI). See pg. 21. LIs must have either an sta and std or an stp. If std is populated,
    at least one activity will be present.

    :param line: raw SCHEDULE characters
    :return: dict
    """

    li = {
        "type": "LI",
        "location": line[2:9].strip(),
        "suffix": suffix(line[9]),
        "sta": parse_time(line[10:15], date),
        "std": parse_time(line[15:20], date),
        "stp": parse_time(line[20:25], date),
        "pta": parse_time(line[25:29], date),
        "ptd": parse_time(line[29:33], date),
        "platform": line[33:36].strip(),
        "line": line[36:39].strip(),
        "path": line[39:42].strip(),
        "engineering_allowance": parse_allowance(line[54:56]),
        "pathing_allowance": parse_allowance(line[56:58]),
        "performance_allowance": parse_allowance(line[58:60])
    }

    li.update(one_hot("activity", line[42:54]))
    li["pass"] = 0 if li["stp"] is None else 1

    li["id"] = bs["id"]
    li["runs_to"] = bs["runs_to"]

    bs["length"] += 1

    return li


def parse_lt(line, bs, date):
    """
    Parse a terminus location (LT). See pg. 23. An LT always has an activity of TF (train finish).

    :param line: raw SCHEDULE characters
    :return: dict
    """

    lt = {
        "type": "LT",
        "location": line[2:9].strip(),
        "suffix": suffix(line[9]),
        "sta": parse_time(line[10:15], date),
        "std": None,
        "stp": None,
        "pta": parse_time(line[15:19], date),
        "pass": 0,
        "ptd": None,
        "platform": line[19:22].strip(),
        "line": None,
        "path": line[22:25].strip(),
        "engineering_allowance": None,
        "pathing_allowance": None,
        "performance_allowance": None
    }

    lt.update(one_hot("activity", line[25:37]))

    lt["id"] = bs["id"]
    lt["runs_to"] = bs["runs_to"]

    bs["length"] += 1
    bs["destination"] = lt["location"]

    # if lt["sta"] < bs["departure_time"]:    # We've rolled over into the next day. Increment sta.
    #
    #     fmt = "%Y-%m-%d %H:%M:%S"
    #
    #     lt["sta"] = (datetime.strptime(lt["sta"], fmt) + timedelta(days=1)).strftime(fmt)

    bs["arrival_time"] = lt["sta"]

    return lt


def bank_holiday_running(char):
    """
    Parse whether or not the train runs on certain types of bank holidays. 1 character. Permissible values are
    X (bank holiday Mondays), E (Edinburgh holidays), G (Glasgow holidays). A value of 1 indicates that the train
    does run on bank holidays.

    :param char:
    :return: 1 if the train runs on bank holidays
    """

    if char in ["X", "E", "G"]:

        return 0

    return 1


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


def speed(string):
    """
    Parse speed. If an empty string, return nan; otherwise, convert.
    :param string:
    :return: int or ""
    """

    if string.strip() == "":

        return float("nan")

    return float(string)


def parse_bs(line):
    """
    Parse a basic schedule record. See pg.17 of CIF USER SPEC v29 FINAL. The majority of fields can simply be stripped
    with no loss of information. Trust yourself on this, Dom.
    :param line:
    :return:
    """

    bs = {
        "transaction_type": line[2],
        "uid": line[3:9],
        "runs_from": parse_date(line[9:15]),
        "runs_to": parse_date(line[15:21]),
        "bank_holiday_running": bank_holiday_running(line[28]),
        "status": status(line[29]),
        "category": line[30:32].strip(),
        "identity": line[32:36].strip(),
        "headcode": line[36:40].strip(),
        "service_code": line[41:49].strip(),
        "power_type": line[50:53].strip(),
        "timing_load": line[53:57].strip(),
        "speed": speed(line[57:60]),
        "seating": seating(line[66]),
        "sleepers": line[67].strip(),
        "reservations": line[68].strip(),
        "branding": line[74:78].strip(),
        "stp_indicator": line[79]
    }

    bs["id"] = bs["uid"] + "_" + bs["runs_from"] + "_" + bs["stp_indicator"]

    if bs["transaction_type"] == "D":

        return bs

    bs.update(one_hot("characteristic", line[60:66]))
    bs.update(one_hot("catering", line[70:74]))

    bs.update(parse_days_run(line[21:28]))

    bs["freight"] = 1 if bs["identity"] == "" else 0

    bs["length"] = 0
    bs["origin"] = None
    bs["departure_time"] = None
    bs["destination"] = None
    bs["arrival_time"] = None

    return bs


def parse_bx(line, bs):
    """
    Parse a basic schedule extended record.
    :param line:
    :return:
    """

    bx = {
        # "transaction_type": line[:2],
        # "traction_class": line[2:6],    # Not used
        # "UIC_code": line[6:11],         # Used for services to/from Europe
        "ATOC_code": line[11:13],       # TOC codes (https://wiki.openraildata.com//index.php?title=TOC_Codes)
        "timetable_code": line[13]      # Y = subject to performance monitoring; N = not subject
    }

    bs.update(bx)


# Okay. I need to simply store the date. And as I don't care about routes, for good...

def full(date, filename):
    """
    Parse a full CIF file. Write two CSVs to the date directory, one for metadata and the other for the routes
    themselves.

    :param date:
    :param filename:
    :return:
    """

    path = os.path.join("data", "schedule", date)

    if not os.path.exists(path):

        os.mkdir(path)

        print("Parsing " + filename + " to " + path + "...", end="")

        fields = {
            "metadata": None,
            # "routes": None,
        }

        start = time.time()

        files = {key: open(os.path.join(path, key + ".csv"), "w", newline="") for key in fields.keys()}
        writers = {key: csv.DictWriter(files[key], None) for key in fields.keys()}

        with open(filename) as file:

            bs = None

            for line in file:

                record_type = line[:2]

                if record_type == "BS":     # Basic schedule.

                    if bs is not None:  # Write to csv. This way both BS and BSX are written. Write the old BS.

                        if writers["metadata"].fieldnames is None:

                            writers["metadata"].fieldnames = bs.keys()
                            writers["metadata"].writeheader()

                        writers["metadata"].writerow(bs)

                    bs = parse_bs(line)

                if record_type == "BX":     # Basic schedule extended

                    parse_bx(line, bs)

                elif record_type == "LO":  # Origin

                    lo = parse_lo(line, bs, date)
                    #
                    # if writers["routes"].fieldnames is None:
                    #
                    #     writers["routes"].fieldnames = lo.keys()
                    #     writers["routes"].writeheader()
                    #
                    # writers["routes"].writerow(lo)

                elif record_type == "LI":  # Intermediate location

                    li = parse_li(line, bs, date)
                    #
                    # writers["routes"].writerow(li)

                elif record_type == "LT":  # Terminating point

                    lt = parse_lt(line, bs, date)
                    #
                    # writers["routes"].writerow(lt)

        for file in files.values():

            file.close()

        print(" DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}...".format(filename))

    return {
        # "routes": pd.read_csv(os.path.join(path, "routes.csv"), index_col="id", parse_dates=True),
        "metadata": pd.read_csv(os.path.join(path, "metadata.csv"), index_col="id", parse_dates=True)
    }


def update(db, date, filename):
    """
    Apply an update CIF to the current DB. Updates always consist of the BS (and possibly the BX) to identify
    the schedule, followed by the changes to the route. Pay special attention to dates. If the putative destination_time
    is smaller than the origin_time (in BS), increment the day by one. Don't bother with LIs, as we aren't using them,
    and doing so would require some clever refactoring.

    :param db:
    :param filename:
    :return:
    """

    changes = {
        "metadata": {"N": [], "R": [], "D": []},
        # "routes": {"N": [], "R": [], "D": []}
    }

    with open(filename) as update:

        print("Parsing {}... \n".format(filename))

        bs = None
        transaction_type = None

        for line in update:

            record_type = line[:2]

            if record_type == "BS":

                transaction_type = line[2]
                bs = parse_bs(line)

                if transaction_type == "D":  # Delete

                    for key in changes.keys():

                        if bs["id"] in db[key].index:

                            changes[key]["D"].append(bs["id"])

                else:

                    changes["metadata"][transaction_type].append(bs)

            if record_type == "BX":

                parse_bx(line, bs)

            elif record_type == "LO":

                lo = parse_lo(line, bs, date)

                # changes["routes"][transaction_type].append(lo)

            elif record_type == "LI":

                li = parse_li(line, bs, date)

                # changes["routes"][transaction_type].append(li)

            elif record_type == "LT":

                lt = parse_lt(line, bs, date)

                # changes["routes"][transaction_type].append(lt)

    for key, value in changes.items():

        df = db[key]

        for transaction_type, _list in value.items():

            start = time.time()

            if transaction_type == "N":

                print("Creating {} records in {}...".format(len(_list), key), end="")

                df = df.append(_list, sort=False)

            elif transaction_type == "R":

                print("Revising {} records in {}...".format(len(_list), key), end="")

                df.update(pd.DataFrame(_list))

            elif transaction_type == "D":

                prev = len(df)

                df = df.drop(_list)

                print("Deleting {} records ({} IDs) from {}...".format(prev - len(df), len(_list), key), end="")

            print(" DONE ({:.2f}s)".format(time.time() - start))

    print("\nRemoving schedules with runs_to < {}...\n".format(date))

    for key, old in db.items():

        start = time.time()

        mask = old["runs_to"] > date

        ids = old.index[~mask].unique()

        db[key] = old.loc[mask]

        print("Deleted {} records ({} IDs) from {}...".format(len(old) - len(db[key]), len(ids), key), end="")

        print(" DONE ({:.2f}s)".format(time.time() - start))


def write(db, date, out_dir):
    """

    Write a single day's schedule to CSV.

    :param db:
    :param date:
    :param out_dir:
    :return:
    """

    path = os.path.join(out_dir, date + ".csv")
    fmt = "%Y-%m-%d"
    metadata = db["metadata"]

    start = time.time()

    print("\nWriting metadata for " + date + " to " + path + "...", end="")

    df = metadata.loc[metadata["runs_from"] <= date, :]     # All rows with date_runs_from <= 2018-04-15. Must be str

    date = datetime.strptime(date, "%Y-%m-%d")
    day = date.strftime("%a").lower()                       # mon, tue, wed, thu, fri, sat, sun

    df = df.loc[df[day] == 1, :]                            # All rows running on today

    df = df.sort_values(["uid", "stp_indicator"])           # Sort stp_indicator
    df = df.drop_duplicates(["uid", "stp_indicator"])       # Keep the rows with the lowest stp_indicator

    # If the arrival_time is smaller than the departure_time, prepend tomorrow's date. Otherwise, prepend today's date.

    mask = (df["arrival_time"] < df["departure_time"])

    df.loc[mask, "arrival_time"] = (date + timedelta(days=1)).strftime(fmt) + " " + df.loc[mask, "arrival_time"]
    df.loc[~mask, "arrival_time"] = date.strftime(fmt) + " " + df.loc[~mask, "arrival_time"]

    df["departure_time"] = date.strftime(fmt) + " " + df["departure_time"]    # Prepend today's date to the arrival time

    df.to_csv(path)

    print(" DONE ({:.2f}s) ({} records)\n".format(time.time() - start, len(df)))

# And the error is clearly here.
# And then it resets every week.
# This does actually make sense, frustratingly. We use the date that we wrote when we wrote the full,
# instead of today's date. There is a solution: fix the dates when writing it. It's not pleasant, though.

# It would be a lot faster without routes.


def transform():

    in_dir = os.path.join("archive", "schedule")
    out_dir = os.path.join("data", "schedule")

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    db = None

    for file in os.listdir(in_dir):

        date = file[:10]

        print(date + "\n")

        path = os.path.join(in_dir, file)

        if file[11:17] == "update":

            update(db, date, path)
            write(db, date, out_dir)

        else:   # A full file.

            db = full(date, path)


if __name__ == "__main__":

    transform()
