# T04 — R12 recompute of 0051 (the Llama long cell) from the Hub mirror

status: DRAFT (recomputed 2026-10-11 by the second family's author on issue #21, ask 1; awaiting the operator's
  re-verify run)
sources: ledger lines at `e0be46d` (the ledger is unchanged from there to main `5c4e645`) — 0051:3870, 3874, 3878,
  3885, 3891. Files — `results/e9fl/summary.json`: the operator's mirror and the Hub backup carry sha256
  `1ac712b3897e…`; the recompute below wrote `b67ebd977cee…` (the difference is confined to the 19 leaves named under
  "What differs", none of them a figure here). Keys: `rule.tau_K`, `rule.tau_V`, `fstar.same_K.{n,median,p10,p90}`,
  `fstar.cross_K.{median,p10,p90}`, `fstar.cross_V.{median,p10,p90}`, `length_profiles.s_len[i].{bin,n_handoffs,
  fstar_K.median}`
conventions: four decimals, as the ledger prints them; every (p10, p90) over handoffs is `e7_stats.quantile` lower
  nearest-rank; "equal" means the recomputed value, printed at four decimals (counts as integers), is the entry's string, and every key also
  equals the Hub backup's `summary.json` value at full float precision
re-verify: sha256sum results/e9fl/summary.json   # 1ac712b3897e8ecf2f55bc1965b58b79d1593aadf97a6c32af5d32b2dd4190fa  results/e9fl/summary.json
re-verify: .venv/Scripts/python.exe -c "import json;s=json.load(open('results/e9fl/summary.json'));f=s['fstar'];r4=lambda x:round(x,4);print(r4(s['rule']['tau_K']),r4(s['rule']['tau_V']),f['same_K']['n'],[r4(f['same_K'][k]) for k in('median','p10','p90')],[r4(f['cross_K'][k]) for k in('median','p10','p90')],[r4(f['cross_V'][k]) for k in('median','p10','p90')],[(b['bin'],b['n_handoffs'],r4(b['fstar_K']['median'])) for b in s['length_profiles']['s_len']])"   # 0.2861 0.5289 32 [0.0, 0.0, 0.0] [0.7626, 0.5963, 0.9212] [0.8522, 0.752, 0.9322] [('32769-49999', 21, 0.0), ('50000-64999', 10, 0.0), ('65000-81920', 1, 0.0)]

What this is: R12's test for 0051, the one 2026-10-01's review ran for 0040 and 0044
(`docs/reviews/2026-09-28-llama-cell-r8-backup-and-recomputation.md`): `summarize_e9 --config config/e9fl.toml` on a
clean clone plus the two R8 backups, run by someone who was not at the sitting. This file is the record the recompute is
cited from.

### The figures (one row per figure issue #21's ask 1 names, plus the counts; recomputed = the summarizer's `results/e9fl/summary.json` from the download)

0051 prints more figures than these (same-model f*(τ_V), the τ ladder, f*(τ_agent_K), the bootstrap, blocks ≥ 4, the
seam and position profiles, matched fraction, ratios, bridge R²). The same passing run printed every one of them, and
`summary.json` matches the backup's on all of them (see "What differs"), but they are not tabulated here.

| figure | 0051 value | ledger line | recomputed | `summary.json` key | |
|---|---|---|---|---|---|
| τ_K (1 − the pair's k = 1 held-out R²_K) | 0.2861 | 0051:3870 | 0.2861 | `rule.tau_K` | equal |
| τ_V | 0.5289 | 0051:3878 | 0.5289 | `rule.tau_V` | equal |
| same-model K, handoffs scored | 32 | 0051:3874 | 32 | `fstar.same_K.n` | equal |
| same-model f*(τ_K), median | 0.0000 | 0051:3874 | 0.0000 | `fstar.same_K.median` | equal |
| same-model f*(τ_K), p10 | 0.0000 | 0051:3874 | 0.0000 | `fstar.same_K.p10` | equal |
| same-model f*(τ_K), p90 | 0.0000 | 0051:3874 | 0.0000 | `fstar.same_K.p90` | equal |
| cross-model f*(τ_K), median | 0.7626 | 0051:3891 | 0.7626 | `fstar.cross_K.median` | equal |
| cross-model f*(τ_K), p10 | 0.5963 | 0051:3891 | 0.5963 | `fstar.cross_K.p10` | equal |
| cross-model f*(τ_K), p90 | 0.9212 | 0051:3891 | 0.9212 | `fstar.cross_K.p90` | equal |
| cross-model f*(τ_V), median | 0.8522 | 0051:3891 | 0.8522 | `fstar.cross_V.median` | equal |
| cross-model f*(τ_V), p10 | 0.7520 | 0051:3891 | 0.7520 | `fstar.cross_V.p10` | equal |
| cross-model f*(τ_V), p90 | 0.9322 | 0051:3891 | 0.9322 | `fstar.cross_V.p90` | equal |
| \|S\| 32769–49999: same-model f*(τ_K) median | 0.0000 | 0051:3885 | 0.0000 | `length_profiles.s_len[0].fstar_K.median` | equal |
| \|S\| 32769–49999: handoffs in bin | 21 | 0051:3885 | 21 | `length_profiles.s_len[0].n_handoffs` | equal |
| \|S\| 50000–64999: same-model f*(τ_K) median | 0.0000 | 0051:3885 | 0.0000 | `length_profiles.s_len[1].fstar_K.median` | equal |
| \|S\| 50000–64999: handoffs in bin | 10 | 0051:3885 | 10 | `length_profiles.s_len[1].n_handoffs` | equal |
| \|S\| 65000–81920: same-model f*(τ_K) median | 0.0000 | 0051:3885 | 0.0000 | `length_profiles.s_len[2].fstar_K.median` | equal |
| \|S\| 65000–81920: handoffs in bin | 1 | 0051:3885 | 1 | `length_profiles.s_len[2].n_handoffs` | equal |

The rows were generated, not typed: each entry value is read off its ledger line at `e0be46d` by pattern, each
recomputed value off its key, and a row reads "equal" only when the two strings match.

### How it was recomputed

- **Result: PASSED.** The fail-closed reader refused nothing: alignments re-derived from the raw traces under the cap
  and floor (32 included / 36 excluded of 68), run order re-derived, the per-dump RoPE record checked over 97 dumps
  (max |diff| 1.2e-07 against atol 1e-05), every R² recomputed from recorded moments, per-token squares summed
  against the moments, the 3 kept handoffs' stride-1 dumps fingerprint-verified and re-scored here under 0028's
  tolerance (every square within 6.9e-04 relative; max |f* diff| 0.0e+00), τ recomputed from the archived mapper.
  Rule line: **HOLDS** (stated descriptively; 0051 carries no hypothesis row). The command, run in the scratch
  clone below and never on a verified mirror (it rewrites `results/e9fl/summary.{json,md}` in place):
  `HF_HUB_OFFLINE=1 .venv/bin/python -m linear_ceiling.summarize_e9 --config config/e9fl.toml`. At main the
  summarizer carries 0059's τ recomputation tolerance and prints one more line; this run used 8696e83's.
- **Code.** linear-ceiling cloned fresh at `8696e83bd2c9` (the driver commit the backup card names), clean;
  kv-transfer-replication cloned fresh from the fork at `06f8d55592570deae70c3feb9f84a75c4044fb03`, clean except the
  untracked archived `results/mapper/llama3.2-3b-to-llama3.1-8b/r2.json` placed in the upstream layout (the upstream
  gate passed). Each in its own environment.
- **Machine.** MacBook Pro (Mac15,6, Apple M3 Pro, arm64), 18 GB RAM, macOS 26.5, CPU only (the upstream scorer
  takes CUDA or CPU; no CUDA here). Python 3.12.13; linear-ceiling:
  torch 2.14.1, numpy 2.5.4, tokenizers 0.23.3, tiktoken 0.14.0, huggingface_hub 2.2.0; upstream: torch 2.14.1,
  transformers 5.19.0.
- **Inputs, each by pin.**
  - `hossainpazooki/linear-ceiling-e9fl-2026-10-07` at revision `cd76559344d5` (private; downloaded with read
    access to it): 572 files / 47.67 GB; all 569
    listed in its `SHA256SUMS` re-hashed after download and matched. Supplies `results/e9fl/`,
    `mappers/llama3.2-3b-to-llama3.1-8b/k1.*` and the archived `r2.json`.
  - The e8f R8 backup the 2026-10-01 record names, at revision `17da9aeb69b0` (public): `data/kv/llama3.2-3b-to-llama3.1-8b/`,
    `data/tokens/`, `results/e8f/report.json` (sha256 `4682508afd35…`) for the τ recomputation. Its archived
    `r2.json` is byte-identical to the e9fl backup's (sha256 `8498e977785e…`).
  - Traces: 188 of 188 files match `config/e7-manifest.json` by byte count and sha256 (`e7_manifest check`: manifest
    sha256 `371fb4bf3cb0…`).
  - Llama-3.2-3B tokenizer: snapshot `13afe5124825`, `config.json` `35f063e9…` and `tokenizer.json` `79e3e522…`
    as the 0051 runbook's R3 table pins them (a gated model), read offline (`HF_HUB_OFFLINE=1`).
  - `results/e7/skeleton_report.json`: deleted, then regenerated in the scratch clone by `e7_manifest check` (manifest
    ok, 188 files) and `e7 --config config/e7.toml`; sha256 `27dc922e3f7d…`. Logged 2026-10-11T22:13:38Z at `8696e83`
    on this machine; the summarizer had read a regeneration made the same way earlier that day, same sha256.

### What differs, and why it may

`summary.json` was compared leaf by leaf with the backup's: 19 leaves differ, in two groups, and no figure above is
among them.

1. **`coverage_comparison.e7_report_sha256`**: `27dc922e3f7d…` here against `0aba0fbe7aba…` in the backup. This is
   the E7-report difference 0044:2919–2930 records and 0045:3122–3128 revisits. 0044 records `27dc922e` for the report
   regenerated on its summarizing machine (0044:2916, 2919–2920 place that at home). 0045 records `0aba0fbe` from the
   home-mirror recomputation and the 2026-10-01 clean-clone record, attributes `27dc922e` to "the box" (0045:3122) and
   calls it the outlier (0045:3127). This recompute ran on 0044's summarizing machine: its own
   `results/e9f/summary.json`, written 2026-09-19, records `27dc922e` and `rescore_agreement.max_rel_square` 8.8e-04,
   0044's printed figure. Regenerated here from a fresh clone and the manifest-verified traces, the report is
   `27dc922e` again, so the value reproduces on this machine and "outlier" describes a machine, not a one-off. Whether
   0045's "box" wording needs a corrective is the operator's call; nothing here asserts one. The operator's Mac mini
   summary (this backup's `summary.json`) records `0aba0fbe`; whether that report was regenerated there is not on
   file. The tiktoken version here matches the
   2026-10-01 record's (0.14.0), and the report holds no machine paths. The cause is not established here and none
   is asserted. As 0044 states, the file feeds only the descriptive coverage comparison, and every coverage figure in
   this run's `summary.json` equals the backup's.
2. **`rescore_agreement.*`** (18 leaves): the box-vs-home re-score agreement figures for the kept handoffs, which
   describe the machine doing the re-score, not the cell. Here: per-head sums within 6.3e-07 relative (backup
   6.4e-07), max |δ_token diff| 9.9e-08 (backup 9.9e-08), bit-identical fractions moving by 6e-06 to 2e-03. All inside 0028's tolerance on both machines; max |f* diff| is 0.0e+00 on both.

### Limits

As the 2026-10-01 review said of 0040/0044: this reruns the project's own summarizer, not an independent
reimplementation. Of the 32 handoffs, the 3 kept ones are re-scored from tensors and the other 29 are checked
through their recorded moments and per-token squares (0019's design). The upstream scorer is the pinned one. It
shows 0051's figures are recomputable by someone who was not at the sitting, from the repository plus the e9fl
backup (private: it needs read access), the public e8f backup and the gated Llama-3.2-3B tokenizer; it is not a
refutation attempt.

Skeptic record: (none yet).

Approval record: (none yet). The status line becomes `APPROVED <date>` only in the operator's approving commit, after
the re-verify lines above have been run on the verified mirror.
