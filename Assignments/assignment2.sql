
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


ALTER TABLE game 
ADD INDEX IF NOT EXISTS(local_date);





-- CREATE games and hitters temp table to use for 100 DAY rolling avg
DROP TABLE IF EXISTS games_and_hitters;

CREATE TEMPORARY TABLE games_and_hitters
SELECT batter, Hit, atBat, DATE(local_date) as dates
FROM batter_counts bc 
JOIN game g ON g.game_id = bc.game_id 
GROUP BY batter, dates;

-- add indexes for faster querying
 ALTER TABLE games_and_hitters
 ADD INDEX IF NOT EXISTS (dates),
 ADD INDEX IF NOT EXISTS (batter);


/*CREATE temp table of cross join between all DATES and batters, so now 
rows contain all dates, rather than just the dates where the player had
a game
*/
DROP TEMPORARY TABLE IF EXISTS batters_dates;

CREATE TEMPORARY TABLE batters_dates
SELECT DISTINCT range_of_dates, batter
FROM date_range dr
CROSS JOIN batter_counts bc 
LIMIT 0,25000;							-- Had to place a limit, because this takes a very long time for entire cross join
										-- Im sure there is a more efficient way, but was not able to find one

/*
 * CREATE temp table which contains all the information needed to calculate the final
 * 100 DAY rolling average
 */
DROP TABLE IF EXISTS final_rolling;

CREATE TEMPORARY TABLE final_rolling
SELECT range_of_dates, bd.batter, COALESCE(atBat,0) as "atBat", COALESCE (Hit,0) as "Hit"
FROM batters_dates bd
LEFT JOIN games_and_hitters gh ON gh.dates = bd.range_of_dates
GROUP BY bd.batter, range_of_dates;

/* ************** 100 DAY ROLLING BATTING AVERAGE **************
 * this query will create a new table "final_100day_rolling_avg" which 
 * contains every player's 100 day rolling batting average. 
 */

DROP TABLE IF EXISTS final_100day_rolling_avg;

CREATE TABLE final_100day_rolling_avg
SELECT batter, Hit, atBat,
CASE 
WHEN atBat = 0			-- Need to check for when dividing by 0, in this case, NULL will be value, and avg will be the same as last non null row above
THEN NULL			
ELSE
SUM(Hit) OVER(PARTITION BY batter ORDER BY batter, range_of_dates ROWS BETWEEN 100 PRECEDING AND CURRENT ROW) / 
SUM(atBat) OVER(PARTITION BY batter ORDER BY batter, range_of_dates ROWS BETWEEN 100 PRECEDING AND CURRENT ROW)
END AS 100_day_rolling_avg, range_of_dates
FROM final_rolling;


SELECT * FROM final_100day_rolling_avg;





