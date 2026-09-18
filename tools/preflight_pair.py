"""Preflight a PAIR against the two models' own recorded facts, before a card is rented.

CPU-only, gate-free, network-free, weights-free. It opens exactly four files -- `config.json` and
`tokenizer.json` under each side's snapshot directory -- and never imports torch, never loads a
model, never calls `weights.snapshot` (the package's only network call) and never reads a
`.safetensors` byte. A snapshot fetched with `allow_patterns=["*.json"]` is enough to run it, so
the whole check costs a few megabytes and a second, and it is meant to be run at home the moment
a new pair is proposed -- every failure below is a failure that would otherwise surface on a
rented GPU, hours and dollars later, or (worse) not at all.

What it asserts, and why each one can end a campaign:

  pair          `seal._validate_pair` (the string may key a path) and `pairs.pair_models`
                (the string must resolve to exactly these two model ids). A pair name that
                resolves to the wrong receiver is unrecoverable once a seal carries it.
  provenance    each snapshot directory must be the HF cache entry of the model id the pair
                resolves to. Community re-uploads of a gated model are NOT the same artifact
                (unsloth's Llama-3.2 mirrors add `pad_token_id`), and under the borrowed-facts
                rule no number written into a config or a ledger entry may come from one.
  matched_kv    `num_key_value_heads` equal AND per-head dim equal, the two clauses of upstream
                `kvt/pairs.check_matched_kv` -- which `scripts/dump_kv.py` calls unconditionally
                on EVERY dump, so a mismatch is not a mapper question, it is a "no dump exists".
                Both the declared `head_dim` and the derived `hidden_size // num_attention_heads`
                are printed per side: Llama-3.1-8B declares none and reaches 128 by the fallback.
  vocab         the `get_vocab()` maps must be equal. This is upstream
                `kvt/models.assert_shared_tokenizer` (`scripts/prepare_tokens.py:21` refuses on
                it, so it gates step ONE of E8) and this repo's `weights.assert_shared_vocab`,
                reproduced here from `tokenizer.json` alone: the base map from `model.vocab`
                updated with `added_tokens`, which is what HF's `get_vocab()` returns. Two models
                of one release can share a 128,256-entry BPE and still differ in a repurposed
                reserved-special-token slot; that difference is fatal and costs nothing to find.
  rope          both sides' scaling blocks, recorded in full. `rope_type` and -- for "llama3" --
                the three band parameters must agree, because they describe the same correction;
                `factor` is recorded PER SIDE and deliberately NOT asserted equal (Llama-3.2
                carries 32.0 and Llama-3.1 8.0, which is expected and harmless: the upstream
                strips with each dump's own recorded RopeSpec at 063f4023 and later). `rope_theta`
                is likewise recorded, never asserted: it is true but INSUFFICIENT once
                rope_type != "default".
  window        for every `--config` given: its `pair` must be this pair, and its `context_cap`
                must fit the window the run actually has -- the models' native
                `max_position_embeddings` when the config declares no `[e9.rope]`, or
                `original_max_position_embeddings x factor` when it does. A cap already inside the
                native window must NOT carry a scaling block: scaling a window that is already
                long enough is an unregistered change to the instrument.

Recorded but never asserted (differences here are real and harmless): `tie_word_embeddings` (the
upstream dumps with `logits_to_keep=1` and never reaches `lm_head`), `num_hidden_layers`,
`hidden_size`, `intermediate_size`, and the fp32 KV bytes per token each model implies.

usage:  .venv/bin/python tools/preflight_pair.py <pair> <source_snapshot_dir> <target_snapshot_dir> \
            [--config config/e9f.toml ...] [--json results/<exp>/preflight.json]
exit 0 only when every assertion passed; the JSON record is written either way.
"""
import argparse
import json
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from linear_ceiling import pairs                                    # noqa: E402
from linear_ceiling.hashing import sha256_file_bytes                # noqa: E402
from linear_ceiling.seal import SealViolation, _validate_pair       # noqa: E402
from linear_ceiling.weights import spec_from_config                 # noqa: E402

# The three "llama3" band parameters describe one correction to one frequency schedule, so they
# must agree across a pair; `factor` is the per-release extrapolation strength and need not.
_ROPE_SHARED = ("rope_type", "low_freq_factor", "high_freq_factor", "original_max_position_embeddings")


def cache_dir_name(d: Path) -> str | None:
    """`.../hub/models--meta-llama--Llama-3.1-8B/snapshots/<rev>` -> "models--meta-llama--Llama-3.1-8B".

    None when the directory is not an HF cache snapshot -- which is itself the answer to "where did
    these numbers come from?", and is reported as a failed provenance check rather than guessed at."""
    parent = d.parent.parent.name if d.parent.name == "snapshots" else ""
    return parent if parent.startswith("models--") else None


def repo_id_from_snapshot(d: Path) -> str | None:
    """The same directory decoded to a REPO ID: "meta-llama/Llama-3.1-8B".

    The record's `repo_id_from_path` is consumed by docs/drafts/append_0039.py, which compares it to
    the pair's model ids, so it must BE a repo id -- this previously returned the raw cache-directory
    name against its own docstring, and the entry script refused a preflight record that had in fact
    passed. The raw directory is still recorded separately as `cache_dir`, because it is the evidence.

    `models--<org>--<name>`: split on the first '--' after the prefix. A '--' inside a repo name would
    be ambiguous; neither of ours has one, and a mismatch surfaces as a failed provenance check rather
    than a silent wrong answer."""
    name = cache_dir_name(d)
    if not name:
        return None
    org, sep, rest = name[len("models--"):].partition("--")
    return f"{org}/{rest}" if sep else None


def get_vocab(tokenizer_json: Path) -> dict[str, int]:
    """HF `PreTrainedTokenizer.get_vocab()` reproduced from tokenizer.json alone: the BPE map plus
    the added/special tokens, which is exactly what `assert_shared_tokenizer` compares. Reading the
    file instead of constructing a tokenizer keeps this script free of `transformers` and of any
    chance of a network call, and added tokens are where two releases of one family actually
    diverge (repurposed `<|reserved_special_token_N|>` slots)."""
    tok = json.loads(tokenizer_json.read_text(encoding="utf-8"))
    vocab = dict(tok["model"]["vocab"])
    for t in tok.get("added_tokens", []) or []:
        vocab[t["content"]] = int(t["id"])
    return vocab


def read_model(model_id: str, snapshot_dir: str) -> dict:
    """Every recorded fact this script has, read from two JSON files. No tensor is opened."""
    d = Path(snapshot_dir).resolve()
    cfg_path, tok_path = d / "config.json", d / "tokenizer.json"
    for p in (cfg_path, tok_path):
        if not p.is_file():
            raise FileNotFoundError(f"{p} not found; point at an HF snapshot directory for {model_id}")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    spec = spec_from_config(cfg, model_id)                     # the repo's own recorded-facts reader
    vocab = get_vocab(tok_path)
    return {
        "model_id": model_id,
        "snapshot_dir": d.as_posix(),
        "repo_id_from_path": repo_id_from_snapshot(d),
        "cache_dir": cache_dir_name(d),
        "revision": d.name if d.parent.name == "snapshots" else None,
        # raw-bytes digests: these are the artifacts AS FETCHED from the gated repo, and a ledger
        # entry citing a shape figure cites these (hashing.sha256_file_bytes, not the canonical
        # JSON hash -- the bytes on the Hub are the provenance, not our re-serialisation).
        "config_json_sha256": sha256_file_bytes(cfg_path),
        "tokenizer_json_sha256": sha256_file_bytes(tok_path),
        "hidden_size": spec.hidden,
        "num_hidden_layers": spec.n_layers,
        "num_attention_heads": spec.n_heads,
        "num_key_value_heads": spec.n_kv,
        "head_dim_declared": cfg.get("head_dim"),              # absent on Llama-3.1-8B; present on 3.2-3B
        "head_dim_derived": cfg["hidden_size"] // cfg["num_attention_heads"],
        "head_dim": spec.d_h,                                  # what kv_shape/check_matched_kv actually use
        "intermediate_size": cfg.get("intermediate_size"),
        "rope_theta": spec.rope_theta,
        "rope_scaling": spec.rope_scaling,
        "max_position_embeddings": int(cfg["max_position_embeddings"]),
        "vocab_size": spec.vocab,
        "get_vocab_entries": len(vocab),
        "tie_word_embeddings": cfg.get("tie_word_embeddings"),
        # arithmetic over the fields above, nothing else: all layers, K and V, float32.
        "kv_bytes_per_token_fp32": spec.n_layers * 2 * spec.n_kv * spec.d_h * 4,
        "_vocab": vocab,                                       # popped before the record is written
    }


def check_window(doc: dict, path: Path, pair: str, native: int) -> list[tuple[str, bool, str]]:
    """A config's pair and its context cap against the window the run will actually have."""
    exp = "e9" if "e9" in doc else "e8" if "e8" in doc else None
    if exp is None:
        return [(f"config {path.name}", False, "no [e8] or [e9] section")]
    rows = [(f"config {path.name} pair", doc[exp].get("pair") == pair,
             f"{doc[exp].get('pair')!r} vs {pair!r}")]
    if exp == "e8":
        return rows                                            # E8 prefills 1,024-token windows; no cap to check
    cap = int(doc["e9"]["handoffs"]["context_cap"])
    floor = int(doc["e9"]["handoffs"].get("context_floor", 0))
    rope = doc["e9"].get("rope")
    if rope:
        window = int(round(int(rope["original_max_position_embeddings"]) * float(rope["factor"])))
        how = f"scaled {rope['rope_type']} x{rope['factor']} from {rope['original_max_position_embeddings']}"
        # A scaling block over a window that is already long enough is an unregistered change to
        # the instrument: it would move every position's frequencies for no gain in reach.
        rows.append((f"config {path.name} scaling is needed", cap > native,
                     f"context_cap {cap} vs native {native}: [e9.rope] present"))
    else:
        window, how = native, "native (no [e9.rope])"
    rows.append((f"config {path.name} context_cap", cap <= window, f"cap {cap} <= {window} ({how})"))
    if floor:
        rows.append((f"config {path.name} context_floor", 0 <= floor < cap, f"floor {floor} < cap {cap}"))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="CPU-only, network-free preflight of a pair's recorded facts")
    ap.add_argument("pair", help="pair name, e.g. qwen3-0.6b-to-1.7b")
    ap.add_argument("source", help="snapshot directory of the SOURCE model")
    ap.add_argument("target", help="snapshot directory of the RECEIVER/TARGET model")
    ap.add_argument("--config", nargs="*", default=[], help="config/*.toml files whose pair and cap to check")
    ap.add_argument("--json", help="write the record here (it is printed either way)")
    a = ap.parse_args()

    rows: list[tuple[str, bool, str]] = []
    try:
        _validate_pair(a.pair)
        src_id, tgt_id = pairs.pair_models(a.pair)
        rows.append(("pair resolves", True, f"{a.pair} -> source {src_id}, target {tgt_id}"))
    except (SealViolation, ValueError) as e:
        rows.append(("pair resolves", False, str(e)))
        print(f"PREFLIGHT FAILED: pair resolves: {e}")
        return 2                                               # nothing below is meaningful without the ids

    models = {}
    for which, mid, d in (("source", src_id, a.source), ("target", tgt_id, a.target)):
        try:
            models[which] = read_model(mid, d)
        except (FileNotFoundError, KeyError, ValueError) as e:
            rows.append((f"{which} snapshot", False, f"{type(e).__name__}: {e}"))
            print(f"PREFLIGHT FAILED: {which} snapshot: {e}")
            return 2
    s, t = models["source"], models["target"]

    for which, m in (("source", s), ("target", t)):
        rows.append((f"{which} provenance", m["repo_id_from_path"] == m["model_id"],
                     f"{m['repo_id_from_path']!r} (cache dir {m['cache_dir']}) for {m['model_id']} "
                     f"at {m['snapshot_dir']}"))
    rows.append(("matched-KV: num_key_value_heads", s["num_key_value_heads"] == t["num_key_value_heads"],
                 f"{s['num_key_value_heads']} vs {t['num_key_value_heads']}"))
    rows.append(("matched-KV: head_dim", s["head_dim"] == t["head_dim"],
                 f"{s['head_dim']} (declared {s['head_dim_declared']}, derived {s['head_dim_derived']}) vs "
                 f"{t['head_dim']} (declared {t['head_dim_declared']}, derived {t['head_dim_derived']})"))
    rows.append(("shared vocab: config vocab_size", s["vocab_size"] == t["vocab_size"],
                 f"{s['vocab_size']} vs {t['vocab_size']}"))
    sv, tv = s.pop("_vocab"), t.pop("_vocab")
    if sv == tv:
        rows.append(("shared vocab: get_vocab() maps", True, f"{len(sv)} entries, identical mapping"))
    else:
        only_s, only_t = sorted(set(sv) - set(tv)), sorted(set(tv) - set(sv))
        moved = sorted(k for k in set(sv) & set(tv) if sv[k] != tv[k])
        rows.append(("shared vocab: get_vocab() maps", False,
                     f"{len(sv)} vs {len(tv)} entries; only in source {only_s[:4]}; only in target "
                     f"{only_t[:4]}; {len(moved)} token(s) at different ids {moved[:4]} -- upstream "
                     "prepare_tokens.py:21 REFUSES this pair; there is no E8 corpus"))
    sr, tr = s["rope_scaling"] or {}, t["rope_scaling"] or {}
    for key in _ROPE_SHARED:
        if key in sr or key in tr:
            rows.append((f"rope {key}", sr.get(key) == tr.get(key), f"{sr.get(key)!r} vs {tr.get(key)!r}"))
    rows.append(("rope factor (recorded, not asserted)", True,
                 f"source {sr.get('factor')!r}, target {tr.get('factor')!r}; theta "
                 f"{s['rope_theta']} / {t['rope_theta']} -- the authority on a dump's frequencies is "
                 "the RopeSpec the upstream reads off the loaded model (063f4023+)"))

    native = min(s["max_position_embeddings"], t["max_position_embeddings"])
    rows.append(("native window (recorded)", True,
                 f"source {s['max_position_embeddings']}, target {t['max_position_embeddings']}; "
                 f"the pair's window is min = {native}"))
    for c in a.config:
        p = Path(c)
        try:
            rows += check_window(tomllib.loads(p.read_text(encoding="utf-8")), p, a.pair, native)
        except (OSError, tomllib.TOMLDecodeError, KeyError) as e:
            rows.append((f"config {p.name}", False, f"{type(e).__name__}: {e}"))
    rows.append(("tie_word_embeddings (recorded, not asserted)", True,
                 f"source {s['tie_word_embeddings']}, target {t['tie_word_embeddings']}; dump_kv passes "
                 "logits_to_keep=1 and never reaches lm_head"))

    ok = all(r[1] for r in rows)
    record = {"tool": "tools/preflight_pair.py", "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "pair": a.pair, "configs": [Path(c).as_posix() for c in a.config], "native_window": native,
              "models": {"source": s, "target": t},
              "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in rows], "ok": ok}
    for which, m in (("source", s), ("target", t)):
        print(f"== {which} {m['model_id']}  rev {m['revision']}")
        print(f"   layers {m['num_hidden_layers']} hidden {m['hidden_size']} heads {m['num_attention_heads']} "
              f"kv {m['num_key_value_heads']} d_h {m['head_dim']} vocab {m['vocab_size']} "
              f"mpe {m['max_position_embeddings']} kv_bytes/token(fp32) {m['kv_bytes_per_token_fp32']}")
        print(f"   config.json sha256 {m['config_json_sha256']}")
        print(f"   tokenizer.json sha256 {m['tokenizer_json_sha256']}")
    for n, o, d in rows:
        print(f"  {'OK  ' if o else 'FAIL'} {n}: {d}")
    if a.json:
        out = Path(a.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=1, sort_keys=False) + "\n", encoding="utf-8")
        print(f"record -> {out.as_posix()}")
    print(f"PREFLIGHT {'OK' if ok else 'FAILED'}: {sum(1 for r in rows if r[1])}/{len(rows)} checks passed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
