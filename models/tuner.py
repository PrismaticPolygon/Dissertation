# https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74
import time
import os

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.utils import shuffle
from sklearn.metrics import average_precision_score, recall_score, classification_report

from imblearn.pipeline import Pipeline as IPipeline
from imblearn.under_sampling import RandomUnderSampler

from models.encoders import RailEncoder, DatetimeEncoder

from joblib import dump


# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
clf = RandomForestClassifier(
    n_estimators=10,        # Number of trees in the forest
    criterion="gini",       # Function to measure the quality of a split.
    max_depth=None,         # Max depth of a tree. If none, nodes are expanded until all leaves are pure
    min_samples_split=2,    # Minimum number of samples required to split an internal node
    min_samples_leaf=1,     # Minimum number of samples required to be at a leaf node
    n_jobs=-1,              # Number of jobs to run in parallel. -1 means use all available processors.
)

def load():

    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed', 'delayed']

    dtype = {key: "uint8" for key in dtype}

    categories = {
        "status": "category",
        "category": "category",
        "power_type": "category",
        "timing_load": "category",
        "seating": "category",
        "reservations": "category",
        "ATOC_code": "category",
        "destination_stanox_area": "category",
        "origin_stanox_area": "category"
    }

    dtype.update(categories)

    start = time.time()

    print("Loading data...", end="")

    df = pd.read_csv("data/dscm_w.csv",
                     index_col=["uid"],
                     parse_dates=["std", "sta", "atd", "ata"],
                     dtype=dtype)

    path = os.path.join("models", "select")

    if not os.path.exists(path):
        os.mkdir(path)

    Y = df["delayed"]
    X = df.drop(["delay", "delayed", "atd", "ata", "origin", "destination"], axis=1)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print(X.info())

    X = RailEncoder().transform(X)

    categorical_features = ["status", "category", "power_type", "timing_load", "seating", "reservations",
                            "characteristics", "catering", "ATOC_code", "origin_stanox_area", "destination_stanox_area"]

    for c in categorical_features:
        X[c] = X[c].cat.codes

    datetime_features = X.select_dtypes(include="datetime").columns.values
    datetime_transformer = Pipeline([
        ("cyclical", DatetimeEncoder(cyclical=True))
    ])

    preprocessor = ColumnTransformer([
        ("datetime", datetime_transformer, datetime_features),
    ], remainder="passthrough")

    resampler = IPipeline([
        # ('over', SMOTE(sampling_strategy=0.2, random_state=1)),                 # Increase minority to 20% of majority
        ('under', RandomUnderSampler(sampling_strategy=1.0, random_state=1)),  # Reduce majority to 50% of minority
    ])

    start = time.time()

    print("\nPreprocessing data...", end="")

    X = preprocessor.fit_transform(X, Y)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print(X.shape)

    print("\nResampling data...", end="")

    X, Y = resampler.fit_resample(X, Y)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print("{}, delayed: {}, not delayed: {}\n".format(X.shape, Y.sum(), len(Y) - Y.sum()))

    return X, Y

def tune():

    X, Y = load()

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=1, shuffle=True)

    params = {
        "n_estimators": [int(x) for x in np.linspace(start=10, stop=1000, num=10)],
        "max_features": ['auto', 'sqrt'],
        "max_depth": [int(x) for x in np.linspace(10, 110, num = 11)] + [None],
        "min_samples_split": [2, 5, 10, 50, 100],
        "min_samples_leaf": [1, 2, 4],
        "bootstrap": [True, False]
    }

    grid = RandomizedSearchCV(clf, params, cv=3, n_iter=300, verbose=2, n_jobs=-1, random_state=1)
    grid.fit(X_train, Y_train)

    print(grid.best_params_)

    best = grid.best_estimator_

    metrics = [
        recall_score,
        average_precision_score,
    ]

    Y_pred = best.predict(X_test)

    results = {
        "name": best.__class__.__name__,
        "score": best.score(X_test, Y_test)
    }

    for m in metrics:

        results[m.__name__] = m(Y_test.values, Y_pred)

    print(best.__class__.__name__ + "\n")
    print(results)
    print(classification_report(Y_test.values, Y_pred, target_names=["not delayed", "delayed"]))

    if not os.path.exists("models/tune"):

        os.mkdir("models/tune")

    model_path = os.path.join("models", "tune", best.__class__.__name__ + ".pickle")

    with open(model_path, "wb") as file:

        dump(best, file)

if __name__ == "__main__":

    tune()


