import requests
import time
import tarfile
import os
import json
import csv

from io import BytesIO
from datetime import datetime, timedelta
from ftplib import FTP
from zipfile import ZipFile
from gzip import GzipFile
from pykml import parser
from bs4 import BeautifulSoup

from config import *

ROOT = "archive"


def dates(start, end, pad=False, before=0, after=0):
    """
    Returns a generator yielding two strings: a date url (YYYY/xM/xD), for downloading files, and a date path
    (YYYY-MM-DD) for writing files.

    1 is subtracted from the start date; can't remember why.

    2 is added to the end date. This is to capture trains that started running on the end date but terminated (at most)
    2 days later.

    :param start: A date in YYYY-MM-DD format.
    :param before: how many days before to retrieve
    :param after: how many days after to retrieve
    :param end:  A date in YYYY-MM-DD format.
    :param pad: whether or not to zero-pad url dates
    :return:
    """

    start = datetime.strptime(start, "%Y-%m-%d") + timedelta(days=-before)
    end = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=after)

    while start < end:

        path = start.strftime("%Y-%m-%d")
        url = start.strftime("%Y/%m/%d") if pad else "{d.year}/{d.month}/{d.day}".format(d=start)

        yield url, path

        start += timedelta(days=1)  # increase day one by one


def generate_years(start, end):
    """
    Return a generator yielding the years between two dates
    :param start: A date in YYYY-MM-DD format.
    :param end:  A date in YYYY-MM-DD format.
    :return:
    """

    start = datetime.strptime(start, "%Y-%m-%d").year
    end = datetime.strptime(end, "%Y-%m-%d").year

    while start <= end:

        yield str(start)

        start += 1


def weather(year):
    """
    Download MIDAS weather data via FTP for a given year. Also get the CSV headers and write them to file.

    :param year: the year to download data for.
    :return: None
    """

    ftp = FTP("ftp.ceda.ac.uk")
    ftp.login(CEDA_USERNAME, CEDA_PASSWORD)
    ftp.set_pasv(False)
    ftp.cwd("badc/ukmo-midas/data/WH/yearly_files")

    folder = os.path.join("D:", ROOT, "weather")

    if not os.path.exists(folder):

        os.mkdir(folder)

    file = "midas_wxhrly_{}01-{}12.txt".format(year, year)
    path = os.path.join(folder, year + ".csv")

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

        print("Skipping {}/{}...".format(ftp.pwd(), file))


def schedule(date, filename):
    """
    Download SCHEDULE extracts from https://cdn.area51.onl/archive/rail/timetable/index.html. For each day, try to
    download both a full and schedule extract. 404s fail silently. Otherwise, write with the appropriate suffix.

    :param date: the date to use in the url
    :param filename: the date to use in the filename
    :return: None
    """

    for schedule_type in ["full", "update"]:

        url = "https://cdn.area51.onl/archive/rail/timetable/{}-{}.cif.gz".format(date, schedule_type)
        path = os.path.join("D:", ROOT, "schedule", "{}-{}.cif".format(filename, schedule_type))

        if not os.path.exists(path):

            start = time.time()

            headers = requests.head(url).headers

            if "x-amz-error-code" in headers:

                continue

            print("Downloading {} to {}... ".format(url, path), end="")

            response = requests.get(url)
            fileobj = BytesIO(response.content)

            try:

                with GzipFile(fileobj=fileobj) as file, open(path, mode="wb") as out:

                    out.write(file.read())

                print("DONE ({:.2f}s)".format(time.time() - start))

            except EOFError as e:

                print(e)

        else:

            print("Skipping " + url)


def movement(source, date, filename):
    """
    Download DARWIN or TRUST extracts from https://cdn.area51.onl/archive/rail/darwin/index.html or
    https://cdn.area51.onl/archive/rail/trust/index.html. Extract every minute message into one file.

    :param source: "darwin" or "trust"
    :param date: the date to use in the url
    :param filename: the date to use in the filename
    :return: None
    """

    url = "https://cdn.area51.onl/archive/rail/{}/{}.tbz2".format(source, date)
    path = os.path.join(ROOT, source, filename + "." + source)

    if not os.path.exists(path):

        start = time.time()

        print("Downloading {} to {}... ".format(url, path), end="")

        response = requests.get(url)
        # fileobj = BytesIO(response.content)

        with open(path, mode="wb") as out:

            out.write(response.content)
        #
        # with tarfile.open(fileobj=fileobj, mode="r:bz2") as tar, open(path, mode="wb") as out:
        #
        #     for member in tar.getmembers():
        #
        #         if member.isreg():
        #
        #             file = tar.extractfile(member)
        #
        #             out.write(file.read())

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}".format(url))


def ceda():
    """
    Download MIDAS station data from CEDA and parse the KMZ file into a CSV. Use the pykml parser for the KML file
    itself, and use BeautifulSoup for the 'description' field containing desirable metadata. "html5lib" must be used as
    the field has no closing tags.

    :return: None
    """

    path = os.path.join(ROOT, "midas.csv")
    url = "http://artefacts.ceda.ac.uk/midas/midas_stations_by_area.kmz"

    if not os.path.exists(path):

        start = time.time()

        print("Downloading {} to {}...".format(url, path), end="")

        response = requests.get(url)
        fileobj = BytesIO(response.content)

        with ZipFile(fileobj) as zipfile, open(path, "w", newline="") as out:

            writer = csv.DictWriter(out, fieldnames=None)

            string = zipfile.read(name="midas_stations_by_area.kml")
            root = parser.fromstring(string)

            for pm in root.findall(".//{http://earth.google.com/kml/2.1}Placemark"):

                station = {
                    "name": pm.Snippet
                }

                longitude, latitude, _ = pm.Point.coordinates.text.split(",")

                station["longitude"] = float(longitude)
                station["latitude"] = float(latitude)

                s = BeautifulSoup(pm.description.text, "html5lib")

                for row in s.find_all("tr"):

                    text = row.text.strip().split(":")

                    key = text[0].lower().replace(" ", "_")
                    value = ":".join(text[1:])

                    station[key] = value

                station["src_id"] = int(station["src_id"])

                if writer.fieldnames is None:

                    writer.fieldnames = station.keys()
                    writer.writeheader()

                writer.writerow(station)

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}".format(url))


def naptan():
    """
    Download the National Public Transport Access Node (NAPTAN) database. Only extract and save the railway nodes.

    :return: None
    """

    filename = "naptan.csv"
    url = "http://naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv"
    path = os.path.join(ROOT, filename)

    if not os.path.exists(path):

        start = time.time()

        print("Downloading {} to {}...".format(url, path), end="")

        response = requests.get(url)
        fileobj = BytesIO(response.content)

        with ZipFile(fileobj) as zipfile:

            info = zipfile.getinfo("RailReferences.csv")
            info.filename = filename

            zipfile.extract(info, ROOT)

        print("DONE ({:.2f}s)".format(time.time() - start))

    else:

        print("Skipping {}".format(url))


def corpus():
    """
    Download the Codes for Operations, Retail, & Planning - a Unified Solution (CORPUS) location reference data.
    Requires authentication. Not clear how it can be done programmatically, unfortunately. Downloaded from
    http://datafeeds.networkrail.co.uk/ntrod/SupportingFileAuthenticate?type=CORPUS

    :return: None
    """

    in_path = os.path.join("D:", ROOT, "CORPUSExtract.json.gz")
    out_path = os.path.join(ROOT, "corpus.csv")

    with GzipFile(in_path) as in_file, open(out_path, "w", newline="") as out_file:

        data = json.load(in_file)["TIPLOCDATA"]
        fieldnames = data[0].keys()

        writer = csv.DictWriter(out_file, fieldnames)
        writer.writeheader()

        for i in data:

            try:

                writer.writerow(i)

            except UnicodeEncodeError:

                pass


def extract(start, end):

    if not os.path.exists(ROOT):

        os.mkdir(ROOT)

    # Download DARWIN data
    print("\nDARWIN\n")

    for date, filename in dates(start, end, after=1):

        movement("darwin", date, filename)

    # # Download SCHEDULE data
    # print("\nSCHEDULE\n")
    #
    # for date, filename in dates(start, end, pad=True, before=2):
    #
    #     schedule(date, filename)

    # # Download weather data
    # print("\nMIDAS\n")
    #
    # for year in generate_years(start, end):
    #
    #     weather(year)

    # Download station data
    print("\nCEDA\n")
    ceda()

    # Download CORPUS data
    print("\nCORPUS\n")

    corpus()

    # Download NAPTAN data
    print("\nNAPTAN\n")

    naptan()
