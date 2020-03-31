import time
import os

from joblib import dump     # More efficient than pickle for objects with large internal NumPy arrays

from models.lib import *


def train(model, model_type, X_train, Y_train):

    print("Fitting {}... ".format(model.__class__.__name__), end="")

    start = time.time()

    model.fit(X_train, Y_train)

    print("DONE ({:.2f}s)".format(time.time() - start))

    model_path = os.path.join("models", model_type, model.__class__.__name__ + ".pickle")

    with open(model_path, "wb") as file:

        dump(model, file)


def main():

    for model_type in model_types:

        print("\n" + pad(model_types, model_type) + "\n")

        models = regressors if model_type == "regression" else classifiers
        Y = df["delay"] if model_type == "regression" else df["delayed"]
        X = df.drop(["delay", "delayed"], axis=1)

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

        for model in models:

            train(model, model_type, X_train, Y_train)


if __name__ == "__main__":

    main()
