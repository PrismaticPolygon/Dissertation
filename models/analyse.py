import os
import time

import pandas as pd
import numpy as np

from sklearn.experimental import enable_hist_gradient_boosting  # to use HistGradientBoosting models

# Metrics
from sklearn.metrics import classification_report, recall_score, average_precision_score

# Utils
from sklearn.model_selection import train_test_split
from joblib import load

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

from models.encoders import DatetimeEncoder


def raw(y_actual, y_hat):

    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for i in range(len(y_hat)):

        if y_actual[i] == y_hat[i] == 1:

            TP += 1

        if y_hat[i] == 1 and y_actual[i] != y_hat[i]:

            FP += 1

        if y_actual[i] == y_hat[i] == 0:

            TN += 1

        if y_hat[i] == 0 and y_actual[i] != y_hat[i]:

            FN += 1

    return {"TP": TP, "FP": FP, "TN": TN, "FN": FN}



def classification(model, X_test, Y_test):

    metrics = [
        recall_score,
        average_precision_score,
    ]

    Y_pred = model.predict(X_test)

    results = {
        "name": model.__class__.__name__,
        "score": model.score(X_test, Y_test)
    }

    results.update(raw(Y_test.values, Y_pred))

    for m in metrics:

        results[m.__name__] = m(Y_test.values, Y_pred)

    print(model.__class__.__name__ + "\n")
    print(results)
    print(classification_report(Y_test.values, Y_pred, target_names=["not delayed", "delayed"]))

    return results


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

    start = time.time()

    print("Loading data...", end="")

    df = pd.read_csv("data/dscm_w.csv",
                     index_col=["uid"],
                     parse_dates=["std", "sta", "atd", "ata"],
                     dtype=dtype)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print(df.info())

    path = os.path.join("models", "select")

    if not os.path.exists(path):
        os.mkdir(path)

    Y = df["delayed"]
    X = df.drop(["delay", "delayed", "atd", "ata", "origin", "destination"], axis=1)

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

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=1)

    root = os.path.join("models", "tune")

    for file in os.listdir(root):

        path = os.path.join(root, file)
        model = load(path)

        classification(model, X_test, Y_test)

# I barely remember how this is supposed to work now! Yeah, let's start the LaTeX.
if __name__ == "__main__":

    run()

# {'n_estimators': 200, 'min_samples_split': 10, 'min_samples_leaf': 2, 'max_features': 'sqrt', 'max_depth': 40, 'bootstrap': False}