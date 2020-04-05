from sklearn.experimental import enable_hist_gradient_boosting  # to use HistGradientBoosting models

# Classifiers
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression, SGDClassifier, RidgeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier

# Regressors
from sklearn.svm import LinearSVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import SGDRegressor, Ridge, BayesianRidge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor

# Metrics
from sklearn.metrics import recall_score, average_precision_score, mean_squared_error, mean_absolute_error, \
    classification_report, confusion_matrix, mean_squared_log_error, r2_score

# Helpers
from sklearn.model_selection import train_test_split

# Pre-processing
from models.preprocess import *

classifiers = [
    # LogisticRegression(),
    # RidgeClassifier(),
    # SGDClassifier(),
    RandomForestClassifier(),
    # GradientBoostingClassifier(),
    # HistGradientBoostingClassifier(),
    # LinearSVC()
]

regressors = [
    RandomForestRegressor(),            # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
    GradientBoostingRegressor(),        # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html
    HistGradientBoostingRegressor(),    # https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html
    Ridge(),                            # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html
    KernelRidge(),                      # https://scikit-learn.org/stable/modules/generated/sklearn.kernel_ridge.KernelRidge.html
    SGDRegressor(),                     # https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDRegressor.html
    LinearSVR(),                        # https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVR.html
    BayesianRidge(),
]

df = preprocess()
model_types = ["regression"]

def pad(_, x):
    # https://stackoverflow.com/questions/4008546/how-to-pad-with-n-characters-in-python

    length = max([len(y) for y in _])

    return "{s:{c}^{n}}".format(s=" " + x.upper() + " ", n=length + 6, c="*")
