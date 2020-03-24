import os

from etl.transform.weather import transform as weather
from etl.transform.location import transform as location
from etl.transform.schedule import transform as schedule

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

    # print("\nLOCATION\n")
    #
    # df = location()
    #
    # print(df.head())
    #
    # df.to_csv(os.path.join("data", "location.csv"))

    print("\nSCHEDULE\n")

    path = os.path.join("data", "schedule")

    if not os.path.exists(path):

        os.mkdir(path)

    schedule()
