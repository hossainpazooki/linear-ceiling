# Handoff — the Llama long cell (0050 → 0051) RAN on a RunPod A100 with the Mac mini as home side: 32 of 32, summarizer PASS, R8 verified, 0051 appended; 0058 (f* is the oracle removal fraction) on the ledger; camera-ready judgment rows done

2026-10-08 ~02:20Z. Describes `8696e83` (origin/main at write time) **plus** the two commits made on the Mac mini
(`91cea79` ledger 0051, `62982a8` script retired; fetched into this clone as `FETCH_HEAD`, `ledger_check` ok, awaiting the
operator's fast-forward and push from Windows) **plus this session's uncommitted docs** (listed under "Open / next" 1).
Same session as the 0047 and 0046 closes (`03ca9159`); this brief covers what happened after them. The sitting's
minute-by-minute evidence is `docs/2026-10-07-llama-long-cell-runpod-runbook.md` §6; this brief points at it.

## Current state

- **on the ledger — 0058, the corrective reading of f*** (operator ruling 2026-10-07, chain `5ba3adab…`, commit `1ca3650`):
  f* is the oracle REMOVAL fraction, not a lower bound on real selective recompute — the mean is over the remaining tokens,
  so the exact-repair fraction on the all-token mean is at most f*, while 0023's two reasons push a real scheme's fraction
  up; no ordering either way; (f* = 0) ⇔ (g* = 0), so no verdict moved. 0023:1281's words requirement and 0027's floor
  reading withdrawn; the summarizer, `f_star` docstring, README, CLAUDE.md and the staged 0057 carry the new words.
  re-verify: `grep -c "oracle REMOVAL fraction" src/linear_ceiling/summarize_e9.py ledger/ledger.md`   # 1 and ≥ 1
- **on the ledger (Mac commit, fetched) — 0051, the Llama long cell's figures**: 32 of 32 handoffs (longer side 32,769–81,920
  Llama-3 tokens) on `meta-llama/Llama-3.1-8B` inside its native window, source 3.2-3B, this pair's own τ; same-model
  f*(τ_K) median 0.0000 (p10/p90 0) stated descriptively (band word HOLDS, decides nothing — the cell has no row); cross
  arm 0.7626 / 0.8522 beyond DEGRADES; RoPE controls on 97 dumps (cap inside every 131,072 window; frequencies identical per
  role); stated beside 0036 and never pooled. The entry states the coverage pin's two renderings (0050's `16121e67` = CRLF
  bytes; the box's LF `9f10092b`; 993 identical lines) and the R8 dataset.
  re-verify: `git show FETCH_HEAD:ledger/ledger.md | grep -c "^### 0051"`   # 1 (after the push: `grep -c "^### 0051" ledger/ledger.md`)
- **built and verified — the run itself.** RunPod SECURE pod `uua1cpjql18jb6` (community A100 stock vanished mid-create),
  A100-SXM4-80GB driver 580.126.16, $1.59/h, created 17:01:48Z, driver 17:35:23 → 19:46:17Z (2 h 11 min, 3,453,566 tokens),
  released 20:03:45Z PROVEN GONE, **sitting $4.80**. Measured probe at T = 74,233: 8B fp32 peak 69.75 GiB reserved,
  headroom 9.08 GiB, `sdpa_repeat_kv`. Home puller: 591 hash checks, 49,377,348,389 B, all three kept trees verified then
  removed from the pod. Home `summarize_e9` PASSED on the Mac in 2 min 21 s (kept re-score within 0028's tolerance on
  16 GB RAM — the risk the plan named did not materialise).
  re-verify: `ssh hossa@192.168.1.26 'shasum -a 256 ~/dev/linear-ceiling/results/e9fl/report.json | cut -c1-16'`   # b046bb9dd70d56d2
- **built and verified — R8**: `hossainpazooki/linear-ceiling-e9fl-2026-10-07` (private), 571 files / 47.7 GB, `BACKUP
  VERIFIED` 2026-10-08 01:31Z (`lfs-compared 398, downloaded+hashed 173, problems 0`); card and `SHA256SUMS` at the root;
  upstream mapper inputs included in the upstream layout. Staging copy `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07/`
  on the Mac (44 G); card copy at `~/dev/hf-staging/linear-ceiling-e9fl-2026-10-07-README.md` on Windows.
  re-verify: `curl -s -o /dev/null -w "%{http_code}\n" https://huggingface.co/api/datasets/hossainpazooki/linear-ceiling-e9fl-2026-10-07`   # 401 (private, exists)
- **built — the Mac mini is a home station** (`~/dev/linear-ceiling`, `~/dev/kv-transfer-replication@06f8d55`, venvs, Hub
  inputs, traces, E7/E8 reports, `~/hf-stage` with both gated snapshots complete, RunPod key, pod keypair, `hf` CLI). Reach it
  by IP (`192.168.1.26` on Wi‑Fi; the mDNS name does not resolve from Windows); `~/.local/bin` is not on a non-interactive
  ssh PATH; `git pull`/checkout there is the operator's (the git-guard matches the command text over ssh too).
  re-verify: `ssh hossa@192.168.1.26 'cd ~/dev/linear-ceiling && git log --oneline -1 && .venv/bin/python -m linear_ceiling.ledger_check | tail -1'`   # 62982a8 …; ledger ok
- **built — `tools/runpod/sitting_b.sh` takes the long cell** (`CONTEXT_FLOOR`, `DUMP_FREE_GIB`; `8696e83`), rehearsed on the
  Mac (`REHEARSAL=1`) and run on the box.
- **recorded — the camera-ready judgment rows** (review `docs/reviews/2026-10-07-submitted-camera-ready-…md` §6): the
  lower-bound sentence's reach (three sentences; App. D right, App. A's reason backwards — settled by 0058), the scoping
  sentences (Llama absent; "a single model pair" false of the record), Table 5's exclusion counts (reconcile; the "4 empty
  receiver" handoffs also exceed 81,920 — precedence, not disjoint facts). Q3 recommended: Llama enters the MLSys draft as the
  second PAIR; now with a long cell too.

## Open / next

1. **Commit (operator).** Windows: discard the local copy of the retired script (identical to the Mac's committed version),
   `git merge --ff-only FETCH_HEAD`, push; then this session's docs: the runbook, five learnings + index, drafts README and
   CLAUDE.md allocator lines, this brief + HANDOFF row. Mac: `git pull --ff-only`. Then **revoke the HF token (R9)**.
2. **MLSys draft** (Oct 30): Llama in as the second pair (short cell 0044 + cross arm + E8 0053 + long cell 0051); the scoping
   sentences rewritten (§6.2 of the review); App. A's "because" clause → App. D's denominator (0058); Table 5's clause.
   #18 rows 29/36/40 move to UPDATE.
3. **0057 (E-TRUNC figures)**: the only staged draft left; needs its L40S/80 GB sitting (`docs/2026-10-04-e-trunc-gpu-runbook.md`);
   home side can be the Mac now.
4. lag-ladder entry 0004 re-pin (kvt moved); `e9.py` `fsync`-on-read-handle Windows red; PR #19 ruling.
5. Housekeeping: `pull_verify_b.py`'s defaults should follow `--exp` (learning 2026-10-08); the launcher's `sitting_b.*`
   names are short-cell in name only; the Mac staging copy (44 G) once a second local copy exists.
6. **Issue #21** (to @emersony99): R12 recompute of 0051 from the Hub mirror (his read-only token for the October datasets
   already covers it) and the MLSys second-pair section. Supersedes #15.

## Learnings written this session (docs/learnings, 2026-10-08)

consumer `allow_patterns` for a staged gated cache · a registered sha pin is a rendering · `pull_verify_b` constant-bound
defaults · detached pushes with `< /dev/null`, `read -s` alone · zsh over ssh does not word-split. (10-07's six from the
0047/0046 sittings are in the earlier briefs.)
