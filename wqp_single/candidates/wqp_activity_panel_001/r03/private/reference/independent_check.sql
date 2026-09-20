-- Independent source implementation: raw wide -> panels -> all withdrawal states.
CREATE TEMP TABLE p AS
WITH v AS (
 SELECT OrganizationIdentifier org,MonitoringLocationIdentifier site,ActivityIdentifier aid,ActivityStartDate day,"ActivityStartTime/Time" tm,
 CAST(substr(ActivityStartDate,1,4) AS INTEGER) y,1+CAST((CAST(substr(ActivityStartDate,6,2) AS INTEGER)-1)/3 AS INTEGER) q,
 USGSPCode code,CAST(ResultMeasureValue AS REAL) val
 FROM wide WHERE ActivityMediaName='Water' AND ActivityTypeCode='Sample-Routine'
 AND ResultStatusIdentifier IN ('Accepted','Final') AND ResultValueTypeName='Actual'
 AND trim(ResultDetectionConditionText)='' AND trim(MeasureQualifierCode)=''
 AND ((USGSPCode='00010' AND "ResultMeasure/MeasureUnitCode"='deg C') OR (USGSPCode='00095' AND "ResultMeasure/MeasureUnitCode"='uS/cm @25C') OR (USGSPCode='00300' AND "ResultMeasure/MeasureUnitCode"='mg/l') OR (USGSPCode='00400' AND "ResultMeasure/MeasureUnitCode"='std units'))
)
SELECT org,site,aid,day,tm,y,q,MAX(CASE WHEN code='00300' THEN val END) oxygen,MAX(CASE WHEN code='00010' THEN val END) temp,MAX(CASE WHEN code='00095' THEN val END) cond,MAX(CASE WHEN code='00400' THEN val END) ph
FROM v GROUP BY org,site,aid,day,tm,y,q HAVING COUNT(DISTINCT code)=4 AND COUNT(DISTINCT code||':'||val)=4;
CREATE TEMP TABLE sc AS SELECT ROW_NUMBER() OVER(ORDER BY org,aid) sid,org,site,aid,day,y,q FROM p;
INSERT INTO sc VALUES(0,'','','','',0,0);
CREATE TEMP TABLE qcounts AS SELECT org,site,y,q,COUNT(*) n FROM p GROUP BY org,site,y,q;
CREATE TEMP TABLE support AS
SELECT sc.sid,q.org,q.site,q.y FROM qcounts q CROSS JOIN sc
GROUP BY sc.sid,q.org,q.site,q.y
HAVING COUNT(*)=4 AND MIN(q.n-CASE WHEN sc.org=q.org AND sc.site=q.site AND sc.y=q.y AND sc.q=q.q THEN 1 ELSE 0 END)>0;
CREATE INDEX support_sid ON support(sid,org,site,y);
CREATE TEMP TABLE intervals AS
WITH RECURSIVE years(y) AS (SELECT 2000 UNION ALL SELECT y+1 FROM years WHERE y<2019)
SELECT a.y lo,b.y hi,b.y-a.y+1 duration FROM years a CROSS JOIN years b WHERE a.y<=b.y;
CREATE TEMP TABLE membership AS
SELECT s.sid,i.lo,i.hi,i.duration,s.org,s.site FROM intervals i JOIN support s ON s.y BETWEEN i.lo AND i.hi
GROUP BY s.sid,i.lo,i.hi,i.duration,s.org,s.site HAVING COUNT(*)=i.duration;
CREATE INDEX membership_sid_interval ON membership(sid,lo,hi,org,site);
CREATE TEMP TABLE feasible AS
SELECT sid,lo,hi,duration,COUNT(*) n,GROUP_CONCAT(site,';') cohort
FROM (SELECT * FROM membership ORDER BY sid,lo,hi,site COLLATE BINARY)
GROUP BY sid,lo,hi,duration HAVING COUNT(*)>=2;
CREATE INDEX feasible_sid ON feasible(sid,duration,n);
CREATE TEMP TABLE frontier AS
SELECT f.* FROM feasible f WHERE NOT EXISTS(SELECT 1 FROM feasible d WHERE d.sid=f.sid AND d.duration>=f.duration AND d.n>=f.n AND (d.duration>f.duration OR d.n>f.n));
CREATE INDEX frontier_sid ON frontier(sid,lo,hi);
CREATE TEMP TABLE frontier_identity AS
SELECT sid,GROUP_CONCAT(lo||':'||hi||':'||cohort,'~') identity
FROM (SELECT * FROM frontier ORDER BY sid,lo,hi) GROUP BY sid;
CREATE TEMP TABLE all_trial_decisions AS
SELECT sc.*,CASE WHEN COALESCE(fi.identity,'')!=(SELECT identity FROM frontier_identity WHERE sid=0) THEN 1 ELSE 0 END changed
FROM sc LEFT JOIN frontier_identity fi USING(sid) WHERE sc.sid>0;
CREATE TEMP TABLE answer AS
WITH ranked AS (
 SELECT sc.org worg,sc.aid waid,sc.site wsite,sc.day wday,sc.q wq,f.lo,f.hi,f.n,f.cohort,
 p.org,p.site,p.aid,p.day,p.oxygen,p.temp,p.cond,p.ph,
 COUNT(*) OVER(PARTITION BY sc.sid,f.lo,f.hi) nactivity,
 ROW_NUMBER() OVER(PARTITION BY sc.sid,f.lo,f.hi ORDER BY p.oxygen,p.day,CASE WHEN p.tm='' THEN 1 ELSE 0 END,p.tm,p.site COLLATE BINARY,p.aid COLLATE BINARY) rn
 FROM all_trial_decisions sc JOIN frontier f ON f.sid=sc.sid
 JOIN membership m ON m.sid=f.sid AND m.lo=f.lo AND m.hi=f.hi
 JOIN p ON p.org=m.org AND p.site=m.site AND p.y BETWEEN f.lo AND f.hi AND p.q=sc.q
 WHERE sc.changed=1 AND NOT(p.org=sc.org AND p.aid=sc.aid)
)
SELECT worg withdrawn_OrganizationIdentifier,waid withdrawn_ActivityIdentifier,wsite withdrawn_MonitoringLocationIdentifier,wday withdrawn_ActivityStartDate,
lo start_year,hi end_year,n cohort_station_count,cohort cohort_station_ids,'Q'||wq quarter,nactivity eligible_activity_count,
org selected_OrganizationIdentifier,site selected_MonitoringLocationIdentifier,aid selected_ActivityIdentifier,day selected_ActivityStartDate,
oxygen dissolved_oxygen_mg_L,temp temperature_deg_C,cond specific_conductance_uS_cm,ph pH FROM ranked WHERE rn=1;
