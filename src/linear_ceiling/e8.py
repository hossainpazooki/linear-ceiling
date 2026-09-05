"""E8 driver and its gate -- transfer under the agent-trace distribution shift (entries 0009, 0016).

`assert_ready` refuses (before any text is read or any dump written) unless: ledger/ledger.md
and config/e8.toml are committed unmodified; the COMMITTED ledger carries entries 0009 and
0016; the upstream checkout's HEAD equals `upstream_sha` from config and its tree is clean for
every path E8 invokes. The upstream is called by subprocess in its own environment -- this
module never imports kvt (UPSTREAM.md).

The run: sample + tokenize agent text (0016 §4) -> dump source and target KV over it with the
upstream's `dump_kv.py` (same stride as arm (a)) -> score every reported mapper on BOTH arms
with the upstream's `score_mapper.py` -> cross-check arm (a) against the archived `r2.json`
(refuse on disagreement) -> write results/e8/report.json. The band outcome is stated for the
verdict k; the verdict on H-E8 is a numbered entry's.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E7Config, E8Config, load_e7_config, load_e8_config
from linear_ceiling.e8_text import iter_trace_texts, qwen_encoder, sample_windows, write_tokens
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.pairs import pair_models
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import WeightReader, assert_shared_vocab, snapshot

REQUIRED_ENTRIES = ("### 0009 ", "### 0016 ")


def required_entries(cfg: E8Config) -> tuple[str, ...]:
    """0009 + 0016 always; an amendment run also requires its own registering entry (e.g. 0030)."""
    return REQUIRED_ENTRIES + ((f"### {cfg.amendment['entry']} ",) if cfg.amendment else ())


def agent_holdout_frac(cfg: E8Config) -> float:
    return cfg.holdout_frac if cfg.agent_holdout_frac is None else cfg.agent_holdout_frac
UPSTREAM_PATHS = ("scripts/dump_kv.py", "scripts/score_mapper.py", "kvt")
_TOL = 1e-6


def upstream_python(upstream: Path) -> Path:
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        p = Path(upstream) / rel
        if p.exists():
            return p
    raise RuntimeError(f"E8 REFUSED: no interpreter under {upstream}/.venv; the upstream runs in its own environment")


def assert_ready(cfg: E8Config, repo_root: Path) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", cfg.upstream_sha):
        raise RuntimeError(f"E8 REFUSED: {cfg.config_path.name} upstream_sha is not a commit sha; the re-pin "
                           "must be recorded before any dump is generated")
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix()):  # noqa: E501
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"E8 REFUSED: {rel} is not committed as-is; entry 0016 and config/e8.toml "
                               "must be committed before any text is read")
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=repo_root,
                               capture_output=True, text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("E8 REFUSED: cannot read HEAD:ledger/ledger.md")
    for marker in required_entries(cfg):
        if marker not in committed.stdout:
            raise RuntimeError(f"E8 REFUSED: committed ledger has no entry {marker.strip('# ').strip()}")
    # Ancestor + paths-unchanged, not HEAD equality: a later experiment's re-pin must not make
    # E8 refuse while E8's own invoked tools are still the pinned bytes.
    check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E8")


def band_outcome(drop: float, band: dict) -> str:
    if drop <= band["holds_max_drop"]:
        return "HOLDS"
    if drop >= band["degrades_min_drop"]:
        return "DEGRADES"
    return "UNRESOLVED"


def run_upstream(cfg: E8Config, args: list[str], runner=subprocess.run) -> None:
    cmd = [str(upstream_python(cfg.upstream_path)), *args]
    r = runner(cmd, cwd=str(cfg.upstream_path), capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace") if isinstance(r.stderr, bytes) else str(r.stderr)
        raise RuntimeError(f"E8 REFUSED: upstream command failed ({' '.join(args[:2])}):\n{err[-2000:]}")


def dump_agent(cfg: E8Config, tokens_path: Path, runner=subprocess.run) -> dict[str, Path]:
    out = {}
    for which in ("source", "target"):
        d = cfg.agent_dumps / which
        run_upstream(cfg, ["scripts/dump_kv.py", "--pair", cfg.pair, "--which", which,
                           "--tokens", str(tokens_path.resolve()), "--stride", str(cfg.stride),
                           "--out", str(d.resolve())], runner)
        if not (d / "meta.json").exists():
            raise RuntimeError(f"E8 REFUSED: dump did not produce {d / 'meta.json'}")
        out[which] = d
    return out


def score(cfg: E8Config, k: int, src: Path, tgt: Path, out: Path, runner=subprocess.run, *,
          holdout_frac: float | None = None, per_token: Path | None = None) -> dict:
    """One score_mapper call. `holdout_frac` defaults to the config's arm (a) fraction; the amendment
    passes arm (b)'s (1.0 = every agent sequence) and a `--per-token` path for the per-sequence record."""
    mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{k}"
    if not mapper.with_suffix(".safetensors").exists():
        raise RuntimeError(f"E8 REFUSED: no fitted mapper at {mapper} (upstream artifact, gitignored)")
    frac = cfg.holdout_frac if holdout_frac is None else holdout_frac
    args = ["scripts/score_mapper.py", "--mapper", str(mapper), "--src", str(Path(src).resolve()),
            "--tgt", str(Path(tgt).resolve()), "--holdout-frac", str(frac), "--out", str(Path(out).resolve())]
    if per_token is not None:
        Path(per_token).parent.mkdir(parents=True, exist_ok=True)
        args += ["--per-token", str(Path(per_token).resolve())]
    run_upstream(cfg, args, runner)
    if not Path(out).exists() or (per_token is not None and not Path(per_token).exists()):
        raise RuntimeError(f"E8 REFUSED: score_mapper wrote nothing to {out}")
    return json.loads(Path(out).read_text(encoding="utf-8"))


def archived_r2(cfg: E8Config, k: int) -> dict:
    p = cfg.upstream_path / "results" / "mapper" / cfg.pair / "r2.json"
    if not p.exists():
        raise RuntimeError(f"E8 REFUSED: archived {p} missing; arm (a) has nothing to cross-check against")
    d = json.loads(p.read_text(encoding="utf-8"))
    try:
        return d["k"][str(k)]
    except KeyError as e:
        raise RuntimeError(f"E8 REFUSED: archived r2.json has no k={k}") from e


def dump_fingerprint(d: Path) -> dict[str, str]:
    """sha256 of every file in a dump directory, keyed by relative path."""
    d = Path(d)
    return {p.relative_to(d).as_posix(): sha256_file_bytes(p) for p in sorted(d.rglob("*")) if p.is_file()}


def crosscheck(k: int, recomputed: dict, archived: dict) -> dict:
    row = {}
    for key in ("K_r2_heldout_layer_mean", "V_r2_heldout_layer_mean"):
        a, b = float(archived[key]), float(recomputed[key])
        if abs(a - b) > _TOL * max(1.0, abs(a), abs(b)):
            raise RuntimeError(f"E8 REFUSED: arm (a) k={k} {key} recomputed {b} != archived {a}; the archived "
                               "dumps or mapper are not what r2.json describes")
        row[key] = {"archived": a, "recomputed": b}
    return row


def _rel(p: Path) -> str:
    p = Path(p).resolve()
    r = Path(REPO_ROOT).resolve()
    return p.relative_to(r).as_posix() if str(p).startswith(str(r)) else str(p).replace("\\", "/")


def assemble(cfg: E8Config, tokens_path: Path, dumps: dict, scores: dict, checks: dict,
             prior_ref: dict | None = None, per_token: dict | None = None) -> dict:
    per_k = {}
    for k in cfg.report_k:
        g, a = scores[("generic", k)], scores[("agent", k)]
        row = {"generic": {"K": g["K_r2_heldout_layer_mean"], "V": g["V_r2_heldout_layer_mean"]},
               "agent": {"K": a["K_r2_heldout_layer_mean"], "V": a["V_r2_heldout_layer_mean"]}}
        row["drop"] = {"K": row["generic"]["K"] - row["agent"]["K"], "V": row["generic"]["V"] - row["agent"]["V"]}
        row["band_outcome"] = {"K": band_outcome(row["drop"]["K"], cfg.band), "V": band_outcome(row["drop"]["V"], cfg.band)}
        if cfg.amendment:
            row["holdout_frac"] = {"generic": cfg.holdout_frac, "agent": agent_holdout_frac(cfg)}
            row["n_heldout_tokens"] = {"generic": g.get("n_heldout_tokens"), "agent": a.get("n_heldout_tokens")}
            row["n_heldout_seqs"] = {"generic": g.get("n_heldout_seqs"), "agent": a.get("n_heldout_seqs")}
            row["per_sequence"] = {arm: {"seq_ids": s["per_sequence"]["seq_ids"],
                                         "K": s["per_sequence"]["K_r2_layer_mean"],
                                         "V": s["per_sequence"]["V_r2_layer_mean"]}
                                   for arm, s in (("generic", g), ("agent", a))}
            row["per_token"] = {arm: {"path": _rel(per_token[(arm, k)]), "sha256": sha256_file_bytes(per_token[(arm, k)])}
                                for arm in ("generic", "agent")}
        per_k[str(k)] = row
    manifest = tokens_path.with_suffix(".manifest.json")
    note = ("band outcomes for the verdict k, K and V separately (entry 0009 reports neither alone); the verdict on "
            "H-E8 enters by a numbered entry")
    if cfg.amendment:
        note = (f"entry {cfg.amendment['entry']}: a DESCRIPTIVE restatement of arm (b) over every agent sequence "
                "(the mapper was never fit on them); band words are read against 0009's band for orientation only; "
                "the H-E8 cell was decided by entry 0020 under the registered 0016 protocol and does not move here")
    return {
        "config_sha256": sha256_file_bytes(cfg.config_path),
        "upstream_sha": cfg.upstream_sha, "pair": cfg.pair,
        "tokens": {"path": tokens_path.resolve().relative_to(Path(REPO_ROOT).resolve()).as_posix()
                   if str(tokens_path.resolve()).startswith(str(Path(REPO_ROOT).resolve())) else str(tokens_path),
                   "sha256": sha256_file_bytes(tokens_path), "manifest_sha256": sha256_file_bytes(manifest)},
        "dumps": {arm: {which: dump_fingerprint(p) for which, p in d.items()} for arm, d in dumps.items()},
        "archived_crosscheck": checks,
        "verdict_k": cfg.verdict_k, "band": cfg.band, "per_k": per_k,
        "verdict_bearing": {"k": cfg.verdict_k, "outcome": per_k[str(cfg.verdict_k)]["band_outcome"], "note": note},
        "scope": "off-policy text for Qwen; single pair; not a real switch point; visible messages only (0012)",
        **({"amendment": dict(cfg.amendment), "reused_agent_dumps_from": prior_ref} if cfg.amendment else {}),
    }


def reuse_agent_dumps(cfg: E8Config, repo_root: Path) -> tuple[dict, Path, dict]:
    """E8 amendment: the agent dumps and token file of a prior run are reused, and must match that run's
    recorded fingerprints byte for byte -- the amendment rescores 0020's tensors, it does not resample."""
    prior_path = Path(cfg.reuse_agent_dumps_from)
    if not prior_path.exists():
        raise RuntimeError(f"E8 REFUSED: prior report {prior_path} to reuse dumps from does not exist")
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    agent = {w: cfg.agent_dumps / w for w in ("source", "target")}
    for w, p in agent.items():
        want = (prior.get("dumps") or {}).get("agent", {}).get(w)
        if not want or dump_fingerprint(p) != want:
            raise RuntimeError(f"E8 REFUSED: agent/{w} dump at {p} does not match the fingerprint recorded in {prior_path}")
    tok = prior.get("tokens") or {}
    tokens_path = Path(tok.get("path", "")) if Path(tok.get("path", "")).is_absolute() else Path(repo_root) / tok.get("path", "")
    if not tokens_path.exists() or sha256_file_bytes(tokens_path) != tok.get("sha256"):
        raise RuntimeError(f"E8 REFUSED: the prior run's agent token file is missing or changed ({tokens_path})")
    if sha256_file_bytes(tokens_path.with_suffix(".manifest.json")) != tok.get("manifest_sha256"):
        raise RuntimeError("E8 REFUSED: the prior run's token manifest changed")
    return agent, tokens_path, {"report": _rel(prior_path), "sha256": sha256_file_bytes(prior_path),
                                "upstream_sha": prior.get("upstream_sha")}


def run(cfg: E8Config, e7: E7Config, *, repo_root: Path, runner=subprocess.run) -> Path:
    assert_ready(cfg, repo_root)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    prior_ref = None
    if cfg.reuse_agent_dumps_from is not None:
        agent, tokens_path, prior_ref = reuse_agent_dumps(cfg, repo_root)
    else:
        src_id, tgt_id = pair_models(cfg.pair)
        snap_s, snap_t = snapshot(src_id), snapshot(tgt_id)
        assert_shared_vocab(WeightReader(snap_s, src_id), WeightReader(snap_t, tgt_id))
        items = list(iter_trace_texts(e7, tuple(cfg.text["suites"])))
        tokens, manifest = sample_windows(items, qwen_encoder(snap_s), cfg)
        tokens_path = write_tokens(cfg, tokens, manifest)
    generic = {w: cfg.upstream_path / cfg.generic_dumps / w for w in ("source", "target")}
    for w, p in generic.items():
        if not (p / "meta.json").exists():
            raise RuntimeError(f"E8 REFUSED: archived generic dump missing at {p} (entry 0016 §2 says it exists)")
    if cfg.reuse_agent_dumps_from is None:
        agent = dump_agent(cfg, tokens_path, runner)
    scores, checks, per_token = {}, {}, {}
    pt = (lambda arm, k: cfg.results_dir / "per_token" / f"{arm}_k{k}.npz") if cfg.amendment else (lambda arm, k: None)
    for k in cfg.report_k:
        per_token[("generic", k)] = pt("generic", k)
        scores[("generic", k)] = score(cfg, k, generic["source"], generic["target"],
                                       cfg.results_dir / "r2" / f"generic_k{k}.json", runner, per_token=per_token[("generic", k)])
        checks[str(k)] = crosscheck(k, scores[("generic", k)], archived_r2(cfg, k))
        per_token[("agent", k)] = pt("agent", k)
        scores[("agent", k)] = score(cfg, k, agent["source"], agent["target"],
                                     cfg.results_dir / "r2" / f"agent_k{k}.json", runner,
                                     holdout_frac=agent_holdout_frac(cfg), per_token=per_token[("agent", k)])
    report = assemble(cfg, tokens_path, {"generic": generic, "agent": agent}, scores, checks,
                      prior_ref=prior_ref, per_token=per_token if cfg.amendment else None)
    out = cfg.results_dir / "report.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e8")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e8.toml"))
    ap.add_argument("--e7-config", default=str(REPO_ROOT / "config" / "e7.toml"))
    ap.add_argument("--check", action="store_true", help="run the gate only; read no text, write no dump")
    a = ap.parse_args(argv)
    cfg = load_e8_config(Path(a.config), REPO_ROOT)
    try:
        if a.check:
            assert_ready(cfg, REPO_ROOT)
            ents = "/".join(m.strip("# ").strip() for m in required_entries(cfg))
            print(f"E8 gate: ready (entries {ents} committed; upstream pinned and clean)")
            return 0
        out = run(cfg, load_e7_config(Path(a.e7_config), REPO_ROOT), repo_root=REPO_ROOT)
        print(f"E8 report: {out}")
        return 0
    except RuntimeError as e:
        print(str(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
