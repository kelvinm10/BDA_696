
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

/* ************** 30 DAY ROLLING BATTING AVERAGE **************
 * this query will create a new table "rolling_batting_average" which 
 * contains every player's 30 day rolling batting average. The "batter_counts"
 * and "game" tables are joined to combine the information such as hits, atbats, batter,
 * and local_date, which will be used to calculate the rolling batting average
 */

DROP TABLE IF EXISTS rolling_batting_average;

CREATE TABLE rolling_batting_average
SELECT batter, Hit, atBat,
CASE 
WHEN SUM(atBat) = 0			-- Need to check for when dividing by 0, in this case, NULL will be value
THEN NULL 					
ELSE
SUM(Hit) OVER(PARTITION BY batter ORDER BY batter, local_date ROWS BETWEEN 100 PRECEDING AND CURRENT ROW) / 
SUM(atBat) OVER(PARTITION BY batter ORDER BY batter, local_date ROWS BETWEEN 100 PRECEDING AND CURRENT ROW)
END AS 100_day_rolling_avg, local_date 
FROM game g 
JOIN batter_counts bc ON g.game_id = bc.game_id 
GROUP BY batter, local_date;		-- want to group by batter first, then date



SELECT * FROM rolling_batting_average LIMIT 0,1100;







