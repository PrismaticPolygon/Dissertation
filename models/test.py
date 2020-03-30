import time
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.experimental import enable_hist_gradient_boosting  # noqa. Required to using HistGradientBoost below.

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, BayesianRidge, SGDClassifier
from joblib import dump, load   # More efficient than pickle for objects with large internal NumPy arrays


def train():

    models = [
        LogisticRegression(),
        BayesianRidge(),
        SGDClassifier(
            loss="hinge",       # (soft-margin) linear SVM
            penalty="l2",
            max_iter=5,
            random_state=0
        ),
        RandomForestClassifier(
            n_jobs=-1,              # Use all available cores on the machine,
            n_estimators=20         # Number of trees. Default of 100 takes too long.
        ),
        GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=1.0,      # Controls over-fitting via shrinkage
            max_depth=1,            # Tree depth
            random_state=0
        ),
        HistGradientBoostingClassifier()
    ]

    # https://stackoverflow.com/questions/4008546/how-to-pad-with-n-characters-in-python
    pad = max([len(x.__class__.__name__) for x in models])

    for model in models:

        name = model.__class__.__name__

        print("\n{s:{c}^{n}}".format(s=" " + name + " ", n=pad + 6, c="*"))
        print("\nFitting model... ", end="")

        start = time.time()

        model.fit(X_train, Y_train)

        print("DONE ({:.2f}s)".format(time.time() - start))
        print("Accuracy: {:.2f}".format(model.score(X_test, Y_test)))

        path = os.path.join("models", "pickles", name + ".pickle")

        with open(path, "wb") as file:

            dump(model, file)


def graph(model, c, std=None, print_ranking=False):

    c = np.abs(c)
    indices = np.argsort(c)[::-1]               # The indices that would sort c in descending order
    num_features = X.shape[1]                   # The number of features
    columns = [df.columns[i] for i in indices]

    print("Accuracy: {:.2f}".format(model.score(X_test, Y_test)))

    if print_ranking:

        for i in range(num_features):

            print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], c[indices[i]]))

    plt.figure()
    plt.title("{} importance".format(model.__class__.__name__))

    if std is not None:

        plt.bar(range(num_features), c[indices], color="r", yerr=std[indices], align="center")

    else:

        plt.bar(range(num_features), c[indices], color="r", align="center")

    plt.xticks(range(num_features), columns, rotation=90)
    plt.xlim([-1, num_features])
    plt.show()

# Seems that there's much more to this.
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

        if isinstance(model, RandomForestClassifier):

            std = np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)
            graph(model, model.feature_importances_, std=std)

        elif isinstance(model, GradientBoostingClassifier):

            graph(model, model.feature_importances_)

        elif isinstance(model, HistGradientBoostingClassifier):

            print(model)

            print(dir(model))

            graph(model, model.feature_importances_)

        elif isinstance(model, LogisticRegression):

            graph(model, model.coef_[0])

        elif isinstance(model, BayesianRidge):

            graph(model, model.coef_)

        elif isinstance(model, SGDClassifier):

            graph(model, model.coef_[0])


if __name__ == "__main__":

    print("Loading data... ", end="")

    start = time.time()

    df = pd.read_csv("sklearn.csv", index_col="id")

    Y = df["delayed"]
    X = df.drop("delayed", axis=1)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

    print("DONE ({:.2f}s)".format(time.time() - start))

    # train()
    test()
