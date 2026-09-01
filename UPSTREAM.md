# Upstream instrument (read-only)

- Repo: https://github.com/hossainpazooki/kv-transfer-replication
- Pinned commit: `36d73b3f29d9b1f3a7c5148525de92b0b1b8ff5b` -- the commit that adds `--per-token` to
  `scripts/score_positions.py` and `scripts/score_mapper.py` plus `kvt/pertoken.py` (re-pin by
  ledger entry 0023; the operator records the sha here and in `config/e9.toml` after committing
  upstream -- `e9.assert_ready` refuses the placeholder by name). Its parent is the prior pin
  `7e41f792df0a03caa745a52de0ad2bd930e52a47` ("feat: score_positions.py -- KV agreement at
  matched positions, and a mapper's transfer to them", authored 2026-09-01; re-pinned by entry
  0019 -- adds exactly one file on top of the prior pin's history). Earlier pins, short form
  (one full sha lives in this file by rule, enforced by `tests/test_imports.py`): `71df4504`
  (entry 0016; added `scripts/score_mapper.py`) and `f3594458` (entry 0001, the original pin;
  full sha there). Every provenance row below that names no sha refers to the
  original pin, whose files are unchanged at the new one. Experiment gates check their OWN
  recorded pin by ancestry + invoked-paths-unchanged (`linear_ceiling.upstream_gate`), so an
  older experiment's pin survives a newer one's re-pin. At re-pin time the upstream
  working tree was clean for every path E8 invokes (`scripts/dump_kv.py`, `scripts/score_mapper.py`,
  `kvt/`) and `e8.assert_ready` re-checks that before each run; other paths there carried
  unrelated local edits (the operator's acknowledged one-time drift), which E8 never reads.
- Local path (used by `config/seal.toml` as `${upstream}`): `../kv-transfer-replication`
- Rule: nothing in this repo writes into the upstream tree, imports `kvt`, or copies its
  code. Fitting, injection, and evaluation are invoked there (W2+), by subprocess, in the
  upstream's own environment.

## Provenance ledger — everything borrowed, with `{sourceRepo, filePath, commitSha}`

`sourceRepo` is the upstream above and `commitSha` is the pin unless stated.

| what | filePath @ sha | used in |
|---|---|---|
| pair naming `qwen3-0.6b-to-1.7b` and model ids | `kvt/pairs.py` | `src/linear_ceiling/pairs.py` |
| KV shape from config (`head_dim` or `hidden/heads`; `rope_theta` may live in `rope_parameters`) | `kvt/pairs.py::kv_shape,_rope_theta` | `src/linear_ceiling/weights.py::spec_from_config` |
| R² definition A5 (pooled over rows and columns; mean of the scored set) -- applied PER HEAD by the mapper scorers and averaged over heads then layers (entry 0023 records the distinction: pooling a layer's heads gives 0.6917, the head-averaged record is 0.6814) | `docs/ledger.md` (A5), `kvt/ridge.py::r2_score`, `kvt/mapper.py::mapper_r2` | `src/linear_ceiling/screen.py::r2_pooled`; E8/E9 figures are the head-averaged form |
| fitted-mapper artifact layout `mappers/<pair>/k<k>.{json,safetensors}`, report `results/mapper/<pair>/r2.json` (both `/<tag>` when tagged) | `kvt/mapper.py::Mapper.save`, `scripts/fit_mapper.py::resolve_out_dirs` | `config/seal.toml` artifact roots |
| shared-tokenizer check compares vocab maps, not names | `kvt/models.py::assert_shared_tokenizer` | `src/linear_ceiling/weights.py::assert_shared_vocab` |
| Run 1 held-out K/V reference for H-S2 (best held-out cell: K_stripped 0.7606, V 0.5473; diagonal-mean held-out 0.6284 / 0.4361) | `docs/ledger.md` § Run 1 | `ledger/ledger.md` entry 0002 |
| Run 2 in-sample vs held-out rank behaviour cited by H-S3 | `docs/ledger.md` § Run 2, Run 4 | `ledger/ledger.md` entry 0002 |
| ledger house style (pre-registered hypotheses, verdict against the rule as written, status tags, immutable entries) | `docs/ledger.md` | `ledger/ledger.md` |
| fail-closed summarizer shape (refuse on missing/empty/mismatched inputs, never emit NaN) | `scripts/summarize_hellaswag.py::load_and_validate_records` | `src/linear_ceiling/summarize_e0.py` |
| existing-mapper scoring by subprocess (`--mapper --src --tgt --holdout-frac --out` -> `r2.json` with `fit_mapper.py`'s keys); held-out = last ceil(frac * n_seqs) sequences | `scripts/score_mapper.py` @ `71df4504` (entry 0016) | `src/linear_ceiling/e8.py::score`, `summarize_e8` |
| matched-position KV scoring (`--same-src --same-tgt --cross-src --mapper --pairs --out`; per-layer/per-head SSE+SST alongside R² so moments reproduce every figure) | `scripts/score_positions.py` @ `7e41f792` (entry 0019) | `src/linear_ceiling/e9.py::score_pairs`, `summarize_e9` |
| per-token record (`--per-token`: squares `[n, L, n_kv]` float32 for same/cross x K/V plus the receiver's own norms; the recorded per-head SSE is the float64 sum of exactly these squares) | `scripts/score_positions.py`, `scripts/score_mapper.py`, `kvt/pertoken.py` @ the 0023 pin | `src/linear_ceiling/e9.py::score_pairs`, `summarize_e9` (sum check, f*, profiles), `summarize_e9.calibrate_tau` |
| A5-pooled-over-heads per-layer R² as a labelled diagnostic beside the head-averaged figure | `kvt/pertoken.py::pooled_r2` @ the 0023 pin | entry 0023 (the 0.6917 vs 0.6814 line) |
| dump layout consumed by `--tokens` (`[n_seqs, seq_len]` int64) and `--out` (writes `meta.json` with `n_seqs`, `stride`) | `scripts/dump_kv.py`, `kvt/data.py::dump_kv` | `src/linear_ceiling/e8_text.py::write_tokens`, `e8.py::dump_agent` |
