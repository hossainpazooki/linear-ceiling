# Upstream instrument (read-only)

- Repo: https://github.com/hossainpazooki/kv-transfer-replication
- Pinned commit: `71df45043a799560e7631faa2b42a9cf3f2be3ad` ("feat: score_mapper.py -- evaluate
  an existing mapper on new dumps without refitting", 2026-09-02; re-pinned by ledger entry
  0016 -- the commit adds exactly one file, `scripts/score_mapper.py`, on top of the prior pin's
  history). Prior pin: `f3594458` ("docs: Runs 5-7, six learnings entries, handoff brief",
  2026-08-25; full sha in ledger entry 0001); every provenance row below that names no sha
  refers to the prior pin, whose files are unchanged at the new one. At re-pin time the upstream
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
| R² definition A5 (pooled over rows and columns; mean of the scored set) | `docs/ledger.md` (A5), `kvt/ridge.py::r2_score` | `src/linear_ceiling/screen.py::r2_pooled` |
| fitted-mapper artifact layout `mappers/<pair>/k<k>.{json,safetensors}`, report `results/mapper/<pair>/r2.json` (both `/<tag>` when tagged) | `kvt/mapper.py::Mapper.save`, `scripts/fit_mapper.py::resolve_out_dirs` | `config/seal.toml` artifact roots |
| shared-tokenizer check compares vocab maps, not names | `kvt/models.py::assert_shared_tokenizer` | `src/linear_ceiling/weights.py::assert_shared_vocab` |
| Run 1 held-out K/V reference for H-S2 (best held-out cell: K_stripped 0.7606, V 0.5473; diagonal-mean held-out 0.6284 / 0.4361) | `docs/ledger.md` § Run 1 | `ledger/ledger.md` entry 0002 |
| Run 2 in-sample vs held-out rank behaviour cited by H-S3 | `docs/ledger.md` § Run 2, Run 4 | `ledger/ledger.md` entry 0002 |
| ledger house style (pre-registered hypotheses, verdict against the rule as written, status tags, immutable entries) | `docs/ledger.md` | `ledger/ledger.md` |
| fail-closed summarizer shape (refuse on missing/empty/mismatched inputs, never emit NaN) | `scripts/summarize_hellaswag.py::load_and_validate_records` | `src/linear_ceiling/summarize_e0.py` |
| existing-mapper scoring by subprocess (`--mapper --src --tgt --holdout-frac --out` -> `r2.json` with `fit_mapper.py`'s keys); held-out = last ceil(frac * n_seqs) sequences | `scripts/score_mapper.py` @ `71df45043a799560e7631faa2b42a9cf3f2be3ad` | `src/linear_ceiling/e8.py::score`, `summarize_e8` |
| dump layout consumed by `--tokens` (`[n_seqs, seq_len]` int64) and `--out` (writes `meta.json` with `n_seqs`, `stride`) | `scripts/dump_kv.py`, `kvt/data.py::dump_kv` | `src/linear_ceiling/e8_text.py::write_tokens`, `e8.py::dump_agent` |
