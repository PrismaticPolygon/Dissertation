import os
import eli5

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from joblib import load
from models.lib import *

def coefficients(model):

    def includes(_list):

        return any([isinstance(model, x) for x in _list])

    if includes([RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier,
                 RandomForestRegressor, GradientBoostingRegressor]):

        return model.feature_importances_

    if includes([LogisticRegression, SGDClassifier, RidgeClassifier]):

        return model.coef_[0]

    else:

        return model.coef_

# There's a library called ELI5 which does this for you!

def graph(model, X, print_ranking=False):

    _, c, indices = rank(model, X)
    num_features = X.shape[1]
    columns = [df.columns[i] for i in indices]

    if print_ranking:

        print("\nRanking\n")

    for i in range(num_features):

        if print_ranking:

            print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], c[indices[i]]))

    plt.figure()
    plt.title("{} importance".format(model.__class__.__name__))

    plt.bar(range(num_features), c[indices], color="r", align="center")

    plt.xticks(range(num_features), columns, rotation=90)
    plt.xlim([-1, num_features])
    plt.show()


def rank(model, X):

    c = np.abs(coefficients(model))     # Absolute coefficients
    indices = np.argsort(c)[::-1]       # The indices that would sort c in descending order
    num_features = X.shape[1]           # The number of features
    ranking = dict()

    for i in range(num_features):

        ranking[df.columns[indices[i]]] = c[indices[i]]

    return ranking, c, indices


# def decode(df):
#
#     accuracy = df["accuracy"]
#     df = df.div(df.sum(axis=1), axis=0)
#     df["accuracy"] = accuracy
#
#     for encode in ["status", "category", "power_type", "timing_load", "ATOC_code", "seating"]:
#
#         df[encode] = 0
#         columns = list(filter(lambda x: x[:len(encode)] == encode, df.columns))
#
#         df[encode] = df[columns].sum(axis=1)


# ANd we also want the other stuff too.
# https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-py
# https://github.com/scikit-learn/scikit-learn/issues/15132

# Cross-validation
# Up-sample

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

    for m in metrics:

        results[m.__name__] = m(Y_test.values, Y_pred)

    print(model.__class__.__name__ + "\n")
    print(results)
    print(classification_report(Y_test.values, Y_pred, target_names=["not delayed", "delayed"]))

    # eli5.show_weights(model, feature_names={i: k for i, k in enumerate(df.columns)}, target_names={0: "not delayed", 1: "delayed"})

    return results


def regression(model, X_test, Y_test):

    metrics = [
        mean_absolute_error,
        mean_squared_error
    ]

    Y_pred = model.predict(X_test)

    results = {
        "name": model.__class__.__name__,
        "score": model.score(X_test, Y_test)
    }

    for m in metrics:

        results[m.__name__] = m(Y_test.values, Y_pred)


    return results


def run():

    root = "models"

    for model_type in model_types:

        folder = os.path.join(root, model_type, arg())
        Y = df["delay"] if model_type == "regression" else df["delayed"]
        X = df.drop(["delay", "delayed"], axis=1)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

        for file in os.listdir(folder):

            path = os.path.join(folder, file)
            model = load(path)

            if model_type == "classification":

                classification(model, X_test, Y_test)

            else:

                regression(model, X_test, Y_test)

# I barely remember how this is supposed to work now! Yeah, let's start the LaTeX.
if __name__ == "__main__":

    run()
