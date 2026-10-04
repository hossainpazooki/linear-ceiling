# Handoff — main-branch close: PRs #8–#17 merged, Condition 1 ruled, 0046/0047/0054/0055/0056 landed, E-TRUNC runbook and figures draft staged

2026-10-04, ~10:15Z. Describes `9e5249b` (= origin/main, CI green) **plus this close's uncommitted files** (listed under
"Open / next" item 1). Session: main-branch dev-fd, transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\f87605d5-fe82-43ce-b903-815d591b48ad.jsonl`. Two sibling lanes closed
the same day and are NOT re-described here: the Llama lane
(`docs/handoff/2026-10-04-llama-branch-close-e8-amendment-0052-0053-on-the-ledger-long-cell-0050-preview-ready-camera-ready-paste-delivered.md`)
and the E-TRUNC lane (`docs/handoff/2026-10-04-e-trunc-for-camera-ready-0055-and-0056-on-the-ledger-pr-17-merged-pilot-figures-citable.md`).

## Current state

- **built — every co-author PR is closed out.** #8, #9, #14 merged (`4edb406`, `c7911a4`, `b26dfdb`) after their frozen
  files were hash-checked on the merged tree; #13 merged (`f836c41`) after this session resolved its run-queue conflict and
  restored the `e9_tail.py` docstring; #10 merged (`f44f5d0`); #11 merged (`672dad9`) keeping
  `results/historical-summary.json` by ruling, its label added in this close (uncommitted); #12's resolved content committed
  on main (`7544f7f`) and the PR recorded merged by a zero-file ours-merge (`1752c82`); #16 (Lean proofs) and #17 (E-TRUNC)
  merged (`e49f63a`, `c37f626`). No PR is open.
  re-verify: `gh pr list --repo hossainpazooki/linear-ceiling --state open --json number --jq length`   # 0
- **built — ledger entries landed today, file order after 0045:** 0046, 0047, 0054, 0052, 0056, 0055, 0053, 0050. This
  session drafted 0046, 0047, 0054, 0056 and checked 0050/0055 before the operator appended; 0052/0053 are the Llama lane's.
  `ledger_check` chains by FILE order, not number. Staged, unrun: 0048/0049 (figures of 0046/0047), 0051 (Llama long
  figures), 0057 (E-TRUNC figures, this close). Next free **0058**.
  re-verify: `grep -o '^### 00[45][0-9]' ledger/ledger.md | tail -9 | tr '\n' ' '; .venv/Scripts/python.exe -m linear_ceiling.ledger_check | tail -1`   # 0045 0046 0047 0054 0052 0056 0055 0053 0050, ledger ok
- **built — Condition 1 discharged by operator ruling** (issue #7 + PR #12 as the confirmation; entry 0054 `a2742b9`), and
  **issue #7 closed** with a row-by-row disposition: R13, R14, the configuration share and 0045's tail recomputed
  operator-side from the raw records and matching the ledger; R2, R5/R6, R11/R12 and a second-person e9l/e9s recompute
  dropped by ruling (https://github.com/hossainpazooki/linear-ceiling/issues/7#issuecomment-5978012666).
  re-verify: `gh issue view 7 --repo hossainpazooki/linear-ceiling --json state --jq .state`   # CLOSED
- **built — co-author pilot figures citable in paper text** under a provenance sentence (entry 0056 `caccab5`); the
  ledger's own R1/R8/R12 for figures are unchanged, so 0048/0049 still need the operator's runs. The W1/W7 sentences and the
  W2 limitation paragraph are in `~/dev/briefs/2026-10-04-lcfm-camera-ready-patch.md` (private).
  re-verify: `grep -c "Co-author pilot figures admitted\|provenance sentence" ledger/ledger.md`   # ≥ 1
- **built (uncommitted) — E-TRUNC runbook** `docs/2026-10-04-e-trunc-gpu-runbook.md`: one g6e.4xlarge sitting, four levels
  FULL → L65 → L49 → L32, per-level `EXP` for `tools/ec2/*`, R3 table with the four configs' LF-normalized shas and the four
  coverage shas, home prerequisites (`--calibrate-tau` × 4), ≈ 4.8 h driver bound (3.58× E9-long, recomputed), ≈ $18–20.
  re-verify: `grep -c "e9t-l32" docs/2026-10-04-e-trunc-gpu-runbook.md`   # > 0
- **built (uncommitted) — `docs/drafts/append_0057.py`**, the E-TRUNC figures entry: runs `summarize_e9` per level then
  `compare_levels` in-process, prints the reading the reader returns, carries 0055's two limitations and an erratum to
  0055's re-matching sentence with counts read from `shrinkage.json`. Rendered from a fabricated comparator output (605
  words, no `verdict:` line); refuses on the real tree because no run exists.
  re-verify: `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe docs/drafts/append_0057.py --box x --launched x --finished 2026-10-20T00:00Z --dataset x --preview 2>&1 | tail -1`   # ValueError: ...results\e9t-full\report.json does not exist; E9 has not run
- **built (uncommitted) — operator-side refutation of 0055's stated figures**
  `docs/reviews/2026-10-04-0055-stated-figures-recomputed.md`: every figure survives; one sentence ("re-matching loses more
  than the removal on 10 handoffs") misdescribes its number — 10 is the count above 0.05, 14 have any loss, none exceed the
  removal. Not independent (same machine and mirrors).
  re-verify: `.venv/Scripts/python.exe -c "import json;s=json.load(open('results/e9t/shrinkage.json',encoding='utf-8'));p=s['per_handoff'].values();print(s['n_void'],s['n_zero'],s['n_with_rematching_loss_over_0_05'],sum(v['rematching_loss']>0 for v in p))"`   # 14 11 10 14
- **built (uncommitted) — small fixes:** `append_0051.py` preview forces UTF-8 stdout; `tools/cache_injection_pilots/results/README.md`
  labels the historical file as not evidence, linked from the pilots README; drafts README and CLAUDE.md allocator at 0058.
  re-verify: `.venv/Scripts/python.exe -c "print(open('docs/drafts/append_0051.py',encoding='utf-8').read().count('reconfigure('))"`   # 1
- **built (uncommitted) — five learnings** under `docs/learnings/2026-10-04-*` (CRLF raw-bytes guard; cp1252 preview;
  shared-tree collision; ours-merge for a PR whose content landed; 0055's re-matching wording) with index rows. Every
  re-verify line was executed from the written files and reproduced. **The rigor `check-learnings` form gate is not
  installed in this plugin version (0.1.0 ships no such script) and has not run.**
- **planned — the four registered sittings, none started:** 0047 cache behavior, E-TRUNC, the Llama long cell (0050),
  0046 same-model extension.
- **unknown — the LCFM camera-ready.** Deadline was 2026-10-04 11:59Z per the operator; whether the paste list was applied
  is not recorded anywhere this session could read.

## Locked decisions

- **Condition 1 is discharged by ruling, not by signatures** (operator, 2026-10-04; 0054). Reason: the review existed and
  its scope was stated; the operator judged the two-approval clause no longer worth gating on. Pick-up checks that 0054 is on
  the ledger, not that signatures exist.
- **Issue #7's uncovered rows were dropped, not deferred** (operator, 2026-10-04). Reason: no ledger sentence depends on them
  and no reviewer asked. The paper says the long and scaled-short cells were recomputed by the operator only.
- **A second-person recompute of 0036/0038 is not a reviewer weakness** (operator, 2026-10-04). Not on any camera-ready or
  MLSys list; welcome if a co-author volunteers.
- **Co-author pilot figures may be cited in paper text with a provenance sentence; the ledger's evidence rules stay** (0056).
  Reason: the operator's standard is "figures posted, code and environment on the record"; the ledger still needs R1/R8/R12.
- **`historical-summary.json` stays in the tree, labelled** (operator, PR #11). Reason: kept as a historical archive; the
  label forbids citing it.
- **f* stays an oracle LOWER BOUND, recompute not remove** (0023:1278/1281, 0027; reaffirmed in 0054 and the #12 merge).
  Reason: a README cannot overturn a registered reading; a contrary view needs a corrective entry.
- **E-TRUNC rulings:** margin ±0.005 on the far-from-seam median; void gate |M_∩| ≥ 2,000 (not the 0.80 ratio, which voids
  29/35); L32-native deferred. Both of the last two are stated LIMITATIONS by operator ruling (0055 Scope, design §9b).
- **Parallel sessions run cloud-only or in their own worktree** (operator feedback, 2026-10-04). Reason: the shared-tree
  collision (learning 2026-10-04). Saved as global memory `parallel-sessions-cloud-runs-or-own-worktree`.
- **R8 backups may be public or private** (operator, 2026-10-04; admission doc §2.4).

## Reuse map

- Entry-script pattern, newest: `docs/drafts/append_0057.py` (`build_entry(out, meta)` separable from the reader, so the
  text can be rendered from a fabricated output before any run); `append_0048.py` / `append_0049.py` for the two
  registered runs.
- Frozen-file and guard hashing on a CRLF clone: `linear_ceiling.hashing.sha256_text_file`; never compare `git show` bytes
  with `read_bytes()`.
- E-TRUNC reader: `python -m linear_ceiling.summarize_e9_trunc [--shrinkage]`; its in-process functions `load_levels`,
  `shrinkage`, `compare_levels`, `_references`.
- Box tooling: `tools/ec2/{box.sh,setup.sh,run.sh,probe_e9l.py,pull.py,verify_mirror.py,release_sweep.sh}`, all
  parameterised by `EXP`; the E9-long runbook `docs/2026-09-10-e9l-gpu-runbook.md` is the shape every new runbook copies.
- Runbooks per sitting: `docs/2026-10-01-cache-behavior-runbook.md` (0047), `docs/2026-10-04-e-trunc-gpu-runbook.md`,
  `~/dev/briefs/2026-10-04-llama-long-sitting-c-preflight.md` (0050), `docs/2026-09-30-consolidation-runbook.md` (0046).
- Admission path for co-author runs: `docs/2026-10-03-co-author-run-admission.md`.
- Response map, with today's two ruling sections and the E-TRUNC limitations: `docs/2026-09-30-review-response-map.md`.

## Invariants

- The ledger is append-only and chained by FILE order; the drafts README is the only allocator. Re-read it at HEAD before
  naming a number (two numbers were taken by other lanes within hours today).
- No ledger figure is typed: every number comes from a fail-closed reader run in-process inside the entry script.
- Append with the venv interpreter and chain the retire: `.venv/Scripts/python.exe docs/drafts/append_NNNN.py && git rm -q
  docs/drafts/append_NNNN.py` (plus its test if one exists, or CI goes red on the ordering guard). The system Python lacks
  the package, so its post-append check fails and the `&&` skips the retire.
- Previews need UTF-8 stdout on this console (`PYTHONIOENCODING=utf-8` or `sys.stdout.reconfigure`).
- Claude never writes git history (rigor git-guard; it also matches git commands quoted inside heredoc bodies — write such
  text through a file).
- `results/` never enters git; the one tracked results file (`tools/cache_injection_pilots/results/historical-summary.json`)
  is labelled not-evidence.
- A second session that edits code works in its own worktree on its own branch.
- `../kv-transfer-replication` is read-only; detach it at a pin only inside an append block and return it to main.

## Open / next

1. **Operator: commit this close** (nothing else is uncommitted):
   ```bash
   cd ~/dev/linear-ceiling
   git add tools/cache_injection_pilots/results/README.md tools/cache_injection_pilots/README.md
   git commit -m "docs: label the historical cache-injection summary as not evidence"
   git add docs/drafts/append_0051.py
   git commit -m "fix: force UTF-8 stdout in the 0051 preview"
   git add docs/2026-10-04-e-trunc-gpu-runbook.md docs/drafts/append_0057.py docs/drafts/README.md CLAUDE.md \
           docs/reviews/2026-10-04-0055-stated-figures-recomputed.md
   git commit -m "docs: E-TRUNC runbook, 0057 figures draft, 0055 figures recomputed"
   git add docs/handoff/ docs/learnings/
   git commit -m "docs: main-branch close; five learnings"
   git push origin main
   ```
2. **Record the camera-ready outcome** (applied or not) as a dated note in the response map; the MLSys draft depends on it.
3. **First sitting: 0047 cache behavior** (recommended order, not ruled: 0047 → E-TRUNC → 0050 long cell → 0046). 0047 is
   the sharpest reviewer point (W1) and its pilot cannot reach the ledger without this run. Blocker: an 80 GB card; a 48 GB
   card needs the largest-case probe first (runbook).
4. **Before the E-TRUNC sitting:** `summarize_e9 --calibrate-tau --config config/e9t-<level>.toml` × 4 at home (runbook §4
   step 0); commit the runbook so `LC_SHA` carries it.
5. **Carried, operator-owned:** send the practitioner consultation (reply-by Oct 10; draft in `~/dev/briefs`); PI review
   Oct 15; HF login revoke; the two empty project-account datasets; AWS key pair. MLSys deadline 2026-10-30 12:00 PDT.
