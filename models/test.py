import time
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump, load   # More efficient than pickle for objects with large internal NumPy arrays


def train():

    models = [
        LogisticRegression(solver="lbfgs", random_state=0, max_iter=2000),
        RandomForestClassifier(random_state=0, n_estimators=20),
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

        path = os.path.join("models", name + ".pickle")

        with open(path, "wb") as file:

            dump(model, file)


def regression_importance(regressor: LogisticRegression):
    """
    Calculate the importance of features for logistic regression. From

    https://stackoverflow.com/questions/47303261/getting-weights-of-features-using-scikit-learn-logistic-regression
    https://towardsdatascience.com/model-based-feature-importance-d4f6fb2ad403

    :param regressor: a classifier of type LogisticRegression
    :return: None
    """

    c = regressor.coef_[0]          # Coefficients. A 1-D array.
    indices = np.argsort(c)         # The indices that would sort c in ascending order. Lower is more important
    columns = [df.columns[i] for i in indices]  # That is not right.

    for i in range(X.shape[1]):

        print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], c[indices[i]]))

    plt.figure()
    plt.title("Logistic regression importances")
    plt.bar(range(X.shape[1]), c[indices], color="b", align="center")
    plt.xticks(range(X.shape[1]), columns, rotation=90)
    plt.xlim([-1, X.shape[1]])
    plt.show()


def forest_importance(forest: RandomForestClassifier):

    """
    Calculate the importance of features for the random forest.

    https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html

    :param forest: a classifier of type RandomForestClassifier
    :return: None
    """

    importances = forest.feature_importances_

    std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]
    columns = [df.columns[i] for i in indices]  # That is not right.

    # I can't wrap my head around what is!

    # Print the feature ranking
    print("Feature ranking:")

    # We should be able to sync that up with column names as well.
    # THe indices is just a sorted ist of importance indices. Gotcha.
    # I.e. the most important feature has an index of indices[i]
    # Okay. Let's figure out the logistic regression.

    for i in range(X.shape[1]):

        print("{}. {} ({:.4f})".format(i + 1, df.columns[indices[i]], importances[indices[i]]))

    plt.figure()
    plt.title("Random forest feature importances")
    plt.bar(range(X.shape[1]), importances[indices], color="r", yerr=std[indices], align="center")
    plt.xticks(range(X.shape[1]), columns, rotation=90)
    plt.xlim([-1, X.shape[1]])
    plt.show()


def test():

    for file in os.listdir("models"):

        name, extension = file.split(".")

        if extension == "pickle":

            print("Loading {}...".format(file), end="")

            start = time.time()

            path = os.path.join("models", file)
            model = load(path)

            print(" DONE ({:.2f}s)".format(time.time() - start))

            if name == "RandomForestClassifier":

                forest_importance(model)

            if name == "LogisticRegression":

                regression_importance(model)

# Possible that they aren't saved in my pickle. I hope that they are though.

if __name__ == "__main__":

    print("Loading data... ", end="")

    start = time.time()

    df = pd.read_csv("sklearn.csv", index_col="id")

    Y = df["delayed"]
    X = df.drop("delayed", axis=1)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

    print("DONE ({:.2f}s)".format(time.time() - start))

    test()