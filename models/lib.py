from sklearn.experimental import enable_hist_gradient_boosting  # to use HistGradientBoosting models

# Regressors
from sklearn.svm import LinearSVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import SGDRegressor, Ridge, BayesianRidge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor

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