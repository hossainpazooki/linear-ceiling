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

Current state (2026-09-19): **0039–0042 are APPENDED** (family registration, E8 figures, the τ-ordering
ruling, the E9 short-cell registration). Their numbers are now permanent, and every remaining draft cites
them by literal rather than by an offset from its own `NUM` — the offsets were correct only while the whole
block moved together, and inserting an entry *inside* the block is exactly the case they got wrong.

**Four drafts staged, in this staging order: `append_0043.py`, `append_0044.py`, `append_0045.py`,
`append_0046.py`.**

- **`append_0043.py`** — the PRE-PREFILL AMENDMENT to 0042, and the only one that can run today.
  Descriptive. Registers (a) the driver's atomic checkpoint write and (b) the stop protocol for a
  budget-limited sitting: the drain, the signal, and the rule that the closing basis after any abnormal
  end is the last checkpoint whose every named artifact is sha-verified at home. Every claim about the
  instrument is asserted against the source, so it cannot describe tooling that does not exist, and R1 is
  checked (`results/e9f/` holds no report, score, token record or kept dump). It also adds itself to
  `config/e9f.toml`'s `[e9.gate]`, which changed that file's sha; the coverage and calibration were
  regenerated under it and the coverage differs in exactly one key, `config_sha256`.
- **`append_0044.py`** — the H-E9F verdict (was 0043). It used to REFUSE any partial close, written when
  the cell forbade one; 0042 registers one, so a budget-stopped run could be closed, mirrored and verified
  and then have no verdict entry to write. It now checks the *shape* — a prefix of the registered order
  with the unscored tail named — and requires `--cutoff-reason` on a partial.
- **`append_0045.py`** — the E9-long registration (was 0044). `config/e9fl.toml`'s `[e9.gate]` moved with it.
- **`append_0046.py`** — the E9-long figures (was 0045).

**Contingency, one commit:** if another session's entry lands first, all four move up together — every
`NUM`/`PREV` string, `[e8.gate]` in `config/e8f.toml`, and `[e9.gate]` in `config/e9f.toml` and
`config/e9fl.toml` — and that commit must precede `e8 --check` / `e9 --check`, which verify each config is
committed unmodified. The drafts are a chain: each refuses unless its predecessor's heading is already on
the ledger, each runs `ledger_check` after appending and exits with its return code, and each is deleted in
the same commit as its append, chained with `&&` (the 0025 lesson). On this checkout the interpreter is
`.venv/bin/python`. **0044–0046 still cannot run:** the upstream commit P is not yet merged at the pin, and
none of their cells has run. What each asserts and refuses on:
**`append_0043.py`** (PRE-PREFILL AMENDMENT to 0042; DESCRIPTIVE, no row, no `verdict:` line): the only
one that can run today. Asserts R1 (`results/e9f/` holds no report, score file, token record or kept dump),
that the config still registers `n_sender_asc` + `allow_partial`, and that the gate list is exactly 0042's
extended by this entry. Every claim it makes about the instrument is checked AGAINST THE SOURCE rather than
typed: `e9._write_checkpoint` writes via a temp file, `fsync` and `os.replace` and `close_partial` uses it;
`pull_verify_b` defines `choose_partial_basis`, `require_driver_stopped`, `final_partial`,
`write_drain_hint` and exposes `--final-partial`; `rp.py` defines `drain_threshold`, `send_drain_signal`,
`read_drain_hint` and signals with `kill -TERM`. The drain fraction and the registered handoff count are
READ (from `DRAIN_FALLBACK_FRACTION` and from `coverage.json`'s `run_order`), never typed.

**`append_0044.py`** (the H-E9F verdict): `summarize_e9 --config config/e9f.toml` in-process, `verdict:
H-E9F = <CELL>` from `ledger_check.VERDICTS` via the band word; run facts as `--box/--launched/--finished`;
refuses a partial close (this config does not allow one) and a run whose dumps carry no RoPE spec. The
τ_K ceiling 0039 registered is derived mechanically from the summary (`tau_K > 0.45` forces the cell to
`unresolved` whatever the band says). Optional `--tau-ceiling-applies {yes,no}` is an assertion that must
agree with that derivation and cannot select the verdict; required `--tau-ceiling-note` records provenance only.
**`append_0045.py`** (E9 long half registration at a NATIVE receiver; DESCRIPTIVE, no row): declares entry
0035's D1(a), its configuration bridge and its scaled-receiver reading INAPPLICABLE, and states that the
cell cannot move, support or refute H-E9L and is never pooled with 0036's handoffs; asserts the floor
equals the short cell's cap AND that the ids it excludes under that floor are EXACTLY the short cell's
included set, so the partition is audited rather than asserted, with the residual above the cap — scored by
neither cell — named and counted; same tau and calibration checks as 0041.
**`append_0046.py`** (long-half figures; DESCRIPTIVE, no `verdict:` line): `summarize_e9 --config
config/e9fl.toml` in-process; `--cutoff-reason` required on a partial close and forbidden otherwise; reads
`results/e9l/summary.json` only to state 0036's scaled-receiver figures BESIDE these, with the
non-comparability spelled out (different models, tokenizers, handoff sets, mappers and τ, and one receiver
scaled past its pretraining window).
Every figure in all six comes from a fail-closed summarizer, a coverage/calibration record or a config at
run time; **no result number is written in any of the scripts**, and each refuses when its summarizer
refuses. Earlier (2026-09-14, later): **0038 APPENDED** 2026-09-14 (chain `c9128ee936cd`, `ledger ok`; both readers passed
in-process; script retired in the same change; **no drafts staged**). Earlier that day: **`append_0038.py` STAGED** (E9 scaled short cell figures: in-process `summarize_e9 --config
config/e9s.toml` then `e9_compare --native config/e9.toml --scaled config/e9s.toml --long results/e9l/summary.json`; descriptive,
no `verdict:` line, no row change; run facts as `--box/--launched/--finished`; refuses on a partial close, a refusing
summarizer or comparison, or a bridge/profile block in the summary; states the two departures from 0037's text — τ calibration
written after the run, kept dumps under `results/e9s/scratch/`). **0038 is allocated here**; origin's ledger ended at 0037 when it
was staged. If the corrective f* entry (another session, 2026-09-11) lands first, this script and its `NUM` strings move to 0039.
Do not run it while a hardlinked R8 stage of `results/e9s/` is uploading. Earlier (2026-09-13, later): **0037 APPENDED** 2026-09-13 (chain `f24f8df65f91`, `ledger ok`; script retired in the same
change; the run itself is on a rented EC2 L40S, runbook `docs/2026-09-13-e9s-gpu-runbook.md`; its figures enter by their own
entry, number allocated at staging). Earlier that day: **`append_0037.py` STAGED** (E9 scaled short cell registration: 0029's 25 handoffs under 0036's
receiver configuration and pin, `config/e9s.toml`; descriptive, no hypothesis row, no verdict; the comparison reader is
`linear_ceiling.e9_compare`; refuses until `results/e9s/align/coverage.json` reproduces 0029's included set, alignments and
keep draw exactly, `results/e9s/` holds nothing else, and the upstream HEAD is at 0036's pin). **0037 is allocated here.** If
the corrective entry on the f* reading (another session, 2026-09-11) lands first, it takes 0037 and this script, its `NUM`,
and `config/e9s.toml` `[e9.gate]` move to 0038 in one commit. Earlier (2026-09-10): **0035 APPENDED** 2026-09-09 (`bacfe86`, script retired `d582f48`); **0036 APPENDED** 2026-09-10 (H-E9L = HELD, 35 scored of 35, from a passing in-process `summarize_e9 --config config/e9l.toml`; script retired in the same change; run on a rented EC2 L40S, runbook `docs/2026-09-10-e9l-gpu-runbook.md`). Earlier that day: **`append_0035.py` STAGED** (E9-long registration: H-E9L row `unresolved`, cap 81,920 by YaRN, floor 32,768, the 35 newly included handoffs, controls incl. the configuration bridge and length profiles, the run order + stopping rule, the paper re-scope superseding 0032's space clause; refuses until `config/e9l.toml` carries the real upstream pin, the upstream HEAD is at it with the RoPE spec, and `results/e9l/` holds nothing but `align/coverage.json`). **`append_0036.py` STAGED** (E9-long figures + H-E9L verdict from an in-process `summarize_e9 --config config/e9l.toml`; `verdict: H-E9L = <CELL>` line; run facts as arguments `--box/--launched/--finished`, `--cutoff-reason` required on a partial close; the bridge reading leads the entry when it is SCALED RECEIVER ONLY; refuses until 0035 is on the ledger and the summary passes). Earlier: **0034 appended** by `append_0034.py` (both summarizers in-process, both passed; script deleted in the
same commit set); **no drafts staged**. Earlier (2026-09-08): **0033 appended** by `append_0033.py` (prose amended first to state the two provenances of the n = 420
dumps — source CPU 2026-08-24, target GPU 2026-09-08 per `docs/2026-09-08-n420-target-dump-runbook.md`; script deleted in the
same commit set), the registered fit launched; **`append_0034.py` staged** (the figures entry: refuses until 0033 is committed
and the e8c / e9c chain has run). Earlier: **two drafts staged, in this order: `append_0033.py` (registration of the calibration-size sensitivity: the k = 1 mapper refit upstream on the n = 420 dumps under a tag, E8 arms rescored under 0030's protocol into `results/e8c/`, the E9 cross arm re-scored on the kept subset; descriptive) and `append_0034.py` (its figures, from `summarize_e8 --config config/e8c.toml` and `e9_rescore summarize` in-process).** **0033 is BLOCKED as staged (pick-up 2026-09-07): the n = 420 TARGET dump does not exist upstream (killed 2026-08-25 at 358/420, zero bytes; upstream learnings) and the script's own `meta.json` assert refuses; its prose says "pre-existing" and needs the operator's ruling (re-dump and amend, or drop) before it runs.** 0031 (E8 amendment figures) and 0032 (E9 admitted to the LCFM 4-pager) were appended 2026-09-07 by `append_0031.py` / `append_0032.py`, 0031 with every figure from `summarize_e8 --config config/e8a.toml` in-process; both scripts are retired in the same commit set. Numbers were allocated at staging (2026-09-06). 0028 (the keep-subset re-score tolerance, post-run, pre-verdict) and
0029 (H-E9 verdict, `verdict: H-E9 = HELD`) were appended 2026-09-04 by `append_0028.py` / `append_0029.py`,
each running `summarize_e9` in-process and pulling every figure from `results/e9/summary.json`; the scripts are
deleted in the same commit set. Earlier: 0025 (the E9 pre-prefill amendment: the independent review's
findings 1–7 plus the E-RL design's τ ladder and keep-subset n 3 → 8) was appended by `append_0025.py`
on its second staging — every figure from config or recomputed in-process from the traces, the
verified E7 report and E8's report, with the `e7-manifest-sha256:` line the 0018 rows require. Its
first staging (`f8cecf7`) had been retired by `cb80ad0` WITHOUT an append: the script's "nothing to
register" guard read the prior keep n from HEAD after the instrument commit had already moved it, so
it refused and the retire step ran anyway (learnings entry). Rule from it: a draft's prior value comes
from a pinned revision, never HEAD, and a retire step is chained to the append with `&&`. Entries 0013–0024 are appended and their scripts deleted
(0023 pulled every figure from `results/e9/calibration/tau.json` via `summarize_e9 --calibrate-tau`;
0024 from `results/e7/recon.json` via `summarize_e7 --overlap-null --cache-aware-ratio`, behind
`e7.assert_ready`). The **H-E9 verdict** is 0029. The **E8 amendment** is 0030 (registration, appended 2026-09-04 by `append_0030.py`
from `config/e8a.toml` and the 0020 record) with its figures entry staged as `append_0031.py` (runs `summarize_e8
--config config/e8a.toml` in-process; refuses until 0030 is committed, the re-pin recorded and the rescoring done). Formerly queued as the **E8 amendment** (`--holdout-frac 1.0` on
`36d73b3`, per-sequence moments from the `--per-token` record, re-pin). **E-RL** (KV reuse across RL
post-training checkpoints) is designed only — `docs/2026-09-02-e-rl-design.md` — and has no
registration script; it takes a number when its script is staged, not before. The 0022 tokenizer
sensitivity (`summarize_e7 --strategy-override`) gets no entry of its own: it ships in the 0009
successor bundled with n = 420, per 0022's "one replay supersedes the figures once."
