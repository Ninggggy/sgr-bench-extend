SELECT m.cve_id,m.matchCriteriaId,m.criteria,CAST(m.vulnerable AS INTEGER) AS vulnerable,
json_extract(b.matchString,'$.status') AS status,
COALESCE(json_array_length(b.matchString,'$.matches'),0) AS visible_matches,
m.versionStartIncluding,m.versionStartExcluding,m.versionEndIncluding,m.versionEndExcluding,
m.path AS configuration_path,b.source_id AS match_source_id
FROM m LEFT JOIN b ON m.cve_id=b.cve_id AND m.matchCriteriaId=json_extract(b.matchString,'$.matchCriteriaId')
ORDER BY m.cve_id,m.matchCriteriaId,m.criteria;
