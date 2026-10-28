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

**State 2026-10-01: 0043 and 0044 are APPENDED (2026-09-19; H-E9F HELD). Numbering ruling 2026-10-01: the
corrective f* entry takes 0045 (**APPENDED 2026-10-01 at `b3bf7ec`**; script and test retired in the follow-up commit), and
the two Llama long drafts moved up in one commit with `config/e9fl.toml`'s `[e9.gate]`: `append_0046.py`
(registration, was 0045) and `append_0047.py` (figures, was 0046). Next free number: 0048.** The paragraph below
is the 2026-09-19 staging record, kept as written.

**Allocation 2026-10-04 (operator: "accept both and add to ledger while I run them"). 0046 and 0047 are APPENDED
2026-10-04 (`a941377`, `55a5c47`, after PRs #8, #9, #14 merged; both scripts retired in the follow-up commit); 0048 and 0049
stay staged until the operator's runs exist.** Four drafts were staged, in this
staging order, for the two co-author-piloted runs the operator re-runs under registration: **`append_0046.py`** (REGISTERED
the same-model extension to Qwen3-4B and SmolLM3-3B with the Qwen3-1.7B bridge; frozen config/manifest from PR #8),
**`append_0047.py`** (REGISTERED the cache-behavior comparison, E-BEH's core FRESH vs REUSE-ALL with controls; frozen
config and driver from PR #14), **`append_0048.py`** (the extension's figures, from `tools/consolidation/summarize.py`
in-process over the operator's verified mirror), **`append_0049.py`** (the cache-behavior figures, from
`tools.cache_behavior.run.summarize` in-process). Both registrations refused until PRs #8 and #14 were merged (they assert
the frozen files' hashes, LF-normalized because this checkout is CRLF) and if any result already existed under the registered
output trees (R1). The two Llama
long drafts moved to **`append_0050.py` / `append_0051.py`** with `config/e9fl.toml`'s gate (`"0050"`) in the same commit.
Next free number: **0052**. The co-authors' own runs (A100, H100; evidence private) are recorded in the registrations as
pilots that preceded upstream registration; their figures enter only through `docs/2026-10-03-co-author-run-admission.md`.

**`append_0052.py` / `append_0053.py` — the second family's E8 amendment — BOTH APPENDED 2026-10-04 (`f016bde`, `0c5ec15`; scripts retired)**, entry
0030's protocol (arm (b) over EVERY agent sequence, per-sequence R², seeded bootstrap, change from the prior arm (b)) re-registered
for `llama3.2-3b-to-llama3.1-8b` under `config/e8fa.toml`, on 0040's own dumps and token file by fingerprint; the rescoring entry
0041 asked for ("whether the inversion is a property of the pair or of the draw"). Descriptive; no row, no `verdict:` line; τ_agent_K
stays 0040's. CPU only (~10 min), no box, no upstream change (the family's pin `06f8d55` already contains 0030's `223f469`). The
registration script checks every claim against the tree (config tracked and unmodified and naming the entry, pin held and containing
223f469, 0040's fingerprints, the 42-distinct-window count recomputed from the token file, 0041's sentence still present, R1 on
`results/e8fa/`); the figures script runs `summarize_e8` in-process. **Numbering:** 0052/0053 are this pair's numbers for good; `ledger_check`
chains by FILE order (the 0054 precedent, below), so the pair appends when its inputs are ready and precedes 0048–0051 in the file.
Ordering guard: 0054 present, 0052 absent; then 0052 present, 0053 absent. `bootstrap_seed` = 52, the entry number, as 0030 used 30.

**Staged 2026-10-04 (evening): `append_0054.py` — Condition 1 discharged by operator ruling** (issue #7 together with PR #12's two
review records is treated as the confirmation; descriptive, no cell moves). By operator instruction it is numbered AFTER the Llama
drafts (0050/0051 long cell, 0052/0053 E8 amendment) and appended before them, so it precedes 0048–0053 in file order;
`ledger_check` chains by file order. Ordering guard: 0047 present, 0054 absent. *(0054 APPENDED 2026-10-04, `a2742b9`.)*

**Staged 2026-10-04 (night): `append_0056.py` — co-author pilot figures admitted to paper text by operator ruling** (the two
merged co-author documents `docs/pilots/2026-10-01-cache-behavior-h100.md` and `docs/pilots/2026-10-01-a100-analysis.md` may be cited under a
provenance sentence; supersedes the "in any paper" clauses of 0046/0047; R1/R8/R12 for LEDGER figures unchanged, so 0048/0049 still
need the operator's run or the admission procedure; types no figure). 0055 is the E-TRUNC registration (PR #17, merged `c37f626`; appended `a5c8691`). 0056 APPENDED `caccab5`.
Ordering guard: 0054 present, 0056 absent. Next free number: **0057**.

**`append_0055.py` — E-TRUNC registration — APPENDED 2026-10-04 (`a5c8691`; script and `tests/test_append_0055.py` retired in the append commit; staged earlier that night)** (design `e-trunc-design.md`; its §10 carries the three
rulings taken that day under the operator's direction — running this script is the operator's ratification; the seed had
allocated 0052, which the E8 amendment above took first). REGISTRATION, descriptive, no hypothesis row, no `verdict:` line.
Ordering guard 0054 present / 0055 absent (0054 is the latest APPENDED entry; 0048–0053 are staged and may land before or after
this one — if one lands first, this script's `NUM`/`PREV` and the four configs' `[e9.gate]` move together in one commit, before
any `e9 --check`). Asserts the four configs `config/e9t-{full,l65,l49,l32}.toml` are committed and hash-equal (LF-normalized)
to the registered values and are `config/e9l.toml`'s instrument on every field but the named lines; asserts R1 (no report,
score, control, bridge, token record or scratch under any `results/e9t*/`; the four alignment passes and
`results/e9t/shrinkage.*` are the only things allowed, as 0035/0037 allowed theirs); runs `summarize_e9_trunc.shrinkage`
IN-PROCESS over the four passes and states every count from it; reads the two reference medians from
`results/e9s/compare.json` / `results/e9l/summary.json` by sha; locates every cited ledger line by sentence search; reads the
E9-long sitting's duration from 0036 and its peak/rate from the runbook. Needs the four `e9 --align-only --config
config/e9t-*.toml` passes on the registrant's machine. *(Allocator state after 2026-10-04: appended in file order 0047, 0054, 0052, 0056, 0055, 0053, 0050 (`cff787f`, script retired); staged 0048/0049 and 0051. Next free number: **0057**.)*

*(2026-10-07: 0047's operator run is DONE and backed up (runbook `docs/runbooks/2026-10-06-cache-behavior-runpod-runbook.md`); `append_0049.py`
now asserts the OPERATOR's inputs manifest `2aeee576…` with its pinned fields checked against the pilot's freeze record, per the operator
ruling of 2026-10-07 quoted in the script (the pilot's frozen `9a6f2923…` embeds the sha of a private file); its `report["identity"]`
key bug fixed. Still queued behind 0048 (`PREV = "0048"`) unless the operator re-sequences. 0046's operator run is in progress.)*

*(2026-10-07 12:13Z: **0048 APPENDED** (chain `08b376985b5c`; the operator's 0046 run on a RunPod A100 SXM, three models, bridge and
summarizer passed, R8 `hossainpazooki/linear-ceiling-consolidation-2026-10-07`); `append_0048.py` retired in the append commit. File
order now ends 0053, 0050, 0048. 0049's ordering guard is therefore satisfied as staged; still staged: 0049, 0051, 0057. Next free: 0058.)*

*(2026-10-07 12:46Z: **0049 APPENDED** (chain `f1efa70bf50f`; the operator's 0047 run on a RunPod A100 SXM, 35/35, summarizer passed,
R8 `hossainpazooki/linear-ceiling-cache-behavior-2026-10-07`), after a skeptic pass over its operator-written paragraph corrected two
wordings (review `docs/reviews/2026-10-07-submitted-camera-ready-…md` §5); `append_0049.py` retired in the append commit. File order
now ends 0050, 0048, 0049. Still staged: 0051 (Llama long figures), 0057 (E-TRUNC figures). Next free: 0058.)*

**Staged 2026-10-07: `append_0058.py` — CORRECTIVE, the reading of f*** (operator ruling 2026-10-07, drafted after the skeptic
pass in `docs/reviews/2026-10-07-submitted-camera-ready-…md` §6.1): 0023's "oracle LOWER BOUND on real selective recompute" and
0027's "HOLDS reads on a floor" are withdrawn — the mean is over the REMAINING tokens, so the exact-repair fraction on the all-token
mean is at most f* while the two registered reasons push real recompute up; no ordering in either direction. f* is read as the
**oracle removal fraction**; every output stating f* carries those words and the entry number. Descriptive, no row, no `verdict:`
line; (f* = 0) ⇔ (g* = 0) so no cell can move. Fail-closed: every cited line located by sentence search inside its entry; the toy
example and a seeded sweep (seed 58) computed in-process with the registered `f_star`; refuses until the living files that print or
state the old words carry the new ones (`summarize_e9` output line, `f_star` docstring, `tests/test_summarize_e9.py`, README.md,
CLAUDE.md, staged `append_0057.py`) — all edited in the staging commit. Ordering guard 0049 present / 0058 absent (0051 and 0057 may
land before or after). Running the script is the ratification (0055 precedent). Next free number: **0059**.
*(0058 APPENDED 2026-10-07 by the operator, chain `5ba3adab23b1`; `ledger ok`; script retired in the append commit. File order now
ends 0048, 0049, 0058. Still staged: 0051, 0057.)*

*(**0051 APPENDED 2026-10-08** by the operator on the Mac mini, chain `75a47a51de6e` (`91cea79`; script retired `62982a8`): the Llama
long cell ran 2026-10-07 on a RunPod secure A100-SXM4-80GB, 32 of 32, complete, R8 `hossainpazooki/linear-ceiling-e9fl-2026-10-07`
verified; runbook `docs/runbooks/2026-10-07-llama-long-cell-runpod-runbook.md`. Before the append the script gained `--dataset`, the 0058
wording, and a computed paragraph stating the coverage pin's two renderings (0050's `16121e67` is the CRLF bytes; the box's LF
rendering is `9f10092b`). File order now ends 0049, 0058, 0051. Still staged: 0057 only. Next free number: **0059**.)*

**Staged 2026-10-08: `append_0059.py` — E9 summarizer enforcement, the τ RECOMPUTATION tolerance (0028's shape)** (operator ruling
2026-10-08 19:5xZ, "recommendation accepted"). 0023's "refuses on disagreement (1e-9)" held on every x86 rendering of the archived
mapper's held-out R² and fails on the arm64 home side (the Mac mini, since 0051): `summarize_e9` refused E-TRUNC's FULL level on
τ_V alone (gap 3.7e-9 in the check's units |a−b|/max(1,|a|,|b|)). Registers 1e-7 for the recorded-vs-recomputed and
config-vs-recomputed τ checks; the τ every reading uses stays the config's float, so nothing can move. Fail-closed: the 0023/0050
sentences located by search; five renderings read from `results/e9t-full/calibration*/` (x86 Linux 13/1 threads from the box with
`platform.json`, arm64 1/8 threads, the live calibration) with the assertions the sentences rest on (every x86 ≤ 1e-9, arm64 V > 1e-9,
arm64 identical across threads, agent_K gap 0, all ≤ 1e-7); the Llama cell's gaps from `results/e9fl/calibration/tau.json`;
`results/e9t-full/summary.json` must have been written UNDER the new check (`calibration.tau_recompute`, the 0028 move); refuses
unless `summarize_e9.py` carries `_TAU_TOL = 1e-7` + the recorded drift, the test exists, and `append_0057.py` asserts 0059 first.
Ordering guard 0058 + 0051 present, 0059 absent, 0057 absent. Runs on the Mac (the files live there). Next free number: **0060**.
*(**0059 APPENDED 2026-10-08** by the operator on the Mac mini, chain `64e1c6ba…` (`0aec95a`; script retired `b33c6ce`); `ledger ok`.
**0057 APPENDED 2026-10-09** by the operator on the Mac mini, chain `815cdcf5…` (`fd76600`; script retired `ce89ef2`), after a
skeptic pass on the rendered text (two wording corrections: 0055's ruling (1) sentence cited by search for a value above both
references; the per-handoff causal clause replaced by the pooled-median move with its zero-spanning interval) and R8
`hossainpazooki/linear-ceiling-e9t-2026-10-08` BACKUP VERIFIED (public). File order now ends 0058, 0051, 0059, 0057.
Nothing staged. Next free number: **0060**.)*

**Staged 2026-10-09: `append_0060.py` — the MLSys 2027 cut, the FIGURE SET frozen** (operator: "write entry 0060 summarizing
experiments addressing review"). Maps the LCFM reviewers' points (`docs/reviews/2026-09-30-review-response-map.md` rows W1–W8) to the
experiments run since — the second pair (0044 / 0053 / 0051), the same-model extension (0048), E-TRUNC (0055 / 0057), the tails
and native-window subset (0045), cache behaviour (0049), the two correctives (0058 / 0059) — with every figure READ from its
summary file in-process (`results/{e9,e9l,e9f,e9fl}/summary.json`, `e9s/compare.json`, `e8fa` and `e9c` summaries,
`consolidation/a100/summary.json`, `cache-behavior/summary.json`, `e9t/compare.json`, the four `tail.json`) and the file's
sha stated; entries located by their header lines (search, never typed). Freezes the set: nothing registered after 0060 enters
the submission; the manuscript tree is pinned at submission by the reconciliation record, not here. Conditions discharged
(0054, 0045) and carried (L32-native cell, long-cohort calibration size, E-BEH, issue #21) named. Descriptive, no `verdict:`
line, nothing runs. Ordering guard: 0057 and 0059 present (file order ends 0059, 0057), 0060 absent. Runs on Windows (the two
Mac-only summary files were copied over on 2026-10-09). Next free number: **0061**.

*(Carried 2026-10-13, no number: the next entry that touches 0045 carries one sentence correcting 0045:3126/3131 — the E7 report hash 27dc922e was regenerated on the second family's summarizing machine at home (0044:2920, 2924), not the GPU box, and T04 reproduces it there; learning 2026-10-13. Next free number unchanged: **0061**.)*

*(2026-10-10: **0060 APPENDED** (`e0be46d`, chain `84e86162…`; script retired in the retire commit; ran on Windows with
`--date 2026-10-10` after the 0060 preview passed the same day). File order now ends 0059, 0057, 0060. Nothing staged.
Next free number: **0061**. From this append on, allocator state is recorded here only; `CLAUDE.md` carries no entry
lines (PR #19's layout).)*

*(2026-10-10, late: **0061 WITHDRAWN before its staging commit** (operator ruling). A draft `append_0061.py` was written and
previewed as a corrective stating that the pooled PER-TOKEN p10/p90/p99 in 0038 (scaled − native) and 0045 (per cell) are
`np.quantile` linear interpolation while every quantile over handoffs is `e7_stats` nearest-rank; the preview reproduced all
11 recorded values and found the largest nearest-rank gap 0.0001001. Dropped because nothing on the record moves: the
summarizers' printed values are the readings, the ledger already carries an interpolated p90 at 0006 line 267, and 0013's
"one convention" sentence describes its own table. The fact lives in `AGENTS.md` (PR #19) and the learnings of 2026-10-01
and 2026-10-10; the rule for printing one of these quantiles in the paper is `tables/T01-pooled-per-token-quantiles.md`
(the first file of `docs/drafts/tables/`, paper-table drafts with their sources). The number 0061 was never used. Nothing staged.
Next free number: **0061**.)*

**Staged 2026-10-13: `append_0061.py` — the cache-behavior REPAIR amendment** (operator rulings B and F, 2026-10-13; private design
`~/dev/briefs/2026-10-13-linear-ceiling-experimental-gaps-plan.md` §9). Registers, before any operator prefill, entry 0047's
instrument on the same 35 long handoffs and the same prepared inputs as 0049 (manifest `2aeee5769c0a…`, reused byte for byte), with
the repair arms 0047 switched off: `oracle_ranked_{5,10,20}pct` (top-f matched tokens by archived δ_K recomputed in place against the
reused predecessors) and the selection control `random_ranked_{5,10,20}pct` (the same budget, drawn by `make_rng(seed + index +
1000003)`). Pins `config/cache-behavior-repair.toml` (`97aa99b1958e…`, every value equal to 0047's config but the two fraction lists),
`tools/cache_behavior/core.py` unchanged (`f346b5fdf3d3…`) and the amended `run.py` (`e137f1d8b8c5…`; two additive changes, the
optional `random_control_fractions` key and one selection branch; 0047's config carries no such key, so its registration reads
unchanged); text files hashed newline-normalized (`sha256_text_file`). Restates 0049's REUSE / RANDOM / CYCLIC figures by READING
`results/cache-behavior/summary.json` (`5228de0dd8c4…`). Output tree `results/cache-behavior-repair/` (R1: refuses if it holds a
run). DESCRIPTIVE, no band, no `verdict:` line. The figures entry is unwritten (0062 or later, by in-process `run.summarize` over the
verified mirror, checking the restated arms against 0049). Ordering guard: 0060 present, 0061 absent. `--preview` RAN 2026-10-13 on
Windows (exit 0, 69 lines). Next free number: **0062**.

*(2026-10-26: **0061 APPENDED** (`c2cb71b`, chain `aa8f79b8…`; script retired in the retire commit; run with `--date 2026-10-26`). File order now ends 0060, 0061. Still staged: 0062, 0063, 0064. Next free number: **0065**.)*

**Staged 2026-10-13, after `append_0061.py`: `append_0062.py` — the L32-NATIVE cell** (operator ruling A, 2026-10-13, same private
design §9; supersedes the wording of 0055's ruling 3, "keep R under YaRN", because every dump of the cell — S' = S[−32768:], S' + 1 for
the prefix control, R at most 25,073 — sits inside the receiver's declared native window, so both models run native and no per-dump
RoPE switch is needed). Registers, before any operator prefill, `config/e9t-l32n.toml` (`5e01f133c3c0…`: `config/e9t-l32.toml`
`3c0663fbb651…` minus `[e9.rope]` and `[e9.bridge]`, results dirs, `[e9.gate]` ending at 0062, plus `[e9.native]`), and the
instrument it needs: `summarize_e9`'s native-window control reads the longest DUMPED length against each dump's recorded window on a
truncated native cell only (every other config keeps the cap as the demand; summaries unchanged), `[e9.native]` in `config.py`, and
`summarize_e9_native` (the paired reader: refuses unless the native matched sets equal the YaRN level's, re-derives M_cap from the four
E-TRUNC passes, recomputes the YaRN-L32 far-from-seam median on the same tokens and refuses if it is not 0057's record). Runs
`summarize_e9_native.alignment_check` in-process over the five alignment passes (native coverage `be3e02040766…`): 35 of 35
identical to L32's, 21 enter / 14 void under the 0055 floor on the same M_cap as 0057. Reads the two reference levels from
`results/e9s/compare.json` (`a0699a826f1f…`) and `results/e9t/compare.json` (`0572662307f3…`), and the declared window from the
receiver's pinned `config.json` (revision `70d244cc86cc…`, the one 0047 pins). The reading, fixed now: native far-from-seam median on
M_cap within ±0.005 of native-short → THE SCALING; within ±0.005 of YaRN-L32 → NOT THE SCALING; between → UNATTRIBUTED. DESCRIPTIVE,
no band, no `verdict:` line. Pins the three source files by LF-normalized sha, so any edit to them before the append re-stages the
script. Ordering guard: 0061 present, 0062 absent. Next free number: **0063**.

*(2026-10-26: **0062 APPENDED** (`3541e16`, chain `72bd3d3c…`; script retired in the retire commit; run with `--date 2026-10-26`). File order now ends 0061, 0062. Still staged: 0063, 0064. Next free number: **0065**.)*

**Staged 2026-10-04 (late): `append_0057.py` — E-TRUNC figures** (registered by 0055; runbook `docs/runbooks/2026-10-04-e-trunc-gpu-runbook.md`).
DESCRIPTIVE, no `verdict:` line. Runs `summarize_e9` on each of the four levels in-process, then `summarize_e9_trunc.compare_levels`;
prints the reading the reader returns; carries 0055's two limitations and an erratum to 0055's re-matching sentence with its counts
read from `results/e9t/shrinkage.json` (review `docs/reviews/2026-10-04-0055-stated-figures-recomputed.md`). Needs `--box --launched
--finished --dataset` and `--cutoff-reason` exactly when a level closed partial. Ordering guard 0055 present, 0057 absent.
Refuses today (no `results/e9t-full/report.json`). Next free number: **0058**.

**0045 APPENDED 2026-10-01 (`b3bf7ec`; staged earlier that day as `append_0045.py`, retired with `tests/test_append_0045.py`)** — the corrective entry (the per-token tail per cell with the per-handoff maximum,
the 0025/0029 R² label, summary-file figures by key, and 0044's E7-hash erratum). Descriptive, no row, no `verdict:` line.
Reads `results/<cell>/tail.json` written by `e9_tail` (which runs `summarize_e9` first) for `e9l`, `e9`, `e9s`, `e9f`, and
refuses when tail.json's summary/report pins no longer match the files; every ledger line it cites is located by
sentence search inside the named entry (refuses on 0 or 2+ hits), never typed. `tests/test_append_0045.py` exercises it on
the synthetic cell. The entry's Condition 1 clause carries the operator's 2026-10-01 ruling that 0032's numbers-freeze is moot for
the camera-ready and the co-author refutation under `docs/reviews/` is what remains. The four tail.json files exist on the home machine only.

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
  *(2026-10-01: now `append_0046.py`; the gate now ends at 0046. 2026-10-04: now `append_0050.py`; gate `"0050"`.)*
- **`append_0046.py`** — the E9-long figures (was 0045). *(2026-10-01: now `append_0047.py`. 2026-10-04: now `append_0051.py`.)*

**Contingency, one commit:** if another session's entry lands first, all four move up together — every
`NUM`/`PREV` string, `[e8.gate]` in `config/e8f.toml`, and `[e9.gate]` in `config/e9f.toml` and
`config/e9fl.toml` — and that commit must precede `e8 --check` / `e9 --check`, which verify each config is
committed unmodified. The drafts are a chain: each refuses unless its predecessor's heading is already on
the ledger, each runs `ledger_check` after appending and exits with its return code, and each is deleted in
the same commit as its append, chained with `&&` (the 0025 lesson). On this checkout the interpreter is
`.venv/bin/python`. **0050–0051 (the Llama long drafts; 0046–0047 until 2026-10-04) still cannot run** (2026-10-01: commit P merged upstream
03:44Z, so the pin is reachable, but the long cell has not run). What each asserts and refuses on:
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
**`append_0050.py`** (**APPENDED 2026-10-04, `cff787f`, script retired**; E9 long half registration at a NATIVE receiver; was `append_0045.py` until 2026-10-01 and `append_0046.py` until 2026-10-04; DESCRIPTIVE, no row): declares entry
0035's D1(a), its configuration bridge and its scaled-receiver reading INAPPLICABLE, and states that the
cell cannot move, support or refute H-E9L and is never pooled with 0036's handoffs; asserts the floor
equals the short cell's cap AND that the ids it excludes under that floor are EXACTLY the short cell's
included set, so the partition is audited rather than asserted, with the residual above the cap — scored by
neither cell — named and counted; same tau and calibration checks as 0041.
**`append_0051.py`** (long-half figures; was `append_0046.py` until 2026-10-01 and `append_0047.py` until 2026-10-04; DESCRIPTIVE, no `verdict:` line): `summarize_e9 --config
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
change; the run itself is on a rented EC2 L40S, runbook `docs/runbooks/2026-09-13-e9s-gpu-runbook.md`; its figures enter by their own
entry, number allocated at staging). Earlier that day: **`append_0037.py` STAGED** (E9 scaled short cell registration: 0029's 25 handoffs under 0036's
receiver configuration and pin, `config/e9s.toml`; descriptive, no hypothesis row, no verdict; the comparison reader is
`linear_ceiling.e9_compare`; refuses until `results/e9s/align/coverage.json` reproduces 0029's included set, alignments and
keep draw exactly, `results/e9s/` holds nothing else, and the upstream HEAD is at 0036's pin). **0037 is allocated here.** If
the corrective entry on the f* reading (another session, 2026-09-11) lands first, it takes 0037 and this script, its `NUM`,
and `config/e9s.toml` `[e9.gate]` move to 0038 in one commit. Earlier (2026-09-10): **0035 APPENDED** 2026-09-09 (`bacfe86`, script retired `d582f48`); **0036 APPENDED** 2026-09-10 (H-E9L = HELD, 35 scored of 35, from a passing in-process `summarize_e9 --config config/e9l.toml`; script retired in the same change; run on a rented EC2 L40S, runbook `docs/runbooks/2026-09-10-e9l-gpu-runbook.md`). Earlier that day: **`append_0035.py` STAGED** (E9-long registration: H-E9L row `unresolved`, cap 81,920 by YaRN, floor 32,768, the 35 newly included handoffs, controls incl. the configuration bridge and length profiles, the run order + stopping rule, the paper re-scope superseding 0032's space clause; refuses until `config/e9l.toml` carries the real upstream pin, the upstream HEAD is at it with the RoPE spec, and `results/e9l/` holds nothing but `align/coverage.json`). **`append_0036.py` STAGED** (E9-long figures + H-E9L verdict from an in-process `summarize_e9 --config config/e9l.toml`; `verdict: H-E9L = <CELL>` line; run facts as arguments `--box/--launched/--finished`, `--cutoff-reason` required on a partial close; the bridge reading leads the entry when it is SCALED RECEIVER ONLY; refuses until 0035 is on the ledger and the summary passes). Earlier: **0034 appended** by `append_0034.py` (both summarizers in-process, both passed; script deleted in the
same commit set); **no drafts staged**. Earlier (2026-09-08): **0033 appended** by `append_0033.py` (prose amended first to state the two provenances of the n = 420
dumps — source CPU 2026-08-24, target GPU 2026-09-08 per `docs/runbooks/2026-09-08-n420-target-dump-runbook.md`; script deleted in the
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
post-training checkpoints) is designed only — `docs/design/2026-09-02-e-rl-design.md` — and has no
registration script; it takes a number when its script is staged, not before. The 0022 tokenizer
sensitivity (`summarize_e7 --strategy-override`) gets no entry of its own: it ships in the 0009
successor bundled with n = 420, per 0022's "one replay supersedes the figures once."

**`append_0063.py` — the TASK-QUALITY cell registered (ruling C of the 2026-10-13 plan; staged 2026-10-21).** Structured-field
recall of method signature lines, asked after R and answered by greedy decoding under FRESH, REUSE-ALL, RANDOM and REPAIR-f
caches (0047's / 0061's `core.py`, byte-identical), on the handoffs of 0036 and 0038 whose sender holds structured
code-search results (floor 10 valid form-2' items: 25 long and 14 short run, the rest listed void). Pins by LF-normalized
sha `config/task-quality-cell.toml`, `tools/task_quality/{items,pilot,cell}.py`, the two tests, the two items files and the
two C2 pilot reports; re-derives both pilot summaries in-process with the pinned reader and reads every count from the
items files. Headline chat form, first def-span exact match, signature items; median with p10/p90 by `e7_stats`, a 2,000-
resample bootstrap of the median, retention raw and floor-normalized against RANDOM; the plain form and the other scorers
in a sensitivity table. DESCRIPTIVE, no band. Refuses unless the items files and pilot reports are present at their hashes
(copy them under `results/task-quality/` from the machine that produced them, or re-extract from the verified mirrors) and
nothing exists under `results/task-quality-cell/`. Ordering guard: 0062 present, 0063 absent. Next free number: **0064**.
*(Re-staged 2026-10-26 after #27 merged: ask 12 of the #27 review packet (the length guard) stood at its default IN, so
`cell.py`'s reader reports mean generated tokens and the fraction at the cap per form and arm, and the script re-pins
`cell.py` and `tests/test_task_quality_cell.py`; the entry's readout states the guard. Nothing else in the draft moved.)*

*(2026-10-26: **0063 APPENDED** (`6f40d90`, chain `454d7439…`; script retired in the retire commit; run with `--date 2026-10-26`). File order now ends 0062, 0063. Still staged: 0064. Next free number: **0065**.)*

**`append_0064.py` — E8 on the MLPerf Agentic Inference text REGISTERED on both pairs (the 2026-10-22 plan, cell 1a; staged
2026-10-26).** `config/e8m.toml` (Qwen3 0.6B → 1.7B) and `config/e8mf.toml` (Llama-3.2-3B → Llama-3.1-8B): the 0016 §4 sampling
rule over two new suites of the MLCommons dataset (113 DeepSWE coding traces, 500 Workato workflow conversations; reasoning kept,
the shared ≈ 31K-token system prefix not rendered), 25 + 25 windows per pair, arm (b) over every sequence with the 0016
last-ten figure beside it. One bridge with lag-ladder: the Qwen token file is, id for id, the file its entry 0030 reads (one
sha, `9dce6082d057…`). DESCRIPTIVE, no hypothesis row, no band decision. Refuses unless both configs are committed unmodified
and name 0064 in `[e8.gate]`, the adapter and tests are the committed files, the dataset, the rendered export and both token
manifests re-derive, the family pin contains 0030's upstream commit, and nothing exists under `results/e8m` or `results/e8mf`
(R1). Ordering guard: 0061, 0062, 0063 present, 0064 absent. Next free number: **0065**.

*(2026-10-26: **0064 APPENDED** (`8d3a48a`, chain `d26c6c9c…`; script retired in the retire commit; run with `--date 2026-10-26`). File order now ends 0063, 0064. Still staged: nothing. Next free number: **0065**.)*

**Staged 2026-10-26: `append_0065.py` — the MLSys 2027 cut RESTATED (operator ruling 2026-10-24: "remove linear ceiling's
freeze"; drafted that day, staged after 0064 appended).** 0060's "Nothing registered after this entry enters the submission" is withdrawn; "a figure that changes re-enters
only through a later entry" is kept and used. The submission draws on every figure an entry on the ledger states at the cut,
2026-10-29 16:00 UTC (09:00 PDT), read from its summary file by sha through AGENTS.md's admitted evidence path; the commit at
the cut is pinned by the reconciliation record, as 0060 provides. 0060's table, wording invariants and conditions stand; no
figure is admitted by name; lag-ladder's figures enter through its own ledger; the MLPerf per-window join is stated only by
the entry that reads 0064's run. Ruling-only: no summarizer, no `verdict:` line, nothing under `results/`. Every cited
sentence located by search inside its entry (0060 ×4, 0064 ×2, AGENTS.md, the draft plan); lag-ladder 0036 read from the
sibling clone (HEAD, entry sha and chain line recorded; refuses when the clone is absent). Refuses until
`docs/paper-to-record.md` names 0065 and this README's last allocator line reads 0066. Ordering guard: 0061, 0062, 0063 and
0064 present, 0065 absent. Next free number: **0066**.

*(2026-10-26: **0065 APPENDED** (`ea2cf92`, chain `55051035…`; script retired in the retire commit; run with `--date 2026-10-26`). File order now ends 0064, 0065. Still staged: nothing. Next free number: **0066**.)*

**Staged 2026-10-27: `append_0066.py` — the conference cut WITHDRAWN (operator rulings 2026-10-27: the submission is not made;
the workshop camera-ready, nine pages, due 2026-11-13, is the one paper's first public form).** Withdraws 0065's
2026-10-29 cut and sets the camera-ready's own, 2026-11-10 16:00 UTC: every figure an entry on the ledger states by then enters,
by sha, through AGENTS.md's admitted evidence path; the next reviewed venue takes its own cut entry when chosen. 0060's
table, invariants and conditions stand; 0065's mechanism stands. Venue-neutral: cites 0060/0065 by number. Ruling-only:
no summarizer, no `verdict:` line, nothing under `results/`. Locates 0060's mechanism sentence and four 0065 sentences by
search. Refuses until `docs/paper-to-record.md` names 0066 with the cut, the denylist pattern carries the venue term, and
this README's last allocator line reads 0067. Ordering guard: 0065 present, 0066 absent. Next free number: **0067**.
