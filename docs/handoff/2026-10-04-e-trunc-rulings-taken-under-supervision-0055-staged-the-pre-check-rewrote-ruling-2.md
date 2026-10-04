# Handoff — E-TRUNC: rulings 1–3 taken under the operator's supervision, the instrument built, the registration staged as 0055, and the CPU pre-check that rewrote ruling 2

2026-10-04 ~10:00Z (session `d4f6aa2f`; transcript
`C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl`). Newest commit this brief
describes: **`a2742b9`** (`ledger: 0054 Condition 1 discharged by operator ruling`, another session's, local `main`, **ahead 4
of origin / behind 7** — PRs #10, #11, #13 merged on origin, fetched 09:5xZ, none touching this session's files). Everything
of this session is UNCOMMITTED on top of it (commit block in the session's final report). Untracked and not this session's:
`.claude/`, `docs/paper/tex/`.

Seed: `~/dev/briefs/linear-ceiling/2026-10-04-seed-e-trunc-rulings-1-3.md`. Picked up from
`2026-10-02-main-branch-second-close-…` with 15 commits of drift, all known to the seed. **Operator ruling mid-session
("needs your supervision"):** the three E-TRUNC rulings were taken by the session on the evidence and are PROVISIONAL —
running `docs/drafts/append_0055.py` is the ratification; nothing is on the ledger.

## Current state

- **built — the truncation key and the descending order.** `[e9.alignment] sender_head_truncate` (int in [1, cap)),
  applied in `e9_align.align` AFTER the cap/floor decision on the full lengths (every level keeps 0036's 35); the record's
  `n_sender` stays the full |S|, the npz holds S'; `[e9.order] by = "n_sender_desc"`; `summarize_e9` re-derives under the
  key and refuses a report whose recorded truncation differs. Existing cells byte-identical (conditional keys only).
  re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_e9_trunc.py` → `12 passed`; `git diff --stat HEAD -- src/` → 4 files.
- **built — the four configs and the comparator.** `config/e9t-{full,l65,l49,l32}.toml` = `config/e9l.toml` byte-for-byte
  except results/scratch dirs, `[e9.gate]` (ends `"0055"`), `[e9.order] by`, the key on the levels and `[e9.trunc]` on FULL
  (levels, floor 2,000, margin 0.005, the two reference records, bootstrap seed 52). `linear_ceiling.summarize_e9_trunc`:
  `--shrinkage` pre-prefill from the four alignment passes; the paired comparison on M_∩ after each level's own
  `summarize_e9` passes; fail-closed on report/config/pin/token/coverage/reference hashes.
  re-verify: `.venv/Scripts/python.exe -m pytest -q tests/test_summarize_e9_trunc.py` → `16 passed`; `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc --shrinkage | grep -c 'median 0.4470'` → `1`.
- **built — the registration draft `docs/drafts/append_0055.py` + `tests/test_append_0055.py`.** Ordering guard 0054
  present / 0055 absent; config hashes asserted; R1; shrinkage in-process; references by sha; ledger lines by sentence;
  E9-long's duration from 0036 and peak/rate from the runbook. `--preview` RAN on this tree (113 lines, exit 0).
  re-verify: `.venv/Scripts/python.exe docs/drafts/append_0055.py --preview | head -1` → starts `### 0055 — `; `.venv/Scripts/python.exe -m pytest -q tests/test_append_0055.py` → `2 passed`.
- **measured — the CPU pre-check (ruling 2's evidence).** |M_∩| / |M_FULL| median 0.447, pooled 0.409 (158,480 / 387,508);
  29 of 35 below 0.80; 14 void under |M_∩| ≥ 2,000 (11 at zero); loss mostly physical (early-S content removed; survivable
  median 0.503), re-matching instability > 0.05 on 10 handoffs (max 0.42). Two independent computations agree to the digit
  (a scratch re-alignment at ~06:40Z; the module at ~09:20Z under the renumbered configs).
  re-verify: `.venv/Scripts/python.exe -m linear_ceiling.summarize_e9_trunc --shrinkage | grep -E 'void under .*: 14 handoffs \(11|proposed: 29' | wc -l` → `2`.
- **verified — gates.** `ledger_check` → `ledger ok`; `lint_scope` → `scope ok`; suite `529 passed, 29 failed, 33 errors`:
  28 reds are the pickup baseline's two Windows classes (`e9.py:418` fsync on an `rb` handle — the line moved by 3 — and
  bash-exec/`os.statvfs` tests); the 29th is the OTHER session's `tests/test_summarize_e8.py::test_a_crlf_checkout_…`
  (`write_text` yields CRLF on Windows; their `484e1be`), not this session's. CI not run (uncommitted).
- **NOT done — the adversarial refutation by a subagent.** The `rigor:skeptic-verifier` dispatch died on usage credits
  before running anything. What stands in its place: every figure the entry states was recomputed by THIS session from
  the raw file at the point of use (coverage.json counts incl. "19 not 18"; 0038's 0.0195/0.0381/0.0629/0.4285 at
  ledger:2361 and in `results/e9s/compare.json` / `results/e9l/summary.json`; runbook :127/:139; 0036's 80 min), and the
  shrinkage distribution by two code paths. A fresh skeptic pass is owed before the append.
- **planned, not started:** the L32-native cell's instrument (per-dump RoPE switch + role-and-name-scoped identity
  check) and its amendment; the GPU request (after 0055 is on the ledger, R1); the figures entry.

## Locked decisions (provisional until the append)

- **Ruling 1:** "±0.005 absolute on the far-from-seam (16+) same-K *median*, as entry 0038 reports it" (run queue §10 item 1,
  verbatim). Reason: medians are what 0038 reports; the seam-bin means run 1.6–1.8× higher (0045). Pick-up check: `[e9.trunc]
  margin_abs = 0.005` in `config/e9t-full.toml`.
- **Ruling 2:** NOT the run queue's 0.80 ratio; the seed's alternative (b) "an absolute floor (|M_∩| ≥ 2,000) beside the
  ratio" as the void gate, ratio reported. Reason: the pre-check — 0.80 leaves 6 of 35. Pick-up check: `min_common_matched
  = 2000`; `results/e9t/shrinkage.json` `n_void` = 14.
- **Ruling 3:** "include it, keep R under YaRN, and state so" — taken AND DEFERRED to its own pre-prefill amendment. Reason:
  no instrument (one `rope_args(cfg)` per run; per-role spec identity in `summarize_e9`), and 0017/0019's never-truncate rule
  makes it descriptive-only regardless. Pick-up check: 0055's text says "not in this entry"; `grep -c 'rope_args(cfg)'
  src/linear_ceiling/e9.py` → 3.
- **The registration takes 0055, not the seed's 0052.** Reason: the other session staged 0052/0053 and appended 0054 while
  this session built (learnings entry). If 0048–0053 land first, NUM/PREV and the four `[e9.gate]` strings move in ONE
  commit, then the four alignment passes are re-run (the coverage pin refuses stale ones — learnings entry).
- **"length" in E-TRUNC means causal-prefix length on the late-S tokens the receiver re-renders**, and M_∩ is biased late;
  the entry says so. Reason: the pre-check.

## Reuse map

- `summarize_e9_trunc.common_subset` / `to_full_frame` — the FULL-frame intersection for any future per-level design.
- `summarize_e9_trunc.shrinkage` — a pre-prefill reading from alignment passes alone; the pattern for any gate that can be
  measured before the ruling.
- `tests/test_summarize_e9_trunc.py::_block_pairs` / `_level_pairs` / `_write_level` — synthetic multi-level cells with
  populated far-from-seam bins (random pairs put every token in seam bin 0).
- `docs/drafts/append_0055.py::cite` / `entry_text` — ledger lines by sentence search; E9-long's duration parsed from 0036.
- The scratch pre-check + diagnostic (survivable fraction vs ratio) lives in this session's scratchpad only; the module
  reproduces it.

## Invariants

- Entries 0001–0047 and 0054 are immutable; `docs/drafts/README.md` is the only allocator; next free is **0056**.
- The four e9t configs are pinned by LF-normalized sha in `append_0055.py`; any edit re-hashes and re-runs the passes.
- Existing cells' coverage.json / report.json are byte-identical under the new keys (conditional emission).
- Two sessions never edit one tree (memory `parallel-sessions-cloud-runs-or-own-worktree`); this session's paths are listed
  in the commit block.
- Private working docs stay under `~/dev/briefs`; the seed is there.

## Open / next

1. **Operator:** reconcile `main` (ahead 4 / behind 7): `git pull --rebase origin main`, then the commit block (final report),
   then push; CI is the Linux truth for the 29 Windows reds.
2. **Operator:** read `docs/drafts/append_0055.py --preview`; ratify or amend the three rulings in design §10; a fresh
   `rigor:skeptic-verifier` pass on the entry's figures (the brief's claim list is in the final report); then append:
   `.venv/Scripts/python.exe docs/drafts/append_0055.py && git rm docs/drafts/append_0055.py tests/test_append_0055.py` in
   ONE commit (the 10-02 learning).
3. **Operator:** the other session left `docs/drafts/README.md` saying 0054 is staged while `a2742b9` appended it, and
   `append_0054.py` still tracked — reconcile (not this session's file to fix).
4. Then the card (R1 → R2 probe under `config/e9t-full.toml` → the four levels, FULL first).
