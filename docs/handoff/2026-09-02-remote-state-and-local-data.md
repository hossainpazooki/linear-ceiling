# Handoff — what is on the remote, what is local by design, and why (reviewer note)

2026-09-02. Newest commit this brief describes: linear-ceiling `bc5acbf` (= `origin/main`,
0 ahead / 0 behind at 03:5xZ); upstream kv-transfer-replication `36d73b3` (= its `origin/main`).
Pick-up measures drift from `bc5acbf`. This brief is the answer to a reviewer's natural
question after the 2026-09-01/02 sessions -- "is everything pushed, and where are the traces
and their hashes?" -- written so the answer can be checked rather than believed.

## Current state

**built — everything the sessions produced is on `origin/main`.** Entry 0023 (E9 per-token
rule) and its upstream re-pin; the CRLF config-sha fix for E9; provisional entry numbering;
`summarize_e7 --strategy-override` with its real-corpus pin test; `e7_manifest fetch`; the
handoff rows and learnings entries; Track B's merge (PR #1) and entry 0024.
re-verify: `git fetch -q origin && git rev-list --left-right --count origin/main...HEAD` → `0	0`; `git status --short` → only the untracked `.claude/` (harness state, not repo content).

**built — the corpus is LOCAL ONLY, by rule, and the committed manifest is its record.**
`traces/` is gitignored (`.gitignore` line 28) and the repo brief says real trajectories never
enter history: 188 public files, 151 MB, re-acquirable. What IS committed is
`config/e7-manifest.json` (entry 0024): sha256 + byte count for all 188, plus the S3 key /
ETag / size for the 180 SWE-bench objects. The manifest on this machine is byte-identical to
`origin/main`'s; the 2026-09-02 restoration changed nothing in it, which is the proof the
rebuilt corpus is the recorded one.
re-verify: `git check-ignore -v traces/tau-bench/gpt-4o-airline.json` → `.gitignore:28:traces/`; `git diff --quiet origin/main -- config/e7-manifest.json && echo same` → `same`; `.venv/Scripts/python.exe -m linear_ceiling.e7_manifest check` → `manifest ok: 188 files match disk; sha256 371fb4bf3cb0…`.

**built — the corpus was emptied on 2026-09-02 and rebuilt byte-for-byte.** `traces/` was
found empty (mtime 2026-09-01 23:11:58 −0400) in the window a Track B worktree that reached it
by directory junction disappeared; mechanism recorded as *suspected*, actor not established
(learnings `2026-09-02-worktree-junction-emptied-the-traces.md`). Rebuilt with the new
`e7_manifest fetch` (180 SWE-bench files from S3, refused on any sha/size mismatch, 27 s) and
from fresh clones of `sierra-research/tau-bench` (`historical_trajectories/`) and
`sierra-research/tau2-bench` (`data/tau2/results/final/`) after CRLF→LF normalization (a
Windows clone hands back CRLF copies that hash wrong; learnings
`2026-09-02-traces-restored-from-manifest-crlf-clone.md`).
re-verify: `stat -c '%y' traces` shows the 23:11:58 mtime is gone only if the directory was recreated; the check that matters is `e7_manifest check` above (188/188).

**built — `results/` is local only, by rule.** Gitignored except two placeholders; numbers
reach the ledger only through a fail-closed summarizer and an ordering-guarded append script.
So `results/e7/recon.json` (the 0024 recon and the 0022 sensitivity block), `results/e8/report.json`,
and `results/e9/calibration/tau.json` exist here and nowhere on the remote. Their figures are
on the record only where an entry cites them (0020, 0023, 0024); the sensitivity figures are
NOT yet in any entry.
re-verify: `git ls-tree -r --name-only origin/main | grep -c '^results/'` → `2`; `ls results/e7/` → `recon.json skeleton_report.json summary.md`.

**built — the 0022 sensitivity, measured and pinned (ruling 1, second half).**
`summarize_e7 --strategy-override composio_swekit=exact` reproduces entry 0022's 565,025 /
255,690,850 = 0.2210% exactly (`tests/test_e7_sensitivity.py::test_pin_composio_exact_reproduces_entry_0022`,
gated on `LC_REAL_TRACES=1` + traces present). The ruling's run
(`composio_swekit=exact,o4-mini*=exact,gpt-4.1*=exact`) gives, under exact: registered cold
0.2210%, registered warm 1.96%, request-level cold **10.62%** (from 10.0012%), request-level
warm 9.13%; the tau2 overrides move per-agent totals only (no Lane A measurable trajectory
there). Note "o1-mini" is a receiver MODEL inside the `composio_swekit` agent, not an agent;
the parser refuses it by name. Decides nothing; ships in the 0009 successor (0022).
re-verify: `LC_REAL_TRACES=1 .venv/Scripts/python.exe -m pytest -q tests/test_e7_sensitivity.py` → `5 passed`; `.venv/Scripts/python.exe -c "import json;s=json.load(open('results/e7/recon.json'))['sensitivity'];print({k:f'{100*v:.4f}%' for k,v in s['cache_aware_override']['pooled']['ratios'].items()})"` → `{'registered_cold': '0.2210%', 'registered_warm': '1.9618%', 'request_cold': '10.6157%', 'request_warm': '9.1319%'}`.

**built — numbering provisional (ruling 2).** `docs/drafts/README.md` is the only allocator;
numbers are assigned when a script is staged, in staging order; no living doc names a number
for an unstaged entry. Queued, unnumbered: the H-E9 verdict (after the A100) and the E8
amendment.
re-verify: `grep -c "PROVISIONAL" docs/drafts/README.md` → 1; `grep -n "0025" CLAUDE.md docs/2026-09-02-e9-gpu-runbook.md` → no hits.

**in-progress — nothing. planned —** the A100 request → runbook → `summarize_e9` → H-E9
verdict entry; the 0009 successor (per-suite calibration / exact-where-public, n = 420, the
sensitivity figures) in the MLSys cycle; the E8 amendment.

## Locked decisions

- **Traces and results stay out of history.** Reason: the repo's numbers-freeze discipline
  (CLAUDE.md; entries 0006/0024) — figures enter the ledger only via summarizers, and the
  manifest is the corpus's identity; committing 151 MB of third-party corpus adds nothing the
  manifest does not already prove.
- **Restoration is by manifest hash, never by trust in a source.** Reason: the fresh tau clones
  hashed wrong (CRLF) until normalized; `fetch` refuses on mismatch and writes no partial file.
- **The sensitivity figures get no entry of their own.** Reason: 0022's "one replay supersedes
  the figures once"; they ship in the 0009 successor bundled with n = 420. Until then the paper
  cites request-level tokenizer sensitivity as "measured in `recon.json` pending registration".
- **Entry numbers are provisional; the drafts README allocates.** Reason: append-only chain
  would otherwise queue the cheap E8 amendment behind the A100-gated H-E9 verdict.
- **The traces-loss mechanism is recorded as suspected, no actor named.** Reason: the evidence
  supports the junction mechanism and the time window, not who ran the delete.

## Reuse map

- `src/linear_ceiling/e7_manifest.py` — `fetch` (S3 re-download verified by sha256+size),
  `check` (disk vs manifest both directions), `write` (NETWORK, once).
- Restoring the 8 tau/tau2 files: clone the two sierra-research repos, take the files by name
  from the paths above, `.replace(b"\r\n", b"\n")`, then `e7_manifest check`.
- `summarize_e7 --strategy-override AGENT=exact[,…]` (fnmatch; refuses a no-op) →
  `results/e7/recon.json["sensitivity"]`; `tests/test_e7_sensitivity.py` for the pin.
- `docs/learnings/2026-09-02-*.md` — the three entries this note rests on.

## Invariants

- `traces/` and `results/*` are gitignored; a commit that adds either breaks the numbers-freeze
  rule and the seal/summarizer provenance model.
- `e7_manifest check` must say 188/188 before any E7 driver run or summary is trusted; the
  driver and summarizer refuse on disk/manifest/report disagreement.
- A worktree must never reach `traces/` by junction; a recursive delete goes through it.
- `LC_REAL_TRACES=1` is the only way the real-corpus pin test runs; without it the suite reports
  `1 skipped`, which is a skip, not a pass.

## Open / next

1. Request the A100; run `docs/2026-09-02-e9-gpu-runbook.md` verbatim; `summarize_e9` at home;
   stage the H-E9 verdict script (number assigned then).
2. Commit this brief and its index row (below). Nothing else is pending on either repo.
