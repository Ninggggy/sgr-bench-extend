"""Checks for answer leakage boundaries and stage prompt separation."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from prepare import assemble_prompt, build_inventory, main, make_public, validate_candidate


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.task = {
            "task_id": "example_001", "domain": "ARXIV",
            "instruction": "Find the requested public records.",
            "output_format": "Return ID|date.",
            "oracle_answer": "SECRET_ANSWER",
            "start_url": "https://private-hint.invalid/",
            "oracle_output_cardinality": 9,
            "metadata": {"nested": ["SECRET_HINT"]},
        }

    def test_projection_excludes_private_fields_and_nested_values(self):
        public = make_public(self.task, "2026-09-07")
        self.assertEqual(set(public), {"instruction", "output_format", "current_date"})
        prompt = assemble_prompt("04_blind_solver", public)
        for private_value in ("SECRET_ANSWER", "SECRET_HINT", "private-hint.invalid", "example_001"):
            self.assertNotIn(private_value, prompt)

    def test_blind_render_refuses_raw_task_instead_of_silently_accepting_it(self):
        with self.assertRaises(ValueError):
            assemble_prompt("04_blind_solver", self.task)
        with self.assertRaises(ValueError):
            assemble_prompt("05_shortcut_attacker", {**make_public(self.task, "2026-09-07"), "oracle": "hidden"})

    def test_confirmation_has_identical_instructions_and_no_construction_common(self):
        public = make_public(self.task, "2026-09-07")
        ordinary = assemble_prompt("04_blind_solver", public)
        confirmation = assemble_prompt("10_confirmation_solver", public)
        self.assertEqual(ordinary, confirmation)
        self.assertNotIn("非盲解阶段共同规则", ordinary)
        self.assertIn("非盲解阶段共同规则", assemble_prompt("02_candidate_designer", {"candidate": "draft"}))

    def test_candidate_variants_are_projected_separately(self):
        candidate = {"public": {"cg": self.task, "go": {**self.task, "instruction": "Goal variant."}}, "private": {"oracle": "SECRET"}}
        self.assertEqual(make_public(candidate, "2026-09-07", "go")["instruction"], "Goal variant.")
        with self.assertRaises(ValueError):
            make_public(candidate, "2026-09-07")

    def test_invalid_dates_and_nontext_instructions_fail(self):
        with self.assertRaises(ValueError):
            make_public(self.task, "2026-02-30")
        with self.assertRaises(ValueError):
            make_public({**self.task, "instruction": {"text": "x", "oracle": "secret"}}, "2026-09-07")

    def test_missing_or_duplicate_formal_pair_fails(self):
        with self.assertRaises(ValueError):
            build_inventory([self.task], [])
        with self.assertRaises(ValueError):
            build_inventory([self.task, self.task], [])


class CandidateConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "candidate_id": "example_candidate",
            "status": "content_validated",
            "private": {
                "oracle_path": "private/oracle.psv",
                "reference_script_path": "private/solve_reference.py",
                "source_manifest_path": "private/source_manifest.json",
                "state_graph_path": None,
            },
            "public": {
                "cg": {"instruction": "Find records using these constraints.", "output_format": "ID|date"},
                "go": {"instruction": "Find the requested records.", "output_format": "ID|date"},
            },
            "validation": {"content": "passed", "difficulty": "structural_only", "report_paths": ["private/audit.json"]},
        }

    def test_draft_can_have_no_reference_or_public_variants(self):
        candidate = {"status": "candidate", "private": {}, "public": {"cg": None, "go": None}, "validation": {}}
        self.assertIs(validate_candidate(candidate), candidate)

    def test_reference_and_later_states_require_each_reference_path(self):
        for status in ("reference_ready", "content_validated", "auto_validated"):
            for key in ("oracle_path", "reference_script_path", "source_manifest_path"):
                with self.subTest(status=status, key=key):
                    candidate = deepcopy(self.candidate)
                    candidate["status"] = status
                    candidate["private"][key] = None
                    candidate["validation"]["difficulty"] = "confirmed_harder"
                    with self.assertRaisesRegex(ValueError, key):
                        validate_candidate(candidate)

    def test_content_states_require_both_prompts_matching_format_and_evidence_status(self):
        for status in ("content_validated", "auto_validated"):
            for defect in ("missing_cg", "empty_go", "format", "content", "reports"):
                with self.subTest(status=status, defect=defect):
                    candidate = deepcopy(self.candidate)
                    candidate["status"] = status
                    candidate["validation"]["difficulty"] = "confirmed_harder"
                    if defect == "missing_cg":
                        candidate["public"]["cg"] = None
                    elif defect == "empty_go":
                        candidate["public"]["go"]["instruction"] = " "
                    elif defect == "format":
                        candidate["public"]["go"]["output_format"] += " "
                    elif defect == "content":
                        candidate["validation"]["content"] = "not_run"
                    else:
                        candidate["validation"]["report_paths"] = []
                    with self.assertRaises(ValueError):
                        validate_candidate(candidate)

    def test_collection_confirmation_cannot_upgrade_candidate(self):
        self.candidate["status"] = "auto_validated"
        self.candidate["collection_validation"] = {"difficulty": "confirmed_harder"}
        with self.assertRaisesRegex(ValueError, "this candidate's"):
            validate_candidate(self.candidate)
        self.assertEqual(self.candidate["validation"]["difficulty"], "structural_only")
        self.candidate["validation"]["difficulty"] = "confirmed_harder"
        self.assertIs(validate_candidate(self.candidate), self.candidate)

    def test_collection_confirmation_preserves_inconclusive_candidate_and_human_status(self):
        self.candidate["collection_validation"] = {"difficulty": "confirmed_harder"}
        self.candidate["validation"]["difficulty"] = "inconclusive"
        self.candidate["validation"]["human_validation"] = "not_performed"
        original = deepcopy(self.candidate)
        validate_candidate(self.candidate)
        self.assertEqual(self.candidate, original)
        self.candidate["status"] = "auto_validated"
        with self.assertRaisesRegex(ValueError, "this candidate's"):
            validate_candidate(self.candidate)

    def test_declared_paths_must_be_nonempty_relative_without_parent_traversal(self):
        for bad_path in ("", " ", "/tmp/oracle.psv", "../oracle.psv", "private/../../oracle.psv", "."):
            with self.subTest(path=bad_path):
                candidate = deepcopy(self.candidate)
                candidate["validation"]["report_paths"] = [bad_path]
                with self.assertRaises(ValueError):
                    validate_candidate(candidate)

    def test_file_checks_are_optional_and_require_actual_contained_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "candidate"
            root.mkdir()
            validate_candidate(self.candidate)
            with self.assertRaisesRegex(ValueError, "does not exist"):
                validate_candidate(self.candidate, check_files=True, base_dir=root)
            for name in ("oracle.psv", "solve_reference.py", "source_manifest.json", "audit.json"):
                path = root / "private" / name
                path.parent.mkdir(exist_ok=True)
                path.touch()
            validate_candidate(self.candidate, check_files=True, base_dir=root)
            oracle = root / "private/oracle.psv"
            oracle.unlink()
            outside = Path(temp_dir) / "outside.psv"
            outside.touch()
            oracle.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "outside"):
                validate_candidate(self.candidate, check_files=True, base_dir=root)

    def test_cli_reports_check_scope_and_rejects_inconsistent_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.json"
            path.write_text(json.dumps(self.candidate), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                main(["validate-candidate", "--candidate", str(path)])
            report = json.loads(output.getvalue())
            self.assertEqual(report["referenced_files"], "not_checked")
            self.assertIn("not full JSON Schema", report["scope"])
            self.candidate["status"] = "auto_validated"
            path.write_text(json.dumps(self.candidate), encoding="utf-8")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failure:
                main(["validate-candidate", "--candidate", str(path)])
            self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
