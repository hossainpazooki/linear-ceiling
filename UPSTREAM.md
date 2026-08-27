# Upstream instrument (read-only)

- Repo: https://github.com/hossainpazooki/kv-transfer-replication
- Pinned commit: `f3594458f73d70a15f195c863d52ea6592f61578` ("docs: Runs 5-7, six learnings
  entries, handoff brief", 2026-08-25). At pin time local `main` == `origin/main`.
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
