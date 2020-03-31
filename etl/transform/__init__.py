import os

from etl.transform.weather import transform as weather
from etl.transform.location import transform as location
from etl.transform.schedule import transform as schedule
from etl.transform.movement import transform as movement

ROOT = "D:/data"


def transform():

    if not os.path.exists(ROOT):

        os.mkdir(ROOT)

    # print("\nWEATHER\n")
    #
    # weather("2018-04-01", "2019-04-02")
    #
    # print("\nLOCATION\n")
    #
    # location()

    print("\nMOVEMENT\n")

    movement("2018-04-01", "2019-04-02")

    print("\nSCHEDULE\n")

    schedule()


if __name__ == "__main__":

    transform()
