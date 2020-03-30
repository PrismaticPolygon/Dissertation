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
]

classifiers = [
    LogisticRegression(),
    BayesianRidge(),
    RidgeClassifier(),
    SGDClassifier(),
    RandomForestClassifier(),
    GradientBoostingClassifier(),
    # HistGradientBoostingClassifier(),
    # LinearSVC()
]


def pad(_, x):
    # https://stackoverflow.com/questions/4008546/how-to-pad-with-n-characters-in-python

    length = max([len(y.__class__.__name__) for y in _])

    return "{s:{c}^{n}}".format(s=" " + x.__class__.__name__ + " ", n=length + 6, c="*")


def train(type, models, X_train, Y_train):

    path = os.path.join("models", "features", type + ".csv")

    with open(path, "w", newline="") as out:

        writer = csv.DictWriter(out, None)

        for model in models:

            print("\n" + pad(models, model))
            print("\nFitting model... ", end="")

            start = time.time()

            model.fit(X_train, Y_train)
            accuracy = model.score(X_test, Y_test)

            print("DONE ({:.2f}s)".format(time.time() - start))
            print("Accuracy: {:.2f}".format(accuracy))

            ranking = graph(model)

            if ranking is not None:

                ranking["name"] = model.__class__.__name__
                ranking["accuracy"] = accuracy

                if writer.fieldnames is None:

                    writer.fieldnames = ranking.keys()
                    writer.writeheader()

                writer.writerow(ranking)

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


def calc_std(model):

    # if isinstance(model, RandomForestClassifier):
    #
    #     return np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)
    #
    # if isinstance(model, RandomForestRegressor):
    #
    #     return np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)

    return None


def graph(model, print_ranking=False):
    """

    :param model:
    :param print_ranking:
    :return: A dictionary of feature to importance
    """

    c = coefficients(model)

    if c is None:

        return None

    c = np.abs(c)
    std = calc_std(model)
    indices = np.argsort(c)[::-1]               # The indices that would sort c in descending order
    num_features = X.shape[1]                   # The number of features
    columns = [df.columns[i] for i in indices]
    ranking = dict()

    if print_ranking:

        print("\nRanking\n")

    for i in range(num_features):

        if print_ranking:

            print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], c[indices[i]]))

        ranking[df.columns[indices[i]]] = c[indices[i]]

    plt.figure()
    plt.title("{} importance".format(model.__class__.__name__))

    if std is not None:

        plt.bar(range(num_features), c[indices], color="r", yerr=std[indices], align="center")

    else:

        plt.bar(range(num_features), c[indices], color="r", align="center")

    plt.xticks(range(num_features), columns, rotation=90)
    plt.xlim([-1, num_features])
    plt.show()

    return ranking

# https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-py
# https://github.com/scikit-learn/scikit-learn/issues/15132


def test():

    path = os.path.join("models", "pickles")

    for file in os.listdir(path):

        name, _ = file.split(".")

        print("\nLoading {}...".format(file), end="")

        start = time.time()

        path = os.path.join("models", file)
        model = load(path)

        print(" DONE ({:.2f}s)\n".format(time.time() - start))

        graph(model)


if __name__ == "__main__":

    df = preprocess()

    for type in ["classification", "regression"]:

        models = regressors if type == "regression" else classifiers
        Y = df["delay"] if type == "regression" else df["delayed"]
        X = df.drop(["delay", "delayed"], axis=1)

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

        train(type, models, X_train, Y_train)
