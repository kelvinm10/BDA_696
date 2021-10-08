from pyspark import keyword_only
from pyspark.ml import Transformer


class rollingTransform(Transformer):
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

    def _transform(self, spark):
        # SQL code via Professor from site: http://teaching.mrsharky.com/code/sql/hw2.sql
        # create temp view of a rolling lookup table by joining game table to itself
        spark.sql(
            """
        CREATE TEMPORARY VIEW t_rolling_lookup AS
        SELECT g.game_id, local_date, batter, atBat, Hit
        FROM batter_counts bc
        JOIN game g ON g.game_id = bc.game_id
        WHERE atBat > 0
        ORDER BY batter, local_date;
            """
        )
        spark.sql("DROP TABLE IF EXISTS rolling_100;")
        # create rolling 100 average table, by using the DATE_SUB method and using 100 days
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
        # return new table from command above
        return result
