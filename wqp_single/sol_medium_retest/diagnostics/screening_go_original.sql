
WITH RECURSIVE years(y) AS (VALUES(2000) UNION ALL SELECT y+1 FROM years WHERE y<2019),
intervals(s,e) AS (SELECT a.y,b.y FROM years a JOIN years b ON b.y>=a.y),
sy AS (SELECT station,yr FROM c GROUP BY station,yr HAVING COUNT(DISTINCT qtr)=4),
im AS (SELECT i.s,i.e,sy.station FROM intervals i JOIN sy ON sy.yr BETWEEN i.s AND i.e GROUP BY i.s,i.e,sy.station HAVING COUNT(DISTINCT sy.yr)=i.e-i.s+1),
od AS (SELECT s,e,COUNT(*) coverage FROM im GROUP BY s,e HAVING COUNT(*)>=2),
of0 AS (SELECT d.* FROM od d WHERE NOT EXISTS(SELECT 1 FROM od x WHERE (x.e-x.s)>=(d.e-d.s) AND x.coverage>=d.coverage AND ((x.e-x.s)>(d.e-d.s) OR x.coverage>d.coverage))),
ofr AS (SELECT f.*,(SELECT group_concat(station,';') FROM (SELECT station FROM im WHERE s=f.s AND e=f.e ORDER BY station)) ids FROM of0 f),
critical AS (
 SELECT c.* FROM c JOIN sy ON sy.station=c.station AND sy.yr=c.yr
 JOIN (SELECT station,yr,qtr,COUNT(*) n FROM c GROUP BY station,yr,qtr) z ON z.station=c.station AND z.yr=c.yr AND z.qtr=c.qtr
 WHERE z.n=1
),
tm AS (SELECT w.aid waid,w.org worg,m.s,m.e,m.station FROM critical w CROSS JOIN im m WHERE NOT(m.station=w.station AND w.yr BETWEEN m.s AND m.e)),
td0 AS (SELECT waid,worg,s,e,COUNT(*) coverage FROM tm GROUP BY waid,worg,s,e HAVING COUNT(*)>=2),
td AS (SELECT d.*,(SELECT group_concat(station,';') FROM (SELECT station FROM tm WHERE waid=d.waid AND worg=d.worg AND s=d.s AND e=d.e ORDER BY station)) ids FROM td0 d),
tf AS (SELECT d.* FROM td d WHERE NOT EXISTS(SELECT 1 FROM td x WHERE x.waid=d.waid AND x.worg=d.worg AND (x.e-x.s)>=(d.e-d.s) AND x.coverage>=d.coverage AND ((x.e-x.s)>(d.e-d.s) OR x.coverage>d.coverage))),
changing AS (
 SELECT w.aid,w.org FROM critical w WHERE
 EXISTS(SELECT 1 FROM tf t WHERE t.waid=w.aid AND t.worg=w.org AND NOT EXISTS(SELECT 1 FROM ofr o WHERE o.s=t.s AND o.e=t.e AND o.ids=t.ids))
 OR EXISTS(SELECT 1 FROM ofr o WHERE NOT EXISTS(SELECT 1 FROM tf t WHERE t.waid=w.aid AND t.worg=w.org AND t.s=o.s AND t.e=o.e AND t.ids=o.ids))
),
br AS (
 SELECT w.org,w.aid,w.station wstation,w.adate wadate,w.qtr,t.s,t.e,t.coverage,t.ids
 FROM critical w JOIN changing g ON g.org=w.org AND g.aid=w.aid
 JOIN tf t ON t.worg=w.org AND t.waid=w.aid
),
eligible AS (
 SELECT DISTINCT b.org worg,b.aid waid,b.s,b.e,c.org,c.aid,c.station,c.adate,c.atime,c.oxy,c.temp,c.cond,c.ph
 FROM br b JOIN tm m ON m.worg=b.org AND m.waid=b.aid AND m.s=b.s AND m.e=b.e
 JOIN c ON c.station=m.station AND c.yr BETWEEN b.s AND b.e AND c.qtr=b.qtr
 WHERE NOT(c.org=b.org AND c.aid=b.aid)
),
ranked AS (
 SELECT e.*,COUNT(*) OVER(PARTITION BY worg,waid,s,e) ec,
 ROW_NUMBER() OVER(PARTITION BY worg,waid,s,e ORDER BY oxy ASC,adate ASC,CASE WHEN TRIM(COALESCE(atime,''))='' THEN 1 ELSE 0 END ASC,atime ASC,station ASC,aid ASC) rn
 FROM eligible e
)
SELECT b.org||'|'||b.aid||'|'||b.wstation||'|'||b.wadate||'|'||
 b.s||'|'||b.e||'|'||b.coverage||'|'||b.ids||'|Q'||b.qtr||'|'||r.ec||'|'||
 r.org||'|'||r.station||'|'||r.aid||'|'||r.adate||'|'||
 printf('%.2f',r.oxy)||'|'||printf('%.2f',r.temp)||'|'||printf('%.2f',r.cond)||'|'||printf('%.2f',r.ph) line
FROM br b JOIN ranked r ON r.worg=b.org AND r.waid=b.aid AND r.s=b.s AND r.e=b.e AND r.rn=1
ORDER BY b.aid,b.s,b.e
