WITH RECURSIVE yrs(y) AS (VALUES(2000) UNION ALL SELECT y+1 FROM yrs WHERE y<2019),
 sy AS (SELECT sid,yr FROM c GROUP BY sid,yr HAVING COUNT(DISTINCT q)=4),
 ints(s,e) AS (SELECT y,y FROM yrs UNION ALL SELECT s,e+1 FROM ints WHERE e<2019),
 feas AS (
  SELECT i.s,i.e,(i.e-i.s+1) dur,
   COUNT(DISTINCT sy.sid) cov
  FROM ints i JOIN sy ON sy.yr BETWEEN i.s AND i.e
  GROUP BY i.s,i.e
  HAVING COUNT(*)=COUNT(DISTINCT sy.sid)*(i.e-i.s+1) AND COUNT(DISTINCT sy.sid)>=2
 ),
 front AS (
 SELECT f.* FROM feas f WHERE NOT EXISTS (SELECT 1 FROM feas d WHERE d.dur>=f.dur AND d.cov>=f.cov AND (d.dur>f.dur OR d.cov>f.cov))
 )
SELECT f.s,f.e,f.dur,f.cov,
 (SELECT group_concat(sid,';') FROM (SELECT sid FROM sy WHERE yr BETWEEN f.s AND f.e GROUP BY sid HAVING COUNT(*)=f.dur ORDER BY sid)) cohort
FROM front f ORDER BY s,e
