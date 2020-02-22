# https://towardsdatascience.com/building-a-logistic-regression-in-python-step-by-step-becd4d56c9c8

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# data = data.drop("origin_delay", axis=1)
#
# data["delayed"] = data["destination_delay"] > 5
# data = data.drop("destination_delay", axis=1)
#
# data.to_csv("logistic_regression.csv")

data = pd.read_csv("logistic_regression.csv")

X = data.drop(["id", "delayed"], axis=1)
Y = data["delayed"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

classifier = LogisticRegression(solver="lbfgs", random_state=0)
classifier.fit(X_train, Y_train)

predicted_y = classifier.predict(X_test)

print("Accuracy: {:.2f}".format(classifier.score(X_test, Y_test)))

