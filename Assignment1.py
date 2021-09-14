import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def main():
    iris_df = pd.read_csv(
        "data/iris.data",
        names=["sepal.length", "sepal.width", "petal.length", "petal.width", "species"],
    )
    # pandas function describe gives overall statistics of dataframe
    print(iris_df.describe())
    print()

    # using numpy, to get statistics
    print("Mean of sepal Length:", np.mean(iris_df["sepal.length"]))
    print("Min of Sepal Length", np.min(iris_df["sepal.length"]))
    print("Max of Sepal Length:", np.max(iris_df["sepal.length"]))
    print("75% quantile of Sepal Length", np.quantile(iris_df["sepal.length"], 0.75))

    # plot different classes against one another
    # scatter plot of petal width vs petal length color coded by species
    fig1 = px.scatter(iris_df, x="petal.width", y="petal.length", color="species")
    fig1.show()

    # violin plot of sepal length color coded by species
    fig2 = px.violin(iris_df, x="sepal.length", box=True, color="species")
    fig2.show()

    # scatter matrix of all features in the data
    fig3 = px.scatter_matrix(
        iris_df,
        dimensions=["sepal.length", "sepal.width", "petal.length", "petal.width"],
        color="species",
    )
    fig3.show()

    # boxplot of petal width for each species
    fig4 = px.box(iris_df, x="species", y="petal.width")
    fig4.show()

    # density heatmap of petal width vs petal length
    fig5 = px.density_heatmap(
        iris_df,
        x="petal.width",
        y="petal.length",
        marginal_x="rug",
        marginal_y="histogram",
    )
    fig5.show()

    # analyze and build models with sklearn
    # First Split up response from features
    X = iris_df.iloc[:, 0:4].values
    y = iris_df["species"].values
    # Random Forest Pipeline
    forest_pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("forest", RandomForestClassifier(random_state=1)),
        ]
    )
    forest_pipe.fit(X, y)
    print()
    print("Random Forest Training Accuracy:", forest_pipe.score(X, y))
    # Logistic Regression Pipeline
    log_pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("log", LogisticRegression(multi_class="multinomial", random_state=2)),
        ]
    )
    log_pipe.fit(X, y)
    print("Logistic Regression Training Accuracy:", round(log_pipe.score(X, y), 2))

    # K Nearest Neighbors Pipeline
    knn_pipe = Pipeline([("scaler", StandardScaler()), ("knn", KNeighborsClassifier())])
    knn_pipe.fit(X, y)
    print("KNN Training Accuracy", round(knn_pipe.score(X, y), 2))


if __name__ == "__main__":
    main()
