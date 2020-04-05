import time
import os

from joblib import dump     # More efficient than pickle for objects with large internal NumPy arrays

from models.lib import *
# from imblearn.over_sampling import SMOTE
# from imblearn.under_sampling import RandomUnderSampler
#
# from sklearn.pipeline import Pipeline
#
# over = SMOTE(sampling_strategy=0.1)                 # Over-sample minority to have 10% samples of majority
# under = RandomUnderSampler(sampling_strategy=0.5)   # Under-sample majority to have 150% samples of minority
#
# # Original paper suggests combining SMOTE with random under-sampling of the majority class.
# # Use repeated stratified k-fold cross-validation to evalute the model.
#
# pipeline = Pipeline([('o', over), ('u', under)])


def train(model, path, X_train, Y_train):

    print("Fitting {}... ".format(model.__class__.__name__), end="")

    start = time.time()

    try:

        model.fit(X_train, Y_train)

        print("DONE ({:.2f}s)".format(time.time() - start))

        model_path = os.path.join(path, model.__class__.__name__ + ".pickle")

        with open(model_path, "wb") as file:

            dump(model, file)

    except ValueError as e: # Catch bad encoding errors

        print(e)


def run():

    for model_type in model_types:

        print("\n" + pad(model_types, model_type) + "\n")

        path = os.path.join("models", model_type)

        if not os.path.exists(path):

            os.mkdir(path)

        path = os.path.join(path, arg())

        if not os.path.exists(path):

            os.mkdir(path)

        models = regressors if model_type == "regression" else classifiers
        Y = df["delay"] if model_type == "regression" else df["delayed"]
        X = df.drop(["delay", "delayed"], axis=1)

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

        for model in models:

            train(model, path, X_train, Y_train)


if __name__ == "__main__":

    run()
