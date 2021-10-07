import os

from pyspark import StorageLevel, keyword_only
from pyspark.ml import Transformer
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql import SparkSession


class rollingTransform(Transformer, DefaultParamsReadable, DefaultParamsWritable):
    @keyword_only
    def __init__(self):
        super(rollingTransform, self).__init__()
        kwargs = self._input_kwargs
        self.setParams(**kwargs)
        return

    @keyword_only
    def setParams(self):
        kwargs = self._input_kwargs
        return self._set(**kwargs)

    def _transform(self, spark, batter_counts, game):

        batter_counts.createOrReplaceTempView("batter_df")
        game.createOrReplaceTempView("game_df")

        spark.sql(
            """
        CREATE TEMPORARY VIEW t_rolling_lookup AS
        SELECT g.game_id, local_date, batter, atBat, Hit
        FROM batter_df bc
        JOIN game_df g ON g.game_id = bc.game_id
        WHERE atBat > 0
        ORDER BY batter, local_date;
            """
        )
        spark.sql("DROP TABLE IF EXISTS rolling_100;")
        spark.sql(
            """
        CREATE TEMPORARY VIEW rolling_100 AS
        SELECT rl1.batter, rl1.game_id, rl1.local_date, SUM(rl2.Hit) / SUM(rl2.atBat) AS BA
        FROM t_rolling_lookup rl1
        JOIN t_rolling_lookup rl2 ON rl1.batter = rl2.batter AND rl2.local_date BETWEEN DATE_SUB(rl1.local_date, 100)
        AND rl1.local_date GROUP BY rl1.batter, rl1.game_id, rl1.local_date;
            """
        )

        result = spark.sql("SELECT * FROM rolling_100 ORDER BY batter, local_date")
        return result


def main():
    jar_path = (
        "/.venv/lib/python3.9/site-packages/pyspark/jars/mariadb-java-client-2.7.4.jar"
    )
    # get path of jar file on system
    spark = (
        SparkSession.builder.config(
            "spark.jars", os.path.abspath(os.path.join("", os.pardir)) + jar_path
        )
        .master("local")
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
    batter_counts_df = reader.option("dbtable", tablename_list[0]).load()
    game_df = reader.option("dbtable", tablename_list[1]).load()
    batter_counts_df.persist(StorageLevel.DISK_ONLY)
    game_df.persist(StorageLevel.DISK_ONLY)
    # Create transformer instance, then transform the dataframes into one rolling_df
    # which contains the 100 day rolling average
    transformer = rollingTransform()
    rolling_df = transformer._transform(spark, batter_counts_df, game_df)
    rolling_df.show()


if __name__ == "__main__":
    main()
