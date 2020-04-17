import os
import time

import pandas as pd
import numpy as np

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import cross_val_score, train_test_split, RepeatedStratifiedKFold, RandomizedSearchCV

from sklearn.ensemble import RandomForestClassifier

class DatetimeEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, cyclical=False):

        self.cyclical = cyclical

    @staticmethod
    def encode(X, column):

        _ = 2 * np.pi * column / np.max(column)

        return np.sin(_), np.cos(_)

    def fit(self, X, y=None):

        return self

    # Fair enough if apply is faster.

    def transform(self, X, y=None):

        columns = X.select_dtypes(include="datetime").columns.values   # [arrival_time, departure_time, ata]

        for column in columns:

            for period in ["dayofyear", "month", "day", "dayofweek", "hour", "minute"]:

                key = "{}_{}".format(column, period)

                if self.cyclical:

                    X[key + "_sin"], X[key + "_cos"] = X[column].dt.__getattribute__(period).map(DatetimeEncoder.encode)

                else:

                    X[key] = X[column].dt.__getattribute__(period).astype("uint8")

        return X.drop(columns, axis=1)





def load():

    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed']

    dtype = {key: "uint8" for key in dtype}

    # Handle mixed DtypeWarning
    dtype["headcode"] = str
    dtype["sleepers"] = str
    dtype["branding"] = str

    df = pd.read_csv(os.path.join("data", "dscm.csv"), index_col=0,
                     parse_dates=["departure_time", "arrival_time", "ata", "atd"], dtype=dtype)

    # Drop useless fields
    df = df.drop(["id", "transaction_type", "runs_to", "runs_from", "identity", "headcode", "service_code",
                  "stp_indicator", "timetable_code", "atd", "sleepers", "reservations", "branding", "origin",
                  "destination", "tiploc_x", "tiploc_y"], axis=1)

    encodes = ["status", "category", "power_type", "timing_load", "ATOC_code", "seating", "origin_stanox_area",
               "destination_stanox_area"]

    for e in encodes:   # Convert strings to floats

        df[e] = df[e].astype("category").cat.codes

    Y = (df["ata"] - df["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0 > 5  # Delays are legally only more than 5 minutes

    return df.drop("ata", axis=1), Y

# But we DO need to correctly encode categorical variables. SO we're back to where we started: wrestling over the bloody data.
# That's fine. Let's do it.
# Okay. So that works,

start = time.time()

print("Loading dataset...", end="")

X, Y = load()

print(" DONE ({:.2f}s)".format(time.time() - start))
#
# encoder = DatetimeEncoder()
#
# Z = encoder.transform(X)
#
# print(Z.info())
#
start = time.time()

print("Splitting dataset...", end="")

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

print(" DONE ({:.2f}s)".format(time.time() - start))

clf = RandomForestClassifier(
    n_estimators=10,       # Number of trees in the forest
    criterion="gini",       # Function to measure the quality of a split.
    max_depth=None,         # Max depth of a tree. If none, nodes are expanded until all leaves are pure
    min_samples_split=2,    # Minimum number of samples required to split an internal node
    min_samples_leaf=1,     # Minimum number of samples required to be at a leaf node
    n_jobs=-1,              # Number of jobs to run in parallel. -1 means use all available processors.
    verbose=1
)

# We'll have to encode ourselves.

# Define pipeline
pipeline = Pipeline([
    ("datetime", DatetimeEncoder()), # Cyclically encode datetime
    # ('over', SMOTE(sampling_strategy=0.1, random_state=1)),
    # ('under', RandomUnderSampler(sampling_strategy=0.5, random_state=1)),
    ('clf', clf)
])

# Evaluate pipeline. Repeated stratified k-fold cross validation
cv = RepeatedStratifiedKFold(
    n_splits=6,
    n_repeats=2,
    random_state=1
)

params = {
    "n_estimators": [int(x) for x in np.linspace(start=100, stop=2000, num=10)],
    "max_features": ['auto', 'sqrt'],
    "max_depth": [int(x) for x in np.linspace(10, 110, num = 11)] + [None],
    "min_samples_split": [2, 5, 10, 50, 100],
    "min_samples_leaf": [1, 2, 4],
    "bootstrap": [True, False]
}

grid = RandomizedSearchCV(clf, params, cv=cv, n_iter=1, verbose=2, n_jobs=-1, random_state=1)
grid.fit(X_train, Y_train)

print(grid.best_params_)

# That's fine.
# Once this is running I'll start porting over my 'solution' stuff.
#
# rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
#
#
# scores = cross_val_score(pipeline, X_train, Y_train, scoring='roc_auc', cv=cv, n_jobs=3)

# print(scores)
#
# print('Mean ROC AUC: {:.3f}'.format(np.mean(scores)))


