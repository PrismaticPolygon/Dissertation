import pandas as pd

encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating"]

# This is going to get VERY meaty.


df = pd.read_csv("models/features/classification.csv", index_col="name")

accuracy = df["accuracy"]
df = df.div(df.sum(axis=1), axis=0)
df["accuracy"] = accuracy

for encode in ["status", "category", "power_type", "timing_load", "ATOC_code", "seating"]:

    df[encode] = 0
    columns = list(filter(lambda x: x[:len(encode)] == encode, df.columns))

    df[encode] = df[columns].sum(axis=1)