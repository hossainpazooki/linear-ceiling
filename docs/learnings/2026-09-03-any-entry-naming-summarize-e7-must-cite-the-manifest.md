# `ledger_check` requires the corpus-manifest sha on ANY entry from 0024 on whose text contains `summarize_e7`, E9 entries included

kills: (nothing)
ts: 2026-09-03T04:04:07Z
commit: 5960c20
session: linear-ceiling-rl-design (session_01DksT5fTgXwHmKFfgLSXmnT)
status: verified
fact: The manifest-citation gate keys on the literal marker `summarize_e7` appearing anywhere in an
entry block numbered >= 24, not on the entry being an E7 entry. The first append of 0025 (an E9
amendment) was refused after writing -- "entry 0025 cites summarize_e7 figures but carries no
`e7-manifest-sha256:` line" -- because its coverage comparison quotes entry 0018's per-handoff rows
and names the summarizer that verified them. The fix is the 0024 pattern: compute
`e7_manifest.manifest_sha256(manifest_path(cfg))` and end the entry with `e7-manifest-sha256: <sha>`;
the gate also requires the newest such line to equal the committed manifest's sha. Any future E8/E9
entry that so much as mentions the E7 summarizer by name inherits the requirement.
basis: `grep -nE 'MANIFEST_MARKER =|MANIFEST_CITED_FROM =|if num < MANIFEST_CITED_FROM' src/linear_ceiling/ledger_check.py` ->
`75:MANIFEST_CITED_FROM = 24`, `76:MANIFEST_MARKER = "summarize_e7"`, `152: if num < MANIFEST_CITED_FROM or MANIFEST_MARKER not in block:`;
the refusal text quoted above is from `append_0025.py` at `01368b8` (restored ledger; fixed in `7213136`).
re-verify: `grep -nE 'MANIFEST_MARKER =|if num < MANIFEST_CITED_FROM' src/linear_ceiling/ledger_check.py && awk '/^### 0025/,/^### 0026/' ledger/ledger.md | grep -c '^e7-manifest-sha256:'` (expect the two lines and 1).
