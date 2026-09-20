# Blind retrieval policy: ten-task-v2-bounded-retrieval

This experiment-level policy overrides any permission for unrestricted bulk retrieval in the task or stage prompt. It applies equally to CG/GO development, attacks and formal retests. Existing safety refusals and tool restrictions remain binding.

Prohibited: whole-database/site downloads; bulk export of the complete task candidate dataset; prejoined exports containing all necessary answer information; reproducing these through split queries, exhaustive pagination or concurrent batches. A small dataset, a public API, or staying under the numerical limits does not exempt a prohibited export.

Allowed: search; ordinary bounded pagination for discovery; individual records and individual original articles; subsequent queries selected using identities or fields actually discovered earlier. Search/index pages may expose candidate identities, including the last discovery page; this is not permission to bulk export their substantive records. Retrieve individual evidence where needed and record what prior evidence determined each subsequent query. A single original article remains allowed; complete answer coverage by that article is a task-quality issue to audit, not automatically a bulk violation.

Uniform limits for every fresh blind session, fixed before testing:
- At most 20 requested list/search records per page, and at most 10 pages per logical query, including the initial page. Cosmetic parameter changes, sort changes, split batches or tool changes do not reset the same logical-query limit.
- At most 60 external retrieval request items in total. Each search query, open/click/find target, download, or other external target counts separately, including failed attempts. A tool invocation containing several targets counts as several requests. Cached web-tool requests count; local reads and local computation do not. Internal transport retries/redirects are not additional model request items.
- At most 2 external request items in flight at once, including items batched within a call. Wait for completion before issuing further items.
- When page size cannot be selected, use the source's ordinary default page and count it as one page; do not choose an export, all-results view or enlarged page. Record this default-page case for review; do not automatically invalidate a normal page merely because it contains over 20 records.

Local SQL, parsing and calculations on legally acquired materials remain allowed without a new calculation quota. Do not retry a resource explicitly denied as non-retryable, or obtain it through another representation/tool. On a quota limit or required inaccessible evidence, return the actual partial answer and limitations; do not invent missing values.

In the final limitations field, report external request count and any default-page cases or incomplete evidence. These self-reports do not replace independent trajectory review. Reviewers must separately check bulk scope, query dependencies, pages, request count, concurrency and safety compliance. Missing evidence is inconclusive; violations retain raw scores but cannot qualify as compliant admission or capability-zero results.
