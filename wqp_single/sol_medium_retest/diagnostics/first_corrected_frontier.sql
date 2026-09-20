WITH RECURSIVE yrs(y) AS (VALUES(2000) UNION ALL SELECT y+1 FROM yrs WHERE y<2019),
 sy AS (SELECT sid,yr FROM c GROUP BY sid,yr HAVING COUNT(DISTINCT q)=4),
 ints(s,e) AS (SELECT y,y FROM yrs UNION ALL SELECT s,e+1 FROM ints WHERE e<2019),
 members AS (
  SELECT i.s,i.e,sy.sid FROM ints i JOIN sy ON sy.yr BETWEEN i.s AND i.e
  GROUP BY i.s,i.e,sy.sid HAVING COUNT(DISTINCT sy.yr)=i.e-i.s+1
 ),
 feas AS (SELECT s,e,e-s+1 dur,COUNT(*) cov FROM members GROUP BY s,e HAVING COUNT(*)>=2),
 front AS (SELECT f.* FROM feas f WHERE NOT EXISTS
  (SELECT 1 FROM feas d WHERE d.dur>=f.dur AND d.cov>=f.cov AND (d.dur>f.dur OR d.cov>f.cov)))
SELECT f.s,f.e,f.dur,f.cov,
 (SELECT group_concat(sid,';') FROM (SELECT sid FROM members m WHERE m.s=f.s AND m.e=f.e ORDER BY sid)) cohort
FROM front f ORDER BY s,e
