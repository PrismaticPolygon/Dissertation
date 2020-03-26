import os

from etl.transform.weather import transform as weather
from etl.transform.location import transform as location
from etl.transform.schedule import transform as schedule
from etl.transform.movement import transform as movement

if __name__ == "__main__":

    if not os.path.exists("data"):

        os.mkdir("data")

    # print("\nWEATHER\n")
    #
    # weather("2018-04-01", "2019-03-30")
    #
    # print("\nLOCATION\n")
    #
    # location()
    #
    # print("\nSCHEDULE\n")
    #
    # schedule()

    print("\nMOVEMENT\n")

    movement("2018-04-01", "2018-05-22")
