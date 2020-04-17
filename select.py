import os
import time

import pandas as pd
import numpy as np

from sklearn.experimental import enable_hist_gradient_boosting  # to use HistGradientBoosting models

# Classifiers
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression, SGDClassifier, RidgeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, \
    HistGradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

# Utils
from sklearn.model_selection import train_test_split
from joblib import dump

# Preprocessing
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Resampling
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as IPipeline


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


classifiers = [
    GaussianNB(),
    LogisticRegression(),
    RidgeClassifier(),
    SGDClassifier(),
    RandomForestClassifier(),
    GradientBoostingClassifier(),
    HistGradientBoostingClassifier(),
    DecisionTreeClassifier(),
    GaussianNB(),
    MLPClassifier(),
    AdaBoostClassifier(),
    LinearSVC()
]

def train(model, path, X_train, Y_train):

    print("Fitting {}... ".format(model.__class__.__name__), end="")

    start = time.time()

    try:

        model.fit(X_train, Y_train)

        print("DONE ({:.2f}s)".format(time.time() - start))

        model_path = os.path.join(path, model.__class__.__name__ + ".pickle")

        with open(model_path, "wb") as file:

            dump(model, file)

    except ValueError as e: # Catch bad encoding errors

        print(e)

def run():

    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed', 'delayed']

    dtype = {key: "uint8" for key in dtype}

    dtype.update({
        "status": "category",
        "category": "category",
        "power_type": "category",
        "timing_load": "category",
        "seating": "category",
        "sleepers": "category",
        "reservations": "category",
        "ATOC_code": "category",
        "destination_stanox_area": "category",
        "origin_stanox_area": "category"
    })

    df = pd.read_csv("data/dscm_w.csv",
                     index_col=["uid"],
                     parse_dates=["std", "sta", "atd", "ata"],
                     dtype=dtype)

    path = os.path.join("models", "select")

    if not os.path.exists(path):

        os.mkdir(path)

    Y = df["delayed"]
    X = df.drop(["delay", "delayed", "atd", "ata"], axis=1)

    categorical_features = X.select_dtypes(include="category").columns.values
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))])

    datetime_features = X.select_dtypes(include="datetime").columns.values
    datetime_transformer = Pipeline([
        ("cyclical", DatetimeEncoder(cyclical=True))
    ])

    numeric_features = ["speed", "length", "duration"]
    numerical_transformer = Pipeline([
        ("scaler", StandardScaler())
    ])

    preprocessor = ColumnTransformer([
        ("categorical", categorical_transformer, categorical_features),
        ("datetime", datetime_transformer, datetime_features),
        ("numeric", numerical_transformer, numeric_features)
    ])

    resampler = IPipeline([
        ('over', SMOTE(sampling_strategy=0.1, random_state=1)),
        ('under', RandomUnderSampler(sampling_strategy=0.5, random_state=1)),
    ])

    X = preprocessor.fit_transform(X, Y)
    X, Y = resampler.fit_resample(X, Y)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

    for clf in classifiers:

        train(clf, path, X_train, Y_train)

if __name__ == "__main__":

    run()