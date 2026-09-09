"""E9 driver and its gate -- the achievable fraction at a re-rendered handoff (ledger entries
0019 and 0023; 0025 adds the descriptive tau ladder and sets the keep-subset size).

`assert_ready` refuses until ledger/ledger.md (with entries 0019 AND 0023) and config/e9.toml
are committed unmodified, and the upstream pin holds for every invoked path (ancestor +
paths-unchanged + clean, `upstream_gate`). The upstream is called by subprocess in its own
environment; this module never imports kvt.

Per included handoff (|S| and |R| within the context cap; the rest EXCLUDED and counted):
three stride-1 single-sequence dumps with the upstream's `dump_kv.py` (receiver on S, receiver
on R, source on S), then `score_positions.py` over the aligned position pairs -> per-layer,
per-head SSE/SST and R² for E9-same and E9-cross, PLUS the per-token record (0023:
`--per-token`, squares [n, L, H] per read-out and arm, from which every 0023 figure is
recomputed on CPU). Dumps are deleted after scoring except for the seeded keep-subset, whose
dumps are fingerprinted so a CPU summarizer can re-score them from tensors. The report is
checkpointed after every handoff, so a reclaimed GPU box loses one handoff, not the run.

Two pre-batch controls (0023) run on the first included handoff's dumps, before it is scored:
the pipeline identity (R := S, pairs (p, p): every per-token square must be exactly zero; a
nonzero HALTS the run) and delta_null (a seeded derangement of sender positions, the
uninformative scale). Both records are kept beside the scores.

The driver states band outcomes for nothing: f*, medians and the H-E9 verdict travel only
through `summarize_e9` and a numbered entry.
"""
import argparse
import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, E9Config, load_e7_config, load_e9_config
from linear_ceiling.e9_align import align, load_handoffs, write_alignment
from linear_ceiling.e9_pertoken import null_pairs
from linear_ceiling.e8 import upstream_python
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.pairs import pair_models
from linear_ceiling.rng import make_rng
from linear_ceiling.e9_pertoken import centered_delta as _centered_delta, token_mean as _token_mean
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import snapshot

REQUIRED_ENTRIES = ("### 0019 ", "### 0023 ", "### 0025 ", "### 0026 ", "### 0027 ")   # 0025: tau ladder + keep n; 0026: upstream re-pin after the 09-04 OOM; 0027: cross-arm outcome, HOLDS-on-a-floor, kernel bound
UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_positions.py", "scripts/score_mapper.py", "kvt")
_PENDING = "UPSTREAM_SHA_PENDING"


def required_markers(cfg: E9Config) -> tuple:
    """The ledger headings the gate requires: config/e9.toml's five (E9, unchanged), or the list a
    later config carries in [e9.gate] (E9-long: entry 0035 and the rule entries it inherits)."""
    if cfg.required_entries:
        return tuple(f"### {n} " for n in cfg.required_entries)
    return REQUIRED_ENTRIES


def entry_list(cfg: E9Config) -> str:
    return "/".join(m.strip("# ").strip() for m in required_markers(cfg))


def rope_args(cfg: E9Config) -> list[str]:
    """`--rope-scaling <json>` for every upstream dump of a scaled run (E9-long); nothing for E9."""
    return ["--rope-scaling", json.dumps(cfg.rope, sort_keys=True)] if cfg.rope else []


def assert_ready(cfg: E9Config, repo_root: Path) -> None:
    cname = cfg.config_path.name
    if _PENDING in cfg.upstream_sha:
        raise RuntimeError(f"E9 REFUSED: config/{cname} still carries the pending upstream pin placeholder; "
                           "commit the upstream change and record its sha (entry 0023 for --per-token; entry 0026 for the attention re-pin; "
                           "entry 0035 for the RoPE spec)")
    mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{cfg.mapper_k}.safetensors"
    if not mapper.exists():   # gitignored E8 artifact; a fresh clone never has it (the 2026-09-04 box run died here after the first handoff's dumps)
        raise RuntimeError(f"E9 REFUSED: mapper artifact missing at {mapper}; copy mappers/{cfg.pair}/k{cfg.mapper_k}.json "
                           "and .safetensors from the home checkout (sha256-verify) before any prefill")
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"E9 REFUSED: {rel} is not committed as-is; entries {entry_list(cfg)} and config/{cname} "
                               "must be committed before any prefill")
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=repo_root,
                               capture_output=True, text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("E9 REFUSED: cannot read HEAD:ledger/ledger.md")
    for marker in required_markers(cfg):
        if marker not in committed.stdout:
            raise RuntimeError(f"E9 REFUSED: committed ledger has no entry {marker.strip('# ').strip()}")
    check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9")


def run_upstream(cfg: E9Config, args: list[str], runner=subprocess.run) -> None:
    cmd = [str(upstream_python(cfg.upstream_path)), *args]
    r = runner(cmd, cwd=str(cfg.upstream_path), capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace") if isinstance(r.stderr, bytes) else str(r.stderr)
        raise RuntimeError(f"E9 REFUSED: upstream command failed ({' '.join(args[:2])}):\n{err[-2000:]}")


def submission_dirs(e7: E7Config, cfg: E9Config) -> list[Path]:
    root = e7.traces_dir / cfg.suite
    subs = sorted(p for p in root.iterdir() if p.is_dir() and p.name.split("_", 1)[-1].startswith(cfg.agent))
    if not subs:
        raise RuntimeError(f"E9 REFUSED: no {cfg.agent} submissions under {root}")
    return subs


def keep_subset(included_ids: list[str], seed: int, n: int) -> list[str]:
    """Seeded draw of handoffs whose dumps are retained, from the sorted included ids."""
    ids = sorted(included_ids)
    if len(ids) <= n:
        return ids
    rng = make_rng(seed)
    picks = sorted(rng.choice(len(ids), size=n, replace=False).tolist())
    return [ids[i] for i in picks]


def _stem(handoff_id: str) -> str:
    return handoff_id.replace("/", "__").replace("#", "_sw")


def dump_fingerprint(d: Path) -> dict[str, str]:
    d = Path(d)
    return {p.relative_to(d).as_posix(): sha256_file_bytes(p) for p in sorted(d.rglob("*")) if p.is_file()}


def score_pairs(cfg: E9Config, hdir: Path, pairs_npz: Path, score_path: Path, tokens_path: Path,
                *, cross: bool, same_tgt: str = "same_tgt", runner=subprocess.run) -> dict:
    """One score_positions call (with --per-token) -> the record the report keeps for it."""
    args = ["scripts/score_positions.py",
            "--same-src", str((hdir / "same_src").resolve()),
            "--same-tgt", str((hdir / same_tgt).resolve()),
            "--pairs", str(pairs_npz.resolve()),
            "--out", str(score_path.resolve()),
            "--per-token", str(tokens_path.resolve())]
    if cross:
        mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{cfg.mapper_k}"
        args += ["--cross-src", str((hdir / "cross_src").resolve()), "--mapper", str(mapper)]
    run_upstream(cfg, args, runner)
    if not score_path.exists() or not tokens_path.exists():
        raise RuntimeError(f"E9 REFUSED: score_positions did not write both {score_path.name} and {tokens_path.name}")
    body = json.loads(score_path.read_text(encoding="utf-8"))
    tok_sha = sha256_file_bytes(tokens_path)
    if body.get("per_token", {}).get("sha256") != tok_sha:
        raise RuntimeError(f"E9 REFUSED: {score_path.name} does not name the per-token file it was written with")
    rec = {"score_file": score_path.name, "score_sha256": sha256_file_bytes(score_path),
           "tokens_file": tokens_path.name, "tokens_sha256": tok_sha, "n_pairs": body["n_pairs"]}
    for key in ("same_K_r2_layer_mean", "same_V_r2_layer_mean", "cross_K_r2_layer_mean", "cross_V_r2_layer_mean"):
        if key in body:
            rec[key] = body[key]
    return rec


def dump_handoff(cfg: E9Config, hdir: Path, s_ids: np.ndarray, r_ids: np.ndarray, runner=subprocess.run) -> dict:
    hdir.mkdir(parents=True, exist_ok=True)
    tok_s, tok_r = hdir / "S.npy", hdir / "R.npy"
    np.save(tok_s, s_ids.reshape(1, -1))
    np.save(tok_r, r_ids.reshape(1, -1))
    dumps = {"same_src": (tok_s, "target"), "same_tgt": (tok_r, "target"), "cross_src": (tok_s, "source")}
    for name, (tok, which) in dumps.items():
        run_upstream(cfg, ["scripts/dump_kv.py", "--pair", cfg.pair, "--which", which,
                           "--tokens", str(tok.resolve()), "--stride", "1",
                           "--out", str((hdir / name).resolve()), *rope_args(cfg)], runner)
        if not (hdir / name / "meta.json").exists():
            raise RuntimeError(f"E9 REFUSED: dump did not produce {hdir / name}/meta.json")
    return dumps


def run_bridge(cfg: E9Config, handoffs: list, enc, runner=subprocess.run) -> dict:
    """E9-long control 4 (entry 0035): the SCALED receiver against the NATIVE one on the same tokens,
    on the same box. For each registered bridge handoff (short ones from 0029's kept subset) the
    receiver prefills S twice -- once with the native RoPE, once under [e9.rope] -- and the two dumps
    are scored at pairs (p, p) over every sender position. Both dumps are kept and fingerprinted so the
    summarizer re-scores them from tensors. The reading is fixed in config (`reading_max_fstar`) and
    stated by the summarizer, never here. Runs BEFORE the first long handoff so a late failure cannot
    lose it."""
    if not cfg.bridge:
        return {}
    by_id = {h.handoff_id: h for h in handoffs}
    out = {"reading_max_fstar": float(cfg.bridge["reading_max_fstar"]), "handoffs": {}}
    bdir = cfg.results_dir / "bridge"
    for hid in cfg.bridge["handoffs"]:
        if hid not in by_id:
            raise RuntimeError(f"E9 REFUSED: bridge handoff {hid} is not among the observed handoffs")
        rec, s_ids, _, _ = align(by_id[hid], enc, cfg.context_cap)      # no floor: bridge handoffs sit below it by design
        if rec.excluded:
            raise RuntimeError(f"E9 REFUSED: bridge handoff {hid} is excluded at the cap ({rec.reason})")
        stem = _stem(hid)
        hdir = bdir / stem
        hdir.mkdir(parents=True, exist_ok=True)
        tok_s = hdir / "S.npy"
        np.save(tok_s, s_ids.reshape(1, -1))
        for name, extra in (("same_src", []), ("scaled", rope_args(cfg))):
            run_upstream(cfg, ["scripts/dump_kv.py", "--pair", cfg.pair, "--which", "target",
                               "--tokens", str(tok_s.resolve()), "--stride", "1",
                               "--out", str((hdir / name).resolve()), *extra], runner)
            if not (hdir / name / "meta.json").exists():
                raise RuntimeError(f"E9 REFUSED: bridge dump did not produce {hdir / name}/meta.json")
        n_s = int(s_ids.shape[0])
        pairs_file = hdir / "identity_pairs.npz"
        np.savez(pairs_file, pairs=np.stack([np.arange(n_s), np.arange(n_s)], 1).astype(np.int64))
        brec = score_pairs(cfg, hdir, pairs_file, bdir / f"{stem}.json", bdir / f"{stem}.tokens.npz",
                           cross=False, same_tgt="scaled", runner=runner)
        brec.update({"handoff_id": hid, "n_sender": n_s, "pairs_file": pairs_file.name,
                     "pairs_sha256": sha256_file_bytes(pairs_file),
                     "kept_dumps": {name: dump_fingerprint(hdir / name) for name in ("same_src", "scaled")},
                     "kept_dir": hdir.resolve().relative_to(cfg.results_dir.resolve()).as_posix()})
        out["handoffs"][hid] = brec
        print(f"[bridge] {hid}: native vs scaled receiver, same K R² {brec['same_K_r2_layer_mean']:.4f} over {n_s} positions")
    return out


def prefix_invariance_max_delta(score_json: Path, tokens_npz: Path, n_s: int) -> float:
    """Entry 0025 control statistic: the largest token-mean centered deviation (K or V) between the
    S dump and rows 0..|S|-1 of the S+1 dump, in R²'s units (0023). Pure arithmetic over the
    per-token record, shared by the driver (halt) and the summarizer (recheck)."""
    body = json.loads(score_json.read_text(encoding="utf-8"))
    worst = 0.0
    with np.load(tokens_npz) as z:
        for key in ("K", "V"):
            sst = np.asarray([layer["sst"] for layer in body["same"][key]], dtype=np.float64)
            d = _token_mean(_centered_delta(z[f"same_{key}"], sst, n_s))
            worst = max(worst, float(np.max(d)) if d.size else 0.0)
    return worst


def run_controls(cfg: E9Config, hid: str, hdir: Path, s_ids: np.ndarray, r_ids: np.ndarray, pairs: np.ndarray,
                 runner=subprocess.run) -> dict:
    """0023 pre-batch controls on the first included handoff's dumps, plus 0025's prefix-invariance
    control. The identity control HALTS the run on any nonzero square; the prefix control HALTS
    when the max centered deviation exceeds the registered tolerance."""
    cdir = cfg.results_dir / "controls"
    cdir.mkdir(parents=True, exist_ok=True)
    n_s = int(s_ids.shape[0])
    id_pairs = cdir / "identity_pairs.npz"
    np.savez(id_pairs, pairs=np.stack([np.arange(n_s), np.arange(n_s)], 1).astype(np.int64))
    ident = score_pairs(cfg, hdir, id_pairs, cdir / "identity.json", cdir / "identity.tokens.npz",
                        cross=False, same_tgt="same_src", runner=runner)
    z = np.load(cdir / "identity.tokens.npz")
    max_abs = max(float(np.abs(z["same_K"]).max()), float(np.abs(z["same_V"]).max()))
    ident["max_abs_square"] = max_abs
    if max_abs != 0.0:
        raise RuntimeError(f"E9 HALTED: pipeline identity control is nonzero (max square {max_abs}); "
                           "the dump/score path does not reproduce a prefill against itself")
    # Entry 0025 (review finding 3): the identity score above loads one dump twice, so zero is the
    # scorer's arithmetic, not the box's. Prefix invariance is the box's: prefill S followed by R's
    # first token, and rows 0..|S|-1 must reproduce the S dump up to kernel arithmetic (causal
    # attention). Transient dump, deleted after scoring; the per-token record is kept.
    plus_dir, tok_p = hdir / "same_src_plus1", hdir / "S_plus1.npy"
    np.save(tok_p, np.concatenate([s_ids, r_ids[:1]]).reshape(1, -1))
    run_upstream(cfg, ["scripts/dump_kv.py", "--pair", cfg.pair, "--which", "target",
                       "--tokens", str(tok_p.resolve()), "--stride", "1", "--out", str(plus_dir.resolve()),
                       *rope_args(cfg)], runner)
    if not (plus_dir / "meta.json").exists():
        raise RuntimeError(f"E9 REFUSED: prefix-invariance dump did not produce {plus_dir}/meta.json")
    pre = score_pairs(cfg, hdir, id_pairs, cdir / "prefix.json", cdir / "prefix.tokens.npz",
                      cross=False, same_tgt="same_src_plus1", runner=runner)
    shutil.rmtree(plus_dir, ignore_errors=True)
    worst = prefix_invariance_max_delta(cdir / "prefix.json", cdir / "prefix.tokens.npz", n_s)
    tol = float(cfg.controls["prefix_invariance_max_delta"])
    pre.update({"max_token_delta": worst, "tolerance": tol, "extra_token": int(r_ids[0]),
                "pairs_file": id_pairs.name, "pairs_sha256": sha256_file_bytes(id_pairs)})
    if worst > tol:
        raise RuntimeError(f"E9 HALTED: prefix-invariance control exceeds tolerance (max centered delta "
                           f"{worst:.3e} > {tol:.1e}); the box does not reproduce a prefix under one extra token")
    null_np = null_pairs(pairs, make_rng(int(cfg.controls["null_seed"])))
    null_file = cdir / "null_pairs.npz"
    np.savez(null_file, pairs=null_np)
    null = score_pairs(cfg, hdir, null_file, cdir / "null.json", cdir / "null.tokens.npz", cross=True, runner=runner)
    null["seed"] = int(cfg.controls["null_seed"])
    null["pairs_file"], null["pairs_sha256"] = null_file.name, sha256_file_bytes(null_file)
    return {"handoff_id": hid, "identity": {**ident, "pairs_file": id_pairs.name,
                                            "pairs_sha256": sha256_file_bytes(id_pairs)},
            "prefix": pre, "null": null}


def score_handoff(cfg: E9Config, stem: str, s_ids: np.ndarray, r_ids: np.ndarray, pairs_npz: Path,
                  *, keep: bool, runner=subprocess.run, controls_for: str | None = None,
                  pairs: np.ndarray | None = None) -> tuple[dict, dict | None]:
    """Three dumps -> (controls, if this is the control handoff) -> score_positions -> record;
    dumps deleted unless keep."""
    hdir = cfg.scratch_dir / stem
    dumps = dump_handoff(cfg, hdir, s_ids, r_ids, runner)
    controls = None
    if controls_for is not None:
        controls = run_controls(cfg, controls_for, hdir, s_ids, r_ids, pairs, runner)
    tdir = cfg.results_dir / "tokens"
    tdir.mkdir(parents=True, exist_ok=True)
    rec = score_pairs(cfg, hdir, pairs_npz, cfg.results_dir / "scores" / f"{stem}.json",
                      tdir / f"{stem}.tokens.npz", cross=True, runner=runner)
    if keep:
        rec["kept_dumps"] = {name: dump_fingerprint(hdir / name) for name in dumps}
        rec["kept_dir"] = hdir.resolve().relative_to(cfg.results_dir.resolve()).as_posix()
    else:
        shutil.rmtree(hdir, ignore_errors=True)
    return rec, controls


def align_only(cfg: E9Config, e7: E7Config, encoder=None) -> Path:
    """Entry 0025 (review finding 5): the alignment outputs on the record BEFORE any prefill --
    per handoff ids + pairs (.npz) and the record (.json) under results/e9/align, plus
    results/e9/align/coverage.json (observed / included / excluded with reasons, keep draw, and
    the matched-block length distribution). No gate: it reads traces and writes under results/
    only; the driver recomputes and overwrites the same files, and summarize_e9 re-derives every
    alignment from the raw traces regardless."""
    from linear_ceiling.e9_pertoken import BLOCK_BIN_LABELS, block_bin, block_lengths
    src_id, _ = pair_models(cfg.pair)
    enc = encoder or qwen_encoder(snapshot(src_id))
    counter = lambda t, ct="assistant": 0     # noqa: E731
    align_dir = cfg.results_dir / "align"
    records, included, blocks = [], [], {}
    for h in load_handoffs(submission_dirs(e7, cfg), counter):
        rec, s_ids, r_ids, pairs = align(h, enc, cfg.context_cap, cfg.context_floor)
        write_alignment(align_dir, rec, s_ids, r_ids, pairs)
        records.append(asdict(rec))
        if not rec.excluded:
            included.append(h.handoff_id)
            bl = block_lengths(pairs)
            bins = block_bin(bl)
            blocks[h.handoff_id] = {"n_blocks": int(round(float(np.sum(1.0 / bl)))) if len(bl) else 0,
                                    "tokens_by_block_len_bin": {lab: int((bins == i).sum()) for i, lab in enumerate(BLOCK_BIN_LABELS)},
                                    "tokens_in_blocks_ge_min": int((bl >= int(cfg.rule["min_block_len"])).sum())}
    included = sorted(included)
    out = {"config_sha256": sha256_text_file(cfg.config_path), "context_cap": cfg.context_cap,
           "context_floor": cfg.context_floor, "rope": cfg.rope,
           "coverage": {"observed": len(records), "included": len(included), "excluded": len(records) - len(included)},
           "exclusion_reasons": sorted({r["reason"] for r in records if r["excluded"]}),
           "run_order": run_order(records, included, cfg.order_by), "order_by": cfg.order_by,
           "keep_subset": keep_subset(included, cfg.keep_seed, cfg.keep_n),
           "min_block_len": int(cfg.rule["min_block_len"]), "blocks_per_handoff": blocks,
           "alignments": records}
    align_dir.mkdir(parents=True, exist_ok=True)
    p = align_dir / "coverage.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return p


def run_order(records: list, included: list[str], order_by: str) -> list[str]:
    """The registered order the driver scores in (entry 0035 stopping rule): by id (E9), or by |S|
    ascending with the id as tie-break (E9-long), so a run stopped at the cutoff has scored a PREFIX."""
    if order_by == "id":
        return sorted(included)
    n_s = {(r["handoff_id"] if isinstance(r, dict) else r.handoff_id): (r["n_sender"] if isinstance(r, dict) else r.n_sender)
           for r in records}
    return sorted(included, key=lambda h: (n_s[h], h))


def _resumable(report: dict, cfg: E9Config) -> dict:
    """Entry 0035: a relaunch after a crash keeps the checkpoint's bridge, controls and every scored
    handoff whose score and per-token files still match their recorded hashes; anything else is redone.
    The checkpoint must be this config's and this pin's, and must not be complete."""
    if report.get("complete"):
        raise RuntimeError("E9 REFUSED: --resume on a complete report; nothing to resume (delete it to rerun)")
    if report.get("config_sha256") != sha256_text_file(cfg.config_path) or report.get("upstream_sha") != cfg.upstream_sha:
        raise RuntimeError("E9 REFUSED: --resume checkpoint was written under another config or pin")
    kept = {}
    for hid, rec in (report.get("scores") or {}).items():
        sf, tf = cfg.results_dir / "scores" / rec["score_file"], cfg.results_dir / "tokens" / rec["tokens_file"]
        if (sf.exists() and tf.exists() and sha256_file_bytes(sf) == rec["score_sha256"]
                and sha256_file_bytes(tf) == rec["tokens_sha256"]):
            kept[hid] = rec
    return kept


def run(cfg: E9Config, e7: E7Config, *, repo_root: Path, runner=subprocess.run,
        encoder=None, resume: bool = False) -> Path:
    assert_ready(cfg, repo_root)
    src_id, _ = pair_models(cfg.pair)
    enc = encoder or qwen_encoder(snapshot(src_id))
    counter = lambda t, ct="assistant": 0     # noqa: E731  (texts only; token counts unused here)
    handoffs = load_handoffs(submission_dirs(e7, cfg), counter)
    align_dir = cfg.results_dir / "align"
    records, aligned = [], {}
    for h in handoffs:
        rec, s_ids, r_ids, pairs = align(h, enc, cfg.context_cap, cfg.context_floor)
        write_alignment(align_dir, rec, s_ids, r_ids, pairs)
        records.append(rec)
        if not rec.excluded:
            aligned[h.handoff_id] = (s_ids, r_ids, pairs)
    included = sorted(aligned)
    order = run_order(records, included, cfg.order_by)
    keep = keep_subset(included, cfg.keep_seed, cfg.keep_n)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.results_dir / "report.json"
    prior_scores, prior = {}, None
    if resume:
        if not out.exists():
            raise RuntimeError("E9 REFUSED: --resume without a checkpoint report")
        prior = json.loads(out.read_text(encoding="utf-8"))
        prior_scores = _resumable(prior, cfg)
    elif out.exists() and not json.loads(out.read_text(encoding="utf-8")).get("complete"):
        raise RuntimeError("E9 REFUSED: an unfinished report exists; relaunch with --resume to keep its scored handoffs, "
                           "or delete it to start over (a rotated log first, R4)")
    report = {
        "config_sha256": sha256_text_file(cfg.config_path),   # newline-normalized: the box writes LF, home checks out CRLF
        "upstream_sha": cfg.upstream_sha, "pair": cfg.pair,
        "alignment_method": cfg.alignment_method, "context_cap": cfg.context_cap,
        "context_floor": cfg.context_floor, "rope": cfg.rope,          # entry 0035 (E9: 0 and null)
        "coverage": {"observed": len(records), "included": len(included),
                     "excluded": len(records) - len(included)},
        "alignments": [asdict(r) for r in records],
        "run_order": order, "order_by": cfg.order_by,
        "keep_subset": keep, "bridge": None, "controls": None, "scores": {}, "complete": False,
        "resumed_from": {"scored": sorted(prior_scores), "bridge": bool(prior and prior.get("bridge")),
                         "controls": bool(prior and prior.get("controls"))} if resume else None,
        "note": "f*, medians and the H-E9 verdict travel only through summarize_e9 and a numbered entry",
    }
    if prior and prior.get("bridge"):
        report["bridge"] = prior["bridge"]
    elif cfg.bridge:
        report["bridge"] = run_bridge(cfg, handoffs, enc, runner)
        out.write_text(json.dumps(report, indent=1), encoding="utf-8")   # checkpoint: the bridge survives a later crash
    if prior and prior.get("controls") and prior["controls"]["handoff_id"] == order[0] and order[0] in prior_scores:
        report["controls"] = prior["controls"]
    for i, hid in enumerate(order):
        stem = _stem(hid)
        s_ids, r_ids, pairs = aligned[hid]
        if hid in prior_scores and (i > 0 or report["controls"] is not None):
            report["scores"][hid] = prior_scores[hid]
            out.write_text(json.dumps(report, indent=1), encoding="utf-8")
            print(f"[{i + 1}/{len(order)}] {hid}: kept from the checkpoint (score and per-token files match their hashes)")
            continue
        t0 = time.time()
        rec, controls = score_handoff(cfg, stem, s_ids, r_ids, align_dir / f"{stem}.npz",
                                      keep=hid in keep, runner=runner,
                                      controls_for=hid if i == 0 else None, pairs=pairs)
        if controls is not None:
            report["controls"] = controls
        report["scores"][hid] = rec
        report["scores"][hid]["seconds"] = time.time() - t0
        out.write_text(json.dumps(report, indent=1), encoding="utf-8")   # checkpoint per handoff
        print(f"[{i + 1}/{len(order)}] {hid}: same K "
              f"{report['scores'][hid]['same_K_r2_layer_mean']:.4f} in {report['scores'][hid]['seconds']:.0f}s")
    report["complete"] = True
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return out


def close_partial(cfg: E9Config) -> Path:
    """Entry 0035 stopping rule: close an unfinished run at the operator's cutoff. Allowed only when
    the config registers it; the scored set must be a prefix of the registered run order (it is, by
    construction, unless files were removed); the unscored handoffs are named in the report and the
    verdict entry, and coverage travels with every number the summarizer states."""
    if not cfg.allow_partial:
        raise RuntimeError("E9 REFUSED: this config does not register a partial close ([e9.order] allow_partial)")
    out = cfg.results_dir / "report.json"
    if not out.exists():
        raise RuntimeError("E9 REFUSED: no report to close")
    rep = json.loads(out.read_text(encoding="utf-8"))
    if rep.get("complete"):
        raise RuntimeError("E9 REFUSED: the report is already complete")
    if rep.get("config_sha256") != sha256_text_file(cfg.config_path):
        raise RuntimeError("E9 REFUSED: the report was written under another config")
    order, scored = rep["run_order"], list(rep["scores"])
    if scored != order[:len(scored)]:
        raise RuntimeError("E9 REFUSED: the scored set is not a prefix of the registered run order")
    if not scored:
        raise RuntimeError("E9 REFUSED: nothing scored; there is no partial run to close")
    if rep.get("controls") is None:
        raise RuntimeError("E9 REFUSED: the controls never ran; a run without them cannot be closed")
    rep["partial"] = {"closed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "n_scored": len(scored), "n_registered": len(order), "unscored": order[len(scored):]}
    rep["complete"] = True
    out.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(f"E9 partial close: {len(scored)} of {len(order)} scored; unscored named in report.json")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e9")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9.toml"))
    ap.add_argument("--e7-config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--check", action="store_true", help="run the gate only; read no trace, dump nothing")
    ap.add_argument("--align-only", action="store_true",
                    help="entry 0025: write every alignment (ids, pairs, records) and the coverage report under "
                         "results/e9/align before any prefill; CPU, no gate, no upstream, no dump")
    ap.add_argument("--resume", action="store_true",
                    help="entry 0035: relaunch after a crash keeping the checkpoint's bridge, controls and every scored "
                         "handoff whose files match their recorded hashes; same config and pin required")
    ap.add_argument("--close-partial", action="store_true",
                    help="entry 0035 stopping rule: close an unfinished run at the cutoff (allowed only by config); the "
                         "scored set must be a prefix of the registered run order; the unscored are named in the report")
    a = ap.parse_args(argv)
    cfg = load_e9_config(Path(a.config), REPO_ROOT)
    try:
        if a.check:
            assert_ready(cfg, REPO_ROOT)
            print(f"E9 gate: ready (entries {entry_list(cfg)} committed; upstream pinned and clean; config/{cfg.config_path.name})")
            return 0
        if a.align_only:
            out = align_only(cfg, load_e7_config(Path(a.e7_config), REPO_ROOT))
            print(f"E9 alignments: {out}")
            return 0
        if a.close_partial:
            print(f"E9 report: {close_partial(cfg)}")
            return 0
        out = run(cfg, load_e7_config(Path(a.e7_config), REPO_ROOT), repo_root=REPO_ROOT, resume=a.resume)
        print(f"E9 report: {out}")
        return 0
    except RuntimeError as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
