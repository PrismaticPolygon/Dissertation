# https://www.tutorialspoint.com/logistic_regression_in_python/index.htm

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

data = pd.read_csv("sklearn.csv", index_col="id")

X = data.drop("delayed", axis=1)
Y = data["delayed"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

classifier = LogisticRegression(solver="lbfgs", random_state=0, max_iter=1000)
classifier.fit(X_train, Y_train)

print(classifier)

predicted_y = classifier.predict(X_test)

print("Accuracy: {:.2f}".format(classifier.score(X_test, Y_test)))

# Failed to converge, but still 96% accuracy! Truly baffling. It's just a warning...
