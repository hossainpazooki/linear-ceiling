# Handoff — 0047's registered run is DONE on RunPod (35/35, summarizer passed, $2.57); 0049 is blocked by its ordering guard and one unpinnable manifest field; 0046's inputs are prepared on Linux and reproduce the frozen manifest

2026-10-07 ~01:40Z. Describes `580f73c` (= origin/main at the operator's commit of the runbook) **plus this close's
uncommitted files** (listed under "Open / next" item 1). Session: pickup → camera-ready record → 0047 sitting, transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\03ca9159-156a-4d71-9250-b553c1b73da3.jsonl`. The sitting's
minute-by-minute evidence is `docs/2026-10-06-cache-behavior-runpod-runbook.md` §6; this brief points at it.

## Current state

- **built — the registered 0047 run exists and is verified.** One sitting on RunPod (`mvwb1quo5c2hi1`, A100-SXM4-80GB
  community, $1.39/h, 23:43–01:34Z), driver at `7c9a5fd`, inputs manifest `2aeee576…`, 35/35 handoffs, `complete: true`,
  max peak 24.95 GiB (= the pilot's figure), every control passed. Home mirror `results/cache-behavior/` (73 files, 318 MB):
  35/35 case fingerprints match `report.json`; `--summarize` from the LF clone passed. Pod terminated, PROVEN GONE.
  **Sitting $2.57**, campaign $2.57 of a $10 cap, balance $7.51.
  re-verify: `.venv-cb/Scripts/python.exe -c "import json,hashlib,pathlib;o=pathlib.Path('results/cache-behavior');r=json.load(open(o/'report.json'));print(r['complete'],len(r['scores']),sum(hashlib.sha256(open(o/v['file'],'rb').read()).hexdigest()==v['sha256'] for v in r['scores'].values()),r['git_commit'][:7])"`   # True 35 35 7c9a5fd
- **built — the operator figures reproduce the pilot's at printed precision** on 9 of 11 checked values (reuse 0.1424 /
  90.20 %, cyclic 0.2826 / 85.49 %, attention 41.00 % / 8.85 %, reuse p10/p90 0.0802 / 0.1900); random-arm mean KL
  11.2981 vs the pilot's 11.2982 (4th decimal, different card); the conditional weighted delta **0.3012** — the App. F
  figure PR #18 could not source in any admitted document — now has an operator-side value. These are the summarizer's
  outputs, NOT ledger figures: they enter only through `append_0049.py`.
  re-verify: `cd ~/dev/lc-lf && PYTHONIOENCODING=utf-8 ~/dev/linear-ceiling/.venv-cb/Scripts/python.exe -m tools.cache_behavior.run --summarize --inputs ~/dev/linear-ceiling/results/cache-behavior/inputs --output ~/dev/linear-ceiling/results/cache-behavior | ~/dev/linear-ceiling/.venv-cb/Scripts/python.exe -c "import json,sys;d=json.load(sys.stdin);print(d['complete'],round(d['arms']['reuse']['mean_kl']['median'],4),round(d['attention']['conditional_weighted_delta_mean']['median'],4))"`   # True 0.1424 0.3012
- **blocked — `append_0049.py` refuses twice over.** First its ordering guard (`0048 present, 0049 absent`: 0048, the
  0046 figures, is staged, not appended — 0049 is queued behind a run that has not happened). Then its manifest assertion:
  the frozen `9a6f2923…` embeds `digest(SHA256SUMS)`, the sha of the pilot author's private evidence file; 192 plausible
  layouts missed. Every other identity field equals the frozen record. Runbook §3, §7.
  re-verify: `cd ~/dev/lc-lf && PYTHONIOENCODING=utf-8 ~/dev/linear-ceiling/.venv-cb/Scripts/python.exe docs/drafts/append_0049.py --box x --launched x --finished 2026-10-07T01:22Z --dataset x --output ~/dev/linear-ceiling/results/cache-behavior --preview 2>&1 | tail -1`   # AssertionError: ordering: 0048 present, 0049 absent
- **built — 0046's home inputs are prepared and admissible.** `tools/consolidation/prepare.py` run in WSL reproduces the
  frozen `config/consolidation-manifest.json` **byte-for-byte** (clean `git status` in the WSL clone); 60 texts, 126 `.npz`
  at WSL `~/Desktop/Carryover-evidence/a100/inputs`. From Windows it diverges on all 126 record shas (below) and writes a
  CRLF `texts.jsonl`.
  re-verify: `wsl.exe -e bash -lc 'cd ~/lc-lf && git status --porcelain config/ | wc -l; ls ~/Desktop/Carryover-evidence/a100/inputs/*/ | grep -c npz'`   # 0, 126
- **built — the camera-ready record** is in `docs/2026-09-30-review-response-map.md` (last section, committed `7c9a5fd`):
  the co-authors' submitted PDF (`6c706bef…`, built 2026-10-04 23:08Z) checked item by item; what the relaxed controls
  produced (pilot figures without the 0056 provenance clause; three unsourced figures; App. A's lower-bound wording
  contradicting 0054; two stale Condition-1 sentences); T1 closed, the rest moved to T2.
- **built (uncommitted) — runbook §6/§7 log lines after `580f73c`**, this brief, six learnings with index rows.
- **unknown — PR #18 / #19** (co-author, 2026-10-06) still open; #18's baseline PDF is the wrong build (`be90e0af…`).
- **built — R8 backup VERIFIED 2026-10-07 03:47Z**: `hossainpazooki/linear-ceiling-cache-behavior-2026-10-07` (private),
  74 files, 70 by LFS sha + 4 downloaded and hashed, 0 problems; this is `append_0049.py`'s `--dataset` value.
  re-verify: `tools/hf_backup.sh --verify-only hossainpazooki/linear-ceiling-cache-behavior-2026-10-07 ~/dev/hf-staging/linear-ceiling-cache-behavior-2026-10-07`   # exit 0, BACKUP VERIFIED (needs a read token or a login)
- **planned** — the 0046 sitting; E-TRUNC (AWS credentials invalid; 61 GB free on C: cannot hold its mirror); the Llama
  long cell (93 GB mirror).

## Locked decisions

- **Prepare inputs on Linux, never on Windows** (this session, from evidence). `np.savez_compressed` writes the zip
  `create_system` byte (0 Windows / 3 Unix): members identical, every `.npz` sha different. Both pilots prepared on Unix.
- **Every `rp.py` call from Git Bash runs under `MSYS_NO_PATHCONV=1`**, uploads are verified on the pod by size + sha, and
  results come home as ONE on-pod tarball by `scp`, extracted with `/usr/bin/tar` (runbook traps (h), (j)).
- **Card for 0047 was the operator's call at $1.39/h** (A100 SXM community) after the $1.19 PCIe row refused twice; the
  sitting-B rule "a fallback above `--max-price 1.25` goes back to the operator" was followed.
- **The create filters, not stock, were the refusal** (RAM ≥ 48 GB / 8 vCPU / CUDA {12.8–13.0}); widened to RAM ≥ 24 GB,
  4 vCPU, CUDA 12.8–13.2 — none registered quantities.
- **0049's queue position is an allocator decision**, not a ledger one: re-sequencing before 0048 edits `PREV` in the
  draft and the drafts README only.

## Reuse map

- `docs/2026-10-06-cache-behavior-runpod-runbook.md` is the template for the 0046 sitting (same pod class, same traps).
- Pinned venvs: Windows `.venv-cb` (torch 2.14.0+cpu) and WSL `~/lc-venv`; LF clones `~/dev/lc-lf` (Windows) and WSL
  `~/lc-lf`, both at `7c9a5fd` — refresh with `git fetch` before use (read-only from Claude).
- Pod setup script `cb-setup.sh` (scratchpad; add `--no-same-owner` to its `tar`).
- `results/e9l/SHA256SUMS` (208 files) is the evidence file 0047's prepare consumes; the pilot's own file is what 0049
  needs.
- Verify receipt format for `rp.py terminate`: `~/.cache/linear-ceiling/cb-verified.json` (schema v1, nonce-bound).

## Invariants

- `results/` never enters git; the one tracked results file stays labelled not-evidence.
- No ledger figure is typed; 0049 reads the summarizer in-process.
- Claude never writes git history; `git checkout` even in a scratch clone is refused by the guard — clone fresh instead.
- `../kv-transfer-replication` is read-only and now at `0d27c68`, past every linear-ceiling pin: home-side E9 gates refuse
  until the operator detaches it at the pin inside an append block (pick-up report, 2026-10-06).
- The Windows CRLF worktree cannot `--check` or `--summarize` Linux-prepared inputs; use the LF clone.

## Open / next

1. **Operator: commit this close** (results stay out of git; `.venv-cb/`, `.claude/`, `docs/paper/tex/` are yours):
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/2026-10-06-cache-behavior-runpod-runbook.md
   git commit -m "docs: 0047 sitting log — run complete, verified, pod released"
   git add docs/handoff/ docs/learnings/
   git commit -m "docs: 0047 sitting close; six learnings"
   git push origin main
   ```
2. ~~R8 backup~~ DONE 03:47Z (above). Revoke the write token in the Hub UI if not yet done (R9); the 09-30 cached login on
   this machine now answers "Invalid username or password", i.e. it is already dead.
3. **Two decisions for 0049**: (a) ask neuriv for the pilot's `SHA256SUMS` (then a WSL re-prepare should hit `9a6f2923…`),
   or rule a reading that pins the manifest by its verified fields; (b) whether 0049 may precede 0048.
4. **0046 sitting** next: inputs ready; L40S/A100 on RunPod under the same runbook shape; ≈ $5–9.
5. Carried: PR #18 baseline fix + merge, PR #19 ruling, the `fsync` Windows fix in `e9.py`, lag-ladder entry 0004.
