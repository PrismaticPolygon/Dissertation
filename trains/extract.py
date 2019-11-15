import os
import tarfile
import time

def extract():

    for file in os.listdir("archive"):

        date = file.split(".")[0]
        root = "extracted"

        if not os.path.exists(root):

            os.mkdir(root)

        out_dir = os.path.join(root, date)

        if not os.path.exists(out_dir):

            try:

                in_file = os.path.join("archive", file)

                print("Extracting " + in_file + " to " + out_dir + "... ", end="")

                with tarfile.open(in_file, mode="r:bz2") as tar:

                    start = time.time()

                    for member in tar.getmembers():

                        if member.isreg():

                            name, year, month, day, hour, minute = member.name.split("/")
                            member.path = hour.zfill(2) + minute.zfill(8)    # Minute also contains ".trust"

                            tar.extract(member, out_dir)

                    print(" DONE ({:.2f}s)".format(time.time() - start))

            except EOFError as e:

                print("\n" + str(e))

            except tarfile.ReadError as e:

                print(e)

        else:

            print("Skipping " + file)

    print("")