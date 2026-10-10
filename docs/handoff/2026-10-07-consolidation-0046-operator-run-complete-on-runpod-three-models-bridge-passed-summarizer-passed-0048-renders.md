# Handoff — 0046's registered run is DONE on RunPod (three models, bridge pause passed, summarizer passed, $3.86); 0048 renders and waits only for the R8 backup; the 0049 ruling is applied

2026-10-07 ~06:50Z. Describes `d4d48a1` (= origin/main) **plus this session's uncommitted files** (listed under "Open /
next" item 1). Same session as the 0047 close (`03ca9159`); this brief covers what happened after it. The sitting's
minute-by-minute evidence is `docs/2026-10-07-consolidation-runpod-runbook.md` §6; this brief points at it.

## Current state

- **built — the registered 0046 run exists and is verified.** One RunPod pod (A100-SXM4-80GB community, $1.39/h,
  03:56–06:43Z), driver at `d4d48a1`, lock runtime `torch 2.14.0+cu130 / transformers 5.17.0 / numpy 2.5.3`. Three models
  on one card in the registered order with the registered pause: `qwen17_bridge` 6/6 → home `--bridge-only` PASSED (max
  relative mean gap 1.2e-5, f* gap 0.0, limits 0.01) → `qwen4` 60/60 (peak 39.72 GiB) → `smollm3` 60/60 (peak 22.96 GiB,
  9 no-RoPE layers). Controls 0.0 on every model. Home mirror `results/consolidation/` (13.18 GB, 668 files + `SHA256SUMS`):
  126/126 fingerprints, 12/12 witness hashes; full `summarize.py` PASSED (`verified: true`). Pod PROVEN GONE. **Sitting
  $3.86**; campaign (0047 + 0046) $6.43 of the $15 cap; balance $23.59.
  re-verify: `.venv-cb/Scripts/python.exe -c "import json,pathlib;M=pathlib.Path('results/consolidation');s=json.load(open(M/'a100/summary.json'));b=s['bridge'];print(s['verified'],len(b),max(r['relative_mean_gap'] for r in b)<0.01,max(r['max_fstar_gap'] for r in b),[json.load(open(M/'a100/results'/m/'report.json'))['complete'] for m in ('qwen17_bridge','qwen4','smollm3')])"`   # True 12 True 0.0 [True, True, True]
- **built — the figures reproduce the pilot document exactly** (summarizer outputs, NOT ledger figures): same-model
  f*(τ_K) median 0 for every model, cohort and kind; f*(0.1)/f*(0.03) Qwen3-4B long 0.0460/0.4979, short 0.0007/0.2739;
  SmolLM3 long 0.0580/0.4529, short 0.0000/0.1527; SmolLM3 long-K zero handoffs 34 of 35 (the pilot's "34 of 35").
  re-verify: `.venv-cb/Scripts/python.exe -c "import json;s=json.load(open('results/consolidation/a100/summary.json'))['models'];m=s['qwen4']['e9l_K']['median'];print(round(m['fstar_0.1'],4),round(m['fstar_0.03'],4),s['smollm3']['e9l_K']['zero_fstar_handoffs'])"`   # 0.046 0.4979 34
- **built — `append_0048.py` renders** against the mirror (rc 0, no `verdict:` line; its ordering guard is 0047, appended;
  one GPU / one runtime / driver hashes all assert). It waits only for `--dataset` (the R8 backup id).
  re-verify: `PYTHONIOENCODING=utf-8 .venv-cb/Scripts/python.exe docs/drafts/append_0048.py --box x --launched 2026-10-07T04:01Z --finished 2026-10-07T06:29Z --dataset pending --preview 2>&1 | grep -c '^### 0048 '`   # 1
- **built — ruling B applied to `append_0049.py`** (operator, 2026-10-07, verbatim in the script and the entry text):
  asserts the operator manifest `2aeee576…` with its four pinned fields checked against the pilot's freeze record; two
  latent bugs fixed on the way (identity keys read at the wrong level; `run.py` loaded by path despite its relative
  import). Renders end to end from a scratch copy with the ordering guard pointed at the last entry. Still `PREV = "0048"`.
  re-verify: `grep -c -E 'INPUT_MANIFEST_SHA = "2aeee576|importlib.import_module\("tools.cache_behavior.run"\)|identity = report\["identity"\]' docs/drafts/append_0049.py`   # 3
- **built — issue #20** to the pilot author (what the two runs did, the backups, the SHA256SUMS ask, the ruling quoted).
- **built (uncommitted)** — runbook `docs/2026-10-07-consolidation-runpod-runbook.md` (§6 complete, §7 open list), the
  0047 runbook's §7 ruling lines, `docs/drafts/{append_0049.py,README.md}`, this brief, four learnings, index rows.
- **built — R8 backup VERIFIED 2026-10-07 12:00Z**: `hossainpazooki/linear-ceiling-consolidation-2026-10-07` (private,
  anonymous read → 401) matches the staging copy both ways (14 GB; LFS by sha, small files downloaded and hashed). The
  first verifier pass failed on Windows `MAX_PATH` (274-character cache paths); `HF_HOME=C:/hf --verify-only` passed.
  This is `append_0048.py`'s `--dataset` value; the preview with it renders (521-word entry, no `verdict:` line).
  re-verify: `HF_HOME=C:/hf tools/hf_backup.sh --verify-only hossainpazooki/linear-ceiling-consolidation-2026-10-07 ~/dev/hf-staging/linear-ceiling-consolidation-2026-10-07`   # exit 0, BACKUP VERIFIED (needs a read token or a login)
- **planned** — E-TRUNC (AWS credentials invalid; 61 → ~45 GB free on C: cannot hold its mirror); the Llama long cell.

## Locked decisions

- **80 GB card for 0046, not the entry's "L40S 48 GB expectation"** (this session, before renting, from arithmetic: fp32 KV
  per token = layers × KV heads × head dim × 4 B × 2 → the 4B at 81,920 tokens ≈ 24 GB cache + 16 GB weights; measured
  peak 39.72 GiB). The entry allowed "a larger card if the probe says so".
- **The bridge pause is sequencing, not convenience**: `qwen4` started only after the home `--bridge-only` passed.
- **A mirror for `summarize.py` carries `archive/records/<cohort>/{report.json, align/, scores/, tokens/}`** — the bridge
  comparison re-derives the archived per-token deltas; `prepare.py` alone needs only `report.json` + `align/`.
- **Arguments the local Python opens get Windows paths; arguments the pod consumes get `MSYS_NO_PATHCONV=1`** — the
  `--verify-file $HOME/…` passed under the override was stored as `C:\c\Users\…` and blocked `terminate` once.

## Reuse map

- Both runbooks (`2026-10-06-cache-behavior-runpod-runbook.md`, `2026-10-07-consolidation-runpod-runbook.md`) are the
  template for any RunPod sitting from this Windows machine; traps (h)–(n) are the cost of learning them.
- Pod setup scripts in the scratchpad (`cb-setup.sh`, `cons-setup.sh`): clone at a sha, lock sync, public snapshots,
  tarball check, `--no-same-owner`, manifest check.
- `~/dev/lc-lf` (Windows LF clone; **its `config/consolidation-manifest.json` is dirty from a Windows `prepare.py` run —
  do not read provenance from it**) and WSL `~/lc-lf` + `~/lc-venv` (clean; use for Linux-side prepares).
- `rp.py` receipt format and the `C:\c` pitfall: write the receipt to `~/.cache/linear-ceiling/<exp>-verified.json` and
  pass `--verify-file ~/.cache/…` WITHOUT the override on `up`.

## Invariants

- `results/` never enters git; the mirror's provenance files are `git show HEAD:` bytes, never a worktree copy.
- No ledger figure is typed; 0048 and 0049 read their summarizers in-process.
- Claude never writes git history; the guard also refuses `git checkout` in scratch clones (clone fresh instead).
- `../kv-transfer-replication` is read-only and at `0d27c68`, past every pin; the lag-ladder gate is red until entry 0004.

## Open / next

1. **Operator: commit this close**:
   ```bash
   cd ~/dev/linear-ceiling
   git add docs/drafts/append_0049.py docs/drafts/README.md docs/2026-10-06-cache-behavior-runpod-runbook.md
   git commit -m "drafts: 0049 asserts the operator manifest per the 2026-10-07 ruling; fix identity-key and import bugs"
   git add docs/2026-10-07-consolidation-runpod-runbook.md
   git commit -m "docs: 0046 sitting runbook and log — three models complete, bridge and summarizer passed, pod released"
   git add docs/handoff/ docs/learnings/
   git commit -m "docs: 0046 sitting close; four learnings"
   git push origin main
   ```
2. **R8 backup** (token env-only, revoke after): `hf repo create hossainpazooki/linear-ceiling-consolidation-2026-10-07
   --repo-type dataset --private`, then `tools/hf_backup.sh --check …` and the push from the staging copy.
3. **Append 0048** with `--dataset` = that id (preview first; retire the script in the append commit), then 0049 (re-sequence
   or wait, operator's call; the pilot author's files from issue #20 would add a dated confirmation note).
4. Carried: PR #18 baseline fix, PR #19, the `fsync` fix, lag-ladder 0004, E-TRUNC/Llama-long disk and credentials.
