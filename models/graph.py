import time
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import plot_roc_curve
from sklearn.model_selection import StratifiedKFold, RepeatedStratifiedKFold

from models.tuner import load

def plot(df, model, print_ranking=True):

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

# https://stats.stackexchange.com/questions/132777/what-does-auc-stand-for-and-what-is-it
# That looks very, very wrong.

def roc():

    # Run classifier with repeated stratified cross-validation and plot ROC curves
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)

    tprs = []
    aucs = []
    mean_fpr = np.linspace(0, 1, 100)

    fig, ax = plt.subplots()

    for i, (train, test) in enumerate(cv.split(X, Y)):

        print(X[train].shape, Y[train].shape)

        start = time.time()

        print("Train Positive", Y[train].sum())
        print("Train Negative", len(Y[train]) - Y[train].sum())

        print("Test Positive", Y[test].sum())
        print("Test Negative", len(Y[test]) - Y[test].sum())

        print("Fitting fold {}...".format(i), end="")

        clf.fit(X[train], Y[train])

        print(" DONE ({:.2f}s)".format(time.time() - start))

        viz = plot_roc_curve(clf, X[test], Y[test], name='ROC fold {}'.format(i), alpha=0.3, lw=1, ax=ax)

        interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
        interp_tpr[0] = 0.0

        tprs.append(interp_tpr)
        aucs.append(viz.roc_auc)

    # Plot the chance
    ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)

    # Plot the perfect model
    ax.plot([0, 0], [0, 1], linestyle='--', lw=2, color='g', label='Perfect', alpha=.8)
    ax.plot([0, 1], [1, 1], linestyle='--', lw=2, color='g', alpha=.8)

    # Plot the mean ROC
    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    ax.plot(mean_fpr, mean_tpr, color='b',
            label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
            lw=2, alpha=.8)

    # Plot the STDs
    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                    label=r'$\pm$ 1 std. dev.')

    ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
           title="Receiver operating characteristic (ROC)")
    ax.legend(loc="lower right")
    plt.show()

if __name__ == "__main__":

    X, Y = load()
    clf = RandomForestClassifier(
        n_estimators=200,
        min_samples_split=10,
        min_samples_leaf=2,
        max_features="sqrt",
        max_depth=10,
        bootstrap=False,
        n_jobs=-1
    )

    roc()
