import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin


class RailEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        catering = ["catering_" + c for c in ["C", "F", "H", "M", "R", "T"]]
        characteristics = ["characteristic_" + c for c in ["B", "C", "D", "E", "G", "M", "P", "Q", "R", "S", "Y", "Z"]]

        for c in characteristics:

            X[c] = X[c].map({1: c[-1], 0: ""})

        for c in catering:

            X[c] = X[c].map({1: c[-1], 0: ""})

        X["characteristics"] = X["characteristic_B"] + X["characteristic_C"] + X["characteristic_D"] + \
                               X["characteristic_E"] + X["characteristic_G"] + X["characteristic_M"] + \
                               X["characteristic_P"] + X["characteristic_Q"] + X["characteristic_R"] + \
                               X["characteristic_S"] + X["characteristic_Y"] + X["characteristic_Z"]

        X["catering"] = X["catering_C"] + X["catering_F"] + X["catering_H"] + X["catering_M"] + X["catering_R"] + \
                        X["catering_T"]

        X["characteristics"] = X["characteristics"].astype("category")
        X["catering"] = X["catering"].astype("category")

        return X.drop(characteristics + catering, axis=1)


class DatetimeEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, cyclical=False):

        self.cyclical = cyclical

    def encode(self, X, column, period):

        key = "{}_{}".format(column, period)  # Oh yeah.

        if not self.cyclical:

            dtype = "uint8" if period != "dayofyear" else "uint16"

            X[key] = X[column].dt.__getattribute__(period).astype(dtype)

        else:

            data = X[column].dt.__getattribute__(period)

            _ = 2 * np.pi * data / np.max(data)

            X[key + "_sin"] = np.sin(_)
            X[key + "_cos"] = np.cos(_)

        return X

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        columns = X.columns.values

        for column in X:

            for period in ["dayofyear", "month", "day", "dayofweek", "hour", "minute"]:

                X = self.encode(X, column, period)

        return X.drop(columns, axis=1)