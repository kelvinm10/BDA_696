import os
import pickle
import random
import sys
import time

# import numpy as np
import pandas as pd
import plotly.express as px
import sqlalchemy
import statsmodels.api as sm
from assignment4 import run_main_rankings
from midterm import run_all
from sklearn import metrics, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit


def random_forest(x_train, x_test, retrain=False, model_path="models/rf_tuned.sav"):
    # first check if model has alredy been trained, if so do not retrain
    if os.path.exists(model_path) and retrain is False:
        model = pickle.load(open(model_path, "rb"))
        return model
    rf = RandomForestClassifier(
        random_state=1,
        n_estimators=200,
        min_samples_split=10,
        min_samples_leaf=2,
        max_features="auto",
        max_depth=10,
        bootstrap=False,
    )

    # n_estimators = [int(x) for x in np.linspace(start=200, stop=2000, num=10)]
    # # Number of features to consider at every split
    # max_features = ["auto", "sqrt"]
    # # Maximum number of levels in tree
    # max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
    # max_depth.append(None)
    # # Minimum number of samples required to split a node
    # min_samples_split = [2, 5, 10]
    # # Minimum number of samples required at each leaf node
    # min_samples_leaf = [1, 2, 4]
    # # Method of selecting samples for training each tree
    # bootstrap = [True, False]
    #
    # random_grid = {
    #     "n_estimators": n_estimators,
    #     "max_features": max_features,
    #     "max_depth": max_depth,
    #     "min_samples_split": min_samples_split,
    #     "min_samples_leaf": min_samples_leaf,
    #     "bootstrap": bootstrap,
    # }
    # tscv = TimeSeriesSplit(n_splits=5)
    # print("running randomized search for forest...")
    # search = RandomizedSearchCV(rf, random_grid, cv=tscv)
    rf.fit(x_train, x_test)
    if not os.path.exists("models"):
        os.makedirs("models")
    pickle.dump(rf, open(model_path, "wb"))
    return rf


def svc(x_train, x_test, retrain=False, model_path="models/svc_tuned.sav"):
    # check if model already exists
    if os.path.exists(model_path) and retrain is False:
        model = pickle.load(open(model_path, "rb"))
        return model

    if not os.path.exists("models"):
        os.makedirs("models")
    clf = svm.SVC()
    # param_grid = {
    #     "C": [0.1, 1, 10],
    #     "gamma": [1, 0.1, 0.01],
    #     "kernel": ["rbf", "linear", "poly"],
    # }
    # tscv = TimeSeriesSplit(n_splits=5)
    # print("Running randomized seach for svc...")
    # sv_search = RandomizedSearchCV(clf, param_grid, cv=tscv, n_jobs=-1)
    clf.fit(x_train, x_test)
    pickle.dump(clf, open(model_path, "wb"))
    return clf


def logit(x_train, x_test, retrain=False, model_path="models/tuned_logit.sav"):
    if os.path.exists(model_path) and retrain is False:
        print("using saved model")
        model = pickle.load(open(model_path, "rb"))
        return model
    if not os.path.exists("models"):
        os.makedirs("models")
    clf = LogisticRegression(random_state=1)
    LRparam_grid = {
        "C": [0.001, 0.01, 0.1, 1, 10, 100],
        "penalty": ["l1", "l2"],
        "max_iter": list(range(100, 800, 100)),
        "solver": ["newton-cg", "lbfgs", "liblinear", "saga"],
    }
    tscv = TimeSeriesSplit(n_splits=4)
    print("Running Logit Randomized Search...")
    lr_search = RandomizedSearchCV(clf, cv=tscv, param_distributions=LRparam_grid)
    lr_search.fit(x_train, x_test)
    pickle.dump(lr_search, open(model_path, "wb"))
    return lr_search


def extract_significant_features(pvalues, features, threshold, filter=False):
    idx = 0
    feature_index = []
    if filter:
        temp = [
            "rolling_whip_diff",
            "historic_oba_diff",
            "rolling_hr9_diff",
            "historic_k9_diff",
            "wind_diff_away",
        ]
    else:
        temp = []
    for i in pvalues:
        if idx == 0:
            idx += 1
            continue
        if i < threshold:
            feature_index.append(idx)
        idx += 1

    significant_feat = []
    idx2 = 1
    for i in features:
        if idx2 in feature_index and i not in temp:
            significant_feat.append(i)
        idx2 += 1

    print("Features in optimization: ", significant_feat)
    return significant_feat


def plot_roc(ytrue, yhat):
    fpr, tpr, thresholds = metrics.roc_curve(ytrue, yhat)

    fig = px.area(
        x=fpr,
        y=tpr,
        title=f"ROC Curve (AUC={metrics.auc(fpr, tpr):.4f})",
        labels=dict(x="False Positive Rate", y="True Positive Rate"),
        width=700,
        height=500,
    )
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")
    fig.show()


def main():
    # db_user = "root"
    # db_pass = "password"  # pragma: allowlist secret
    # #    db_host = "localhost"
    # db_database = "baseball"
    # connect_string = (
    #     f"mariadb+mariadbconnector://{db_user}:{db_pass}@127.0.0.1/{db_database}"
    # )
    # # pragma: allowlist secret
    # sql_engine = sqlalchemy.create_engine(connect_string)
    #
    # query = """
    #           SELECT *
    #           FROM final_diff_features;
    #     """
    # df = pd.read_sql_query(query, sql_engine)

    # db is the name of the service of the mariadb container in the compose file
    connect_string = "mysql+mysqlconnector://root:password@db:3306/baseball"  # pragma: allowlist secret

    # the first time connecting to the mariadb connector, it will take a few minutes to
    # connect (due to inserting and reading baseball.sql database), this loop will continue to try to
    # connect
    # this sleep function allows the mariadb container to fully spin up when creating the container for the
    # first time. Can lower the sleep value once re running already built container
    while True:
        try:
            sql_engine = sqlalchemy.create_engine(connect_string)
            query = """
                       SELECT *
                       FROM final_diff_features;
                 """
            df = pd.read_sql_query(query, sql_engine)
            break
        except Exception:
            print("connection failed, sleeping then retrying...")
            time.sleep(300)

    # there are some empty strings in our response (exhibition game ending in a tie) drop these rows
    baseball_df = df[df["winner_home_or_away"] != ""]
    baseball_df.reset_index(inplace=True)
    baseball_df = baseball_df[baseball_df.columns[6:]]
    # baseball_df.drop(["start_time", "ampm"], axis=1, inplace=True)

    # Drop all NA values (I decided to drop, because when a stat had NA, then it was that pitchers or teams
    # first game, so they had no previous game stats, thus doing something like filling in the na with mean would
    # not necessarily make sense)
    all_columns = list(baseball_df.columns)
    print(all_columns)
    features = all_columns[: len(all_columns) - 1]
    features = features[1:]
    baseball_df.dropna(inplace=True)
    baseball_df.reset_index(inplace=True, drop=True)

    # change response to binary (1s and 0s instead of strings)
    baseball_df["winner_home_or_away"].replace(("H", "A"), (1, 0), inplace=True)
    response = all_columns[-1]

    print("ALL FEATURES: ", features)
    run_main_rankings(baseball_df, features, response)
    run_all(baseball_df, features, response)

    # first, split the data into training and testing, in order to correctly do this, my training set will
    # be the all the years except 2012, and my testing set will be all the games that occurredc in 2012.

    training_df = baseball_df[baseball_df["Year"] != 2012]
    test_df = baseball_df[baseball_df["Year"] == 2012]

    x_train = training_df[features].values
    y_train = training_df[response].values

    x_test = test_df[features].values
    y_test = test_df[response].values

    random.seed(100)
    # now build a random forest classifier
    rf_model = RandomForestClassifier(random_state=100)
    rf_model.fit(x_train, y_train)

    y_hat = rf_model.predict(x_test)
    print("RF Accuracy: ", metrics.accuracy_score(y_test, y_hat))

    # fit a logistic regression
    logistic_model = sm.Logit(y_train, sm.add_constant(x_train)).fit()

    logit_pred = logistic_model.predict(sm.add_constant(x_test))
    logit_pred = list(map(round, logit_pred))
    print("logit Accuracy: ", metrics.accuracy_score(y_test, logit_pred))

    print(logistic_model.summary())

    # extract p values from logistic model and get only significant features (< 0.5)
    pvalues = logistic_model.pvalues
    significant_feat = extract_significant_features(pvalues, features, 0.5, filter=True)

    print("Significant features: ", significant_feat)

    x_train_opt = training_df[significant_feat].values
    x_test_opt = test_df[significant_feat].values
    run_main_rankings(training_df, significant_feat, response)
    run_all(training_df, significant_feat, response)
    log_optimized = sm.Logit(y_train, sm.add_constant(x_train_opt)).fit()
    log_optimized_pred = log_optimized.predict(sm.add_constant(x_test_opt))
    log_optimized_pred = list(map(round, log_optimized_pred))
    print(
        "logit optimized Accuracy: ", metrics.accuracy_score(y_test, log_optimized_pred)
    )
    print(log_optimized.summary())

    # build tuned logistic regression on optimized parameters
    lr_search = logit(
        x_train_opt,
        y_train,
        retrain=True,
        model_path="models/tuned_logit_diff.sav",
    )
    lr_yhat = lr_search.predict(x_test_opt)
    print("tuned logit best params: ", lr_search.best_params_)
    print("tuned logit Accuracy: ", metrics.accuracy_score(y_test, lr_yhat))
    print("Logit Confusion matrix: ", confusion_matrix(y_test, lr_yhat))
    plot_roc(y_test, lr_yhat)

    # now do a random forest for these optimized predictors
    # I did a tuned RF for my final model, but commented out the code
    # because it took a very long time to run, so uncomment if you want to
    # run that in the random_forest function
    rf_search = random_forest(
        x_train_opt,
        y_train,
        retrain=True,
        model_path="models/tuned_rf_diff.sav",
    )
    rf_yhat = rf_search.predict(x_test_opt)
    # print("tuned random forest best params: ", rf_search.best_params_)
    print("tuned random forest Accuracy: ", metrics.accuracy_score(y_test, rf_yhat))
    print("Random Forest Confusion Matrix: ", confusion_matrix(y_test, rf_yhat))
    plot_roc(y_test, rf_yhat)

    # now run a support vector machine
    svc_model = svc(
        x_train_opt,
        y_train,
        retrain=True,
        model_path="models/svc_diff.sav",
    )
    svc_yhat = svc_model.predict(x_test_opt)
    # print("svc best params: ", svc_model.best_params_)
    print("svc Accuracy: ", metrics.accuracy_score(y_test, svc_yhat))
    print("SVC Confusion Matrix: ", confusion_matrix(y_test, svc_yhat))
    plot_roc(y_test, svc_yhat)


if __name__ == "__main__":
    if not os.path.exists("finalTables"):
        os.makedirs("finalTables")

    # delete any existing html files in current directory
    for f in os.listdir(os.getcwd() + "/" + "finalTables/"):
        if not f.endswith(".html"):
            continue
        os.remove(os.path.join(os.getcwd() + "/" + "finalTables/", f))

    for f in os.listdir(os.getcwd()):
        if not f.endswith(".html"):
            continue
        os.remove(os.path.join(os.getcwd(), f))

    sys.exit(main())
