import requests
from io import BytesIO
from datetime import datetime, timedelta
from pathlib import Path
import time
import gzip
import tarfile
import os
from ftplib import FTP
from zipfile import ZipFile

def dates(start, end):
    """
    Returns a generator yielding two strings: a date url (YYYY/M/D), for downloading files, and a date path (YYYY-MM-DD)
    for writing files.

    :param start: A date in YYYY-MM-DD format.
    :param end:  A date in YYYY-MM-DD format.
    :return:
    """

    start = datetime.strptime(start, "%Y-%m-%d") + timedelta(days=-1)
    end = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=2)

    while start < end:

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

    headers = ['ob_time', 'id', 'id_type', 'met_domain_name', 'version_num', 'src_id', 'rec_st_ind',
               'wind_speed_unit_id', 'src_opr_type', 'wind_direction', 'wind_speed', 'prst_wx_id', 'past_wx_id_1',
               'past_wx_id_2', 'cld_ttl_amt_id', 'low_cld_type_id', 'med_cld_type_id', 'hi_cld_type_id',
               'cld_base_amt_id', 'cld_base_ht', 'visibility', 'msl_pressure', 'cld_amt_id_1', 'cloud_type_id_1',
               'cld_base_ht_id_1', 'cld_amt_id_2', 'cloud_type_id_2', 'cld_base_ht_id_2', 'cld_amt_id_3',
               'cloud_type_id_3', 'cld_base_ht_id_3', 'cld_amt_id_4', 'cloud_type_id_4', 'cld_base_ht_id_4',
               'vert_vsby', 'air_temperature', 'dewpoint', 'wetb_temp', 'stn_pres', 'alt_pres', 'ground_state_id',
               'q10mnt_mxgst_spd', 'cavok_flag', 'cs_hr_sun_dur', 'wmo_hr_sun_dur', 'wind_direction_q', 'wind_speed_q',
               'prst_wx_id_q', 'past_wx_id_1_q', 'past_wx_id_2_q', 'cld_ttl_amt_id_q', 'low_cld_type_id_q',
               'med_cld_type_id_q', 'hi_cld_type_id_q', 'cld_base_amt_id_q', 'cld_base_ht_q', 'visibility_q',
               'msl_pressure_q', 'air_temperature_q', 'dewpoint_q', 'wetb_temp_q', 'ground_state_id_q',
               'cld_amt_id_1_q', 'cloud_type_id_1_q', 'cld_base_ht_id_1_q', 'cld_amt_id_2_q', 'cloud_type_id_2_q',
               'cld_base_ht_id_2_q', 'cld_amt_id_3_q', 'cloud_type_id_3_q', 'cld_base_ht_id_3_q', 'cld_amt_id_4_q',
               'cloud_type_id_4_q', 'cld_base_ht_id_4_q', 'vert_vsby_q', 'stn_pres_q', 'alt_pres_q',
               'q10mnt_mxgst_spd_q', 'cs_hr_sun_dur_q', 'wmo_hr_sun_dur_q', 'meto_stmp_time', 'midas_stmp_etime',
               'wind_direction_j', 'wind_speed_j', 'prst_wx_id_j', 'past_wx_id_1_j', 'past_wx_id_2_j', 'cld_amt_id_j',
               'cld_ht_j', 'visibility_j', 'msl_pressure_j', 'air_temperature_j', 'dewpoint_j', 'wetb_temp_j',
               'vert_vsby_j', 'stn_pres_j', 'alt_pres_j', 'q10mnt_mxgst_spd_j', 'rltv_hum', 'rltv_hum_j', 'snow_depth',
               'snow_depth_q', 'drv_hr_sun_dur', 'drv_hr_sun_dur_q']

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

            with gzip.GzipFile(fileobj=fileobj) as file, open(path, mode="wb") as out:

                out.write(file.read())

            print("DONE ({:.2f}s)".format(time.time() - start))

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

    # Ah. I need to have an active account for that one.
    # Not worth the effort right now.

    # And we also need CORPUS.


def download(source, start, end):

    root = os.path.join("archive", source)

    Path(root).mkdir(parents=True, exist_ok=True)

    for date, filename in dates(start, end):

        movement(source, date, filename)

# weather("2018")


location()