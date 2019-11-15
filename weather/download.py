from ftplib import FTP
import os
import time

def download():

    ftp = FTP("ftp.ceda.ac.uk")
    ftp.login("diplodocus", "55d^FNYPofyA")
    ftp.set_pasv(False)

    ftp.cwd("badc/ukmo-midas/data/WH/yearly_files")

    for year in ["2018", "2019"]:

        file = "midas_wxhrly_{}01-{}12.txt".format(year, year)
        path = os.path.join("weather", year + ".csv")

        print("Downloading {} to {}... ".format(ftp.pwd() + "/" + file, path), end="")

        start = time.time()

        with open(path, "wb") as fp, open("WH_Column_Headers.csv") as header_file:

            headers = header_file.read().replace(" ", "").lower() + "\n"

            fp.write(bytes(headers, "utf-8"))

            ftp.retrbinary("RETR {}".format(file), fp.write)

        print(" DONE ({:.2f}s)".format(time.time() - start))