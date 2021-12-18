USE baseball;



# Rolling K/9 for past 10 starts
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_k_per_nine
SELECT g.game_id,pitcher, 
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN 0
	ELSE ((SUM(Strikeout) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_DP`)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) + 
		 SUM(`Strikeout_-_TP`)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING))*9) /
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
END AS '10_game_rolling_K/9'
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10game_rolling_k_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_k_per_nine(game_id);








# DROP TEMPORARY TABLE IF EXISTS historic_k_per_nine;
# historic strikeouts per 9
CREATE TEMPORARY TABLE IF NOT EXISTS historic_k_per_nine
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

# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_hr_per_nine;
# rolling hr/9 for past 10 starts
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_hr_per_nine
SELECT g.game_id, pitcher,
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN SUM(Home_Run * 9 / 0.1)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
	ELSE SUM(Home_Run*9)OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)  / 
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
END AS "10_game_rolling_hr/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10game_rolling_hr_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_hr_per_nine(game_id);


# DROP TEMPORARY TABLE IF EXISTS historic_hr_per_nine;
# historic hr per 9
CREATE TEMPORARY TABLE IF NOT EXISTS historic_hr_per_nine
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


# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_hits_per_nine;
# rolling hits / 9 for past 5 starts
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_hits_per_nine
SELECT g.game_id, pitcher,
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN SUM(Hit * 9 / 0.1) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
	ELSE SUM(Hit*9) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
		 SUM(outsPlayed/3) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
END AS "10_game_rolling_h/9"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10game_rolling_hits_per_nine(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_hits_per_nine(game_id);


# DROP TEMPORARY TABLE IF EXISTS historic_hits_per_nine;
#historic hits / 9 
CREATE TEMPORARY TABLE IF NOT EXISTS historic_hits_per_nine
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

# 10 game rolling whip (walks + hits)/ Innings Pitched
# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_whip;
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_whip
SELECT g.game_id, pitcher, 
CASE 
	WHEN SUM(outsPlayed) = 0
	THEN SUM(Hit + Walk + Intent_Walk) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 0.1
	ELSE SUM(Hit + Walk + Intent_Walk) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
		 SUM(outsPlayed / 3) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
END AS "10_game_rolling_whip"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10game_rolling_whip(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_whip(game_id);



# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_oba;
# rolling 5 game opponents batting average (OBA) (Hits / at bats)
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_oba
SELECT g.game_id, pitcher, 
CASE 
	WHEN SUM(atBat) = 0
	THEN 0
	ELSE SUM(Hit) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
		 SUM(atBat) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date  ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
END AS "10_game_rolling_OBA"
FROM pitcher_counts pc 
JOIN game g 
ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10game_rolling_oba(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_oba(game_id);


# DROP TEMPORARY TABLE IF EXISTS historic_oba;
#historic OBA
CREATE TEMPORARY TABLE IF NOT EXISTS historic_oba
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

# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_teamBA;
# rolling 10 game team batting average
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_teamBA
SELECT game_id, team_id,
SUM(Hit) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
SUM(atBat)OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS "10_day_rolling_BA"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 10game_rolling_teamBA(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_teamBA(game_id);


# DROP TEMPORARY TABLE IF EXISTS 10game_rolling_teamRuns;
# rolling 10 day average of runs scored by each team
CREATE TEMPORARY TABLE IF NOT EXISTS 10game_rolling_teamRuns
SELECT game_id, team_id,
AVG(finalScore) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS "10_game_rolling_runs_scored"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 10game_rolling_teamRuns(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10game_rolling_teamRuns(game_id);

# rolling 20 game bullpen whip
# DROP TEMPORARY TABLE IF EXISTS 20game_rolling_bullwhip;
CREATE TEMPORARY TABLE IF NOT EXISTS 20game_rolling_bullwhip
SELECT game_id, team_id,
SUM(bullpenWalk + bullpenIntentWalk + bullpenHit)OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 21 PRECEDING AND 1 PRECEDING) /
SUM(bullpenOutsPlayed / 3) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 21 PRECEDING AND 1 PRECEDING) AS "20_game_bullpen_whip"
FROM team_pitching_counts tpc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 20game_rolling_bullwhip(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 20game_rolling_bullwhip(game_id);



# DROP TEMPORARY TABLE IF EXISTS rolling_season_win_pct;
# rolling win percentage for a team throughout the whole season (rolling over 162 games)
CREATE TEMPORARY TABLE IF NOT EXISTS rolling_season_win_pct
SELECT game_id, team_id, win,
AVG(win) OVER(PARTITION BY team_id ORDER BY team_id, game_id ROWS BETWEEN 162 PRECEDING AND 1 PRECEDING) AS "rolling_win_pct"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON rolling_season_win_pct(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON rolling_season_win_pct(game_id);

CREATE TEMPORARY TABLE IF NOT EXISTS 20rolling_avgruns_allowed
SELECT game_id, team_id, opponent_finalScore,
AVG(opponent_finalScore) OVER (PARTITION BY team_id ORDER BY team_id ,game_id ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS "20rolling_avgruns_allowed"
FROM team_batting_counts tbc 
GROUP BY team_id, game_id;

CREATE INDEX IF NOT EXISTS team_idx ON 20rolling_avgruns_allowed(team_id);
CREATE INDEX IF NOT EXISTS game_id_idx ON 20rolling_avgruns_allowed(game_id);

# 10 game rolling FIP
# DROP TEMPORARY TABLE IF EXISTS 10rolling_fip;
CREATE TEMPORARY TABLE IF NOT EXISTS 10rolling_fip
SELECT g.game_id, pitcher,
SUM(Home_Run * 13 + 3 * (Hit_By_Pitch + Walk) - 2 * (Strikeout + `Strikeout_-_DP` + `Strikeout_-_TP`)) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) / 
(SUM(outsPlayed / 3) OVER (PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) + 3.2) 
AS "10rolling_fip"
FROM pitcher_counts pc 
JOIN game g ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10rolling_fip(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10rolling_fip(game_id);

# strikeout to walk ratio
# DROP TEMPORARY TABLE IF EXISTS 10rolling_kbb;
CREATE TEMPORARY TABLE IF NOT EXISTS 10rolling_kbb
SELECT g.game_id, pitcher, 
SUM((Strikeout + `Strikeout_-_DP` + `Strikeout_-_TP`) / (NULLIF((Walk + Intent_Walk), 0))) OVER(PARTITION BY pitcher ORDER BY pitcher, g.game_id, local_date ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING)
AS "10rolling_kbb"
FROM pitcher_counts pc 
JOIN game g ON g.game_id = pc.game_id 
WHERE startingPitcher = 1
GROUP BY pitcher, g.game_id, local_date;

CREATE INDEX IF NOT EXISTS pitcher_idx ON 10rolling_kbb(pitcher);
CREATE INDEX IF NOT EXISTS game_id_idx ON 10rolling_kbb(game_id);

# TEMPERATURE DIFFERENCE FROM PREVIOUS GAME
CREATE TEMPORARY TABLE IF NOT EXISTS temperature_difference
SELECT g.game_id, tbc.team_id,
CAST(REPLACE(temp, " degrees", "") as int ) - 
LAG(CAST(REPLACE(temp, " degrees", "") as int ),1) OVER(PARTITION BY tbc.team_id ORDER BY tbc.team_id, g.game_id) AS temp_diff
FROM boxscore b
JOIN game g ON g.game_id = b.game_id
JOIN team_batting_counts tbc ON tbc.game_id = b.game_id
ORDER BY tbc.team_id , g.game_id;

CREATE INDEX IF NOT EXISTS game_idx ON temperature_difference(game_id);
CREATE INDEX IF NOT EXISTS team_idx ON temperature_difference(team_id);

# WIND DIFFERENCE FROM PREVIOUS GAME

# DROP TEMPORARY TABLE IF EXISTS wind_cleaned;
CREATE TEMPORARY TABLE IF NOT EXISTS wind_cleaned
SELECT g.game_id, tbc.team_id,
REPLACE(wind, "Indoors", 0) AS wind
FROM boxscore b
JOIN game g ON g.game_id = b.game_id
JOIN team_batting_counts tbc ON tbc.game_id = b.game_id
ORDER BY tbc.team_id , g.game_id;

CREATE INDEX IF NOT EXISTS game_idx ON wind_cleaned(game_id);
CREATE INDEX IF NOT EXISTS team_idx ON wind_cleaned(team_id);

CREATE TEMPORARY TABLE IF NOT EXISTS wind_difference
SELECT game_id, team_id, 
CAST(REPLACE(wind, " mph", "") AS INT) - 
LAG(CAST(REPLACE(wind, " mph", "") AS INT ),1) OVER(PARTITION BY team_id ORDER BY team_id, game_id) AS wind_diff
FROM wind_cleaned wc 
ORDER BY team_id, game_id;

CREATE INDEX IF NOT EXISTS game_idx ON wind_difference(game_id);
CREATE INDEX IF NOT EXISTS team_idx ON wind_difference(team_id);



# NOW JOIN ALL TABLES TOGETHER TO ONE, IN DOING THIS, I WILL CALCULATE THE DIFFERENCE BETWEEN THE HOME AND AWAY PITCHER STATS
# IN ORDER TO CAPTURE POSSIBLE ADVANTAGES THAT THE HOME OR AWAY TEAM HAS IN TERMS OF THEIR STARTING PITCHER.
# DROP TABLE IF EXISTS final_diff_features;
CREATE TABLE IF NOT EXISTS final_diff_features
SELECT g.game_id, g.home_team_id, g.away_team_id, g.home_pitcher, g.away_pitcher, YEAR(g.local_date) as `Year`,
	   rkp9.`10_game_rolling_K/9` - rkp9a.`10_game_rolling_K/9` AS rolling_k9_diff,
	   hkp9.`K/9` -  hkp9a.`K/9` AS historic_k9_diff, 
	   rhrp9.`10_game_rolling_hr/9` - rhrp9a.`10_game_rolling_hr/9` AS rolling_hr9_diff,
	   hhrp9.`HR/9` - hhrp9a.`HR/9` AS historic_HR9_diff, 
	   rhp9.`10_game_rolling_h/9` - rhp9a.`10_game_rolling_h/9` AS rolling_hits9_diff,
	   hhp9.`hits/9` - hhp9a.`hits/9` AS historic_hits9_diff,
	   roba.`10_game_rolling_OBA` - roba1.`10_game_rolling_OBA` AS rolling_oba_diff,
	   hoba.`historic_OBA` - hoba1.`historic_OBA` AS historic_oba_diff,
	   rwhip.`10_game_rolling_whip` - rwhipa.`10_game_rolling_whip` AS rolling_whip_diff,
	   hfip.`10rolling_fip` - afip.`10rolling_fip` AS rolling10_fip_diff,
	   hkbb.`10rolling_kbb` - akbb.`10rolling_kbb` AS rolling10_kbb_diff,
	   rtba.`10_day_rolling_BA`- rtba1.`10_day_rolling_BA` AS rolling_BA_diff, 
	   bull.`20_game_bullpen_whip` - bulla.`20_game_bullpen_whip` AS rolling_bullwhip_diff,
	   rtr.`10_game_rolling_runs_scored` - rtr1.`10_game_rolling_runs_scored` AS rolling_avgrunsScored_diff, 
	   rwpcth.rolling_win_pct - rwpcta.rolling_win_pct AS diff_team_win_pct,
	   tempd.temp_diff AS temp_diff_home,
	   tempda.temp_diff AS temp_diff_away,
	   windh.wind_diff AS wind_diff_home,
	   winda.wind_diff AS wind_diff_away,
	   winner_home_or_away
FROM boxscore b 
JOIN game 							g 			ON g.game_id = b.game_id 
JOIN 10game_rolling_k_per_nine 		rkp9 		ON g.game_id = rkp9.game_id AND g.home_pitcher = rkp9.pitcher
JOIN 10game_rolling_k_per_nine 		rkp9a 		ON g.game_id = rkp9a.game_id AND g.away_pitcher = rkp9a.pitcher
JOIN historic_k_per_nine	  		hkp9 		ON g.game_id = hkp9.game_id AND g.home_pitcher = hkp9.pitcher
JOIN historic_k_per_nine 	  		hkp9a 		ON g.game_id = hkp9a.game_id AND g.away_pitcher = hkp9a.pitcher
JOIN 10game_rolling_hr_per_nine		rhrp9		ON g.game_id = rhrp9.game_id AND g.home_pitcher = rhrp9.pitcher
JOIN 10game_rolling_hr_per_nine		rhrp9a		On g.game_id = rhrp9a.game_id AND g.away_pitcher = rhrp9a.pitcher
JOIN historic_hr_per_nine			hhrp9 		ON g.game_id = hhrp9.game_id AND g.home_pitcher = hhrp9.pitcher
JOIN historic_hr_per_nine 			hhrp9a		ON g.game_id = hhrp9a.game_id AND g.away_pitcher = hhrp9a.pitcher
JOIN 10game_rolling_hits_per_nine	rhp9		ON g.game_id = rhp9.game_id AND g.home_pitcher = rhp9.pitcher
JOIN 10game_rolling_hits_per_nine	rhp9a		ON g.game_id = rhp9a.game_id AND g.away_pitcher = rhp9a.pitcher
JOIN historic_hits_per_nine			hhp9		ON g.game_id = hhp9.game_id AND g.home_pitcher = hhp9.pitcher
JOIN historic_hits_per_nine			hhp9a		ON g.game_id = hhp9a.game_id AND g.away_pitcher = hhp9a.pitcher
JOIN 10game_rolling_oba				roba		ON g.game_id = roba.game_id AND g.home_pitcher = roba.pitcher
JOIN 10game_rolling_oba				roba1		ON g.game_id = roba1.game_id AND g.away_pitcher = roba1.pitcher
JOIN historic_oba					hoba 		ON g.game_id = hoba.game_id AND g.home_pitcher = hoba.pitcher
JOIN historic_oba					hoba1 		ON g.game_id = hoba1.game_id AND g.away_pitcher = hoba1.pitcher
JOIN 10game_rolling_teamBA			rtba		ON g.game_id = rtba.game_id AND g.home_team_id = rtba.team_id
JOIN 10game_rolling_teamBA			rtba1		ON g.game_id = rtba1.game_id AND g.away_team_id = rtba1.team_id 
JOIN 10game_rolling_teamRuns		rtr			ON g.game_id = rtr.game_id AND g.home_team_id = rtr.team_id
JOIN 10game_rolling_teamRuns		rtr1		ON g.game_id = rtr1.game_id AND g.away_team_id = rtr1.team_id
JOIN 10game_rolling_whip			rwhip 		ON g.game_id = rwhip.game_id AND g.home_pitcher = rwhip.pitcher
JOIN 10game_rolling_whip			rwhipa 		ON g.game_id = rwhipa.game_id AND g.away_pitcher = rwhipa.pitcher
JOIN rolling_season_win_pct			rwpcth		ON g.game_id = rwpcth.game_id AND g.home_team_id = rwpcth.team_id
JOIN rolling_season_win_pct			rwpcta 		ON g.game_id = rwpcta.game_id AND g.away_team_id = rwpcta.team_id
JOIN 20game_rolling_bullwhip		bull		ON g.game_id = bull.game_id AND g.home_team_id = bull.team_id
JOIN 20game_rolling_bullwhip		bulla		ON g.game_id = bulla.game_id AND g.away_team_id = bulla.team_id
JOIN 10rolling_fip					hfip 		ON g.game_id = hfip.game_id AND g.home_pitcher = hfip.pitcher
JOIN 10rolling_fip					afip		ON g.game_id = afip.game_id AND g.away_pitcher = afip.pitcher
JOIN 10rolling_kbb					hkbb		ON g.game_id = hkbb.game_id AND g.home_pitcher = hkbb.pitcher
JOIN 10rolling_kbb					akbb		ON g.game_id = akbb.game_id AND g.away_pitcher = akbb.pitcher
JOIN temperature_difference			tempd		ON g.game_id = tempd.game_id AND g.home_team_id = tempd.team_id
JOIN temperature_difference 		tempda 		ON g.game_id = tempda.game_id AND g.away_team_id = tempda.team_id	
JOIN wind_difference				windh 		ON g.game_id = windh.game_id AND g.home_team_id = windh.team_id
JOIN wind_difference 				winda 		ON g.game_id = winda.game_id AND g.away_team_id = winda.team_id
ORDER BY g.game_id;


#CREATE A TABLE WITH ALL THESE STATS BUT WITH NO TRANSFORMATIONS
# DROP TABLE IF EXISTS final_individual_features;
/*
CREATE TABLE IF NOT EXISTS final_individual_features
SELECT g.game_id, g.home_team_id, g.away_team_id, g.home_pitcher, g.away_pitcher, YEAR(g.local_date) as `Year`,
	   rkp9.`10_game_rolling_K/9` AS rolling_k9_home,
	   rkp9a.`10_game_rolling_K/9` AS rolling_k9_away,
	   hkp9.`K/9` AS historic_k9_home,
	   hkp9a.`K/9`AS historic_k9_away,
	   rhrp9.`10_game_rolling_hr/9` AS rolling_hr9_home,
	   rhrp9a.`10_game_rolling_hr/9` AS rolling_hr9_away,
	   hhrp9.`HR/9` AS historic_HR9_home,
	   hhrp9a.`HR/9`AS historic_hr9_away,
	   rhp9.`10_game_rolling_h/9` AS rolling_hits9_home,
	   rhp9a.`10_game_rolling_h/9` AS rolling_hits9_away,
	   hhp9.`hits/9` AS historic_hits9_home,
	   hhp9a.`hits/9` AS historic_hits9_away,
	   roba.`10_game_rolling_OBA` AS rolling_oba_home,
	   roba1.`10_game_rolling_OBA` AS rolling_oba_away,
	   hoba.`historic_OBA` AS historic_oba_home,
	   hoba1.`historic_OBA` AS historic_oba_away,
	   hfip.`10rolling_fip` AS rolling10_fip_home,
	   afip.`10rolling_fip` AS rolling10_fip_away,
	   hkbb.`10rolling_kbb` AS rolling10_kbb_home,
	   akbb.`10rolling_kbb` AS rolling10_kbb_away,
	   rwhip.`10_game_rolling_whip` AS rolling_whip_home,
	   rwhipa.`10_game_rolling_whip` AS rolling_whip_away,
	   bull.`20_game_bullpen_whip` AS rolling_bull_whip_home,
	   bulla.`20_game_bullpen_whip` AS rolling_bull_whip_away,
	   rtba.`10_day_rolling_BA` AS rolling_BA_home,
	   rtba1.`10_day_rolling_BA` AS rolling_BA_away,
	   rtr.`10_game_rolling_runs_scored` AS home_team_rolling_avgrunsScored,
	   rtr1.`10_game_rolling_runs_scored` AS away_team_rolling_avgrunsScored,
	   rra.`20rolling_avgruns_allowed` AS home_team_rolling_avgrunsAllowed,
	   rraa.`20rolling_avgruns_allowed` AS away_team_rolling_avgrunsAllowed,
	   rwpcth.rolling_win_pct AS home_team_win_pct,
	   rwpcta.rolling_win_pct AS away_team_win_pct,
	   pg.start_time AS start_time,
	   pg.ampm AS ampm,
	   tempd.temp_diff AS temp_diff_home,
	   tempda.temp_diff AS temp_diff_away,
	   windh.wind_diff AS wind_diff_home,
	   winda.wind_diff AS wind_diff_away,
	   winner_home_or_away
FROM boxscore b 
JOIN game 							g 			ON g.game_id = b.game_id 
JOIN 10game_rolling_k_per_nine 		rkp9 		ON g.game_id = rkp9.game_id AND g.home_pitcher = rkp9.pitcher
JOIN 10game_rolling_k_per_nine 		rkp9a 		ON g.game_id = rkp9a.game_id AND g.away_pitcher = rkp9a.pitcher
JOIN historic_k_per_nine	  		hkp9 		ON g.game_id = hkp9.game_id AND g.home_pitcher = hkp9.pitcher
JOIN historic_k_per_nine 	  		hkp9a 		ON g.game_id = hkp9a.game_id AND g.away_pitcher = hkp9a.pitcher
JOIN 10game_rolling_hr_per_nine		rhrp9		ON g.game_id = rhrp9.game_id AND g.home_pitcher = rhrp9.pitcher
JOIN 10game_rolling_hr_per_nine		rhrp9a		On g.game_id = rhrp9a.game_id AND g.away_pitcher = rhrp9a.pitcher
JOIN historic_hr_per_nine			hhrp9 		ON g.game_id = hhrp9.game_id AND g.home_pitcher = hhrp9.pitcher
JOIN historic_hr_per_nine 			hhrp9a		ON g.game_id = hhrp9a.game_id AND g.away_pitcher = hhrp9a.pitcher
JOIN 10game_rolling_hits_per_nine	rhp9		ON g.game_id = rhp9.game_id AND g.home_pitcher = rhp9.pitcher
JOIN 10game_rolling_hits_per_nine	rhp9a		ON g.game_id = rhp9a.game_id AND g.away_pitcher = rhp9a.pitcher
JOIN historic_hits_per_nine			hhp9		ON g.game_id = hhp9.game_id AND g.home_pitcher = hhp9.pitcher
JOIN historic_hits_per_nine			hhp9a		ON g.game_id = hhp9a.game_id AND g.away_pitcher = hhp9a.pitcher
JOIN 10game_rolling_oba				roba		ON g.game_id = roba.game_id AND g.home_pitcher = roba.pitcher
JOIN 10game_rolling_oba				roba1		ON g.game_id = roba1.game_id AND g.away_pitcher = roba1.pitcher
JOIN historic_oba					hoba 		ON g.game_id = hoba.game_id AND g.home_pitcher = hoba.pitcher
JOIN historic_oba					hoba1 		ON g.game_id = hoba1.game_id AND g.away_pitcher = hoba1.pitcher
JOIN 10game_rolling_teamBA			rtba		ON g.game_id = rtba.game_id AND g.home_team_id = rtba.team_id
JOIN 10game_rolling_teamBA			rtba1		ON g.game_id = rtba1.game_id AND g.away_team_id = rtba1.team_id 
JOIN 10game_rolling_teamRuns		rtr			ON g.game_id = rtr.game_id AND g.home_team_id = rtr.team_id
JOIN 10game_rolling_teamRuns		rtr1		ON g.game_id = rtr1.game_id AND g.away_team_id = rtr1.team_id
JOIN 10game_rolling_whip			rwhip 		ON g.game_id = rwhip.game_id AND g.home_pitcher = rwhip.pitcher
JOIN 10game_rolling_whip			rwhipa 		ON g.game_id = rwhipa.game_id AND g.away_pitcher = rwhipa.pitcher
JOIN rolling_season_win_pct			rwpcth		ON g.game_id = rwpcth.game_id AND g.home_team_id = rwpcth.team_id
JOIN rolling_season_win_pct			rwpcta 		ON g.game_id = rwpcta.game_id AND g.away_team_id = rwpcta.team_id
JOIN 20game_rolling_bullwhip		bull		ON g.game_id = bull.game_id AND g.home_team_id = bull.team_id
JOIN 20game_rolling_bullwhip		bulla		ON g.game_id = bulla.game_id AND g.away_team_id = bulla.team_id
JOIN 20rolling_avgruns_allowed		rra			ON g.game_id = rra.game_id AND g.home_team_id = rra.team_id
JOIN 20rolling_avgruns_allowed		rraa		ON g.game_id = rraa.game_id AND g.away_team_id = rraa.team_id
JOIN 10rolling_fip					hfip 		ON g.game_id = hfip.game_id AND g.home_pitcher = hfip.pitcher
JOIN 10rolling_fip					afip 		ON g.game_id = afip.game_id	AND g.away_pitcher = afip.pitcher
JOIN 10rolling_kbb					hkbb		ON g.game_id = hkbb.game_id AND g.home_pitcher = hkbb.pitcher
JOIN 10rolling_kbb					akbb		ON g.game_id = akbb.game_id AND g.away_pitcher = akbb.pitcher
JOIN pregame 						pg			ON g.game_id = pg.game_id 
JOIN temperature_difference			tempd		ON g.game_id = tempd.game_id AND g.home_team_id = tempd.team_id
JOIN temperature_difference 		tempda 		ON g.game_id = tempda.game_id AND g.away_team_id = tempda.team_id	 
JOIN wind_difference				windh 		ON g.game_id = windh.game_id AND g.home_team_id = windh.team_id
JOIN wind_difference 				winda 		ON g.game_id = winda.game_id AND g.away_team_id = winda.team_id
ORDER BY g.game_id;
*/






