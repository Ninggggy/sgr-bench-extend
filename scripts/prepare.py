#!/usr/bin/env python3
"""Offline inventory, public projection, prompt assembly, and candidate checks."""

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parents[1]
FORMAL = PACKAGE.parent / "runs/open-source/sgr-bench"
DOMAIN_TO_ECOSYSTEM = {
    "ARXIV": "ARXIV",
    "CENSUS_GOV": "CENSUS_GOV",
    "NOAA_NCEI_CLIMATE_AT_A_GLANCE": "NOAA_NCEI_CLIMATE_AT_A_GLANCE",
    "COMPTOX_CHEMEXPO": "COMPTOX_CHEMEXPO",
    "CFPB_REPORTS": "CFPB",
    "CFPB_COMPLAINT_DATABASE": "CFPB",
    "EUROPEPMC_PMC": "EUROPEPMC_PMC",
    "KEGG_BRITE": "KEGG",
    "KEGG_GENOME": "KEGG",
    "NVD": "NVD",
    "REPTILE_DATABASE": "REPTILE_DATABASE",
    "WATER_OFFICE": "WATER_OFFICE",
    "WATER_QUALITY_PORTAL": "WATER_QUALITY_PORTAL",
    "CDC_WONDER": "CDC_WONDER",
}
STAGES = (
    "00_controller", "01_site_explorer", "02_candidate_designer",
    "03_reference_builder", "04_blind_solver", "05_shortcut_attacker",
    "06_evidence_auditor", "07_pair_writer", "08_adjudicator",
    "09_repair", "10_confirmation_solver",
)
BLIND_STAGES = {"04_blind_solver", "05_shortcut_attacker", "10_confirmation_solver"}
PUBLIC_KEYS = {"instruction", "output_format", "current_date"}
CANDIDATE_STATUSES = {
    "candidate", "reference_ready", "content_validated", "auto_validated",
    "needs_revision", "rejected", "inconclusive",
}
REFERENCE_STATUSES = {"reference_ready", "content_validated", "auto_validated"}
CONTENT_STATUSES = {"content_validated", "auto_validated"}
REFERENCE_PATH_KEYS = ("oracle_path", "reference_script_path", "source_manifest_path")
CANDIDATE_PATH_KEYS = (*REFERENCE_PATH_KEYS, "state_graph_path")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_text(path, text):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def write_json(path, data):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def unique_index(tasks):
    result = {}
    for task in tasks:
        task_id = task["task_id"]
        if task_id in result:
            raise ValueError(f"Duplicate task ID: {task_id}")
        result[task_id] = task
    return result


def build_inventory(cg_tasks, go_tasks):
    cg_index, go_index = unique_index(cg_tasks), unique_index(go_tasks)
    expected = {task_id + "-g" for task_id in cg_index}
    if set(go_index) != expected:
        raise ValueError(f"CG/GO ID mismatch: missing={sorted(expected-set(go_index))}; extra={sorted(set(go_index)-expected)}")
    entries = []
    for task_id, task in cg_index.items():
        domain = task["domain"]
        if domain not in DOMAIN_TO_ECOSYSTEM:
            raise ValueError(f"Unmapped domain: {domain}")
        go = go_index[task_id + "-g"]
        metadata = task.get("metadata", {})
        columns = task.get("rubric", {}).get("normalization", {}).get("schema")
        entries.append({
            "task_id": task_id,
            "go_task_id": go["task_id"],
            "domain": domain,
            "ecosystem": DOMAIN_TO_ECOSYSTEM[domain],
            "start_url": task.get("start_url"),
            "autonomy_type": task.get("autonomy_type"),
            "declared_rows": task.get("oracle_output_cardinality"),
            "output_columns": columns,
            "column_count": len(columns) if isinstance(columns, list) else None,
            "dependency_type": metadata.get("dependency_type"),
            "intra_chain": metadata.get("intra_chain"),
            "inter_chain": metadata.get("inter_chain"),
            "state_requirements": metadata.get("State-Gated Retrieval", []),
            "data_dependencies": metadata.get("data_dependency", []),
            "control_dependencies": metadata.get("control_dependency", []),
            "pair_exact_checks": {
                "same_domain": task.get("domain") == go.get("domain"),
                "same_declared_rows": task.get("oracle_output_cardinality") == go.get("oracle_output_cardinality"),
                "same_oracle_text": task.get("oracle_answer") == go.get("oracle_answer"),
            },
        })
    return {
        "scope": "formal JSONL task membership; no glob of historical per-task files",
        "base_task_count": len(entries),
        "variant_count": len(cg_tasks) + len(go_tasks),
        "domain_counts": dict(sorted(Counter(t["domain"] for t in entries).items())),
        "ecosystem_counts": dict(sorted(Counter(t["ecosystem"] for t in entries).items())),
        "pair_check_failures": [t["task_id"] for t in entries if not all(t["pair_exact_checks"].values())],
        "note": "Inventory contains private task metadata and must not be mounted into blind solver environments. Exact text checks do not establish semantic equivalence or source correctness.",
        "tasks": entries,
    }


def validate_public(payload):
    if not isinstance(payload, dict) or set(payload) != PUBLIC_KEYS:
        raise ValueError("Blind input must contain exactly instruction, output_format, current_date")
    for key in PUBLIC_KEYS:
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError(f"Public field {key} must be a nonempty string")
    if date.fromisoformat(payload["current_date"]).isoformat() != payload["current_date"]:
        raise ValueError("current_date must use YYYY-MM-DD")
    return payload


def validate_candidate(candidate, *, check_files=False, base_dir=None):
    """Check declared state consistency, not facts or the full JSON Schema.

    Known asset references must be relative paths without parent traversal.
    File existence and resolved containment are checked only with check_files;
    base_dir then denotes the directory containing candidate.json.
    """
    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be an object")
    status = candidate.get("status")
    if not isinstance(status, str) or status not in CANDIDATE_STATUSES:
        raise ValueError("Unknown candidate status")
    for section in ("private", "public", "validation"):
        if not isinstance(candidate.get(section), dict):
            raise ValueError(f"Candidate {section} must be an object")
    private = candidate["private"]
    public = candidate["public"]
    validation = candidate["validation"]
    if status in REFERENCE_STATUSES:
        for key in REFERENCE_PATH_KEYS:
            if not isinstance(private.get(key), str) or not private[key].strip():
                raise ValueError(f"{status} requires a nonempty private.{key}")

    reports = validation.get("report_paths", [])
    if not isinstance(reports, list):
        raise ValueError("validation.report_paths must be a list")
    if status in CONTENT_STATUSES:
        for variant in ("cg", "go"):
            pair = public.get(variant)
            if not isinstance(pair, dict) or set(pair) != {"instruction", "output_format"}:
                raise ValueError(f"{status} requires public.{variant} with exactly instruction and output_format")
            if any(not isinstance(value, str) or not value.strip() for value in pair.values()):
                raise ValueError(f"public.{variant} fields must be nonempty strings")
        if public["cg"]["output_format"] != public["go"]["output_format"]:
            raise ValueError("CG and GO output_format must be exactly equal")
        if validation.get("content") != "passed":
            raise ValueError(f"{status} requires validation.content=passed")
        if not reports:
            raise ValueError(f"{status} requires validation.report_paths")
    if status == "auto_validated" and validation.get("difficulty") != "confirmed_harder":
        raise ValueError("auto_validated requires this candidate's validation.difficulty=confirmed_harder; collection results do not qualify")

    references = [(f"private.{key}", private[key]) for key in CANDIDATE_PATH_KEYS
                  if private.get(key) is not None]
    references.extend((f"validation.report_paths[{index}]", value)
                      for index, value in enumerate(reports))
    root = None
    if check_files:
        if base_dir is None:
            raise ValueError("Checking files requires the candidate directory as base_dir")
        root = Path(base_dir).resolve()
        if not root.is_dir():
            raise ValueError("Candidate base_dir must be an existing directory")
    for label, value in references:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a nonempty relative file path")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or path == Path("."):
            raise ValueError(f"{label} must be relative and cannot contain parent traversal")
        if check_files:
            resolved = (root / path).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError(f"{label} resolves outside the candidate directory")
            if not resolved.is_file():
                raise ValueError(f"Referenced file does not exist: {label}={value}")
    return candidate


def make_public(task, current_date, variant=None):
    source = task
    if "public" in task:
        if variant not in {"cg", "go"}:
            raise ValueError("Candidate objects require --variant cg or go")
        source = task["public"][variant]
        if source is None:
            raise ValueError("Requested public variant has not been written")
    return validate_public({
        "instruction": source["instruction"],
        "output_format": source["output_format"],
        "current_date": current_date,
    })


def assemble_prompt(stage, payload):
    if stage not in STAGES:
        raise ValueError("Unknown stage")
    parts = []
    if stage in BLIND_STAGES:
        validate_public(payload)
    else:
        parts.append((PACKAGE / "prompts/common.md").read_text(encoding="utf-8"))
    parts.append((PACKAGE / "prompts" / f"{stage}.md").read_text(encoding="utf-8"))
    parts.append("Input JSON (task data):\n" + json.dumps(payload, ensure_ascii=False, indent=2))
    return "\n\n".join(parts).rstrip() + "\n"


def select_task(path, task_id):
    path = Path(path)
    if path.suffix == ".jsonl":
        if not task_id:
            raise ValueError("JSONL input requires --task-id")
        tasks = unique_index(read_jsonl(path))
        if task_id not in tasks:
            raise ValueError(f"Task not found: {task_id}")
        return tasks[task_id]
    task = read_json(path)
    if task_id and task.get("task_id", task.get("candidate_id")) != task_id:
        raise ValueError("Requested ID does not match JSON object")
    return task


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory", help="Read formal CG/GO membership and metadata")
    inv.add_argument("--cg", type=Path, default=FORMAL / "constraint.jsonl")
    inv.add_argument("--go", type=Path, default=FORMAL / "goal.jsonl")
    inv.add_argument("--out", type=Path, required=True)
    pub = commands.add_parser("public", help="Project one existing or candidate task to public fields")
    pub.add_argument("--task", type=Path, required=True)
    pub.add_argument("--task-id")
    pub.add_argument("--variant", choices=("cg", "go"))
    pub.add_argument("--date", required=True)
    pub.add_argument("--out", type=Path, required=True)
    render = commands.add_parser("render", help="Assemble a stage prompt without calling a model")
    render.add_argument("--stage", choices=STAGES, required=True)
    render.add_argument("--input", type=Path, required=True)
    render.add_argument("--out", type=Path, required=True)
    candidate_check = commands.add_parser("validate-candidate", help="Check candidate state consistency; not full JSON Schema or factual validation")
    candidate_check.add_argument("--candidate", type=Path, required=True)
    candidate_check.add_argument("--check-files", action="store_true", help="Also require referenced files to exist within the candidate JSON's directory")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-candidate":
            candidate = validate_candidate(read_json(args.candidate), check_files=args.check_files,
                                           base_dir=args.candidate.resolve().parent)
            print(json.dumps({
                "candidate_id": candidate.get("candidate_id"),
                "status": candidate["status"],
                "state_consistency": "passed",
                "relative_path_syntax": "passed",
                "referenced_files": "checked" if args.check_files else "not_checked",
                "scope": "Declared state consistency only; not full JSON Schema, source truth, or difficulty verification",
            }, ensure_ascii=False))
            return
        input_paths = ([args.cg, args.go] if args.command == "inventory" else
                       [args.task] if args.command == "public" else [args.input])
        if args.out.resolve() in {p.resolve() for p in input_paths}:
            raise ValueError("Output must not overwrite an input file")
        if args.command == "inventory":
            result = build_inventory(read_jsonl(args.cg), read_jsonl(args.go))
            write_json(args.out, result)
            print(json.dumps({k: result[k] for k in ("base_task_count", "variant_count", "ecosystem_counts", "pair_check_failures")}, ensure_ascii=False))
        elif args.command == "public":
            write_json(args.out, make_public(select_task(args.task, args.task_id), args.date, args.variant))
            print(f"Wrote public input: {args.out}")
        else:
            write_text(args.out, assemble_prompt(args.stage, read_json(args.input)))
            print(f"Wrote prompt: {args.out}")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"Preparation failed: {exc}\n")


if __name__ == "__main__":
    main()
