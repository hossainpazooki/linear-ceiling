# Handoff — E-TRUNC (0055 → 0057) RAN on a RunPod A100 from the Mac mini: four levels, 35 of 35 each, four mirrors verified, pod gone at $12.60; the registered reading is "unattributed" (ABOVE both references); 0059 (τ recomputation tolerance) appended; R8 staged by hard links, push pending the "public" ruling

2026-10-08 ~23:55Z. Describes `b33c6ce` (origin/main; 0059 appended and retired by the operator on the Mac, fetched and
pushed) **plus this session's uncommitted files** (listed under "Open / next" 1). Same session as the 0051 close
(`03ca9159`); this brief covers what happened after it. The sitting's minute-by-minute evidence is
`docs/2026-10-04-e-trunc-gpu-runbook.md` §6; this brief points at it.

## Current state

- **on the ledger — 0059** (operator ruling 2026-10-08 "recommendation accepted"; chain `64e1c6ba…`, commits `0aec95a` +
  `b33c6ce`): E9 summarizer enforcement in 0028's shape — the τ RECOMPUTATION tolerance 1e-9 → 1e-7 in `_close`'s units
  (|a − b| ≤ tol·max(1,|a|,|b|)). The arm64 Mac refused E-TRUNC's FULL level on τ_V at 3.7e-9 while every x86 rendering
  of the same arithmetic sits within 1e-9 (and x86 renderings differ by thread count); five renderings captured as files
  under `results/e9t-full/calibration-{x86,arm64}/threads*/`. The τ every reading uses stays the config float; nothing moved.
  `summarize_e9` now records `calibration.tau_recompute` (gaps + platform) and prints it.
  re-verify: `grep -c "^### 0059 " ledger/ledger.md; grep -n "_TAU_TOL = 1e-7" src/linear_ceiling/summarize_e9.py`   # 1; one line
- **ran — the E-TRUNC sitting (0055)**, home side the Mac mini, box a RunPod SECURE A100-SXM4-80GB ($1.79/h; community
  A100 stock vanished at 16:16Z), pod `w28h3vp07g8nnz` 16:26:57 → 23:29:10Z. FULL 16:35:23 → 19:05:31Z, L65 19:06:19 →
  20:44:22Z, L49 20:45:28 → 22:12:53Z, L32 22:14:08 → 23:25:49Z; every level 35/35, 0 Tracebacks, no partial close.
  Four mirrors on the Mac verified from raw bytes by `verify_mirror.py` (529 fingerprinted files each; 61.1 / 60.0 / 51.5 /
  40.1 GB). R7 by hand on the box (no tensors left, 17 log + 4×222 record hashes pulled to `results/e9t/release/`, token
  sweep clean, HF cache removed), terminate with the nonce-bound receipt → PROVEN GONE. **Final: sitting $12.60, campaign
  $17.42, balance $6.09.**
  re-verify: `ssh hossa@192.168.1.26 'cd ~/dev/linear-ceiling && for e in e9t-full e9t-l65 e9t-l49 e9t-l32; do shasum -a 256 results/$e/report.json | cut -c1-12; done; .venv/bin/python tools/runpod/rp.py status | tail -1'`   # 5a7ab122fcc1 b72a49869092 c7535211d033 c166d8f11427; (none — nothing is billing)
- **two interventions mid-sitting, both in §6:** (a) the per-token scorer ran 191 threads on a 13.6-CPU cgroup quota (48 %
  of periods throttled; GPU idle) — drained by pid, relaunched with `--resume` under a 13-thread cap at 18:30:53Z; 19
  handoffs kept from the checkpoint; 255–370 s → 130–150 s per handoff; (b) the watchdog's `--kill` default ($9 of
  CAMPAIGN spend, no drain) was five minutes from terminating the pod at 18:40Z — supervisor replaced with `--kill 18`,
  then (ruling "option 1") `--no-drain --sitting-max 14.5 --kill 18 --ttl 8.1`. Three restarts; two 3-second unwatched windows.
- **two reader corrections before any figure**: 0059 (above), and `summarize_e9` compared a truncated level's identity /
  bridge control coverage with the FULL |S| (0055 keeps it) and refused L65 on a correct 65,536-pair control with every
  square zero → `_dumped_sender_len` = min(|S|, L); test added (`tests/test_e9_trunc.py`, 55 pass on the Mac). 0057 states
  both from the records.
  re-verify: `.venv/Scripts/python.exe -c "import json;r=json.load(open('results/e9t-l65/report.json'));print(r['controls']['identity']['n_pairs'], r['sender_head_truncate'])"`   # 65536 65536
- **read — the comparison** (`summarize_e9_trunc`, rc 0 at 23:41:04Z; `results/e9t/compare.json` `0572662307f3…`): 35
  scored at every level, 14 void under |M_∩| ≥ 2,000, 21 enter on 154,620 common tokens. **Registered reading: L32's
  far-from-seam pooled median δ_K on M_∩ = 0.0868 vs scaled-short 0.0381 / long 0.0629 (FULL on the same tokens 0.1112),
  margin ±0.005 → "unattributed"** — and ABOVE both references (0.0239 above the long level); truncation to S[−32,768:]
  moved FULL's 0.1112 to 0.0868 on identical tokens (paired median −0.0257, bootstrap [−0.0434, 0.0024]); L65/L49 moved
  nothing. Descriptive; no cell moves.
  re-verify: `ssh hossa@192.168.1.26 'grep "reads as" ~/dev/linear-ceiling/results/e9t/compare.md'`
- **staged — 0057 rendered** (`append_0057.py --preview` rc 0 on the Mac, 23:50:57Z; text at
  `~/.cache/linear-ceiling/append_0057.preview.txt` there): Setup, coverage renderings, the reader-corrections paragraph,
  the void gate, per-level figures, the reading with its position, the 0055 erratum (10 / 14 / 0), scope. A skeptic pass
  was dispatched against the rendered text at ~23:55Z; its verdict is not in this brief — read the session's last
  messages or re-run the preview and refute it before appending.
- **staged — R8** by hard links (`tools/hf_stage_e9t_r8.sh` → Mac `~/dev/hf-staging/linear-ceiling-e9t-2026-10-08/`):
  2,893 files incl. card and `SHA256SUMS` (2,891 lines), 217,253,073,065 B; the four levels without `recheck/`,
  `results/e9t/`, and the upstream INPUTS (mappers, archived `r2.json`, `data/kv/<pair>`, probe) per the campaign runbook
  §11; token sweep clean with a planted control. **Not pushed**: the dataset must be PUBLIC (217 G > 100 GB private) and the
  operator's ruling had not arrived at write time. The e9fl staging copy (44 G) was deleted on the operator's word; Mac 72 Gi free.
  re-verify: `ssh hossa@192.168.1.26 'wc -l < ~/dev/hf-staging/linear-ceiling-e9t-2026-10-08/SHA256SUMS; ls ~/dev/hf-staging/linear-ceiling-e9t-2026-10-08'`   # 2891; README.md SHA256SUMS data mappers results

## Open / next

1. **Commit (operator), Windows:** this session's docs and fixes — `docs/2026-10-04-e-trunc-gpu-runbook.md` (§6 complete),
   four learnings + `docs/learnings/LEARNINGS.md` rows, `tools/ec2/run.sh` (cgroup thread cap), `tools/hf_stage_e9t_r8.sh`,
   `docs/drafts/append_0057.py` (reader corrections + position sentence), this brief + `HANDOFF.md` row. One concern per
   commit: `fix(tools)` for run.sh, `docs:` for the rest. `docs/paper/tex/` is untracked and not this session's.
2. **R8 push** (operator token, R9): `hf repo create … --repo-type dataset` (public), `ALLOW_PUBLIC=1 tools/hf_backup.sh --check`,
   then the push detached under `caffeinate -i` with `< /dev/null`, chained to the verifier inside the script; hours at
   217 G; ends in `BACKUP VERIFIED`; revoke the token after.
3. **Append 0057 on the Mac** after the skeptic verdict and BACKUP VERIFIED: `.venv/bin/python docs/drafts/append_0057.py
   --box "RunPod secure cloud, 1x NVIDIA A100-SXM4-80GB (driver 580.126.16, 128 vCPU shown / 13.6-CPU cgroup quota, 2 TB host
   RAM), pod w28h3vp07g8nnz" --launched 2026-10-08T16:35:23Z --finished 2026-10-08T23:25:49Z --dataset
   hossainpazooki/linear-ceiling-e9t-2026-10-08 && rm docs/drafts/append_0057.py`; two commits; fetch to Windows over the LAN; push.
   Then drafts README + CLAUDE.md allocator lines (0057 appended; no draft staged; next free 0060).
4. **Paper**: E-TRUNC = one descriptive paragraph in §4 of the MLSys draft (a non-attribution with a direction: shorter causal
   prefix lowers late-position deviation on identical tokens and does not close the short↔long gap; M_∩ vs full-set
   references stated; 0055's two limitations), paragraph-then-justification with entry:line pointers; the MLSys draft plan's
   P1–P4 / Llama table / scoping sentence still await per-paragraph approval.
5. Housekeeping: `tools/ec2/release_sweep.sh` is single-level (`OURS_FILES`) — a multi-level sitting needs it to accept all
   levels' logs; `pull.py` leaves `launches.log` as of each level's last pull (L32's copy is the final one); `rp.py up --cap`
   should seed the watchdog's `--kill` and `--ttl` (learning 2026-10-08).
6. Standing: issue #21 (Emerson's R12 recompute of 0051); lag-ladder 0004 re-pin; `e9.py` fsync-on-read-handle Windows red
   (the whole `tests/test_summarize_e9.py` module errors on Windows); PR #19 ruling.

## Learnings written this session (docs/learnings, 2026-10-08; every re-verify line executed from the written file)

- the watchdog's `--kill` default is $9 of campaign spend and `up --hours` is its TTL;
- the EC2 launcher set no CPU thread cap (191 threads on a 13.6-CPU quota halved throughput);
- a registered float tolerance is a platform rendering (0023's 1e-9 held on x86, refused arm64 at 3.7e-9; 0059);
- a reader adapted to a new instrument compared a truncated level's controls with the full sender length.
