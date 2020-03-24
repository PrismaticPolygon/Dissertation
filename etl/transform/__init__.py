import os

from etl.transform.weather import transform as weather
from etl.transform.location import transform as location

if __name__ == "__main__":

    if not os.path.exists("data"):

        os.mkdir("data")

    # print("\nWEATHER\n")
    #
    # df = weather("2018-04-01", "2019-03-30")
    #
    # print(df.head())
    #
    # df.to_csv(os.path.join("data", "weather.csv"))

    print("\nLOCATION\n")

    df = location()

    print(df.head())

    df.to_csv(os.path.join("data", "location.csv"))

    # And these are the easy two, let's not forget!
