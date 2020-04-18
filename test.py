import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class RailEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        characteristics = ["char_" + c for c in ["A", "B", "C", "D"]]

        for characteristic in characteristics:

            X[characteristic] = X[characteristic].map({1: characteristic[-1], 0: ""})

            # Ah, right.
            # It's probably fastest manually.

        X["characteristics"] = X[characteristics].agg(str.__add__, axis=1)

        return X.drop(characteristics, axis=1)


df = pd.DataFrame({
    "char_A": [0, 1, 0],
    "char_B": [1, 1, 0],
    "char_C": [1, 0, 0],
    "char_D": [0, 0, 1]
})

encoder = RailEncoder()

Z = encoder.transform(df)

print(Z)