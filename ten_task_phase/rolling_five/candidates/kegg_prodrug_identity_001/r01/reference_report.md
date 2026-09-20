The supplied complete official records support two distinct prodrug-to-active-drug pairs, totaling four output fields. The static oracle is derived from the two own Comment annotations and the linked Drug identity. It agrees with the provisional text supplied by the controller; this is not a new execution result.

The [group record](https://rest.kegg.jp/get/DG00739) defines four direct Drug members. The [member batch](https://rest.kegg.jp/get/D00752+D05094+D05095+D05096) supplies every complete member record. D00752 and D05094 explicitly link their active form to D05096. D05095 has an unrelated Comment. D05096 has no Comment in its complete terminated record. Evidence and all member decisions are recorded in evidence.json and inclusionledger.json.

From the r01 directory, run:

```sh
python3 reference.py --source-dir ../sources --out-dir reference_output
```

The program uses only the Python standard library. It reads 12-column fields, retains field continuations and record boundaries, enumerates the full Member field, verifies exact member coverage and Drug identities, and extracts only own Comment relations. It derives inventory.json, inclusionledger.json, evidence.json, executionchecks.json, and oracle.psv. It contains no answer IDs or expected row-count assertions. DG00739 and its name/type are the public scope constants.

Every observed target already has a Drug record in the supplied batch. Requiring an available target identity record is a completeness check, not an eligibility condition that targets belong to the group. An unresolved target, malformed record, missing member, or identity mismatch makes execution fail without an oracle. The program removes its designated result artifacts from OUT on failure and writes an unresolved execution record. Use a dedicated output directory.

The pinned scorer and its normalization remain unchanged. Both columns form the row key because a relation is identified by its ordered pair, including when one drug has multiple active forms. Source-access failure must be resolved outside the answer scorer: its empty-answer behavior must not convert such failure to a scored zero. Bare NONE is reserved for a successfully verified empty result.

The reference observation is 2026-09-12, at the two timestamps in source_manifest.json. The evaluation date remains 2026-09-09. No historical September 9 state or database-release identifier is claimed.

Execution of this delivered script, independent final quality audit, and full source-stability rechecks before and after any later blind evaluation are pending. No solver tests were performed. Human review: not_performed. Candidate state remains candidate until the controller verifies the reference and applies the workflow's required checks.
