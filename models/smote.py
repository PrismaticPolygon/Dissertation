# from collections import Counter
# from sklearn.datasets import make_classification
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import imblearn.pipeline.Pipeline as IPipeline

import pandas as pd
import numpy as np


from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.linear_model import LogisticRegression


class DatetimeEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, cyclical=False):

        self.cyclical = cyclical

    @staticmethod
    def encode(column):

        _ = 2 * np.pi * column / np.max(column)

        return np.sin(_), np.cos(_)

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        columns = X.select_dtypes("datetime").columns   # [arrival_time, departure_time]

        for column in columns:

            for period in ["dayofyear", "month", "day", "dayofweek", "hour", "minute"]:

                key = "{}_{}".format(column, period)

                if self.cyclical:

                    X[[key + "_sin", key + "_cos"]] = X[column].dt[period].map(DatetimeEncoder.encode)

                else:

                    X[key] = X[column].dt[period].astype("uint8")

        X = X.drop(columns, axis=1)

        return X

# Might need a custom list encoder.

class ListOneHotEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        return X


# So we probably still want our split.
X, Y = [], []

#
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

# Resample pipeline
i_pipeline = IPipeline([
    ('over', SMOTE(sampling_strategy=0.1)),
    ('under', RandomUnderSampler(sampling_strategy=0.5))
])

X_train, Y_train = i_pipeline.fit_resample(X_train, Y_train)

# Use StandardScaler(with_mean=False) for sparse matrices.

# Training pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('onehot', OneHotEncoder()),    # One-hot encode categorical variables
    ("cylical", DatetimeEncoder(cyclical=False)), # Cyclically encode datetime
    ('clf', LogisticRegression())
])

# k-fold cross validation on the pipeline
scores = cross_val_score(pipeline, X_train, Y_train, cv=3, scoring='f1_micro')

# pipeline.fit(X_train,y_train)


