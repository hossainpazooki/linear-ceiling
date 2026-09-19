# Upstream patch specification — commit P: register `llama3.2-3b-to-llama3.1-8b`

**Date:** written 2026-09-18 · **Status:** specification only; nothing has been written to the upstream tree.
`../kv-transfer-replication` is read-only and pinned (`CLAUDE.md`, `UPSTREAM.md`), so this document is the whole
delivery: the operator lands the commit in their own clone, pushes it, and records the sha in `UPSTREAM.md` and in
the three new configs. It is written to be reviewed line by line before it is typed — every claim below was checked
against the upstream working tree at `d5786df` and against `git show 063f402:<path>`, and the two claims that could
not be checked here are marked as such in §7.

**The whole diff is one dict entry in one file.** That is the point of the matched-KV decision: the pair
meta-llama/Llama-3.2-3B → meta-llama/Llama-3.1-8B carries 8 KV heads × 128 head dim on both sides, so
`check_matched_kv` passes unrelaxed and the estimator, the scorers and the dump format need no extension at all.
An earlier draft of this campaign, written for Llama-3.2-1B → 3B (head dim 64 → 128), specified a rectangular
per-head map across `kvt/{pairs,mapper,ridge}.py`, `scripts/{dump_kv,probe,fit_mapper}.py` and a new test fixture.
**All of that is dropped.** Nothing is relaxed, nothing is gated on a registry flag, and no signature changes.

## 1. Base commit, and why it is not the current checkout

Base the commit on **`063f4023`** — `feat(rope): RoPE spec from the model's rotary embedding; YaRN-scaled dumps
strip exactly` — which is the tip of `origin/main` and a descendant of the recorded pin `223f4691` and of
`d5786df9` (verified here: `git merge-base --is-ancestor d5786df 063f402` and `… 223f469 063f402` both true; the
history is linear). The result of adding the entry below to it is commit **P**.

**P must not be based on `d5786df`, the commit this checkout is detached at.** At `d5786df`, `KVDump` strips RoPE
with `rope_cos_sin(positions, d_h, rope_theta)` — plain theta. Both models in this pair declare
`rope_scaling.rope_type = "llama3"`, which rescales the low-frequency bands, so a plain-theta strip is *silently
wrong on both sides*: it would not raise, it would produce content-space tensors that are not content-space, and
every R² and every τ downstream of them would be a number about nothing. At `063f4023`, `RopeSpec.from_model`
reads the model's own `rotary_emb.inv_freq` and `attention_scaling`, `dump_kv` halt-checks the reconstruction at
every dumped position at `ROPE_CHECK_ATOL = 1e-5`, and `kvt/data.py` records the spec into each dump's
`meta.json` — so the correction is inside the recorded spec and the strip round-trips exactly.
(`attention_scaling` is 1.0 for `rope_type "llama3"`; there is no YaRN anywhere in this campaign.)

The two sides carry **different** llama3 RoPE schedules — `factor` 32.0 on Llama-3.2, 8.0 on Llama-3.1 — which is
legal and expected here: `check_matched_kv` tests `n_kv` and `d_h` only, and the mapper is fitted in content
space, after each side has been stripped with *its own* recorded spec. Two consequences that belong to
linear-ceiling rather than to this patch, recorded here so the reviewer sees them together: the summarizer's
RoPE-identity assertion must be scoped **per model role** (receiver dumps agree with each other, source dumps
agree with each other) and never across roles, and the `context_cap ≤ every dump's recorded
max_position_embeddings` assertion is unchanged and is the native-window control for both Llama cells.

## 2. The diff

### 2.1 Required — `kvt/pairs.py`, symbol `PAIRS`

`PAIRS` is a `dict[str, Pair]` at `kvt/pairs.py:19-23`. Add one entry to it, after the three Qwen entries and
before the closing brace. `Pair` is a three-field frozen dataclass (`name`, `source`, `target`) at `kvt/pairs.py:12-16`
and is **not** modified.

```python
    # linear-ceiling entry NNNN (provisional): second model family, cross-release.
    # Matched-KV under paper Sec. 2.1: both sides num_key_value_heads=8, head_dim=128
    # (the 8B declares no head_dim; kv_shape reaches 128 via hidden_size // num_attention_heads),
    # so check_matched_kv passes without relaxation. The two sides carry DIFFERENT llama3 RoPE
    # scaling (3.2: factor 32.0; 3.1: factor 8.0), which is why this pair requires 063f4023 or
    # later: KVDump strips with each dump's own recorded RopeSpec, not with plain rope_theta.
    "llama3.2-3b-to-llama3.1-8b": Pair("llama3.2-3b-to-llama3.1-8b",
                                       "meta-llama/Llama-3.2-3B", "meta-llama/Llama-3.1-8B"),
```

`NNNN` is the registering linear-ceiling entry number. It is **provisional** until `docs/drafts/README.md`
allocates it at staging time, in staging order; the ledger currently ends at 0038. If the number moves, this
comment moves with it — it is a comment, so it costs nothing, but it must not be left naming an entry that turns
out to be something else.

**The key string is `llama3.2-3b-to-llama3.1-8b`, not `llama3.2-3b-to-8b`.** The upstream convention
(`short_name(source) + "-to-" + <target size>`) encodes "one ladder inside one release" and carries the release
prefix only on the source; applied across releases it would name the receiver **Llama-3.2-8B, a model that does
not exist**. The string keys the mapper directory, `results/mapper/<pair>/r2.json`, `data/kv/<pair>/{source,target}`,
`data/tokens/<pair>_n50_len1024_seed0.npy`, the sealed prediction `ledger/predictions/<pair>.json` and every
report; a seal is never rewritten, so a string that names the wrong receiver is not recoverable. The Qwen key
`qwen3-0.6b-to-1.7b` is untouched and stays byte-identical — it is baked into `PAIRS`, into
`mappers/qwen3-0.6b-to-1.7b/k1.{json,safetensors}` whose sha256 `calibrate_tau` records, and into four published
datasets.

That is the entire required change: **one file, one entry, no behaviour.**

### 2.2 Optional, same commit — a docstring that is no longer true

`_rope_theta`'s docstring opens "Read rope_theta from a Qwen3Config" and the registry is now family-general. If
the operator wants it fixed, it is a pure comment change with zero behaviour:

- make the first line family-neutral ("Read rope_theta from a model config");
- add one sentence: for `rope_type != "default"` the theta is true but **insufficient** — the `RopeSpec` recorded
  by `kvt/rope.py` is the authority, and any consumer that rotates from theta alone is wrong for this pair.

### 2.3 Optional, same commit — one cheap test

In `tests/test_pairs.py`, a matched-KV case built from the two real config shapes: a source stub declaring
`head_dim = 128`, `num_key_value_heads = 8`; a receiver stub with **`head_dim` absent**, `hidden_size = 4096`,
`num_attention_heads = 32`, `num_key_value_heads = 8`; assert `check_matched_kv` does not raise. It pins the
`hidden_size // num_attention_heads` fallback in `kv_shape` (`kvt/pairs.py:44-46`) that this pair's matched-KV
premise depends on, and it would catch a future edit that made `head_dim` mandatory.

`test_matched_kv_rejects_mismatch` and `test_wp1_chain_pairs_are_registered_and_consistent` are **untouched** —
the former exercises a genuine mismatch and stays a real assertion, the latter reads three Qwen keys by name.

## 3. What does not change, each line of it checked

| path | verdict | evidence |
|---|---|---|
| `kvt/pairs.py::check_matched_kv` (50-62) | **passes unchanged**: `n_kv` 8 = 8, `d_h` 128 = 128 | `kv_shape` uses `getattr(config, "head_dim", None) or hidden_size // num_attention_heads`; the 3B declares 128, the 8B computes 4096 / 32 = 128 |
| `kvt/pairs.py::_rope_theta` | works | both configs carry `rope_theta` (transformers 4 form) or `rope_parameters.rope_theta` (transformers 5) |
| `scripts/dump_kv.py:31` | **no change**: `check_matched_kv(...)` stays unconditional and passes | line 16's `choices=sorted(PAIRS)` picks the new key up for free |
| `kvt/rope.py` | **no change at all** — and this is the answer to "does a natively-131,072 receiver need anything here": no. `RopeSpec.from_model` reads the model's own `rotary_emb.inv_freq` and `attention_scaling`, so the llama3 correction is already inside the recorded spec | `git show 063f402:kvt/rope.py` |
| `kvt/models.py` | no change. `scaled_config()` is never reached: neither Llama config carries `[e9.rope]`, so `load_model(..., rope_scaling=None)` takes the plain path | `src/linear_ceiling/e9.py:67-68`; the 063f402 diff |
| `kvt/data.py` | no change. It already writes `meta["rope"]` (spec, `check_max_abs`, `check_atol`, `max_position_embeddings`) and strips with the spec; the pre-2026-09-09 fallback keeps archived Qwen dumps bit-identical | the 063f402 diff |
| `kvt/ridge.py:46` | **passes unchanged**: `assert src.n_kv == tgt.n_kv and src.d_h == tgt.d_h` is satisfied (8/8, 128/128) | |
| `scripts/probe.py` | no change. `p_over_n_probe = src.d_h / n_train` is unambiguous when the dims match; the loop is 28 × 32 × 8 = 7,168 fits per kind | |
| `scripts/fit_mapper.py` | **no change.** `p = sel.shape[1] * src.n_kv * src.d_h` is already source dims and equals target dims here; `Mapper.formula_params(tgt.n_layers, tgt.n_kv, k, tgt.d_h)` is exact for this pair, so the Appendix-D / Table-12 parameter-count control is **preserved, not forfeited** | lines 145, 149 |
| `kvt/mapper.py` | **no change.** `fit_mapper` takes `n_kv`/`d_h` from the target, which are the source's; `mapper_r2` slices `h*d_h:(h+1)*d_h` correctly; `mappers/qwen3-0.6b-to-1.7b/k1.json` stays byte-identical | |
| `scripts/score_mapper.py` | no change; it checks only target-vs-mapper shapes (71-73) | |
| `scripts/score_positions.py` | no change; geometry-agnostic given matched KV. `score_same` uses the receiver's `n_kv`/`d_h` for two receiver dumps; `score_cross` goes through `build_features` + `predict` in content space and never through `apply_mapper` | read in full |
| `scripts/prepare_tokens.py` | no change — **but see §4.1** | |

One number the reviewer should see beside this table, because the 1B → 3B draft got it wrong in the other
direction: `p = k · n_kv · d_h = 1024k` and `n_train = 0.8 × 50 × (1024/4) = 10,240`, so **p/n is
0.10 / 0.40 / 0.80 at k = 1/4/8 — numerically identical to Qwen's.** The earlier plan's caveat ("state the p/n
difference so a non-collapse at k = 4 is not misread as refuting 0016") is deleted: entry 0016's k = 4 collapse is
directly comparable on this pair at the same p/n.

## 4. Two upstream facts that are not diffs and will still stop the campaign

### 4.1 `assert_shared_tokenizer` is a hard gate on step one

`scripts/prepare_tokens.py:21` calls `assert_shared_tokenizer(tok_s, tok_t)`, which compares
`tok_a.get_vocab()` against `tok_b.get_vocab()` and raises on any difference (`kvt/models.py:51-55`). Both models ship the
128,256-entry Llama-3 BPE, but `get_vocab()` includes added and special tokens, and the Llama-3.2 release
repurposed several `<|reserved_special_token_N|>` slots. **If the two maps differ by one entry, `prepare_tokens`
refuses, there is no E8 corpus, and the pair is dead.** This is a pure `tokenizer.json` comparison on CPU that
costs nothing, it is the cheapest kill-shot in the whole plan, and it must be run *before a card is rented* —
`tools/preflight_pair.py` at home, against the gated `meta-llama` snapshots. It could not be run here (both repos
are gated and neither is cached on this machine). The same check backs linear-ceiling's `weights.assert_shared_vocab`.

If it fails, do not patch around it: the pair decision reopens.

### 4.2 `kvt/mapper.py::apply_mapper` is wrong for this pair, and is deliberately left wrong

`apply_mapper` builds `cos/sin` from `rope_cos_sin(positions, d_h, m.src_theta)` — plain theta — and the `Mapper`
record carries only the two theta floats, never a spec. For any `rope_type != "default"`, including this pair's
`llama3` on both sides, its strip/re-apply uses the unscaled schedule and is silently wrong.

It is **off the E8/E9 path**: grep over `kvt/`, `scripts/` and `tests/` gives three non-test call sites, in two
files — `kvt/hellaswag.py:114` and `scripts/compose_mapper.py:24-25` — and `score_positions` (`score_same` at
line 50, `score_cross` at 63) is not among them. So P changes nothing
there. The cost of that choice is a limitation that must be recorded rather than discovered later:
**`eval_hellaswag.py` and `compose_mapper.py` (H-C3) must not be run on this pair without a fix first.** It is
recorded in `UPSTREAM.md` and must be repeated in the registration entry. Keeping the diff at one dict entry is
worth more than pre-emptively fixing a path nobody on this campaign calls.

## 5. Landing it, and the re-pin

1. **Branch from `origin/main`** (already at `063f4023`; nothing to fetch — it is present locally). Do not branch
   from the detached `d5786df` checkout.
2. Apply §2.1 (and, if wanted, §2.2 / §2.3). Commit message in the upstream's own style, e.g.
   `feat(pairs): register llama3.2-3b-to-llama3.1-8b (matched-KV, cross-release)`.
3. `.venv/bin/python -m pytest -q` in the upstream tree: the existing suite must stay green. The new entry changes
   no behaviour, so a failure here means something else moved.
4. **Push to `https://github.com/hossainpazooki/kv-transfer-replication`.** `tools/ec2/setup.sh:22-24` clones both
   repos from `github.com/hossainpazooki` *at a sha*, so an unpushed P cannot be brought up on a box at all. Every
   linear-ceiling commit the sitting needs must be pushed for the same reason.
5. Record the resulting 40-hex sha in exactly three places plus one:
   - `UPSTREAM.md`, replacing the `UNRESOLVED::upstream_sha@P::…` marker (the file carries **one** full sha by
     rule, enforced by `tests/test_imports.py`, so recording P in full means the short form takes over wherever
     the previous pin was written in full, and `linear_ceiling.UPSTREAM_SHA` moves with it);
   - `config/e8f.toml`, `config/e9f.toml`, `config/e9fl.toml` as `upstream_sha`.
6. `git -C ../kv-transfer-replication checkout --detach <P>` before any Llama gate is run.

## 6. Which gates refuse until this lands, and what refuses while the checkout sits at P

`kvt/` is inside **both** gates' path sets — `src/linear_ceiling/e9.py:52`
`UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_positions.py", "scripts/score_mapper.py", "kvt")` and
`src/linear_ceiling/e8.py:39` `UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_mapper.py", "kvt")` — and
`check_upstream` (called at `e8.py:70` and `e9.py:96`) demands HEAD == the config's `upstream_sha` with those
paths tracked and clean. So:

- **Before P lands**, `e8 --check --config config/e8f.toml` and `e9 --check --config config/e9f.toml` (and
  `config/e9fl.toml`) refuse by name on the placeholder `upstream_sha`. That refusal is correct and is the reason
  nothing about the Llama pair can be fitted, dumped or scored yet. A one-line registry addition **cannot** be
  landed as a local edit in the pinned tree: `check_upstream` would see a dirty `kvt/`.
- **While the single checkout sits at P**, the Qwen configs refuse at their own gates. This is **existing
  practice, not a regression introduced here**: today, with the checkout detached at `d5786df`, `config/e9l.toml`
  and `config/e9s.toml` both pin `063f4023` — a *descendant* of HEAD — and already refuse, and `config/e8.toml`
  pins `71df4504`. Re-summarizing a Qwen cell has meant `git -C ../kv-transfer-replication checkout --detach
  <that cell's pin>` since 2026-09-10.
- **Do not create a second upstream clone** to dodge that. The case for one rests on the claim that the Qwen
  gates work today, which is false on the evidence above; and the proposed `${upstream_llama}` seal root cannot
  resolve — `config.py::_resolve` (lines 40-46) expands only the literal `${upstream}`, so anything else resolves
  to a path that does not exist and `seal.find_mapper_artifacts` fails closed on it. With one clone the four
  existing `artifact_roots` patterns in `config/seal.toml` (`{pair}/**/…` under `mappers`, `results/mapper`,
  `${upstream}/mappers`, `${upstream}/results/mapper`) already cover the Llama mapper, and `config/seal.toml`
  needs **no edit**.

## 7. What this specification does not settle

- **The Llama-3.2-3B config values.** No 3B snapshot or config exists on this machine. The matched-KV premise —
  `num_key_value_heads = 8`, `head_dim = 128` on the source side — is the one claim in this document that was not
  read from a file here. `tools/preflight_pair.py`, run against the **gated `meta-llama` repos** (not an unsloth
  or NousResearch mirror: those are re-uploads and cannot be the provenance of a number under the borrowed-facts
  rule), is the gate. If the 3B side is not 8 × 128, this specification is void and the rectangular extension it
  replaced comes back.
  `UNRESOLVED::src_config@meta-llama/Llama-3.2-3B::read config.json from the gated repo via tools/preflight_pair.py`
- **The receiver's own config.** The 8B numbers quoted above (`num_key_value_heads` 8, `num_attention_heads` 32,
  `hidden_size` 4096, `num_hidden_layers` 32, `max_position_embeddings` 131072, `vocab_size` 128256, `rope_theta`
  5e5, llama3 `factor` 8.0, no `head_dim` key) were read from the **Instruct sibling's** cached config.json, not
  from `meta-llama/Llama-3.1-8B` itself. The architecture and RoPE are the same across that pair by construction,
  but preflight must confirm it on the base repo before any of it is written into a config or an entry.
  `UNRESOLVED::tgt_config@meta-llama/Llama-3.1-8B::confirm against the gated base repo, not the Instruct sibling`
- **Whether the two `get_vocab()` maps are equal** (§4.1). Not checkable here; go/no-go for the whole campaign.
- **P's sha**, which does not exist until the operator commits.
  `UNRESOLVED::upstream_sha@P::the commit is not landed; record the 40-hex sha in UPSTREAM.md and in config/e8f.toml, config/e9f.toml, config/e9fl.toml`
