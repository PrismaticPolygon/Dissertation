# https://towardsdatascience.com/hyperparameter-tuning-the-random-forest-in-python-using-scikit-learn-28d2aa77dd74


from sklearn.model_selection import RepeatedStratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder

from models.experiment import *

import matplotlib.pyplot as plt

# https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
clf = RandomForestClassifier(
    n_estimators=10,        # Number of trees in the forest
    criterion="gini",       # Function to measure the quality of a split.
    max_depth=None,         # Max depth of a tree. If none, nodes are expanded until all leaves are pure
    min_samples_split=2,    # Minimum number of samples required to split an internal node
    min_samples_leaf=1,     # Minimum number of samples required to be at a leaf node
    n_jobs=-1,              # Number of jobs to run in parallel. -1 means use all available processors.
)

class RailEncoder(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):

        return self

    def transform(self, X, y=None):

        catering = ["catering_" + c for c in ["C", "F", "H", "M", "R", "T"]]
        characteristics = ["characteristic_" + c for c in ["B", "C", "D", "E", "G", "M", "P", "Q", "R", "S", "Y", "Z"]]

        for c in characteristics:

            X[c] = X[c].map({1: c[-1], 0: ""})

        for c in catering:

            X[c] = X[c].map({1: c[-1], 0: ""})

        X["characteristics"] = X["characteristic_B"] + X["characteristic_C"] + X["characteristic_D"] + \
                               X["characteristic_E"] + X["characteristic_G"] + X["characteristic_M"] + \
                               X["characteristic_P"] + X["characteristic_Q"] + X["characteristic_R"] + \
                               X["characteristic_S"] + X["characteristic_Y"] + X["characteristic_Z"]

        X["catering"] = X["catering_C"] + X["catering_F"] + X["catering_H"] + X["catering_M"] + X["catering_R"] + \
                        X["catering_T"]

        X["characteristics"] = X["characteristics"].astype("category")
        X["catering"] = X["catering"].astype("category")

        return X.drop(characteristics + catering, axis=1)

# But what is the DF? I really have no idea.

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


def tune():

    dtype = ['characteristic_B', 'characteristic_C', 'characteristic_D', 'characteristic_E', 'characteristic_G',
             'characteristic_M', 'characteristic_P', 'characteristic_Q', 'characteristic_R', 'characteristic_S',
             'characteristic_Y', 'characteristic_Z', 'catering_C', 'catering_F', 'catering_H', 'catering_M',
             'catering_R', 'catering_T', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'freight',
             'bank_holiday_running', 'length', 'speed', 'delayed']

    dtype = {key: "uint8" for key in dtype}

    categories = {
        "status": "category",
        "category": "category",
        "power_type": "category",
        "timing_load": "category",
        "seating": "category",
        "reservations": "category",
        "ATOC_code": "category",
        "destination_stanox_area": "category",
        "origin_stanox_area": "category"
    }

    dtype.update(categories)

    start = time.time()

    print("Loading data...", end="")

    df = pd.read_csv("data/dscm_w.csv",
                     index_col=["uid"],
                     parse_dates=["std", "sta", "atd", "ata"],
                     dtype=dtype)

    # for category in categories.keys():
    #
    #     df[category] = df[category].cat.codes

    path = os.path.join("models", "select")

    if not os.path.exists(path):

        os.mkdir(path)

    Y = df["delayed"]
    X = df.drop(["delay", "delayed", "atd", "ata", "origin", "destination"], axis=1)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print(X.info())

    deonehot_features = ["catering_" + c for c in ["C", "F", "H", "M", "R", "T"]] + \
                        ["characteristic_" + c for c in ["B", "C", "D", "E", "G", "M", "P", "Q", "R", "S", "Y", "Z"]]

    X = RailEncoder().transform(X)

    categorical_features = ["status", "category", "power_type", "timing_load", "seating", "reservations",
                            "characteristics", "catering", "ATOC_code", "origin_stanox_area", "destination_stanox_area"]

    for c in categorical_features:

        X[c] = X[c].cat.codes

    print(X.info())

    # categorical_transformer = Pipeline([
    #     ('imputer', SimpleImputer(strategy='constant', fill_value='missing'))
    # ])

    datetime_features = X.select_dtypes(include="datetime").columns.values
    datetime_transformer = Pipeline([
        ("cyclical", DatetimeEncoder(cyclical=True))
    ])

    # numeric_features = ["speed", "length", "duration"]
    # numerical_transformer = Pipeline([
    #     ("scaler", StandardScaler())
    # ])

    preprocessor = ColumnTransformer([
        # ("deonehot", deonehot_transformer, deonehot_features),
        # ("categorical", categorical_transformer, categorical_features),
        ("datetime", datetime_transformer, datetime_features),
        # ("numeric", numerical_transformer, numeric_features)
    ], remainder="passthrough")

    resampler = IPipeline([
        # ('over', SMOTE(sampling_strategy=0.2, random_state=1)),                 # Increase minority to 20% of majority
        ('under', RandomUnderSampler(sampling_strategy=1.0, random_state=1)),   # Reduce majority to 50% of minority
    ])

    start = time.time()

    print("\nPreprocessing data...", end="")

    X = preprocessor.fit_transform(X, Y)

    print(X)
    print(X.shape)
    print(type(X))

    print(preprocessor.get_feature_names())



    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print(X.shape)

    print("\nResampling data...", end="")

    X, Y = resampler.fit_resample(X, Y)

    print(" DONE ({:.2f}s)".format(time.time() - start), end="\n\n")

    print("{}, delayed: {}, not delayed: {}\n".format(X.shape, Y.sum(), len(Y) - Y.sum()))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=1)

    # Evaluate pipeline. Repeated stratified k-fold cross validation
    # cv = RepeatedStratifiedKFold(
    #     n_splits=6,
    #     n_repeats=2,
    #     random_state=1
    # )

    params = {
        "n_estimators": [int(x) for x in np.linspace(start=10, stop=200, num=10)],
        "max_features": ['auto', 'sqrt'],
        "max_depth": [int(x) for x in np.linspace(10, 110, num = 11)] + [None],
        "min_samples_split": [2, 5, 10, 50, 100],
        "min_samples_leaf": [1, 2, 4],
        "bootstrap": [True, False]
    }

    grid = RandomizedSearchCV(clf, params, cv=3, n_iter=50, verbose=2, n_jobs=3, random_state=1)
    grid.fit(X_train, Y_train)

    print(grid.best_params_)

    best = grid.best_estimator_

    metrics = [
        recall_score,
        average_precision_score,
    ]

    Y_pred = best.predict(X_test)

    results = {
        "name": best.__class__.__name__,
        "score": best.score(X_test, Y_test)
    }

    for m in metrics:

        results[m.__name__] = m(Y_test.values, Y_pred)

    print(best.__class__.__name__ + "\n")
    print(results)
    print(classification_report(Y_test.values, Y_pred, target_names=["not delayed", "delayed"]))

    if not os.path.exists("models/tune"):

        os.mkdir("models/tune")

    model_path = os.path.join("models", "tune", best.__class__.__name__ + ".pickle")

    with open(model_path, "wb") as file:

        dump(best, file)

if __name__ == "__main__":

    tune()


