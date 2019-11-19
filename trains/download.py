from datetime import datetime, timedelta
import time
import requests
import os


def dates():

    start_date = "2018/4/1"
    stop_date = "2019/4/1"

    start = datetime.strptime(start_date, "%Y/%m/%d")
    stop = datetime.strptime(stop_date, "%Y/%m/%d")

    while start < stop:

        year = str(start.year)
        month = str(start.month)
        day = str(start.day)

        yield year + "/" + month + "/" + day, year + "-" + month.zfill(2) + "-" + day.zfill(2)

        start = start + timedelta(days=1)  # increase day one by one


def download():

    for date_url, date_path in dates():

        url = "https://cdn.area51.onl/archive/rail/trust/" + date_url + ".tbz2"

        if not os.path.exists("archive"):

            os.mkdir("archive")

        path = os.path.join("archive", date_path + ".tbz2")

        if not os.path.exists(path):

            start = time.time()

            print("Downloading " + url + " to " + path + "...", end="")

            req = requests.get(url, stream=True)

            with open(path, "wb") as fp:

                for chunk in req.iter_content(1024):

                    fp.write(chunk)

            print(" DONE ({:.2f}s)".format(time.time() - start))

        else:

            print("Skipping " + url)

    print("")