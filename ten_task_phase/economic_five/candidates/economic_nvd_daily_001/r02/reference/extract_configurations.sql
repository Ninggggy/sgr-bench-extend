WITH RECURSIVE
seq(i) AS (SELECT 0 UNION ALL SELECT i+1 FROM seq WHERE i<1023),
configs(cve_id,path,node) AS (
 SELECT json_extract(cve,'$.id'),'$.configurations['||i||']',json_extract(cve,'$.configurations['||i||']')
 FROM c JOIN seq ON i<COALESCE(json_array_length(cve,'$.configurations'),0)
),
walk(cve_id,path,node) AS (
 SELECT * FROM configs
 UNION ALL
 SELECT w.cve_id,w.path||'.'||k.field||'['||i||']',json_extract(w.node,'$.'||k.field||'['||i||']')
 FROM walk w JOIN (SELECT 'nodes' AS field UNION ALL SELECT 'children') k
 JOIN seq ON i<COALESCE(json_array_length(w.node,'$.'||k.field),0)
),
matches AS (
 SELECT cve_id,path||'.cpeMatch['||i||']' AS path,json_extract(node,'$.cpeMatch['||i||']') AS criterion
 FROM walk JOIN seq ON i<COALESCE(json_array_length(node,'$.cpeMatch'),0)
)
SELECT cve_id,path,json_extract(criterion,'$.matchCriteriaId') AS matchCriteriaId,
 json_extract(criterion,'$.criteria') AS criteria,json_extract(criterion,'$.vulnerable') AS vulnerable,
 json_extract(criterion,'$.versionStartIncluding') AS versionStartIncluding,
 json_extract(criterion,'$.versionStartExcluding') AS versionStartExcluding,
 json_extract(criterion,'$.versionEndIncluding') AS versionEndIncluding,
 json_extract(criterion,'$.versionEndExcluding') AS versionEndExcluding
FROM matches ORDER BY cve_id,matchCriteriaId,path;
