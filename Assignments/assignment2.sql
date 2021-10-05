
USE baseball;

/* ************** HISTORIC BATTING AVERAGE FOR ALL PLAYERS **************
 *  This query will create a new table "historic_batting_average" that 
 * contains the historic batting average of all batters in the 
 * "batter_counts" table. It will also check for a batter with a sum 
 * of 0 atBats and simply insert NULL as their batting average, as 
 * if they had no atBats, then they do not have a batting average
 */
DROP TABLE IF EXISTS historic_batting_average;

CREATE TABLE historic_batting_average
SELECT batter, 
CASE 
WHEN SUM(atBat) = 0
THEN NULL 					-- Need to check for when dividing by 0 in this case, NULL will be value
ELSE SUM(Hit)/SUM(atBat)
END AS Historic_Batting_Avg
FROM batter_counts bc 
GROUP BY batter;

SELECT * FROM historic_batting_average LIMIT 0,20;

/* ************** ANNUAL BATTING AVERAGE **************
 * This query creates a new table "annual_batting_average"
 * which contains the annual batting average for every player 
 * in the "batter_counts" table. It does this by Joining the 
 * "batter_counts" table with the "game" table in order to extract 
 * the year the game was played (using the YEAR() function). Then,
 * the annual batting average is calculated.
 */

DROP TABLE IF EXISTS annual_batting_average;

CREATE TABLE annual_batting_average
SELECT batter, YEAR (local_date) as local_year,
CASE 
WHEN SUM(atBat) = 0
THEN NULL 					-- Need to check for when dividing by 0, in this case, NULL will be value
ELSE SUM(Hit)/SUM(atBat)
END AS Annual_Batting_Avg
FROM batter_counts bc 
JOIN game g ON bc.game_id = g.game_id 
GROUP BY batter, YEAR (local_date);		-- want to group by batter first then year 

SELECT * FROM annual_batting_average LIMIT 0,20;


-- 100 GAME ROLLING BATTING AVERAGE ** (100 DAY IS DONE BELOW)**
/* ************** 100 GAME ROLLING BATTING AVERAGE **************
 * this query will create a new table "rolling_batting_average" which 
 * contains every player's 100 GAME rolling batting average. The "batter_counts"
 * and "game" tables are joined to combine the information such as hits, atbats, batter,
 * and local_date, which will be used to calculate the rolling batting average
 */

-- via http://teaching.mrsharky.com/code/sql/hw2.sql 

-- Create a "master" table
DROP TEMPORARY TABLE IF EXISTS t_rolling_lookup;
CREATE TEMPORARY TABLE t_rolling_lookup AS 
SELECT 
		g.game_id
		, local_date
		, batter
		, atBat
		, Hit
    FROM batter_counts bc
    JOIN game g ON g.game_id = bc.game_id
    WHERE atBat > 0
	ORDER BY batter, local_date;

CREATE UNIQUE INDEX rolling_lookup_date_game_batter_id_idx ON t_rolling_lookup (game_id, batter, local_date);
CREATE UNIQUE INDEX rolling_lookup_game_batter_id_idx ON t_rolling_lookup (game_id, batter);
CREATE UNIQUE INDEX rolling_lookup_date_batter_id_idx ON t_rolling_lookup (local_date, batter);
CREATE INDEX rolling_lookup_game_id_idx ON t_rolling_lookup (game_id);
CREATE INDEX rolling_lookup_local_date_idx ON t_rolling_lookup (local_date);
CREATE INDEX rolling_lookup_batter_idx ON t_rolling_lookup (batter);

-- Create the rolling 100 days table
DROP TABLE IF EXISTS rolling_100;
CREATE TABLE rolling_100 AS
SELECT 
		rl1.batter
		, rl1.game_id
		, rl1.local_date
		, SUM(rl2.Hit) / SUM(rl2.atBat) AS BA
	FROM t_rolling_lookup rl1
	JOIN t_rolling_lookup rl2 ON rl1.batter = rl2.batter
		AND rl2.local_date BETWEEN DATE_SUB(rl1.local_date, INTERVAL 100 DAY) AND rl1.local_date
	GROUP BY rl1.batter, rl1.game_id, rl1.local_date;