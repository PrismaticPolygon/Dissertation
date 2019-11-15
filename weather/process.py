import pandas as pd
# Forecast fields

# Wind Gust (mph)
# Screen Relative Humidity
# Temperature (C)
# Visibility
# Wind direction (compass)
# Wind speed (mph)
# Max UV Index. Calculated from sun position, forecast cloud cover, and ozone amounts.
# Weather type
# Precipitation probability (%)

def knots_to_mph(wind):

    return wind * 1.15078

def metres_per_second_to_mph(wind):

    return wind * 2.23694

def q10mnt_mxgst_spd_to_mph(row):

    wind_gust = row["q10mnt_mxgst_spd"]
    unit = row["wind_speed_unit_id"]

    if unit == 4:

        knots_to_mph(wind_gust)

    return metres_per_second_to_mph(wind_gust)

def wind_speed(row):

    wind_speed = row["wind_speed"]
    unit = row["wind_speed_unit_id"]

    if unit == 4:

        knots_to_mph(wind_speed)

    return metres_per_second_to_mph(wind_speed)


def degrees_to_direction(degrees):

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

    i = int(((degrees + 11.25) % 360) / 22.5)

    return directions[i]

def automatic_to_code(prst_wx_id):

    map = {
        "00": 0,
        "01": 0,
        "02": 2,
        "03": 2,
        "04": 31,
        "05": 31,
        "06": 31,
        "07": 31,
        "08": 31,
        "09": 31,
        "10": 5,
        "11": 31,
        "12": 8,
        "13": 31,
        "14": 31,
        "15": 31,
        "16": 31,
        "17": 31,
        "18": 31,
        "19": 31,
        "20": 6,
        "21": 12,
        "22": 11,
        "23": 12,
        "24": 24,
        "25": 11,
        "26": 30,
        "27": 24,
        "28": 24,
        "29": 24,
        "30": 6,
        "31": 6,
        "32": 6,
        "33": 6,
        "34": 6,
        "35": 6,
        "36": 31,
        "37": 31,
        "38": 31,
        "39": 31,
        "40": 12,
        "41": 12,
        "42": 15,
        "43": 12,
        "44": 15,
        "45": 24,
        "46": 27,
        "47": 12,
        "48": 15,
        "49": 31,
        "50": 11,
        "51": 11,
        "52": 11,
        "53": 11,
        "54": 11,
        "55": 11,
        "56": 11,
        "57": 11,
        "58": 11,
        "59": 31,
        "60": 12,
        "61": 12,
        "62": 15,
        "63": 15,
        "64": 12,
        "65": 15,
        "66": 15,
        "67": 18,
        "68": 18,
        "69": 31,
        "70": 24,
        "71": 24,
        "72": 27,
        "73": 27,
        "74": 21,
        "75": 21,
        "76": 21,
        "77": 22,
        "78": 21,
        "79": 31,
        "80": 9,
        "81": 9,
        "82": 9,
        "83": 13,
        "84": 13,
        "85": 22,
        "86": 25,
        "87": 25,
        "88": 31,
        "89": 21,
        "90": 30,
        "91": 30,
        "92": 30,
        "93": 30,
        "94": 30,
        "95": 30,
        "96": 30,
        "97": 31,
        "98": 31,
        "99": 31
    }

    key = str(int(prst_wx_id)).zfill(2)

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

    return codes[int(map[key])]

def manual_to_code(prst_wx_id):

    map = {
        "00": 0,
        "01": 0,
        "02": 0,
        "03": 2,
        "04": 31,
        "05": 31,
        "06": 31,
        "07": 31,
        "08": 31,
        "09": 31,
        "10": 5,
        "11": 6,
        "12": 6,
        "13": 8,
        "14": 8,
        "15": 8,
        "16": 8,
        "17": 30,
        "18": 31,
        "19": 31,
        "20": 11,
        "21": 12,
        "22": 24,
        "23": 18,
        "24": 11,
        "25": 0,
        "26": 16,
        "27": 19,
        "28": 6,
        "29": 30,
        "30": 31,
        "31": 31,
        "32": 31,
        "33": 31,
        "34": 31,
        "35": 31,
        "36": 23,
        "37": 25,
        "38": 24,
        "39": 27,
        "40": 6,
        "41": 6,
        "42": 6,
        "43": 6,
        "44": 6,
        "45": 6,
        "46": 6,
        "47": 6,
        "48": 6,
        "49": 6,
        "50": 11,
        "51": 11,
        "52": 11,
        "53": 11,
        "54": 11,
        "55": 11,
        "56": 11,
        "57": 11,
        "58": 11,
        "59": 12,
        "60": 9,
        "61": 12,
        "62": 13,
        "63": 15,
        "64": 13,
        "65": 15,
        "66": 12,
        "67": 15,
        "68": 18,
        "69": 18,
        "70": 22,
        "71": 24,
        "72": 25,
        "73": 27,
        "74": 25,
        "75": 27,
        "76": 31,
        "77": 24,
        "78": 24,
        "79": 21,
        "80": 9,
        "81": 13,
        "82": 13,
        "83": 16,
        "84": 17,
        "85": 22,
        "86": 25,
        "87": 16,
        "88": 16,
        "89": 20,
        "90": 20,
        "91": 28,
        "92": 30,
        "93": 30,
        "94": 30,
        "95": 30,
        "96": 30,
        "97": 30,
        "98": 30,
        "99": 30
    }

    key = str(int(prst_wx_id)).zfill(2)

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

    return codes[int(map[key])]

def visibility_to_code(visibility):

    # 100 decameters is 1 kilometer

    if visibility < 100:
        return "VP" # Very poor

    elif visibility < 400:
        return "PO" # Poor

    elif visibility < 1000:
        return "MO" # Moderate

    elif visibility < 2000:
        return "GO" # Good

    elif visibility < 4000:
        return "VG" # Very good

    elif visibility >= 4000:
        return "EX" # Excellent


def convert_to_forecast_format(file):

    df = pd.read_csv("weather/{}".format(file),
                     parse_dates=[0],
                     usecols=["ob_time", "src_id", "wind_direction", "wind_speed", "q10mnt_mxgst_spd", "wind_speed_unit_id",
                              "air_temperature", "visibility", "rltv_hum", "src_opr_type", "prst_wx_id"],
                     na_values=" ",
                     index_col=["ob_time"])

    df = df.loc["2018-04-01":"2019-03-31"]
    df = df.reset_index(level=0)    # Return ob_time to a column
    df = df.set_index("src_id")

    # Assume that wind direction is fairly consistent (as it is in the UK: south-westerly). Convert to a compass direction.
    df["wind_direction"] = df["wind_direction"].fillna(df["wind_direction"].mean())
    df["wind_direction"] = df["wind_direction"].map(degrees_to_direction).astype("category")

    # Assume that " "s are 0s.
    df["wind_speed_unit_id"] = df["wind_speed_unit_id"].fillna(0)
    df["wind_speed_unit_id"] = df["wind_speed_unit_id"].astype("uint8")

    # Build a mask for knots.
    knots_mask = (df["wind_speed_unit_id"] == 4)

    # Add a temporary column
    df["wind_speed_mph"] = 0

    # Fill wind speed with the mean
    df["wind_speed"] = df["wind_speed"].fillna(df["wind_speed"].mean())

    # Convert wind speed in knots to mph and m/s to mph
    df.loc[knots_mask, "wind_speed_mph"] = df[knots_mask]["wind_speed"].map(knots_to_mph)
    df.loc[~knots_mask, "wind_speed_mph"] = df[~knots_mask]["wind_speed"].map(metres_per_second_to_mph)

    # Add a column
    df["wind_gust"] = 0

    # Convert gust speed in knots to mph and in m/s to mph
    df["q10mnt_mxgst_spd"] = df["q10mnt_mxgst_spd"].fillna(df["q10mnt_mxgst_spd"].mean())
    df.loc[knots_mask, "wind_gust"] = df[knots_mask]["q10mnt_mxgst_spd"].map(knots_to_mph)
    df.loc[~knots_mask, "wind_gust"] = df[~knots_mask]["q10mnt_mxgst_spd"].map(metres_per_second_to_mph)

    # Rename dummy column
    df = df.rename({"wind_speed_mph": "wind_speed"}, axis=1)

    # Create new temperature column
    df["temperature"] = df["air_temperature"].fillna(df["air_temperature"].mean())

    # Convert visibility to a category
    df["visibility"] = df["visibility"].fillna(df["visibility"].mean())
    df["visibility"] = df["visibility"].map(visibility_to_code).astype("category")

    # Create a new humidity column
    df["relative_humidity"] = df["rltv_hum"].fillna(df["rltv_hum"].mean())

    # Create a mask for manual measurements
    manual_mask = (df["src_opr_type"] <= 3)

    # Create an empty column for the weather type
    df["weather_type"] = ""

    # Fill observation codes with the most common (presumably some form of rain)
    df["prst_wx_id"] = df["prst_wx_id"].fillna(df["prst_wx_id"].median()).astype(int).astype(str)

    # Convert manual and automatic observations to their categories
    df.loc[manual_mask, "weather_type"] = df[manual_mask]["prst_wx_id"].map(manual_to_code).astype("category")
    df.loc[~manual_mask, "weather_type"] = df[~manual_mask]["prst_wx_id"].map(automatic_to_code).astype("category")

    # Drop superfluous columns
    return df.drop(["air_temperature", "src_opr_type", "prst_wx_id", "rltv_hum", "q10mnt_mxgst_spd", "wind_speed_unit_id"], axis=1)

def get_weather_df():

    df_2019 = convert_to_forecast_format("2019.csv")
    df_2018 = convert_to_forecast_format("2018.csv")

    return pd.concat([df_2018, df_2019])
