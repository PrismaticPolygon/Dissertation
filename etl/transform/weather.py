import os

import pandas as pd

from etl.extract import generate_years


def knots_to_mph(wind):

    return int(wind * 1.15078)


def ms_to_mph(wind):

    return int(wind * 2.23694)


def degrees_to_direction(degrees):
    """
    Convert wind direction in degrees to a direction on a 16-point compass. A direction is 22.5 degrees wide.
    The first term (degrees + 11.25) % 360 is used to convert the band between 348.5 to >0, so that it can be correctly
    mapped to N.

    :param degrees: MIDAS wind direction in degrees
    :return: Datapoint wind direction in 16-point compass directions
    """

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

    i = int(((degrees + 11.25) % 360) / 22.5)

    return directions[i]


def automatic_observation_to_code(prst_wx_id):

    map = {
        0: 0,
        1: 0,
        2: 2,
        3: 2,
        4: 31,
        5: 31,
        6: 31,
        7: 31,
        8: 31,
        9: 31,
        10: 5,
        11: 31,
        12: 8,
        13: 31,
        14: 31,
        15: 31,
        16: 31,
        17: 31,
        18: 31,
        19: 31,
        20: 6,
        21: 12,
        22: 11,
        23: 12,
        24: 24,
        25: 11,
        26: 30,
        27: 24,
        28: 24,
        29: 24,
        30: 6,
        31: 6,
        32: 6,
        33: 6,
        34: 6,
        35: 6,
        36: 31,
        37: 31,
        38: 31,
        39: 31,
        40: 12,
        41: 12,
        42: 15,
        43: 12,
        44: 15,
        45: 24,
        46: 27,
        47: 12,
        48: 15,
        49: 31,
        50: 11,
        51: 11,
        52: 11,
        53: 11,
        54: 11,
        55: 11,
        56: 11,
        57: 11,
        58: 11,
        59: 31,
        60: 12,
        61: 12,
        62: 15,
        63: 15,
        64: 12,
        65: 15,
        66: 15,
        67: 18,
        68: 18,
        69: 31,
        70: 24,
        71: 24,
        72: 27,
        73: 27,
        74: 21,
        75: 21,
        76: 21,
        77: 22,
        78: 21,
        79: 31,
        80: 9,
        81: 9,
        82: 9,
        83: 13,
        84: 13,
        85: 22,
        86: 25,
        87: 25,
        88: 31,
        89: 21,
        90: 30,
        91: 30,
        92: 30,
        93: 30,
        94: 30,
        95: 30,
        96: 30,
        97: 31,
        98: 31,
        99: 31
    }

    codes = {
        0: "Clear",
        1: "Clear",
        2: "Partly cloudy",
        3: "Partly cloudy",
        4: "Not used",
        5: "Mist",
        6: "Fog",
        7: "Cloudy",
        8: "Overcast",
        9: "Light rain shower",
        10: "Light rain shower",
        11: "Drizzle",
        12: "Light rain",
        13: "Heavy rain shower",
        14: "Heavy rain shower",
        15: "Heavy rain",
        16: "Sleet shower",
        17: "Sleet shower",
        18: "Sleet",
        19: "Hail shower",
        20: "Hail shower",
        21: "Hail",
        22: "Light snow shower",
        23: "Light snow shower",
        24: "Light snow",
        25: "Heavy snow shower",
        26: "Heavy snow shower",
        27: "Heavy snow",
        28: "Thunder shower",
        29: "Thunder shower",
        30: "Thunder",
        31: "Unknown"
    }

    return codes[map[prst_wx_id]]


def manual_observation_to_code(prst_wx_id):

    map = {
        0: 0,
        1: 0,
        2: 0,
        3: 2,
        4: 31,
        5: 31,
        6: 31,
        7: 31,
        8: 31,
        9: 31,
        10: 5,
        11: 6,
        12: 6,
        13: 8,
        14: 8,
        15: 8,
        16: 8,
        17: 30,
        18: 31,
        19: 31,
        20: 11,
        21: 12,
        22: 24,
        23: 18,
        24: 11,
        25: 0,
        26: 16,
        27: 19,
        28: 6,
        29: 30,
        30: 31,
        31: 31,
        32: 31,
        33: 31,
        34: 31,
        35: 31,
        36: 23,
        37: 25,
        38: 24,
        39: 27,
        40: 6,
        41: 6,
        42: 6,
        43: 6,
        44: 6,
        45: 6,
        46: 6,
        47: 6,
        48: 6,
        49: 6,
        50: 11,
        51: 11,
        52: 11,
        53: 11,
        54: 11,
        55: 11,
        56: 11,
        57: 11,
        58: 11,
        59: 12,
        60: 9,
        61: 12,
        62: 13,
        63: 15,
        64: 13,
        65: 15,
        66: 12,
        67: 15,
        68: 18,
        69: 18,
        70: 22,
        71: 24,
        72: 25,
        73: 27,
        74: 25,
        75: 27,
        76: 31,
        77: 24,
        78: 24,
        79: 21,
        80: 9,
        81: 13,
        82: 13,
        83: 16,
        84: 17,
        85: 22,
        86: 25,
        87: 16,
        88: 16,
        89: 20,
        90: 20,
        91: 28,
        92: 30,
        93: 30,
        94: 30,
        95: 30,
        96: 30,
        97: 30,
        98: 30,
        99: 30
    }

    codes = {
        0: "Clear",
        1: "Clear",
        2: "Partly cloudy",
        3: "Partly cloudy",
        4: "Not used",
        5: "Mist",
        6: "Fog",
        7: "Cloudy",
        8: "Overcast",
        9: "Light rain shower",
        10: "Light rain shower",
        11: "Drizzle",
        12: "Light rain",
        13: "Heavy rain shower",
        14: "Heavy rain shower",
        15: "Heavy rain",
        16: "Sleet shower",
        17: "Sleet shower",
        18: "Sleet",
        19: "Hail shower",
        20: "Hail shower",
        21: "Hail",
        22: "Light snow shower",
        23: "Light snow shower",
        24: "Light snow",
        25: "Heavy snow shower",
        26: "Heavy snow shower",
        27: "Heavy snow",
        28: "Thunder shower",
        29: "Thunder shower",
        30: "Thunder",
        31: "Unknown"
    }

    return codes[map[prst_wx_id]]


def visibility_to_code(visibility):
    """

    :param visibility: MIDAS visibility in decametres. 100 decametres is 1 kilometre
    :return: a Datapoint visibility code
    """

    if visibility < 100:

        return "VP"  # Very poor

    elif visibility < 400:

        return "PO"  # Poor

    elif visibility < 1000:

        return "MO"  # Moderate

    elif visibility < 2000:

        return "GO"  # Good

    elif visibility < 4000:

        return "VG"  # Very good

    elif visibility >= 4000:

        return "EX"  # Excellent


def transform(start, end):

    # end = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=2)

    years = list(generate_years(start, end))
    dfs = []

    for i, year in enumerate(years):

        df = pd.read_csv("D:/archive/weather/{}.csv".format(year), parse_dates=[0],
                         usecols=["ob_time", "src_id", "wind_direction", "wind_speed", "q10mnt_mxgst_spd",
                                  "wind_speed_unit_id", "air_temperature", "visibility", "rltv_hum", "src_opr_type", "prst_wx_id"],
                         na_values=" ",
                         index_col=["ob_time"])

        if i == 0:  # Truncate all values before the start date

            df = df.loc[start:]

        elif i == len(years) - 1:   # Truncate all values after the end date

            df = df.loc[:end]

        df = df.reset_index()  # Reset ob_time to a column
        df = df.set_index("src_id")

        # Assume that wind direction is fairly consistent (south-westerly in the UK). Convert to compass direction.
        df["wind_direction"] = df["wind_direction"].fillna(df["wind_direction"].mean())
        df["wind_direction"] = df["wind_direction"].map(degrees_to_direction).astype("category")

        # Convert visibility
        df["visibility"] = df["visibility"].fillna(df["visibility"].mean())
        df["visibility"] = df["visibility"].map(visibility_to_code)

        # Build a mask for knots. Faster this way, as the same operation is performed twice using the mask.
        knots_mask = (df["wind_speed_unit_id"] == 4)

        # Add temporary columns for wind
        df["wind_speed_mph"] = 0

        # Fill wind speeds with the mean
        df["wind_speed"] = df["wind_speed"].fillna(df["wind_speed"].mean())
        df["q10mnt_mxgst_spd"] = df["q10mnt_mxgst_spd"].fillna(df["q10mnt_mxgst_spd"].mean())

        # Convert wind speed in knots to mph and m/s to mph
        df.loc[knots_mask, "wind_speed_mph"] = df[knots_mask]["wind_speed"].map(knots_to_mph)
        df.loc[~knots_mask, "wind_speed_mph"] = df[~knots_mask]["wind_speed"].map(ms_to_mph)

        df.loc[knots_mask, "q10mnt_mxgst_spd"] = df[knots_mask]["q10mnt_mxgst_spd"].map(knots_to_mph)
        df.loc[~knots_mask, "q10mnt_mxgst_spd"] = df[~knots_mask]["q10mnt_mxgst_spd"].map(ms_to_mph)

        # Drop columns and rename dummy
        df = df.drop(["wind_speed_unit_id", "q10mnt_mxgst_spd", "wind_speed"], axis=1)
        df = df.rename({"wind_speed_mph": "wind_speed", "q10mnt_mxgst_spd": "wind_gust"}, axis=1)

        # Fill new temperature column and rename
        df["air_temperature"] = df["air_temperature"].fillna(df["air_temperature"].mean()).astype("uint8")
        df = df.rename({"air_temperature": "temperature"}, axis=1)

        # Fill new humidity column and rename
        df["rltv_hum"] = df["rltv_hum"].fillna(df["rltv_hum"].mean())
        df = df.rename({"rltv_hum": "relative_humidity"}, axis=1)

        # Create a mask for manual measurements
        manual_mask = (df["src_opr_type"] <= 3)

        # Create an empty column for the weather type
        df["weather_type"] = ""

        # Ah, right. This is why. Fuck the weather for now. Let's do this.
        # Fill observation codes with the most common (presumably some form of rain) and convert to int
        df["prst_wx_id"] = df["prst_wx_id"].fillna(df["prst_wx_id"].median()).astype(int)

        # Convert manual and automatic observations to their categories
        df.loc[manual_mask, "weather_type"] = df[manual_mask]["prst_wx_id"].map(manual_observation_to_code).astype("category")
        df.loc[~manual_mask, "weather_type"] = df[~manual_mask]["prst_wx_id"].map(automatic_observation_to_code).astype("category")

        df = df.drop(["src_opr_type", "prst_wx_id"], axis=1)

        dfs.append(df)

    df = pd.concat(dfs)

    df.to_csv(os.path.join("D:", "data", "weather.csv"))
