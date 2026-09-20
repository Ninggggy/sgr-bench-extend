"""Describe the saved small probe. These are observations, not a task oracle."""

import csv
from collections import Counter, defaultdict
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_csv(name):
    return list(csv.DictReader(io.StringIO((ROOT / name).read_text(encoding="utf-8-sig"))))


def key(row):
    return (row["OrganizationIdentifier"], row["MonitoringLocationIdentifier"], row["ActivityIdentifier"])


def main():
    activities = read_csv("wqp_activity_1978_probe.response")
    results = read_csv("wqp_result_1978_probe.response")
    activity_keys = {key(row) for row in activities}
    by_activity = defaultdict(set)
    for row in results:
        by_activity[key(row)].add(row["CharacteristicName"])
    # Presence-only diagnostic, not a scientifically validated measurement panel.
    panel = {"Temperature, sample", "Specific conductance", "pH", "Oxygen"}
    union = set().union(*by_activity.values())
    report = {
        "scope": "Returned CSVs for TCEQMAIN-10580, calendar 1978, current endpoint/profile",
        "is_task_oracle": False,
        "activity_rows": len(activities),
        "result_rows": len(results),
        "distinct_activity_keys": len(activity_keys),
        "distinct_result_activity_keys": len(by_activity),
        "result_keys_absent_from_activity_response": [list(k) for k in sorted(set(by_activity)-activity_keys)],
        "activity_keys_without_results_in_response": [list(k) for k in sorted(activity_keys-set(by_activity))],
        "raw_media_counts": dict(Counter(row["ActivityMediaName"] for row in results)),
        "result_characteristics": dict(sorted(Counter(row["CharacteristicName"] for row in results).items())),
        "presence_only_diagnostic": {
            "panel": sorted(panel),
            "panel_present_somewhere_in_station_response": panel <= union,
            "complete_result_activity_count": sum(panel <= values for values in by_activity.values()),
            "incomplete_result_activities": [{"key": list(k), "missing": sorted(panel-values)} for k, values in sorted(by_activity.items()) if not panel <= values],
        },
        "limitations": [
            "Counts describe returned records; source completeness and endpoint profile still need verification.",
            "Characteristic-name presence does not validate units, qualifiers, fractions, depth or sample comparability.",
            "ActivityMediaName is reported as supplied; do not reinterpret Other as Water.",
            "No candidate station comparison, new CG/GO, reference answer, or model difficulty test has been completed.",
        ],
    }
    (ROOT / "wqp_probe_analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("activity_rows", "result_rows", "distinct_activity_keys", "distinct_result_activity_keys", "raw_media_counts", "presence_only_diagnostic")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
