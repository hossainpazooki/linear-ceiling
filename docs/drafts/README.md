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

Current state (2026-09-18): **six drafts staged, in this staging order: `append_0039.py`, `append_0040.py`,
`append_0041.py`, `append_0042.py`, `append_0043.py`, `append_0044.py`** — the second model family
(`llama3.2-3b-to-llama3.1-8b`, source meta-llama/Llama-3.2-3B, receiver meta-llama/Llama-3.1-8B, a
MATCHED-KV pair: 8 KV heads x head_dim 128 on both sides, so the upstream delta is one `PAIRS` entry and
nothing about the estimator is extended). **0039–0044 are allocated here, at staging, in staging order**;
the committed ledger ended at **0038** and no entry had been appended since 2026-09-14 when they were
written. **Contingency, one commit:** if the corrective f* entry (another session, 2026-09-11) lands first
it takes 0039 and **all six move up by one together** — every `NUM`/`PREV` string, `[e8.gate]
required_entries` in `config/e8f.toml`, and `[e9.gate] required_entries` in `config/e9f.toml` and
`config/e9fl.toml` — and that commit must precede `e8 --check` / `e9 --check`, which verify each config is
committed unmodified. Nothing else is entangled: the scripts derive their sibling entry numbers from their
own `NUM` (`FAMILY`, `SHORT`, `E8FIG`), so renumbering is a string edit, not a rewrite. They are a chain —
each refuses unless its predecessor's heading is already on the ledger — so they cannot run out of order,
and each runs `ledger_check` after appending and exits with its return code; delete each in the same commit
as its append, chained with `&&` (the 0025 lesson). On this checkout the interpreter is `.venv/bin/python`,
not the `.venv/Scripts/python.exe` of the convention line above. **None of the six can run today** and each
says so by refusing: the upstream commit P (the one-line `kvt/pairs.py` `PAIRS` entry on top of the
RoPE-spec commit `063f402`) is neither written nor pushed, both `meta-llama` repos are gated, there is no
GPU here, and `traces/` is unrestored. What each asserts and refuses on:
**`append_0039.py`** (family registration; DESCRIPTIVE, no row, no `verdict:` line): asserts the pair
round-trips through `pairs.pair_name`/`pair_models`; that `config/e8f.toml` carries 0009's band and 0016's
sampling rule byte-for-byte, its own directories and its own `scope_note`, and a `[e8.gate]` that EXTENDS
0009/0016 and ends at its own number; R1 — no `results/e8f/report.json`, no agent dumps, no token draw;
that entry 0039's operator ruling is enforced by the absence of any prediction sidecar and that NO mapper
for the pair exists in any configured artifact root; that a PASSING `tools/preflight_pair.py` record over
the two GATED snapshots says the pair is matched-KV and shares its `get_vocab()` map (every shape figure in
the entry is read from that record, cited by sha, and nothing about either checkpoint is typed); that
`config/e9f.toml` and `config/e9fl.toml` still carry their refusing `UNRESOLVED::` tau markers; and that
the pin is a real sha, checked out, clean, registering the pair in `kvt/pairs.py`, and a DESCENDANT of the
commit `config/e9l.toml` pins. **New convention, used by two of the six:** operator DECISIONS the repo
cannot derive are required arguments quoted verbatim into the entry, exactly as run facts are —
`--tau-ladder-rule`, `--prefix-delta-rule` and `--tau-ceiling` here, so the two absolute constants and the
ceiling decision are fixed before tau_K exists.
**`append_0040.py`** (E8 figures; DESCRIPTIVE, no `verdict:` line, H-E8 does not move): runs
`summarize_e8 --config config/e8f.toml` IN-PROCESS and reads every number from the report it just verified;
re-verifies the no-seal ruling AFTER the fit; refuses unless the two E9 configs are still uncalibrated. It STATES
this pair's tau_K/tau_V/tau_agent_K, because `summarize_e9 --calibrate-tau` cannot reach them yet
(`load_e9_config` refuses a config whose tau keys are markers, so the calibration cannot be run through a
config that will not load); the quantity itself is 1 − arm (a)/(b)'s held-out R² at the verdict k, which
the summarizer has just re-derived from the tensors. It also states, without asserting, when
tau_K < tau_agent_K < 1 FAILS on this pair — `config.py` then refuses both E9 cells and 0039's
pre-registered contingency is what resolves it, never an edit made after the score file exists.
**`append_0041.py`** (E9 short cell registration; the ONLY verdict-bearing cell of the campaign, ONE new
row **H-E9F** `unresolved` spliced after the H-E9L row — the id matches `ledger_check._ROW`, which
`H-E9-llama` silently would not): asserts `[e9.rule]`/`[e9.controls]` are `config/e9.toml`'s key by key
EXCEPT the three pair-calibrated tau values plus the pre-registered absolute ladder and prefix-delta
constants; that the three tau values are this pair's own, cross-checked against entry 0040's E8 report
AND against `results/e9f/calibration/tau.json`; that the cell registers no rope and no bridge;
R1; and that `align/coverage.json` was written under this exact config sha. **It checks the tau
calibration at REGISTRATION**, which `e9 --check` never does — the 2026-09-14 sitting printed ready, ran
25 of 25 and was refused at home for exactly that gap.
**`append_0042.py`** (the H-E9F verdict): `summarize_e9 --config config/e9f.toml` in-process, `verdict:
H-E9F = <CELL>` from `ledger_check.VERDICTS` via the band word; run facts as `--box/--launched/--finished`;
refuses a partial close (this config does not allow one) and a run whose dumps carry no RoPE spec. The
τ_K ceiling 0039 registered is a required `--tau-ceiling-applies {yes,no}` + `--tau-ceiling-note`: nothing
in `results/` records that decision, and `yes` forces the cell to `unresolved` whatever the band says.
**`append_0043.py`** (E9 long half registration at a NATIVE receiver; DESCRIPTIVE, no row): declares entry
0035's D1(a), its configuration bridge and its scaled-receiver reading INAPPLICABLE, and states that the
cell cannot move, support or refute H-E9L and is never pooled with 0036's handoffs; asserts the floor
equals the short cell's cap AND that the ids it excludes under that floor are EXACTLY the short cell's
included set, so the partition is audited rather than asserted, with the residual above the cap — scored by
neither cell — named and counted; same tau and calibration checks as 0041.
**`append_0044.py`** (long-half figures; DESCRIPTIVE, no `verdict:` line): `summarize_e9 --config
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
