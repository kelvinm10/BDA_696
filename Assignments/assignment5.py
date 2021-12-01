import os
import sys
import time

import pandas as pd
import sqlalchemy
import statsmodels.api as sm
from assignment4 import run_main_rankings
from flask import Flask
from midterm import run_all
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)


def main():
    # db_user = "root"
    # db_pass = ""  # pragma: allowlist secret
    # db_host = "localhost"
    # db_database = "baseball"
    # # connect_string = (
    # #     f"mariadb+mariadbconnector://{db_user}:{db_pass}@{db_host}/{db_database}"
    # # )

    # db is the name of the service of the mariadb container in the compose file
    connect_string = "mysql+mysqlconnector://root:example@db:3306/baseball"  # pragma: allowlist secret

    # the first time connecting to the mariadb connector, it will take a few minutes to
    # connect (due to inserting and reading baseball.sql database), this loop will continue to try to
    # connect
    # this sleep function allows the mariadb container to fully spin up when creating the container for the
    # first time. Can lower the sleep value once re running already built container
    time.sleep(600)
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
            print("connection failed, retrying...")

    # there are some empty strings in our response (exhibition game ending in a tie) drop these rows
    baseball_df = df[df["winner_home_or_away"] != ""]
    baseball_df.reset_index(inplace=True)
    # print(baseball_df)
    baseball_df = baseball_df[baseball_df.columns[6:]]
    # print(baseball_df)

    # Drop all NA values (I decided to drop, because when a stat had NA, then it was that pitchers or teams
    # first game, so they had no previous game stats, thus doing something like filling in the na with mean would
    # not necessarily make sense)
    all_columns = list(baseball_df.columns)
    features = all_columns[: len(all_columns) - 1]

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

    # both models are performing pretty poorly, but the logistic regression model seems to perform slightly better than
    # the random forest. If I had more time, I would try to hypertune the parameters for each of the models using grid
    # search or randomized search in order to try to improve the accuracy. I would also try to engineer better features
    # in sql, as it seems that the features that I chose and calculated were not very effective in predicting a win or
    # a loss for the home team. I thought that these features would be effective in predicting who would win the game,
    # because I took the difference in both the home and away pitcher's stats such as rolling strikeouts per nine
    # innings, rolling home runs allowed per nine innings, etc. I did the difference between the home and away pitcher
    # stats, because I thought this would capture the difference in skill level between the two pitchers, and thus
    # provide an advantage to the home or away team, but maybe there is something that I am missing. I will explore
    # further and do all of these steps (and more) for the final project in order to try to improve my final model.


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
