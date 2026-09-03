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
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import snapshot

REQUIRED_ENTRIES = ("### 0019 ", "### 0023 ", "### 0025 ")   # 0025: tau ladder (descriptive) + keep n, before any prefill
UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_positions.py", "scripts/score_mapper.py", "kvt")
_PENDING = "UPSTREAM_SHA_PENDING"


def assert_ready(cfg: E9Config, repo_root: Path) -> None:
    if _PENDING in cfg.upstream_sha:
        raise RuntimeError("E9 REFUSED: config/e9.toml still carries the pending upstream pin placeholder; "
                           "commit the upstream --per-token change and record its sha (entry 0023)")
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"E9 REFUSED: {rel} is not committed as-is; entries 0019/0023/0025 and config/e9.toml "
                               "must be committed before any prefill")
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=repo_root,
                               capture_output=True, text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("E9 REFUSED: cannot read HEAD:ledger/ledger.md")
    for marker in REQUIRED_ENTRIES:
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
                           "--out", str((hdir / name).resolve())], runner)
        if not (hdir / name / "meta.json").exists():
            raise RuntimeError(f"E9 REFUSED: dump did not produce {hdir / name}/meta.json")
    return dumps


def run_controls(cfg: E9Config, hid: str, hdir: Path, s_ids: np.ndarray, pairs: np.ndarray,
                 runner=subprocess.run) -> dict:
    """0023 pre-batch controls on the first included handoff's dumps. The identity control
    HALTS the run on any nonzero square."""
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
    null_np = null_pairs(pairs, make_rng(int(cfg.controls["null_seed"])))
    null_file = cdir / "null_pairs.npz"
    np.savez(null_file, pairs=null_np)
    null = score_pairs(cfg, hdir, null_file, cdir / "null.json", cdir / "null.tokens.npz", cross=True, runner=runner)
    null["seed"] = int(cfg.controls["null_seed"])
    null["pairs_file"], null["pairs_sha256"] = null_file.name, sha256_file_bytes(null_file)
    return {"handoff_id": hid, "identity": {**ident, "pairs_file": id_pairs.name,
                                            "pairs_sha256": sha256_file_bytes(id_pairs)},
            "null": null}


def score_handoff(cfg: E9Config, stem: str, s_ids: np.ndarray, r_ids: np.ndarray, pairs_npz: Path,
                  *, keep: bool, runner=subprocess.run, controls_for: str | None = None,
                  pairs: np.ndarray | None = None) -> tuple[dict, dict | None]:
    """Three dumps -> (controls, if this is the control handoff) -> score_positions -> record;
    dumps deleted unless keep."""
    hdir = cfg.scratch_dir / stem
    dumps = dump_handoff(cfg, hdir, s_ids, r_ids, runner)
    controls = None
    if controls_for is not None:
        controls = run_controls(cfg, controls_for, hdir, s_ids, pairs, runner)
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


def run(cfg: E9Config, e7: E7Config, *, repo_root: Path, runner=subprocess.run,
        encoder=None) -> Path:
    assert_ready(cfg, repo_root)
    src_id, _ = pair_models(cfg.pair)
    enc = encoder or qwen_encoder(snapshot(src_id))
    counter = lambda t, ct="assistant": 0     # noqa: E731  (texts only; token counts unused here)
    handoffs = load_handoffs(submission_dirs(e7, cfg), counter)
    align_dir = cfg.results_dir / "align"
    records, aligned = [], {}
    for h in handoffs:
        rec, s_ids, r_ids, pairs = align(h, enc, cfg.context_cap)
        write_alignment(align_dir, rec, s_ids, r_ids, pairs)
        records.append(rec)
        if not rec.excluded:
            aligned[h.handoff_id] = (s_ids, r_ids, pairs)
    included = sorted(aligned)
    keep = keep_subset(included, cfg.keep_seed, cfg.keep_n)
    report = {
        "config_sha256": sha256_text_file(cfg.config_path),   # newline-normalized: the box writes LF, home checks out CRLF
        "upstream_sha": cfg.upstream_sha, "pair": cfg.pair,
        "alignment_method": cfg.alignment_method, "context_cap": cfg.context_cap,
        "coverage": {"observed": len(records), "included": len(included),
                     "excluded": len(records) - len(included)},
        "alignments": [asdict(r) for r in records],
        "keep_subset": keep, "controls": None, "scores": {}, "complete": False,
        "note": "f*, medians and the H-E9 verdict travel only through summarize_e9 and a numbered entry",
    }
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.results_dir / "report.json"
    for i, hid in enumerate(included):
        stem = _stem(hid)
        s_ids, r_ids, pairs = aligned[hid]
        t0 = time.time()
        rec, controls = score_handoff(cfg, stem, s_ids, r_ids, align_dir / f"{stem}.npz",
                                      keep=hid in keep, runner=runner,
                                      controls_for=hid if i == 0 else None, pairs=pairs)
        if controls is not None:
            report["controls"] = controls
        report["scores"][hid] = rec
        report["scores"][hid]["seconds"] = time.time() - t0
        out.write_text(json.dumps(report, indent=1), encoding="utf-8")   # checkpoint per handoff
        print(f"[{i + 1}/{len(included)}] {hid}: same K "
              f"{report['scores'][hid]['same_K_r2_layer_mean']:.4f} in {report['scores'][hid]['seconds']:.0f}s")
    report["complete"] = True
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e9")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9.toml"))
    ap.add_argument("--e7-config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--check", action="store_true", help="run the gate only; read no trace, dump nothing")
    a = ap.parse_args(argv)
    cfg = load_e9_config(Path(a.config), REPO_ROOT)
    try:
        if a.check:
            assert_ready(cfg, REPO_ROOT)
            print("E9 gate: ready (entries 0019, 0023 and 0025 committed; upstream pinned and clean)")
            return 0
        out = run(cfg, load_e7_config(Path(a.e7_config), REPO_ROOT), repo_root=REPO_ROOT)
        print(f"E9 report: {out}")
        return 0
    except RuntimeError as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
