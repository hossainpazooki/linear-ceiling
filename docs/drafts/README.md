# Entry drafts (delete each script once its entry is appended)

Convention: an entry that carries numbers is appended by an ordering-guarded script that runs
the relevant fail-closed summarizer IN-PROCESS first and pulls every figure from its verified
output — the script refuses to run out of order and runs `ledger_check` after appending. Run
from the repo root with `.venv/Scripts/python.exe`.

**Numbering (decided 2026-09-02): entry numbers are PROVISIONAL until a script is staged here — a
number is assigned at staging time as the next free one, in staging order, and no living doc names a
number for an entry that has no script yet; this README is the only allocator.** Reason: the ledger
is append-only and chain-hashed, so a pre-assigned number would force a cheap entry (the E8
amendment: one upstream commit + re-pin) to queue behind an expensive one (the H-E9 verdict, which
waits on an A100 not yet requested). Earlier allocations ("0025 = H-E9 verdict", the seed's
"0025 = E8 amendment") are superseded by this sentence.

Current state: **one draft staged — `append_0025.py` = the E9 pre-prefill amendment** (the independent
review's findings 1–7 plus the E-RL design's τ ladder and keep-subset n 3 → 8; every figure from config
or recomputed in-process from the traces, the verified E7 report and E8's report; refuses if a prefill
has happened; `e9.REQUIRED_ENTRIES` already names 0025 so the gate and the entry agree). Its first
staging (`f8cecf7`) was retired by `cb80ad0` WITHOUT an append: the script's "nothing to register"
guard read the prior keep n from HEAD after the instrument commit had already moved it, so it refused
and the retire step ran anyway. The restored script reads the prior value from a pinned revision. Entries 0013–0024 are appended and their scripts deleted
(0023 pulled every figure from `results/e9/calibration/tau.json` via `summarize_e9 --calibrate-tau`;
0024 from `results/e7/recon.json` via `summarize_e7 --overlap-null --cache-aware-ratio`, behind
`e7.assert_ready`). Queued, unnumbered: the **H-E9 verdict** (Track A; written from a clean
`summarize_e9` run after the A100 day, `docs/2026-09-02-e9-gpu-runbook.md`; must carry a
`verdict: H-E9 = <VERDICT>` line, `ledger_check`) and the **E8 amendment** (`--holdout-frac 1.0` on
`36d73b3`, per-sequence moments from the `--per-token` record, re-pin). **E-RL** (KV reuse across RL
post-training checkpoints) is designed only — `docs/2026-09-02-e-rl-design.md` — and has no
registration script; it takes a number when its script is staged, not before. The 0022 tokenizer
sensitivity (`summarize_e7 --strategy-override`) gets no entry of its own: it ships in the 0009
successor bundled with n = 420, per 0022's "one replay supersedes the figures once."
