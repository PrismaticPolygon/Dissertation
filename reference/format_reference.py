import pandas as pd
import csv
from datetime import datetime
import json

def format_call_codes():

    # https://wiki.openraildata.com/index.php?title=Call_Code

    # Hours are easy to convert. But I can deal with that problem later.

    df = pd.read_csv("raw/call_codes.csv", index_col="Code")

    df.index.rename("code", inplace=True)

    def time(string):

        top = string[-4:]
        hours = int(top[:2])
        minutes = int(top[2:])

        return hours * 60 + minutes

    df['minutes'] = df['Departure time'].map(time)

    df.drop(labels="Departure time", inplace=True, axis=1)



def format_toc():

    # https://wiki.openraildata.com/index.php?title=TOC_Codes

    tocs = [{"code": "00", "name": "Unknown"}]

    with open("raw/toc.csv") as file:

        for row in csv.DictReader(file):

            if "Unmapped" not in row["Company name"] and \
                    "defunct" not in row["Company name"] and \
                    "?" not in row["Sector code"]:

                sector_code = row["Sector code"].zfill(2)

                tocs.append({"code": sector_code, "name": row["Company name"]})

    with open("formatted/toc.csv", "w", newline="") as file:

        writer = csv.writer(file)
        writer.writerow(["code", "name"])

        for toc in sorted(tocs, key=lambda x: x['code']):

            writer.writerow([toc["code"], toc["name"]])


def format_holidays():

    # https://www.dmo.gov.uk/media/15008/ukbankholidays.xls

    with open("raw/ukbankholidays.csv") as input:

        dates = [date[:-2] for date in input.readlines()][1:]

        dates = [datetime.strptime(date, "%d-%b-%Y").strftime("%Y-%m-%d") for date in dates]

        dates = [date for date in dates if "2018-04-01" <= date <= "2019-04-01"]

        with open("formatted/bank_holidays.json", "w") as output:

            json.dump(dates, output)


# format_call_codes()

with open('formatted/call_codes.csv', mode='r') as infile:

    reader = csv.reader(infile)

    mydict = dict()
    i = 0

    for row in reader:

        if i > 0:

            mydict[row[0]] = int(row[1])

        else:

            i += 1

    with open("call_codes.json", "w") as out:

        json.dump(mydict, out)