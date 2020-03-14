import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

data = pd.read_csv("sklearn.csv", index_col="id")

X = data.drop("delayed", axis=1)
Y = data["delayed"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=0)

rf = RandomForestClassifier(random_state=0, n_estimators=20)

rf.fit(X_train, Y_train)

predicted_y = rf.predict(X_test)

print("Accuracy: {:.2f}".format(rf.score(X_test, Y_test)))

# Goddamn this takes ages!

# This takes ages as well.
# No built-in save. That's a shame.
# There's not much more that I can do now. Time to head back. I'll chase up Nathaniel.
# And then... one fine morning...


