#!/usr/bin/env python3
"""Rebuild reference artifacts from saved original official responses.
No network access, hardcoded answers, or dependency on generated oracle tables.
Run from the materialized stage directory:
  python3 reference/solve_reference.py --stage . --out controller_rebuild
Then compare controller_rebuild/reference/oracle.psv with reference/oracle.psv.
This program has NOT been executed in the construction environment.
"""
import argparse
import collections
import json
import re
from pathlib import Path

RANGES = ("versionStartIncluding", "versionStartExcluding",
          "versionEndIncluding", "versionEndExcluding")
COLUMNS = ("cve_id", "matchCriteriaId", "criteria")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def identity(row):
    return (row["criteria"],) + tuple(row.get(k) for k in RANGES)

def walk(value, path):
    """Visit every configuration container; do not flatten only the first node."""
    if isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f"{path}[{i}]")
    elif isinstance(value, dict):
        for key, child in value.items():
            if key == "cpeMatch":
                require(isinstance(child, list), "cpeMatch is not an array")
                for i, criterion in enumerate(child):
                    yield path + f".cpeMatch[{i}]", criterion
            else:
                yield from walk(child, path + "." + key)

def cpe_parts(text):
    result, part, escaped = [], "", False
    for char in text:
        if char == ":" and not escaped:
            result.append(part)
            part = ""
        else:
            part += char
        escaped = not escaped if char == "\\" else False
    result.append(part)
    require(len(result) == 13, "Invalid formatted CPE component count")
    return result

def reconstruct(stage):
    manifest = json.loads((stage / "source_manifest.json").read_text())
    entries = manifest["sources"]
    texts, bodies = {}, {}
    for e in entries:
        if e.get("body_format") == "json":
            raw = (stage / e["path"]).read_bytes()
            # Original registered bytes were compared directly during controller integration.
            texts[e["path"]] = raw.decode("utf-8")
            bodies[e["path"]] = json.loads(texts[e["path"]])

    def page(e, array):
        require(e["status"] == 200, "Unsuccessful response: " + e["path"])
        body = bodies[e["path"]]
        require(body["startIndex"] == 0 and
                body["resultsPerPage"] == len(body[array]) and
                body["totalResults"] == len(body[array]),
                "Incomplete one-page response: " + e["path"])
        return body

    scopes = [e for e in entries if e.get("role") == "scope"]
    require(len(scopes) == 1, "Ambiguous primary scope")
    scope_entry = scopes[0]
    scope = page(scope_entry, "vulnerabilities")
    universe, occurrences = [], []
    for i, wrapper in enumerate(scope["vulnerabilities"]):
        cve = wrapper["cve"]
        require(cve["published"][:10] == manifest["published_day"], "Wrong day")
        prefix = f"$.vulnerabilities[{i}].cve"
        start = len(occurrences)
        for path, criterion in walk(cve.get("configurations"), prefix + ".configurations"):
            occurrences.append(dict(criterion, cve_id=cve["id"], path=path))
        universe.append(dict(cve_id=cve["id"], published=cve["published"],
            lastModified=cve["lastModified"], vulnStatus=cve["vulnStatus"],
            source=scope_entry["path"], path=prefix,
            configuration_occurrences=len(occurrences)-start))
    require(len({r["cve_id"] for r in universe}) == len(universe), "Duplicate CVE")
    require(len(re.findall(r'"matchCriteriaId"\s*:', texts[scope_entry["path"]]))
            == len(occurrences), "Unvisited UUID outside traversed configuration")
    by_cve, by_uuid, match_refs = {}, {}, {}
    for e in entries:
        if e.get("role") != "match":
            continue
        require(e["cve_id"] not in by_cve, "Duplicate CVE match batch")
        items = {}
        for i, wrapper in enumerate(page(e, "matchStrings")["matchStrings"]):
            item = wrapper["matchString"]
            uid = item["matchCriteriaId"]
            require(uid not in items, "Duplicate UUID within batch")
            if uid in by_uuid:
                require(canonical(by_uuid[uid]) == canonical(item), "Match revision conflict")
            items[uid] = by_uuid[uid] = item
            match_refs[(e["cve_id"], uid)] = dict(source=e["path"],
                path=f"$.matchStrings[{i}].matchString")
        wanted = [r for r in occurrences if r["cve_id"] == e["cve_id"]]
        require(set(items) == {r["matchCriteriaId"] for r in wanted}, "CVE UUID coverage mismatch")
        for row in wanted:
            require(identity(row) == identity(items[row["matchCriteriaId"]]),
                    "Criteria or version-range disagreement")
        by_cve[e["cve_id"]] = items
    require(set(by_cve) == {r["cve_id"] for r in occurrences}, "Missing CVE batch")
    exact = {}
    for e in entries:
        if e.get("role") not in ("cpe_zero", "cpe_check"):
            continue
        uid = e["uuid"]
        require(e["query"]["matchCriteriaId"] == [uid], "Wrong dictionary UUID parameter")
        require(uid in by_uuid and uid not in exact, "Duplicate or extraneous exact UUID")
        body = page(e, "products")
        exact[uid] = e, body
        matches = by_uuid[uid].get("matches", [])
        if matches:
            from_match = sorted((m["cpeNameId"], m["cpeName"]) for m in matches)
            from_cpe = sorted((p["cpe"]["cpeNameId"], p["cpe"]["cpeName"])
                              for p in body["products"])
            require(from_match == from_cpe and body["totalResults"] > 0,
                    "Match names disagree with dictionary")
    # Independent public revision-index and broader-scope evidence.
    # These checks support this construction window only; later evaluation is separate.
    records = lambda body: {x["cve"]["id"]: x["cve"] for x in body["vulnerabilities"]}
    primary_records = records(scope)
    for role in ("scope_recheck", "scope_broad"):
        checks = [e for e in entries if e.get("role") == role]
        require(len(checks) == 1, "Missing independent scope evidence")
        other = records(page(checks[0], "vulnerabilities"))
        if role == "scope_broad":
            other = {k:v for k,v in other.items()
                     if v["published"][:10] == manifest["published_day"]}
        require(other == primary_records, "Independent scope differs")
    delta = sorted((e for e in entries if e.get("role") == "match_changes"),
                   key=lambda e:int(e["query"]["startIndex"][0]))
    require(bool(delta), "Missing public revision-index evidence")
    offset, total = 0, None
    for e in delta:
        require(e["status"] == 200, "Revision query failed")
        body = bodies[e["path"]]
        require(body["startIndex"] == offset and
                body["resultsPerPage"] == len(body["matchStrings"]), "Revision pagination")
        if total is None:
            total = body["totalResults"]
        require(total == body["totalResults"], "Revision total changed")
        require(not any(x["matchString"]["matchCriteriaId"] in by_uuid
                        for x in body["matchStrings"]), "Relevant revision requires refresh")
        offset += len(body["matchStrings"])
    require(offset == total, "Incomplete revision-index enumeration")
    change_start = delta[0]["query"]["lastModStartDate"][0]
    require(scope_entry["requested_at"][:19] >= change_start[:19], "Revision window starts too late")
    for item in by_uuid.values():
        for field in ("created", "lastModified", "cpeLastModified"):
            require(not item.get(field) or item[field] < change_start,
                    "Observed primary revision lies inside stability window")
    grouped = collections.defaultdict(list)
    for row in occurrences:
        grouped[(row["cve_id"], row["matchCriteriaId"])].append(row)
    ledger, evidence, oracle = [], [], []
    cv_map = {r["cve_id"]: r for r in universe}
    for key, rows in sorted(grouped.items()):
        row = rows[0]
        uid = row["matchCriteriaId"]
        match = by_uuid[uid]
        require(all(identity(r) == identity(row) for r in rows), "Duplicate identity conflict")
        require(all(type(r.get("vulnerable")) is bool for r in rows), "Unknown vulnerable flag")
        require(match["status"] in ("Active", "Inactive"), "Unknown Match status")
        vulnerable = any(r["vulnerable"] is True for r in rows)
        active = match["status"] == "Active"
        zero, coverage = None, None
        ref = match_refs[key]
        if uid in exact:
            e, body = exact[uid]
            zero = body["totalResults"] == 0
            coverage = dict(source=e["path"], path="$.totalResults", value=body["totalResults"])
        elif match.get("matches"):
            zero = False
            coverage = dict(ref, path=ref["path"]+".matches", value=len(match["matches"]),
                interpretation="nonempty official dictionary name/ID list proves nonzero, not an exact dictionary count")
        require(not vulnerable or not active or zero is not None,
                "Unresolved dictionary coverage for " + repr(key))
        included = vulnerable and active and zero is True
        config_sources = [dict(source=scope_entry["path"], path=r["path"]) for r in rows]
        result = dict(cve_id=key[0], matchCriteriaId=uid, criteria=row["criteria"],
            ranges={k:row.get(k) for k in RANGES}, vulnerable=vulnerable, active=active,
            dictionary_zero=zero, included=included,
            reason=("not_vulnerable" if not vulnerable else "inactive" if not active else
                    "confirmed_exact_zero" if zero is True else
                    "dictionary_present" if zero is False else "unknown"),
            configuration_sources=config_sources, match_source=ref, coverage_source=coverage)
        ledger.append(result)
        fields = {
            "cve_id": dict(source=scope_entry["path"], path=cv_map[key[0]]["path"]+".id"),
            "active": dict(ref, path=ref["path"]+".status"),
            "dictionary_zero": coverage,
            "included": dict(input_row_keys=["|".join(key)],
                formula="any(vulnerable === true) AND status === 'Active' AND exact dictionary totalResults === 0")}
        for field in ("matchCriteriaId", "criteria", "vulnerable"):
            fields[field] = [dict(s, path=s["path"]+"."+field) for s in config_sources]
        fields["published"] = dict(source=scope_entry["path"],
            path=cv_map[key[0]]["path"]+".published", value=cv_map[key[0]]["published"],
            formula="UTC field date equals "+manifest["published_day"])
        fields["ranges"] = {k:dict(value=result["ranges"][k],
            configuration_sources=[dict(s,path=s["path"]+"."+k) for s in config_sources],
            match_source=dict(ref,path=ref["path"]+"."+k),
            null_meaning="field absent; no boundary stated") for k in RANGES}
        evidence.append(dict(row_key=[key[0],uid,row["criteria"]], fields=fields))
        if included:
            oracle.append({k:result[k] for k in COLUMNS})
    sort_key = lambda r: tuple(r[k] for k in COLUMNS)
    ledger.sort(key=sort_key)
    oracle.sort(key=sort_key)
    universe.sort(key=lambda r:r["cve_id"])
    dropped = []
    for row in (r for r in ledger if r["included"]):
        parts = cpe_parts(row["criteria"])
        if parts[6] == "*":
            continue
        for sibling in ledger:
            if sibling["cve_id"] != row["cve_id"] or sibling["dictionary_zero"] is not False:
                continue
            if sibling["ranges"] != row["ranges"]:
                continue
            other = cpe_parts(sibling["criteria"])
            if other[6] == "*" and all(a == b for i,(a,b) in enumerate(zip(parts,other)) if i != 6):
                dropped.append(dict(row_key=[row[k] for k in COLUMNS],
                    incorrect_coverage_from=[sibling[k] for k in COLUMNS]))
                break
    cross_dropped, seen = [], set()
    for row in oracle:
        if row["matchCriteriaId"] in seen:
            cross_dropped.append(row)
        seen.add(row["matchCriteriaId"])
    counterfactuals = dict(baseline_rows=len(oracle),
        patch_overlap=dict(rule="Treat an otherwise identical same-CVE criterion with wildcard update and nonzero coverage as covering the update-specific UUID; ranges must be equal.",
            wrong_rows=len(oracle)-len(dropped), removed=dropped),
        global_uuid_deduplication=dict(wrong_rows=len(oracle)-len(cross_dropped), removed=cross_dropped),
        vulnerable_flag=dict(changes_rows=False, reason="All observed occurrences are vulnerable=true; no effectiveness claim."
            if all(r["vulnerable"] is True for r in occurrences) else "Not evaluated here."))
    require(all(all(isinstance(v,str) and v and not re.search(r"[|\r\n]",v) for v in r.values())
                for r in oracle), "Invalid PSV field")
    require(len({tuple(r[k] for k in COLUMNS) for r in oracle}) == len(oracle), "Duplicate oracle key")
    psv = ("|".join(COLUMNS)+"\n"+"\n".join("|".join(r[k] for k in COLUMNS) for r in oracle)+"\n"
           if oracle else "NONE\n")
    summary = dict(cves=len(universe), occurrences=len(occurrences), unique_uuid=len(by_uuid),
                   ledger_rows=len(ledger), oracle_rows=len(oracle), unknown=0)
    return locals()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Use a new output directory; preserve previous runs")
    result = reconstruct(args.stage)
    args.out.mkdir(parents=True)
    (args.out/"reference").mkdir()
    for key, path in (("universe","candidate_universe.jsonl"),
                      ("occurrences","reference/normalized_occurrences.jsonl"),
                      ("ledger","inclusion_ledger.jsonl"),
                      ("evidence","field_evidence.jsonl")):
        (args.out/path).write_text("".join(canonical(row)+"\n" for row in result[key]), encoding="utf-8")
    (args.out/"reference/oracle.psv").write_text(result["psv"], encoding="utf-8")
    (args.out/"reference/counterfactuals.json").write_text(canonical(result["counterfactuals"])+"\n")
    (args.out/"reference/run_summary.json").write_text(canonical(result["summary"])+"\n")
    print(canonical(result["summary"]))

if __name__ == "__main__":
    main()
