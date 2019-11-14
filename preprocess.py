import pandas as pd

dtype = {
    "event_type": "category",    # Do we want to split it into arrival and departure delays?,
    "train_id": "object",
    "planned_timestamp": "object",  # Needs to be parsed first,
    "actual_timestamp": "object",
    "gbtt_timestamp": "object",
    "original_loc_timestamp": "object"
}

df = pd.read_csv("data/0003.csv", dtype=dtype)

def origin_stanox_area(trust_id):

    return int(trust_id[:2])

def tspeed(trust_id):

    tspeed = trust_id[6]

    # P = Passenger and Parcels in WTT
    # F = Freight trains in WTT
    # T = Trips and agreed pathways
    # S = Special Trains (Freight or Passenger)

    tspeed_map = {
        "M": "P", "N": "P", "O": "P", "C": "F", "D": "F", "E": "F", "F": "F", "G": "F", "A": "T", "B": "T", "H": "T",
        "I": "T", "J": "T", "K": "T", "L": "T", "P": "T", "Q": "T", "R": "T", "S": "T", "T": "T", "U": "T", "V": "T",
        "W": "T", "X": "T", "Y": "T", "Z": "T", "0": "S", "1": "S", "2": "S", "3": "S", "4": "S", "5": "S", "6": "S",
        "7": "S", "8": "S", "9": "S"
    }

    return tspeed_map[tspeed]

def origin_departure_time_minutes(trust_id):

    call_codes = {"0": 59, "1": 119, "2": 179, "3": 239, "4": 299, "5": 359, "6": 419, "A": 449, "B": 479, "C": 509,
                  "D": 539, "E": 569, "F": 599, "G": 629, "H": 659, "I": 689, "J": 719, "K": 749, "L": 779, "M": 809,
                  "N": 839, "O": 869, "P": 899, "Q": 929, "R": 959, "S": 989, "T": 1019, "U": 1049, "V": 1079,
                  "W": 1109, "X": 1139, "Y": 1199, "Z": 1259, "7": 1319, "8": 1379, "9": 1439}

    call_code = trust_id[7]

    return call_codes[call_code]

def delayed(variation_status):

    if variation_status == "LATE":

        return True

    return False

df["tspeed"] = df["train_id"].map(tspeed).astype("category")
df["origin_stanox_area"] = df["train_id"].map(origin_stanox_area)

# planned and actual have 3 extra zeros by default; gbtt and original_loc have 6
for timestamp in ["planned_timestamp", "actual_timestamp", "gbtt_timestamp", "original_loc_timestamp"]:

    df[timestamp] = pd.to_datetime(df[timestamp].map(str).map(lambda x: x[:10]), unit="s")

df["run_time"] = df["train_id"].map(origin_departure_time_minutes) - (df["actual_timestamp"].dt.hour * 60 + df["actual_timestamp"].dt.minute)

print(df.head())
print(df.info())
