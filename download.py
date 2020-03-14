import requests
import time
import gzip
import tarfile
import os

from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
from ftplib import FTP
from zipfile import ZipFile


def dates(start, end, pad=False):
    """
    Returns a generator yielding two strings: a date url (YYYY/M/D), for downloading files, and a date path (YYYY-MM-DD)
    for writing files.

    :param start: A date in YYYY-MM-DD format.
    :param end:  A date in YYYY-MM-DD format.
    :param pad: whether or not to zero-pad url dates
    :return:
    """

    start = datetime.strptime(start, "%Y-%m-%d") + timedelta(days=-1)
    end = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=2)

    while start < end:

        if pad is True:

            yield start.strftime("%Y/%m/%d"), start.strftime("%Y-%m-%d")  # need to pad for dates

        else:

            yield "{d.year}/{d.month}/{d.day}".format(d=start), start.strftime("%Y-%m-%d")  # don't want zero-pad for url

        start += timedelta(days=1)  # increase day one by one


def weather(year):

    ftp = FTP("ftp.ceda.ac.uk")
    ftp.login("diplodocus", "55d^FNYPofyA")
    ftp.set_pasv(False)

    ftp.cwd("badc/ukmo-midas/data/WH/yearly_files")

    if not os.path.exists("archive/weather"):

        os.mkdir("archive/weather")

    file = "midas_wxhrly_{}01-{}12.txt".format(year, year)
    path = os.path.join("archive", "weather", year + ".csv")

    r = requests.get("https://artefacts.ceda.ac.uk/badc_datadocs/ukmo-midas/Headers/WH_Column_Headers.txt")
    headers = [x.strip().lower() for x in r.text.split(",")]

    if not os.path.exists(path):

        print("Downloading {}/{} to {}... ".format(ftp.pwd(), file, path), end="")

        start = time.time()

        with open(path, "wb") as out:

            out.write(bytes(",".join(headers) + "\n", "utf-8"))

            ftp.retrbinary("RETR {}".format(file), out.write)

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}...".format(ftp.pwd()))


def schedule(date, filename):

    """
    Download SCHEDULE extracts from https://cdn.area51.onl/archive/rail/timetable/index.html
    :param date:
    :param filename:
    :return:
    """

    for schedule_type in ["full", "update"]:

        url = "https://cdn.area51.onl/archive/rail/timetable/{}-{}.cif.gz".format(date, schedule_type)
        path = os.path.join("archive", "schedule", "{}-{}.schedule".format(filename, schedule_type))

        if not os.path.exists(path):

            start = time.time()

            headers = requests.head(url).headers

            if "x-amz-error-code" in headers:

                continue

            print("Downloading {} to {}... ".format(url, path), end="")

            response = requests.get(url)
            fileobj = BytesIO(response.content)

            try:

                with gzip.GzipFile(fileobj=fileobj) as file, open(path, mode="wb") as out:

                    out.write(file.read())

                print("DONE ({:.2f}s)".format(time.time() - start))

            except EOFError as e:

                print(e)

        else:

            print("Skipping " + url)


def movement(source, date, filename):

    url = "https://cdn.area51.onl/archive/rail/{}/{}.tbz2".format(source, date)
    path = os.path.join("archive", source, filename + "." + source)

    if not os.path.exists(path):

        start = time.time()

        print("Downloading {} to {}... ".format(url, path), end="")

        response = requests.get(url)
        fileobj = BytesIO(response.content)

        with tarfile.open(fileobj=fileobj, mode="r:bz2") as tar, open(path, mode="wb") as out:

            for member in tar.getmembers():

                if member.isreg():

                    file = tar.extractfile(member)

                    out.write(file.read())

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}".format(url))


def location():

    filename = "naptan.csv"
    url = "http://naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv"
    path = os.path.join("archive", filename)

    if not os.path.exists(path):

        start = time.time()

        print("Downloading {} to {}...".format(url, path), end="")

        response = requests.get(url)
        fileobj = BytesIO(response.content)

        with ZipFile(fileobj) as zipfile:

            info = zipfile.getinfo("RailReferences.csv")
            info.filename = filename

            zipfile.extract(info, "archive")

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}".format(url))


def download(type, start, end):

    root = os.path.join("archive", "schedule")

    Path(root).mkdir(parents=True, exist_ok=True)

    for date, filename in dates(start, end, pad=True):

        if type == "schedule":

            schedule(date, filename)


if __name__ == "__main__":

    download("schedule", "2017-01-01", "2020-01-01")
