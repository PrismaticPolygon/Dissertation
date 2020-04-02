import pandas as pd
import time

from random import sample

categories = ["D ", "TF", "X ", "A ", "B "]

df = pd.DataFrame({
    "category": ["      ", "D     ", "  TF  ", "X A B "],
    "UID": ["a", "b", "c", "d"]
})

# print(df.head())

# And the string is the row.
# We can add the null columns. And then expand them?
# Convert a string to a list, and then one-hot encode.

def one_hot(string):

    count = 6
    length = 2

    code = {k: 0 for k in categories}

    for i in range(0, count, length):

        chars = string[i:i + length]

        if chars in code:

            code[chars] = 1

    return {"category_" + k: v for k, v in code.items()}


start = time.time()

x = df["category"].map(one_hot).values

c = pd.DataFrame(x)

y = df.join(c)
y = y.drop("category", axis=1)

print(y)
print(len(y))

print("{.:2f}s".format(time.time() - start))
