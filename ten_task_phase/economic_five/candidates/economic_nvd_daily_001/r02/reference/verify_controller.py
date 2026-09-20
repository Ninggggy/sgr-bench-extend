#!/usr/bin/env python3
"""Controller-only execution and cross-language comparison; not run by constructor."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--stage", type=Path, required=True)
p.add_argument("--run", type=Path, required=True)
args = p.parse_args()
stage, run = args.stage.resolve(), args.run.resolve()
if run.exists():
    raise SystemExit("Use a new run directory.")
command = [sys.executable, str(stage/"reference/solve_reference.py"),
           "--stage", str(stage), "--out", str(run)]
result = subprocess.run(command, capture_output=True, text=True)
if result.returncode:
    print(result.stdout, end="")
    print(result.stderr, end="", file=sys.stderr)
    raise SystemExit(result.returncode)
checks = {}
for name in ("candidate_universe.jsonl", "reference/normalized_occurrences.jsonl",
             "inclusion_ledger.jsonl", "field_evidence.jsonl"):
    expected = [json.loads(line) for line in (stage/name).read_text().splitlines()]
    actual = [json.loads(line) for line in (run/name).read_text().splitlines()]
    checks[name] = expected == actual
for name in ("reference/counterfactuals.json", "reference/run_summary.json"):
    checks[name] = json.loads((stage/name).read_text()) == json.loads((run/name).read_text())
checks["reference/oracle.psv"] = (stage/"reference/oracle.psv").read_bytes() == (run/"reference/oracle.psv").read_bytes()
record = dict(command=command, returncode=result.returncode, stdout=result.stdout,
              stderr=result.stderr, checks=checks, passed=all(checks.values()))
(run/"controller_execution.json").write_text(json.dumps(record, indent=2)+"\n")
print(json.dumps(record, indent=2))
raise SystemExit(0 if record["passed"] else 1)
