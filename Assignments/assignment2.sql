USE baseball;
SHOW TABLES;

SELECT * 
FROM batter_counts 
LIMIT 0,60;

SELECT * 
FROM battersInGame 
LIMIT 0,40;

SELECT batter, SUM(Hit)/SUM(atBat) Historic_Batting_Avg
FROM batter_counts bc 
GROUP BY batter 
LIMIT 0,100;


