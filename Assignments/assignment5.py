import os
import sys

import pandas as pd
import sqlalchemy
import statsmodels.api as sm
from assignment4 import run_main_rankings
from midterm import run_all
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier


def main():
    db_user = "root"
    db_pass = ""  # pragma: allowlist secret
    db_host = "localhost"
    db_database = "baseball"
    connect_string = (
        f"mariadb+mariadbconnector://{db_user}:{db_pass}@{db_host}/{db_database}"
    )
    # pragma: allowlist secret
    sql_engine = sqlalchemy.create_engine(connect_string)

    query = """
           SELECT *
           FROM final_diff_features;
     """
    df = pd.read_sql_query(query, sql_engine)
    # there are some empty strings in our response (exhibition game ending in a tie) drop these rows
    baseball_df = df[df["winner_home_or_away"] != ""]
    baseball_df.reset_index(inplace=True)
    # print(baseball_df)
    baseball_df = baseball_df[baseball_df.columns[6:]]
    # print(baseball_df)

    # need to fill NAs with values (will fill with mean of column)
    all_columns = list(baseball_df.columns)
    features = all_columns[: len(all_columns) - 1]
    # for i in features:
    #     mean_value = baseball_df[i].mean()
    #     baseball_df[i].fillna(mean_value, inplace=True)

    baseball_df.dropna(inplace=True)
    baseball_df.reset_index(inplace=True, drop=True)

    # change response to binary (1s and 0s instead of strings)

    baseball_df["winner_home_or_away"].replace(("H", "A"), (1, 0), inplace=True)
    response = all_columns[-1]
    # print(features)
    # print(response)
    run_main_rankings(baseball_df, features, response)
    run_all(baseball_df, features, response)

    # first, split the data into training and testing, in order to correctly do this, my training set will
    # be the first 80% of the data, and my test set will be the last 20% of the data (in order to preserve the notion
    # of time) because the data is ordered by game id, and thus also by date.
    #
    percent_index = round(0.8 * len(baseball_df))
    training_df = baseball_df[:percent_index]
    test_df = baseball_df[percent_index:]

    x_train = training_df[features].values
    y_train = training_df[response].values

    x_test = test_df[features].values
    y_test = test_df[response].values

    # now build a random forest classifier
    rf_model = RandomForestClassifier()
    rf_model.fit(x_train, y_train)

    y_hat = rf_model.predict(x_test)
    print("RF Accuracy: ", metrics.accuracy_score(y_test, y_hat))

    # fit a logistic regression
    logistic_model = sm.Logit(y_train, sm.add_constant(x_train)).fit()

    logit_pred = logistic_model.predict(sm.add_constant(x_test))
    logit_pred = list(map(round, logit_pred))
    print("logit Accuracy: ", metrics.accuracy_score(y_test, logit_pred))

    print(logistic_model.summary())

    # 1st, 4, 7, 11 features are significant, only keep these and re fit model
    significant_feat = []
    idx = 1
    for i in features:
        if idx == 1 or idx == 4 or idx == 7 or idx == 11:
            significant_feat.append(i)
        idx += 1

    x_train_opt = training_df[significant_feat].values
    x_test_opt = test_df[significant_feat].values

    log_optimized = sm.Logit(y_train, sm.add_constant(x_train_opt)).fit()
    log_optimized_pred = log_optimized.predict(sm.add_constant(x_test_opt))
    log_optimized_pred = list(map(round, log_optimized_pred))
    print(
        "logit optimized Accuracy: ", metrics.accuracy_score(y_test, log_optimized_pred)
    )
    print(log_optimized.summary())


if __name__ == "__main__":
    # delete any existing html files in current directory
    for f in os.listdir(os.getcwd()):
        if not f.endswith(".html"):
            continue
        os.remove(os.path.join(os.getcwd(), f))

    sys.exit(main())
