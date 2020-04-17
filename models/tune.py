import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from joblib import load

# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
clf = RandomForestClassifier(
    n_estimators=100,   # Number of trees in the forest
    criterion="gini",    # Function to measure the quality of a split.
    max_depth=None,     # Max depth of a tree. If none, nodes are expanded until all leaves are pure
    min_samples_split=2, # Minimum number of samples required to split an internal node
    min_samples_leaf=1,  # Minimum number of samples required to be at a leaf node
    n_jobs=-1,               # Number of jobs to run in parallel. -1 means use all available processors.
    verbose=1
)


# df = pd.read_csv("data/preprocessed/cyclical.csv")
# model = load("models/classification/cyclical/RandomForestClassifier.pickle")

def plot(df, model, print_ranking=True):

    # It's clear that several characteristics are useless. But why the size mismatch? Because they have a different number of columns

    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    num_features = df.shape[1]
    columns = [df.columns[i] for i in indices]

    print("num_features: {}".format(num_features))
    print("columns: {}".format(len(columns)))

    if print_ranking:

        print("\nRanking\n")

        for i in range(num_features):

            if print_ranking:

                print("{}. {} ({:.4E})".format(i + 1, df.columns[indices[i]], importances[indices[i]]))

    # Plot the feature importances of the forest
    plt.figure()
    plt.title("Feature importances")
    plt.bar(range(num_features), importances[indices], color="r", yerr=std[indices], align="center")
    plt.xticks(range(num_features), columns, rotation=90)
    plt.xlim([-1, df.shape[1]])
    plt.show()


















# plot(print_ranking=True)