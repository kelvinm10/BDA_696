USE baseball;


DROP TEMPORARY TABLE IF EXISTS 5game_rolling_k_per_nine;

# Rolling K/9 for past 5 starts
CREATE TEMPORARY TABLE 5game_rolling_k_per_nine
SELECT g.game_id,pitcher, 
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN 0
	ELSE ((SUM(Strikeout) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_DP`)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_TP`)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING))*9) /
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
END AS '5_game_rolling_K/9'
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 5game_rolling_k_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 5game_rolling_k_per_nine(game_id);






DROP TEMPORARY TABLE IF EXISTS historic_k_per_nine;
# historic strikeouts per 9
CREATE TEMPORARY TABLE historic_k_per_nine
SELECT g.game_id, pitcher,
((SUM(Strikeout) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_DP`) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_TP`) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) * 9) / 
		 SUM(outsPlayed/3)  OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
AS 'K/9'
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON historic_k_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON historic_k_per_nine(game_id);

DROP TEMPORARY TABLE IF EXISTS 5game_rolling_hr_per_nine;
# rolling hr/9 for past 5 starts
CREATE TEMPORARY TABLE 5game_rolling_hr_per_nine
SELECT g.game_id, pitcher,
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN SUM(Home_Run * 9 / 0.1)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
	ELSE SUM(Home_Run*9)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)  / 
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
END AS "5_game_rolling_hr/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 5game_rolling_hr_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 5game_rolling_hr_per_nine(game_id);


DROP TEMPORARY TABLE IF EXISTS historic_hr_per_nine;
# historic hr per 9
CREATE TEMPORARY TABLE historic_hr_per_nine
SELECT g.game_id, pitcher,
SUM(Home_Run*9) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) / 
SUM(outsPlayed/3)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
AS "HR/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON historic_hr_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON historic_hr_per_nine(game_id);


DROP TEMPORARY TABLE IF EXISTS 5game_rolling_hits_per_nine;
# rolling hits / 9 for past 5 starts
CREATE TEMPORARY TABLE 5game_rolling_hits_per_nine
SELECT g.game_id, pitcher,
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN SUM(Hit * 9 / 0.1) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
	ELSE SUM(Hit*9) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) / 
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
END AS "5_game_rolling_h/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 5game_rolling_hits_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 5game_rolling_hits_per_nine(game_id);


DROP TEMPORARY TABLE IF EXISTS historic_hits_per_nine;
#historic hits / 9 
CREATE TEMPORARY TABLE historic_hits_per_nine
SELECT g.game_id, pitcher, 
SUM(Hit*9) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) / 
SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
AS "hits/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON historic_hits_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON historic_hits_per_nine(game_id);


DROP TEMPORARY TABLE IF EXISTS 5game_rolling_oba;
# rolling 5 game opponents batting average (OBA) (Hits / at bats)
CREATE TEMPORARY TABLE 5game_rolling_oba
SELECT g.game_id, pitcher, 
CASE 
	WHEN SUM(atBat) = 0
	THEN 0
	ELSE SUM(Hit) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING) / 
		 SUM(atBat) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING)
END AS "5_game_rolling_OBA"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 5game_rolling_oba(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 5game_rolling_oba(game_id);


DROP TEMPORARY TABLE IF EXISTS historic_oba;
#historic OBA
CREATE TEMPORARY TABLE historic_oba
SELECT g.game_id, pitcher, local_date,
SUM(Hit) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) / 
SUM(atBat) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
AS "historic_OBA"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON historic_oba(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON historic_oba(game_id);

DROP TEMPORARY TABLE IF EXISTS 10game_rolling_teamBA;
# rolling 10 game team batting average
CREATE TEMPORARY TABLE 10game_rolling_teamBA
SELECT game_id, team_id,
SUM(Hit) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
SUM(atBat)OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS "10_day_rolling_BA"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 10game_rolling_teamBA(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_teamBA(game_id);


DROP TEMPORARY TABLE IF EXISTS 10game_rolling_teamRuns;
# rolling 10 day average of runs scored by each team
CREATE TEMPORARY TABLE 10game_rolling_teamRuns
SELECT game_id, team_id,
AVG(finalScore) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS "10_game_rolling_runs_scored"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 10game_rolling_teamRuns(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_teamRuns(game_id);


DROP TABLE IF EXISTS final_diff_features;
# NOW JOIN ALL TABLES TOGETHER TO ONE
CREATE TABLE final_diff_features
SELECT g.game_id, g.home_team_id, g.away_team_id, g.home_pitcher, g.away_pitcher, 
	   rkp9.`5_game_rolling_K/9` - rkp9a.`5_game_rolling_K/9` AS rolling_k9_diff,
	   hkp9.`K/9` -  hkp9a.`K/9` AS historic_k9_diff, 
	   rhrp9.`5_game_rolling_hr/9` - rhrp9a.`5_game_rolling_hr/9` AS rolling_hr9_diff,
	   hhrp9.`HR/9` - hhrp9a.`HR/9` AS historic_HR9_diff, 
	   rhp9.`5_game_rolling_h/9` - rhp9a.`5_game_rolling_h/9` AS rolling_hits9_diff,
	   hhp9.`hits/9` - hhp9a.`hits/9` AS historic_hits9_diff,
	   roba.`5_game_rolling_OBA` - roba1.`5_game_rolling_OBA` AS rolling_oba_diff,
	   hoba.`historic_OBA` - hoba1.`historic_OBA` AS historic_oba_diff,
	   rtba.`10_day_rolling_BA`- rtba1.`10_day_rolling_BA` AS rolling_BA_diff, 
	   rtr.`10_game_rolling_runs_scored` AS home_team_rolling_avgrunsScored, 
	   rtr1.`10_game_rolling_runs_scored` AS away_team_rolling_avgrunsScored, winner_home_or_away
FROM boxscore b 
JOIN game 							g 			ON g.game_id = b.game_id 
JOIN 5game_rolling_k_per_nine 		rkp9 		ON g.game_id = rkp9.game_id AND g.home_pitcher = rkp9.pitcher
JOIN 5game_rolling_k_per_nine 		rkp9a 		ON g.game_id = rkp9a.game_id AND g.away_pitcher = rkp9a.pitcher
JOIN historic_k_per_nine	  		hkp9 		ON g.game_id = hkp9.game_id AND g.home_pitcher = hkp9.pitcher
JOIN historic_k_per_nine 	  		hkp9a 		ON g.game_id = hkp9a.game_id AND g.away_pitcher = hkp9a.pitcher
JOIN 5game_rolling_hr_per_nine		rhrp9		ON g.game_id = rhrp9.game_id AND g.home_pitcher = rhrp9.pitcher
JOIN 5game_rolling_hr_per_nine		rhrp9a		On g.game_id = rhrp9a.game_id AND g.away_pitcher = rhrp9a.pitcher
JOIN historic_hr_per_nine			hhrp9 		ON g.game_id = hhrp9.game_id AND g.home_pitcher = hhrp9.pitcher
JOIN historic_hr_per_nine 			hhrp9a		ON g.game_id = hhrp9a.game_id AND g.away_pitcher = hhrp9a.pitcher
JOIN 5game_rolling_hits_per_nine	rhp9		ON g.game_id = rhp9.game_id AND g.home_pitcher = rhp9.pitcher
JOIN 5game_rolling_hits_per_nine	rhp9a		ON g.game_id = rhp9a.game_id AND g.away_pitcher = rhp9a.pitcher
JOIN historic_hits_per_nine			hhp9		ON g.game_id = hhp9.game_id AND g.home_pitcher = hhp9.pitcher
JOIN historic_hits_per_nine			hhp9a		ON g.game_id = hhp9a.game_id AND g.away_pitcher = hhp9a.pitcher
JOIN 5game_rolling_oba				roba		ON g.game_id = roba.game_id AND g.home_pitcher = roba.pitcher
JOIN 5game_rolling_oba				roba1		ON g.game_id = roba1.game_id AND g.away_pitcher = roba1.pitcher
JOIN historic_oba					hoba 		ON g.game_id = hoba.game_id AND g.home_pitcher = hoba.pitcher
JOIN historic_oba					hoba1 		ON g.game_id = hoba1.game_id AND g.away_pitcher = hoba1.pitcher
JOIN 10game_rolling_teamBA			rtba		ON g.game_id = rtba.game_id AND g.home_team_id = rtba.team_id
JOIN 10game_rolling_teamBA			rtba1		ON g.game_id = rtba1.game_id AND g.away_team_id = rtba1.team_id 
JOIN 10game_rolling_teamRuns		rtr			ON g.game_id = rtr.game_id AND g.home_team_id = rtr.team_id
JOIN 10game_rolling_teamRuns		rtr1		ON g.game_id = rtr1.game_id AND g.away_team_id = rtr1.team_id
ORDER BY g.game_id;


SELECT * FROM final_diff_features fdf2 


