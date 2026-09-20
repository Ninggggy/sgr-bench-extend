The delivered oracle is a source-supported proposal. reference.py has not been executed in this role. Its six supporting files therefore remain pending.

The [official history](https://arxiv.org/abs/1705.08366) lists three versions. Section 1.3 in [v1](https://arxiv.org/pdf/1705.08366v1) uses unrestricted selections from the combined matrices and rank t. Section 1.3 in [v2](https://arxiv.org/pdf/1705.08366v2) uses matched indices and rank 2t. The supplied v3 PDF evidence and [official v3 HTML](https://arxiv.org/html/1705.08366v3) agree on the latter definition. The v3 corrected theorem requires 2-very general position, whose Definition 11 includes 2-general position. Earlier main statements require 2-general position.

Run from any directory:

    python3 r02/reference.py --source-dir DIR --out r02

DIR must contain v1.txt, v2.txt, v3.txt, v3.html, and history.html, as archived by the controller. Keep the ten delivered construction files together in r02. Original PDFs are optional additional manifest inputs; their text outputs are required.

The program parses identity, official version numbers and UTC timestamps, matrix-selection wording, symbolic ranks, theorem numbering, the numerical assumption parameter, and the dimension boundary. It validates these against the transparent annotations and public scope, checks correction precedence and named-condition inclusion, and compares the reproduced PSV with the proposal. Source hashes, matched anchors, inclusion decisions, dependencies, and validation results are generated deterministically. The equation (13) rendering discrepancy is recorded but is not used to infer any output.

A missing or conflicting decisive anchor causes failure, not an invented value or dropped row. Existing differing output files are never overwritten. These are corpus and construction checks, not solver tests or proof verification. Controller execution must establish whether the archived extraction matches the reference's anchors before the candidate is treated as executable-validated.
