# Handoff — E9-long built end to end (upstream RoPE spec, instrument, 0035 staged, summarizer, 0036 staged), paper re-cut v2

2026-09-09 22:35Z (session `dev-47`, `9c42735d`; the builds-and-review session of the overnight plan; the other session owns the
AWS box, the launch and the pull). Newest commit this brief describes: linear-ceiling `407a38e` = origin/main plus this
session's UNCOMMITTED work; upstream `kv-transfer-replication` at `4633718` plus its UNCOMMITTED RoPE-spec change. Nothing
below is in history yet; the commit block is at the end. Deadline 2026-09-11 11:59 UTC.

## Current state

- **built / verified — upstream RoPE spec** (`kvt/rope.py::RopeSpec`, `kvt/data.py` dump + `KVDump` strip, `kvt/models.py
  scaled_config` + `load_model(rope_scaling=)`, `scripts/dump_kv.py --rope-scaling`, `tests/test_rope_spec.py`). Skeptic
  verdict SURVIVES on four attacks (bitwise cos/sin over 81,920 positions of the real config; divide-once residual 9.5e-7;
  YaRN static under the dynamic-update decorator; archived dumps bit-identical). One seam outside E9's route, named in 0035:
  `kvt/mapper.py::apply_mapper` is still plain-θ.
  re-verify: `cd ../kv-transfer-replication && .venv/Scripts/python.exe -m pytest -q` → 153 passed.
- **built / verified — E9-long instrument** (`config/e9l.toml`; `config.py` E9Config fields with E9 defaults; `e9_align`
  floor + `excluded_prior_cap` group; `e9.py` per-config gate markers, `rope_args`, `run_bridge`, `run_order`, `--resume`,
  `close_partial`; `summarize_e9.py` floor, run order, partial prefix, bridge re-score + reading, length profiles, None-safe
  re-score line). `config/e9.toml` untouched (its sha is in 0029's report).
  re-verify: `.venv/Scripts/python.exe -m pytest -q` → 423 passed, 1 skipped; `lint_scope` ok; `ledger_check` ok; `git diff --check` clean.
- **verified — alignment pass under the new config** reproduces the seed: 68 observed, 35 included, 25 prior-cap, 4 above
  cap, 4 empty R, budget 3,970,435 tokens, keep draw of 3.
  re-verify: `python -c "import json;c=json.load(open('results/e9l/align/coverage.json'));print(c['coverage'],c['keep_subset'])"`.
  NOTE: written under the PENDING-pin config sha; regenerate after the pin is recorded (the append script refuses otherwise).
- **staged — `docs/drafts/append_0035.py`** (registration + H-E9L row + paper scope superseding 0032's space clause; every
  number from config or coverage.json; refuses until the pin is real, HEAD == pin with the spec, and `results/e9l/` holds
  nothing but `align/`). `--preview` passed every assertion at 22:20Z.
- **staged — `docs/drafts/append_0036.py`** (figures + `verdict: H-E9L`; `--box/--launched/--finished`; `--cutoff-reason`
  required on a partial close; bridge reading leads the entry when SCALED RECEIVER ONLY). Parses; not runnable until 0035 and
  a passing e9l summary.
- **built — paper outline v2** `docs/paper/2026-09-10-lcfm-outline-v2.md` (two axes, one yardstick; §4.1 numbers recomputed
  from `results/e9/summary.json` this session, one typed error caught and fixed: matched fraction 0.9344 not 0.7746); the
  09-06 outline carries a supersession pointer and is otherwise unedited.
- **built — README rewritten around the objective** (the LCFM re-cut, the two-axis table with implemented-vs-planned states, the two conditions that decide the paper's content, decided cells incl. the H-E9L row); the two prior READMEs archived verbatim with banners under `docs/archive/` (`README-2026-09-04-visual.md` = the mermaid-heavy version at `7ce63cf`; `README-2026-09-09-status.md` = the status form at `b4b56aa`); scope sentence kept verbatim (`lint_scope` ok).
- **built — CLAUDE.md** command lines for e9l; **drafts README** allocator rows for 0035/0036; three learnings entries.
- **not started** — the box side (other session): AWS L40S, torch, clones at the pins, mapper by sha, traces via the manifest
  fetch, the R2 probe at T = 80,111 through `load_model(rope_scaling=…)`, launch, pull. **not started** — the co-author
  refutation of 0025–0029 (cond. 1 of the paper). **not started** — `summarize_e9 --calibrate-tau --config config/e9l.toml`
  (home, ~2 min, after the pin; writes `results/e9l/calibration/tau.json`, which the e9l summary requires).

## Locked decisions — premises checked

- **D1(a) YaRN factor 2.5, cap 81,920; D2 H-E9L verdict-bearing on the newly included set only; D3 keep n = 3 seed 9;
  D4 n = 50 mapper in the driver, n = 420 at home via `e9_rescore` if time; D5 the eight exclusions by name** (operator,
  2026-09-09, via the other session's picker). Premises hold at the alignment pass.
- **The bridge control runs on one platform** (the box dumps native and scaled itself) — my change to the seed's home-native
  comparison; reason: no 20 GB transfer, no cross-platform tolerance; stated in 0035.
- **Stopping rule = registered order + prefix property**, cutoff reason operator-stated in 0036 (learnings entry).
- **0035 carries the paper re-scope and supersedes 0032's space clause; every other 0032 clause kept, including the
  co-author condition unchanged.** Loosening that condition is the operator's call by a later entry, not mine.
- **Decision gate 23:30 UTC**: Build B green (it is) → register D1(a). Not needed: the fallback D1(c) is unused.

## Reuse map

- `docs/paper/2026-09-10-lcfm-outline-v2.md` — the team writes from this; §4.2 slots marked PENDING 0036.
- `docs/drafts/append_0035.py --preview` / `append_0036.py --preview --box … --launched … --finished …` — read the entry before
  appending; both refuse on anything out of order.
- `tests/test_e9_long.py`, `tests/test_summarize_e9_long.py` — the fake-runner shape for every new path (bridge, resume,
  partial, profiles).
- `results/e9l/align/coverage.json` — run order, keep draw, exclusions by reason.
- Upstream `tests/test_rope_spec.py` — the halt check and the wrong-strip demonstration.

## Invariants

`results/`, `data/`, `traces/` never enter history; `results/e9/` never rewritten (this session read it only); entries
0025–0034 immutable; `config/e9.toml` byte-unchanged; no number enters the ledger, the outline or a brief that a summarizer
did not produce (the outline's PENDING slots stay empty until 0036); upstream read-only from linear-ceiling (its change is
its own commit, by the operator); git history is the operator's; double-blind rules.

## Open / next (the morning sequence)

1. **Operator, now:** the commit block (upstream first; record the pin; regenerate `align/coverage.json`; commit the
   instrument; append 0035; commit the ledger alone; retire the script; `e9 --check --config config/e9l.toml` → ready;
   `summarize_e9 --calibrate-tau --config config/e9l.toml`). Second block for the summarizer/paper/docs work is in the
   session's closing message.
2. **Other session:** box + launch (detached, log rotated) → per-handoff pull → at the cutoff `e9 --close-partial` on the
   box if unfinished → pull `results/e9l/` whole.
3. **Home, morning:** `summarize_e9 --config config/e9l.toml` (a refusal is pasted verbatim into the brief and investigated,
   never worked around) → `append_0036.py --box … --launched … --finished … [--cutoff-reason …]` → commit ledger alone →
   retire → fill the outline's PENDING slots from 0036 only.
4. **Paper:** the team writes from outline v2; `/honesty-check` on §5's verbs before submission; cond. 1 (co-author
   refutation) decides whether §4.1 stays.
5. Not done, left to the operator: the n = 420 arm on the e9l kept subset (needs a `config/e9lc.toml` and its own entry);
   the `apply_mapper` seam upstream; the lit sweep; `check-learnings` reds (7 pre-existing).
