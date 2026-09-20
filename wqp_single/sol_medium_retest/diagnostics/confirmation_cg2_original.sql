
WITH RECURSIVE
qcounts AS (
 SELECT sid,yr,qtr,COUNT(*) n FROM p GROUP BY sid,yr,qtr
),
sy AS (
 SELECT sid,yr FROM qcounts GROUP BY sid,yr HAVING COUNT(*)=4
),
stations AS (SELECT DISTINCT sid FROM p),
years(y) AS (VALUES(2000) UNION ALL SELECT y+1 FROM years WHERE y<2019),
intervals AS (
 SELECT a.y sy,b.y ey,b.y-a.y+1 dur FROM years a JOIN years b ON b.y>=a.y
),
orig_members AS (
 SELECT i.sy,i.ey,i.dur,s.sid FROM intervals i JOIN stations s
 WHERE (SELECT COUNT(*) FROM sy WHERE sy.sid=s.sid AND sy.yr BETWEEN i.sy AND i.ey)=i.dur
),
orig_members_sorted AS (SELECT * FROM orig_members ORDER BY sy,ey,sid),
orig_designs AS (
 SELECT sy,ey,dur,COUNT(*) coverage,GROUP_CONCAT(sid,';') cohort
 FROM orig_members_sorted GROUP BY sy,ey,dur HAVING COUNT(*)>=2
),
orig_frontier AS (
 SELECT d.* FROM orig_designs d WHERE NOT EXISTS (
 SELECT 1 FROM orig_designs x WHERE x.dur>=d.dur AND x.coverage>=d.coverage
 AND (x.dur>d.dur OR x.coverage>d.coverage))
),
v AS (
 SELECT p.* FROM p JOIN qcounts q USING(sid,yr,qtr) WHERE q.n=1
),
trial_members AS (
 SELECT v.aid wid,i.sy,i.ey,i.dur,s.sid
 FROM v CROSS JOIN intervals i CROSS JOIN stations s
 WHERE (SELECT COUNT(*) FROM sy
        WHERE sy.sid=s.sid AND sy.yr BETWEEN i.sy AND i.ey
          AND NOT (s.sid=v.sid AND sy.yr=v.yr))=i.dur
),
trial_members_sorted AS (SELECT * FROM trial_members ORDER BY wid,sy,ey,sid),
trial_designs AS (
 SELECT wid,sy,ey,dur,COUNT(*) coverage,GROUP_CONCAT(sid,';') cohort
 FROM trial_members_sorted GROUP BY wid,sy,ey,dur HAVING COUNT(*)>=2
),
trial_frontier AS (
 SELECT d.* FROM trial_designs d WHERE NOT EXISTS (
 SELECT 1 FROM trial_designs x WHERE x.wid=d.wid AND x.dur>=d.dur AND x.coverage>=d.coverage
 AND (x.dur>d.dur OR x.coverage>d.coverage))
),
changing AS (
 SELECT v.aid wid FROM v
 WHERE EXISTS (SELECT 1 FROM trial_frontier t WHERE t.wid=v.aid
               AND NOT EXISTS (SELECT 1 FROM orig_frontier o WHERE o.sy=t.sy AND o.ey=t.ey AND o.cohort=t.cohort))
    OR EXISTS (SELECT 1 FROM orig_frontier o
               WHERE NOT EXISTS (SELECT 1 FROM trial_frontier t WHERE t.wid=v.aid AND o.sy=t.sy AND o.ey=t.ey AND o.cohort=t.cohort))
),
event_pool AS (
 SELECT t.wid,t.sy,t.ey,t.coverage,t.cohort,e.*,
 COUNT(*) OVER (PARTITION BY t.wid,t.sy,t.ey) activity_count,
 ROW_NUMBER() OVER (
   PARTITION BY t.wid,t.sy,t.ey
   ORDER BY e.oxy,e.adate,CASE WHEN e.atime='' THEN 1 ELSE 0 END,e.atime,e.sid,e.aid
 ) rn
 FROM trial_frontier t
 JOIN v w ON w.aid=t.wid
 JOIN trial_members m ON m.wid=t.wid AND m.sy=t.sy AND m.ey=t.ey
 JOIN p e ON e.sid=m.sid AND e.yr BETWEEN t.sy AND t.ey AND e.qtr=w.qtr AND e.aid<>t.wid
 JOIN changing c ON c.wid=t.wid
)
SELECT w.org,w.aid,w.sid,w.adate,
       ep.sy,ep.ey,ep.coverage,ep.cohort,
       'Q'||w.qtr,ep.activity_count,
       ep.org,ep.sid,ep.aid,ep.adate,
       printf('%.2f',floor(ep.oxy*100+0.5)/100.0),
       printf('%.2f',floor(ep.temp*100+0.5)/100.0),
       printf('%.2f',floor(ep.cond*100+0.5)/100.0),
       printf('%.2f',floor(ep.ph*100+0.5)/100.0)
FROM event_pool ep JOIN v w ON w.aid=ep.wid
WHERE ep.rn=1
UNION ALL
SELECT w.org,w.aid,w.sid,w.adate,0,0,0,'NONE','Q'||w.qtr,0,
       'NONE','NONE','NONE','NONE','NA','NA','NA','NA'
FROM v w JOIN changing c ON c.wid=w.aid
WHERE NOT EXISTS (SELECT 1 FROM trial_frontier t WHERE t.wid=w.aid)
ORDER BY 2,5,6
