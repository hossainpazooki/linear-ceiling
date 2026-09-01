"""E9 driver and its gate -- the achievable fraction at a re-rendered handoff (ledger entry 0019).

`assert_ready` refuses until ledger/ledger.md (with entry 0019) and config/e9.toml are
committed unmodified, and the upstream pin holds for every invoked path (ancestor +
paths-unchanged + clean, `upstream_gate`). The upstream is called by subprocess in its own
environment; this module never imports kvt.

Per included handoff (|S| and |R| within the context cap; the rest EXCLUDED and counted):
three stride-1 single-sequence dumps with the upstream's `dump_kv.py` (receiver on S, receiver
on R, source on S), then `score_positions.py` over the aligned position pairs -> per-layer,
per-head SSE/SST and R² for E9-same and E9-cross. Dumps are deleted after scoring except for
the seeded keep-subset, whose dumps are fingerprinted so a CPU summarizer can recompute those
R² from tensors. The report is checkpointed after every handoff, so a reclaimed GPU box loses
one handoff, not the run.

The driver states band outcomes for nothing: medians and the H-E9 verdict travel only through
`summarize_e9` and a numbered entry.
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
from linear_ceiling.e8 import upstream_python
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.pairs import pair_models
from linear_ceiling.rng import make_rng
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import snapshot

REQUIRED_ENTRIES = ("### 0019 ",)
UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_positions.py", "kvt")


def assert_ready(cfg: E9Config, repo_root: Path) -> None:
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"E9 REFUSED: {rel} is not committed as-is; entry 0019 and config/e9.toml "
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


def score_handoff(cfg: E9Config, stem: str, s_ids: np.ndarray, r_ids: np.ndarray, pairs_npz: Path,
                  *, keep: bool, runner=subprocess.run) -> dict:
    """Three dumps -> score_positions -> score dict; dumps deleted unless keep."""
    hdir = cfg.scratch_dir / stem
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
    score_path = cfg.results_dir / "scores" / f"{stem}.json"
    mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{cfg.mapper_k}"
    run_upstream(cfg, ["scripts/score_positions.py",
                       "--same-src", str((hdir / "same_src").resolve()),
                       "--same-tgt", str((hdir / "same_tgt").resolve()),
                       "--cross-src", str((hdir / "cross_src").resolve()),
                       "--mapper", str(mapper), "--pairs", str(pairs_npz.resolve()),
                       "--out", str(score_path.resolve())], runner)
    if not score_path.exists():
        raise RuntimeError(f"E9 REFUSED: score_positions wrote nothing to {score_path}")
    rec = {"score_file": score_path.name, "score_sha256": sha256_file_bytes(score_path)}
    body = json.loads(score_path.read_text(encoding="utf-8"))
    for key in ("n_pairs", "same_K_r2_layer_mean", "same_V_r2_layer_mean",
                "cross_K_r2_layer_mean", "cross_V_r2_layer_mean"):
        rec[key] = body[key]
    if keep:
        rec["kept_dumps"] = {name: dump_fingerprint(hdir / name) for name in dumps}
        rec["kept_dir"] = hdir.resolve().relative_to(cfg.results_dir.resolve()).as_posix()
    else:
        shutil.rmtree(hdir, ignore_errors=True)
    return rec


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
            aligned[h.handoff_id] = (s_ids, r_ids)
    included = sorted(aligned)
    keep = keep_subset(included, cfg.keep_seed, cfg.keep_n)
    report = {
        "config_sha256": sha256_file_bytes(cfg.config_path),
        "upstream_sha": cfg.upstream_sha, "pair": cfg.pair,
        "alignment_method": cfg.alignment_method, "context_cap": cfg.context_cap,
        "coverage": {"observed": len(records), "included": len(included),
                     "excluded": len(records) - len(included)},
        "alignments": [asdict(r) for r in records],
        "keep_subset": keep, "scores": {}, "complete": False,
        "note": "medians and the H-E9 verdict travel only through summarize_e9 and a numbered entry",
    }
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    out = cfg.results_dir / "report.json"
    for i, hid in enumerate(included):
        stem = _stem(hid)
        s_ids, r_ids = aligned[hid]
        t0 = time.time()
        report["scores"][hid] = score_handoff(cfg, stem, s_ids, r_ids,
                                              align_dir / f"{stem}.npz", keep=hid in keep, runner=runner)
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
            print("E9 gate: ready (entry 0019 committed; upstream pinned and clean)")
            return 0
        out = run(cfg, load_e7_config(Path(a.e7_config), REPO_ROOT), repo_root=REPO_ROOT)
        print(f"E9 report: {out}")
        return 0
    except RuntimeError as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
