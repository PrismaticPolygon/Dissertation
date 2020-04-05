# from collections import Counter
# from sklearn.datasets import make_classification
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import imblearn.pipeline.Pipeline as IPipeline

import pandas as pd
import numpy as np

# import matplotlib.pyplot as plt
# from numpy import where
#
# # define dataset
# X, y = make_classification(n_samples=10000, n_features=2, n_redundant=0, n_clusters_per_class=1, weights=[0.99], flip_y=0, random_state=1)
#
# # summarize class distribution
# counter = Counter(y)
# print(counter)
#
# # define pipeline
# over = SMOTE(sampling_strategy=0.1)
# under = RandomUnderSampler(sampling_strategy=0.5)
# steps = [('o', over), ('u', under)]
# pipeline = Pipeline(steps=steps)
#
# # transform the dataset
# X, y = pipeline.fit_resample(X, y)
#
# # summarize the new class distribution
# counter = Counter(y)
# print(counter)
#
# # scatter plot of examples by class label
# for label, _ in counter.items():
#     row_ix = where(y == label)[0]
#     plt.scatter(X[row_ix, 0], X[row_ix, 1], label=str(label))
#
# plt.legend()
# plt.show()

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression

class CyclicalEncoder(BaseEstimator, TransformerMixin):
    """Convert datetime columns to their cyclical representation"""

    @staticmethod
    def cyclical(column):

        _ = 2 * np.pi * column / np.max(column)

        return np.sin(_), np.cos(_)

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        columns = X.select_dtypes("datetime").columns

        for column in columns:

            for period in ["month", "day", "dayofweek", "hour", "minute"]:

                key = "{}_{}".format(column, period)

                X[[key + "_sin", key + "_cos"]] = X[column].dt[period].map(CyclicalEncoder.cyclical)

            X = X.drop(column, axis=1)

        return X

class DatetimeEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        columns = X.select_dtypes("datetime").columns

        for column in columns:

            for period in ["month", "day", "dayofweek", "hour", "minute"]:

                key = "{}_{}".format(column, period)

                X[key] = X[column].dt[period].astype("uint8")

            X = X.drop(column, axis=1)

        return X


# class DelayEncoder(BaseEstimator, TransformerMixin):
#
#     def __init__(self):
#
#         pass
#
#     def fit(self, X, y=None):
#
#         return self
#
#     def transform(self, X, y=None):
#
#         X["delay"] = (X["ata"] - X["arrival_time"]).map(lambda x: x.total_seconds()) / 60.0
#         X["delayed"] = X["delay"] > 5  # Delays are legally only more than 5 minutes
#
#         X = X[X["delay"] > -120]  # Filter out ridiculous values caused by day mismatch (yet to be debugged)
#
#         return X.drop(["departure_time", "arrival_time", "ata"], axis=1)





# add your data here
X_train, Y_train = [], []

# Resample pipeline
i_pipeline = IPipeline([
    ('over', SMOTE(sampling_strategy=0.1)),
    ('under', RandomUnderSampler(sampling_strategy=0.5))
])

X_train, Y_train = i_pipeline.fit_resample(X_train, Y_train)

# Training pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('onehot', OneHotEncoder()),    # One-hot encode categorical variables
    ("cylical", CyclicalEncoder()), # Cyclically encode datetime
    ('clf', LogisticRegression())
])

# 3-fold cross validation on the pipeline
scores = cross_val_score(pipeline, X_train, Y_train, cv=3, scoring='f1_micro')

# pipeline.fit(X_train,y_train)


