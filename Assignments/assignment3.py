import os

from pyspark import StorageLevel
from pyspark.sql import SparkSession
from rollingTransform import rollingTransform


def main():
    jar_path = "/data/mariadb-java-client-2.7.4.jar"
    # get path of jar file on system
    spark = (
        SparkSession.builder.master("local[*]")
        .config("spark.jars", os.path.abspath(os.path.join("", os.pardir)) + jar_path)
        .getOrCreate()
    )

    # connect to mariadb with spark and load batter_counts and game
    url = "jdbc:mysql://localhost:3306/baseball"
    tablename_list = ["batter_counts", "game"]
    reader = (
        spark.read.format("jdbc")
        .option("url", url)
        .option("user", "root")
        .option("password", "")
    )
    # Read batter counts table, then create temp view
    batter_counts_df = reader.option("dbtable", tablename_list[0]).load()
    batter_counts_df.createOrReplaceTempView("batter_counts")

    # read game table, then crceate temp view
    game_df = reader.option("dbtable", tablename_list[1]).load()
    game_df.createOrReplaceTempView("game")

    # persist
    batter_counts_df.persist(StorageLevel.DISK_ONLY)
    game_df.persist(StorageLevel.DISK_ONLY)

    # Create transformer instance, then transform the dataframes into one rolling_df
    # which contains the 100 day rolling average
    transformer = rollingTransform()
    rolling_df = transformer.transform(spark)
    rolling_df.show()


if __name__ == "__main__":
    main()
