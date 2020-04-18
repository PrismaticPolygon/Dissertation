import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, RandomizedSearchCV

# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
clf = RandomForestClassifier(
    n_estimators=10,        # Number of trees in the forest
    criterion="gini",       # Function to measure the quality of a split.
    max_depth=None,         # Max depth of a tree. If none, nodes are expanded until all leaves are pure
    min_samples_split=2,    # Minimum number of samples required to split an internal node
    min_samples_leaf=1,     # Minimum number of samples required to be at a leaf node
    n_jobs=-1,              # Number of jobs to run in parallel. -1 means use all available processors.
)

# Evaluate pipeline. Repeated stratified k-fold cross validation
cv = RepeatedStratifiedKFold(
    n_splits=6,
    n_repeats=2,
    random_state=1
)

params = {
    "n_estimators": [int(x) for x in np.linspace(start=100, stop=2000, num=10)],
    "max_features": ['auto', 'sqrt'],
    "max_depth": [int(x) for x in np.linspace(10, 110, num = 11)] + [None],
    "min_samples_split": [2, 5, 10, 50, 100],
    "min_samples_leaf": [1, 2, 4],
    "bootstrap": [True, False]
}

# And use the preprocessor from the other one.

grid = RandomizedSearchCV(clf, params, cv=cv, n_iter=1, verbose=2, n_jobs=-1, random_state=0)
grid.fit(X_train, Y_train)

print(grid.best_params_)

# That's fine.
# Once this is running I'll start porting over my 'solution' stuff.
#
# rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
#
#
# scores = cross_val_score(pipeline, X_train, Y_train, scoring='roc_auc', cv=cv, n_jobs=3)

# print(scores)
#
# print('Mean ROC AUC: {:.3f}'.format(np.mean(scores)))


