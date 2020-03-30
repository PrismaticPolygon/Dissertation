import time
import os
import csv

import numpy as np
import matplotlib.pyplot as plt

from sklearn.experimental import enable_hist_gradient_boosting  # noqa. Required to using HistGradientBoost below.

# Classifiers
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, BayesianRidge, SGDClassifier, RidgeClassifier

# Regressors
from sklearn.svm import LinearSVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import SGDRegressor, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor

# Helpers
from sklearn.metrics import recall_score, average_precision_score, mean_squared_error, mean_absolute_error, \
    classification_report
from sklearn.model_selection import train_test_split
from joblib import dump, load   # More efficient than pickle for objects with large internal NumPy arrays

from models.preprocess import preprocess

regressors = [
    RandomForestRegressor(),            # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
    GradientBoostingRegressor(),        # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html
    # HistGradientBoostingRegressor(),    # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html
    Ridge(),                            # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html
    # KernelRidge(),                      # https://scikit-learn.org/stable/modules/generated/sklearn.kernel_ridge.KernelRidge.html
    SGDRegressor(),                     # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDRegressor.html
    LinearSVR(),                        # https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVR.html
    BayesianRidge(),
]

classifiers = [
    LogisticRegression(),
    RidgeClassifier(),
    SGDClassifier(),
    RandomForestClassifier(),
    GradientBoostingClassifier(),
    # HistGradientBoostingClassifier(),
    # LinearSVC()
]


def pad(_, x):
    # https://stackoverflow.com/questions/4008546/how-to-pad-with-n-characters-in-python

    length = max([len(y) for y in _])

    return "{s:{c}^{n}}".format(s=" " + x.upper() + " ", n=length + 6, c="*")


def train(model, X_train, Y_train):

    print("Fitting {}... ".format(model.__class__.__name__), end="")

    start = time.time()

    model.fit(X_train, Y_train)

    print("DONE ({:.2f}s)".format(time.time() - start))

    model_path = os.path.join("models", "pickles", model.__class__.__name__ + ".pickle")

    with open(model_path, "wb") as file:

        dump(model, file)


def coefficients(model):

    if isinstance(model, RandomForestClassifier):

        return model.feature_importances_

    elif isinstance(model, GradientBoostingClassifier):

        return model.feature_importances_

    elif isinstance(model, HistGradientBoostingClassifier):

        return model.feature_importances_

    elif isinstance(model, LogisticRegression):

        return model.coef_[0]

    elif isinstance(model, BayesianRidge):

        return model.coef_

    elif isinstance(model, SGDClassifier):

        return model.coef_[0]

    elif isinstance(model, RidgeClassifier):

        return model.coef_[0]

    elif isinstance(model, RandomForestRegressor):

        return model.feature_importances_

    elif isinstance(model, GradientBoostingRegressor):

        return model.feature_importances_

    elif isinstance(model, Ridge):

        return model.coef_

    elif isinstance(model, KernelRidge):

        return None

    elif isinstance(model, LinearSVR):

        return model.coef_

    elif isinstance(model, SGDRegressor):

        return model.coef_


def rank(model, X, df):

    c = np.abs(coefficients(model))     # Absolute coefficients
    indices = np.argsort(c)[::-1]       # The indices that would sort c in descending order
    num_features = X.shape[1]           # The number of features
    ranking = dict()

    for i in range(num_features):

        ranking[df.columns[indices[i]]] = c[indices[i]]

    return ranking, c, indices


# def graph(model, print_ranking=False):
#
#     _, c, indices = rank(model)
#     num_features = X.shape[1]
#     columns = [df.columns[i] for i in indices]
#
#     if print_ranking:
#
#         print("\nRanking\n")
#
#     for i in range(num_features):
#
#         if print_ranking:
#
#             print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], c[indices[i]]))
#
#     plt.figure()
#     plt.title("{} importance".format(model.__class__.__name__))
#
#     plt.bar(range(num_features), c[indices], color="r", align="center")
#
#     plt.xticks(range(num_features), columns, rotation=90)
#     plt.xlim([-1, num_features])
#     plt.show()

# https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-py
# https://github.com/scikit-learn/scikit-learn/issues/15132

# Cross-validation
# Up-sample


def test(model_type, models, X, df, X_test, Y_test):

    path = os.path.join("models", "features", model_type + ".csv")

    if model_type == "classification":

        metrics = [
            recall_score,
            average_precision_score,
        ]

    else:

        metrics = [
            mean_absolute_error,
            mean_squared_error
        ]

    with open(path, "w", newline="") as out:

        writer = csv.DictWriter(out, None)

        for model in models:

            Y_pred = model.predict(X_test)

            results = {
                "accuracy": model.score(X_test, Y_test)
            }

            ranking, _, _ = rank(model, X, df)
            ranking["name"] = model.__class__.__name__

            for m in metrics:

                results[m.__name__] = m(Y_test.values, Y_pred)

            if model_type == "classification":

                print(model.__class__.__name__ + "\n")
                print(classification_report(Y_test.values, Y_pred, target_names=["not delayed", "delayed"]))

            else:

                print(model.__class__.__name__, results)

            ranking.update(results)

            if writer.fieldnames is None:

                writer.fieldnames = ranking.keys()
                writer.writeheader()

            writer.writerow(ranking)

def run():

    df = preprocess()
    model_types = ["classification", "regression"]

    for model_type in model_types:

        print("\n" + pad(model_types, model_type) + "\n")

        models = regressors if model_type == "regression" else classifiers
        Y = df["delay"] if model_type == "regression" else df["delayed"]
        X = df.drop(["delay", "delayed"], axis=1)

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

        for model in models:

            train(model, X_train, Y_train)

        print("")

        test(model_type, models, X, df, X_test, Y_test)


if __name__ == "__main__":

    run()