import pandas as pd
import csv

# with open("data/darwinII/2018-04-01.csv") as f:
#
#     a = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

df = pd.DataFrame(a)


df = df.drop_duplicates(ignore_index=True)
df = df.sort_values(["uid", "at"])

# Keep only destination and origins. If they don't match, fuck it.

for uid, train in df.groupby("uid"):

    # train = train.sort_values("at")

    print(train)



# print(df)