"""Entry 0033: the E9 cross arm re-scored on the kept subset with a differently calibrated mapper.

Nothing is prefilled. The 0029 run kept the stride-1 dumps (same_src, same_tgt, cross_src) of a seeded subset of
the included handoffs at home; this module runs the upstream `score_positions.py` over exactly those tensors and
0029's alignments, with the mapper under a tag (`mappers/<pair>/<tag>/k<k>`, fit upstream on more calibration
sequences), into a separate results directory. Two things make the re-score readable:

- the SAME-model arm does not depend on the mapper, so its per-token squares must reproduce 0028's home
  re-score (`results/e9/recheck/*.tokens.npz`) within 0028's tolerance -- the built-in control. The summarizer
  refuses before any cross figure is read otherwise;
- every cross figure is reported BESIDE 0029's cross figure on the same handoffs, computed here by the same
  arithmetic from 0028's recheck record, never read from a summary.

Descriptive: the H-E9 cell (0029) does not move; no band is read against a rule here. Verbs, per house style:
`run` writes `results/<dir>/report.json`; `summarize` recomputes and refuses (ValueError) on any disagreement.
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9RescoreConfig, load_e9_config, load_e9_rescore_config
from linear_ceiling.e7_stats import quantile, summary
from linear_ceiling.e9 import UPSTREAM_PATHS, _stem, dump_fingerprint
from linear_ceiling.e9_pertoken import band_outcome, bootstrap_median_interval, centered_delta, f_star, token_mean
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file
from linear_ceiling.rng import make_rng
from linear_ceiling.upstream_gate import check_upstream

REQUIRED_ENTRIES = ("### 0019 ", "### 0023 ", "### 0025 ", "### 0027 ", "### 0029 ")
KEPT = ("same_src", "same_tgt", "cross_src")
SAME_ARMS = ("same_K", "same_V", "ref_K", "ref_V")     # mapper-independent: the control
CROSS_ARMS = ("cross_K", "cross_V")
_SUM_TOL = 1e-5          # as summarize_e9: per-token float32 squares vs the float64 SSE they sum to
_RESCORE_RTOL = 1e-2     # entry 0028: per-square tolerance for a re-score on another BLAS reduction order
_R2_TOL = 1e-6


def mapper_path(cfg: E9RescoreConfig) -> Path:
    return cfg.upstream_path / "mappers" / cfg.pair / cfg.mapper_tag / f"k{cfg.mapper_k}"


def mapper_fingerprint(cfg: E9RescoreConfig) -> dict:
    m = mapper_path(cfg)
    out = {}
    for suf in (".json", ".safetensors"):
        p = m.with_suffix(suf)
        if not p.exists():
            raise RuntimeError(f"E9 rescore REFUSED: mapper artifact {p} missing (upstream fit_mapper.py --tag {cfg.mapper_tag})")
        out[suf.lstrip(".")] = sha256_file_bytes(p)
    return {"tag": cfg.mapper_tag, "k": cfg.mapper_k, "path": f"mappers/{cfg.pair}/{cfg.mapper_tag}/k{cfg.mapper_k}", "files": out}


def assert_ready(cfg: E9RescoreConfig, repo_root: Path) -> None:
    entry = f"### {cfg.amendment['entry']} "
    for rel in ("ledger/ledger.md", cfg.config_path.resolve().relative_to(Path(repo_root).resolve()).as_posix(),
                "config/e9.toml"):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=repo_root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=repo_root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"E9 rescore REFUSED: {rel} is not committed as-is")
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=repo_root,
                               capture_output=True, text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("E9 rescore REFUSED: cannot read HEAD:ledger/ledger.md")
    for marker in REQUIRED_ENTRIES + (entry,):
        if marker not in committed.stdout:
            raise RuntimeError(f"E9 rescore REFUSED: committed ledger has no entry {marker.strip('# ').strip()}")
    if not (cfg.prior_results_dir / "report.json").exists():
        raise RuntimeError(f"E9 rescore REFUSED: prior report {cfg.prior_results_dir / 'report.json'} missing")
    mapper_fingerprint(cfg)
    check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 rescore")


def run_upstream(cfg: E9RescoreConfig, args: list[str], runner=subprocess.run) -> None:
    py = cfg.upstream_path / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        py = cfg.upstream_path / ".venv" / "bin" / "python"
    if not py.exists():
        raise RuntimeError(f"E9 rescore REFUSED: no upstream interpreter under {cfg.upstream_path / '.venv'}")
    r = runner([str(py)] + args, cwd=str(cfg.upstream_path), capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace") if isinstance(r.stderr, bytes) else str(r.stderr)
        raise RuntimeError(f"E9 rescore REFUSED: upstream {args[0]} failed: {err[-2000:]}")


def kept_handoffs(prior: dict) -> dict:
    out = {hid: rec for hid, rec in (prior.get("scores") or {}).items() if "kept_dumps" in rec}
    if not out:
        raise RuntimeError("E9 rescore REFUSED: the prior report records no kept dumps")
    return out


def _check_kept(cfg: E9RescoreConfig, hid: str, rec: dict) -> Path:
    hdir = cfg.prior_results_dir / rec["kept_dir"]
    for name in KEPT:
        fp = rec["kept_dumps"].get(name)
        if not fp or dump_fingerprint(hdir / name) != fp:
            raise RuntimeError(f"E9 rescore REFUSED: {hid}: kept dump {name} does not match the fingerprint 0029 recorded")
    return hdir


def run(cfg: E9RescoreConfig, *, repo_root: Path = REPO_ROOT, runner=subprocess.run) -> Path:
    assert_ready(cfg, repo_root)
    prior_path = cfg.prior_results_dir / "report.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    mapper = mapper_path(cfg)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    (cfg.results_dir / "scores").mkdir(exist_ok=True)
    (cfg.results_dir / "tokens").mkdir(exist_ok=True)
    scores = {}
    for hid, rec in kept_handoffs(prior).items():
        hdir = _check_kept(cfg, hid, rec)
        pairs = cfg.prior_results_dir / "align" / f"{_stem(hid)}.npz"
        if not pairs.exists():
            raise RuntimeError(f"E9 rescore REFUSED: {hid}: alignment {pairs} missing")
        out, out_tok = cfg.results_dir / "scores" / f"{_stem(hid)}.json", cfg.results_dir / "tokens" / f"{_stem(hid)}.tokens.npz"
        run_upstream(cfg, ["scripts/score_positions.py",
                           "--same-src", str((hdir / "same_src").resolve()), "--same-tgt", str((hdir / "same_tgt").resolve()),
                           "--cross-src", str((hdir / "cross_src").resolve()), "--mapper", str(mapper),
                           "--pairs", str(pairs.resolve()), "--out", str(out.resolve()), "--per-token", str(out_tok.resolve())], runner)
        if not out.exists() or not out_tok.exists():
            raise RuntimeError(f"E9 rescore REFUSED: {hid}: score_positions wrote nothing")
        body = json.loads(out.read_text(encoding="utf-8"))
        scores[hid] = {"score_file": out.name, "score_sha256": sha256_file_bytes(out),
                       "tokens_file": out_tok.name, "tokens_sha256": sha256_file_bytes(out_tok),
                       "n_pairs": int(body["n_pairs"]), "pairs_sha256": sha256_file_bytes(pairs),
                       "kept_dumps": rec["kept_dumps"],
                       **{f"{a}_r2_layer_mean": float(body[f"{a}_r2_layer_mean"]) for a in SAME_ARMS[:2] + CROSS_ARMS}}
    report = {"config_sha256": sha256_text_file(cfg.config_path), "upstream_sha": cfg.upstream_sha, "pair": cfg.pair,
              "amendment": dict(cfg.amendment), "mapper": mapper_fingerprint(cfg),
              "prior": {"report": _rel(prior_path), "sha256": sha256_file_bytes(prior_path),
                        "upstream_sha": prior.get("upstream_sha")},
              "scores": scores,
              "note": ("entry {e}: the 0029 cross arm re-scored on the kept subset with a differently calibrated mapper; "
                       "DESCRIPTIVE, the H-E9 cell does not move; same-model squares are a control against 0028's "
                       "re-score").format(e=cfg.amendment["entry"])}
    rp = cfg.results_dir / "report.json"
    rp.write_text(json.dumps(report, indent=1), encoding="utf-8")
    return rp


def _rel(p: Path) -> str:
    p, r = Path(p).resolve(), Path(REPO_ROOT).resolve()
    return p.relative_to(r).as_posix() if str(p).startswith(str(r)) else str(p).replace("\\", "/")


def _sst(body: dict, part: str, key: str) -> np.ndarray:
    return np.asarray([layer["sst"] for layer in body[part][key]], dtype=np.float64)


def _load_npz(path: Path, want_sha: str | None, who: str) -> dict:
    if not path.exists() or (want_sha is not None and sha256_file_bytes(path) != want_sha):
        raise ValueError(f"{who}: per-token file {path.name} missing or off-hash")
    with np.load(path) as z:
        return {k: z[k] for k in z.files}


def _check_sums(body: dict, tok: dict, n: int, who: str) -> None:
    for arm in SAME_ARMS[:2] + CROSS_ARMS:
        part, key = arm.split("_")
        if arm not in tok:
            raise ValueError(f"{who}: per-token record lacks {arm}")
        arr = np.asarray(tok[arm], dtype=np.float64)
        sse = np.asarray([layer["sse"] for layer in body[part][key]], dtype=np.float64)
        if arr.shape != (n,) + sse.shape or not np.isfinite(arr).all() or (arr < 0).any():
            raise ValueError(f"{who}: {arm} has the wrong shape or a non-finite/negative square")
        if not np.allclose(arr.sum(0), sse, rtol=_SUM_TOL, atol=0):
            raise ValueError(f"{who}: {arm} per-token squares do not sum to the recorded SSE")


def _same_arm_control(prior_tok: dict, mine: dict, who: str) -> dict:
    """The mapper-independent arms must reproduce 0028's home re-score: shapes equal, per-head sums within
    _SUM_TOL, every square within _RESCORE_RTOL relative. Refuses otherwise; returns the agreement figures."""
    out = {}
    for arm in SAME_ARMS:
        if arm not in prior_tok or arm not in mine:
            raise ValueError(f"{who}: control record lacks {arm}")
        a, b = np.asarray(prior_tok[arm], dtype=np.float64), np.asarray(mine[arm], dtype=np.float64)
        if a.shape != b.shape:
            raise ValueError(f"{who}: same-arm control FAILED on {arm}: shape {b.shape} vs 0028's {a.shape}")
        if not np.allclose(b.sum(0), a.sum(0), rtol=_SUM_TOL, atol=0):
            raise ValueError(f"{who}: same-arm control FAILED on {arm}: per-head sums beyond {_SUM_TOL:.0e} relative of 0028's")
        if not np.allclose(b, a, rtol=_RESCORE_RTOL, atol=0):
            raise ValueError(f"{who}: same-arm control FAILED on {arm}: a square beyond {_RESCORE_RTOL:.0e} relative of 0028's")
        rel = np.abs(a - b) / np.maximum(np.abs(a), 1e-300)
        out[arm] = {"max_rel_square": float(rel.max()), "bit_identical_frac": float((a == b).mean())}
    return out


def _tau_key(t: float) -> str:
    return f"{float(t):.4g}"


def summarize(cfg: E9RescoreConfig, *, repo_root: Path = REPO_ROOT) -> dict:
    rp = cfg.results_dir / "report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; the re-score has not run")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    if rep.get("config_sha256") != sha256_text_file(cfg.config_path):
        raise ValueError("config changed since the run (config_sha256 mismatch)")
    if rep.get("upstream_sha") != cfg.upstream_sha:
        raise ValueError("report's upstream_sha differs from config; the pin moved")
    try:
        check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 rescore summary")
        mine_fp = mapper_fingerprint(cfg)
    except RuntimeError as e:
        raise ValueError(str(e)) from e
    if rep.get("mapper") != mine_fp:
        raise ValueError("mapper artifacts do not match the fingerprint recorded at run time")
    prior_path = cfg.prior_results_dir / "report.json"
    if not prior_path.exists() or sha256_file_bytes(prior_path) != (rep.get("prior") or {}).get("sha256"):
        raise ValueError("the prior (0029) report is missing or changed since the run")
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    kept = kept_handoffs(prior)
    if set(rep.get("scores") or {}) != set(kept):
        raise ValueError("re-scored handoffs are not exactly the prior report's kept subset")
    # tau under the tagged mapper: the E8 report scored with the SAME tagged artifact, verified by its own
    # summarizer against the upstream r2.json; tau_K(tag) = 1 - its arm (a) K figure at the compared k.
    if not cfg.e8_report.exists():
        raise ValueError(f"{cfg.e8_report} missing: the tagged mapper's held-out figure has not been recorded by E8")
    e8 = json.loads(cfg.e8_report.read_text(encoding="utf-8"))
    e8m = e8.get("mapper") or {}
    if e8m.get("tag") != cfg.mapper_tag or (e8m.get("files") or {}).get(str(cfg.mapper_k)) != mine_fp["files"]:
        raise ValueError("the E8 report was not scored with this mapper (tag or artifact bytes differ)")
    e8_generic = e8["per_k"][str(cfg.mapper_k)]["generic"]
    tau_tag = {"K": 1.0 - float(e8_generic["K"]), "V": 1.0 - float(e8_generic["V"])}
    rule = load_e9_config(Path(repo_root) / "config" / "e9.toml", repo_root).rule
    tau_reg = {"K": float(rule["tau_K"]), "V": float(rule["tau_V"])}
    tau_agent = float(rule["tau_agent_K"])
    ladder = [float(t) for t in rule["tau_ladder"]]

    per = {}
    control = {}
    for hid in sorted(kept):
        rec, prec = rep["scores"][hid], kept[hid]
        who = hid
        _check_kept_or_raise(cfg, hid, prec)
        sp, tp = cfg.results_dir / "scores" / rec["score_file"], cfg.results_dir / "tokens" / rec["tokens_file"]
        if not sp.exists() or sha256_file_bytes(sp) != rec["score_sha256"]:
            raise ValueError(f"{who}: score file missing or off-hash")
        body = json.loads(sp.read_text(encoding="utf-8"))
        if body.get("per_token", {}).get("sha256") != rec["tokens_sha256"]:
            raise ValueError(f"{who}: score file and report disagree on the per-token file hash")
        tok = _load_npz(tp, rec["tokens_sha256"], who)
        n = int(body["n_pairs"])
        pairs = cfg.prior_results_dir / "align" / f"{_stem(hid)}.npz"
        if n != rec["n_pairs"] or n != int(prec["n_pairs"]) or sha256_file_bytes(pairs) != rec["pairs_sha256"]:
            raise ValueError(f"{who}: n_pairs or the alignment file differ from the record")
        _check_sums(body, tok, n, who)
        for a in SAME_ARMS[:2] + CROSS_ARMS:
            if abs(float(body[f"{a}_r2_layer_mean"]) - float(rec[f"{a}_r2_layer_mean"])) > _R2_TOL:
                raise ValueError(f"{who}: {a} layer-mean R^2 in the score file differs from the report")
        # the control: 0028's home re-score of the same tensors under the n = 50 mapper
        ptp = cfg.prior_results_dir / "recheck" / f"{_stem(hid)}.tokens.npz"
        psp = cfg.prior_results_dir / "recheck" / f"{_stem(hid)}.json"
        if not ptp.exists() or not psp.exists():
            raise ValueError(f"{who}: 0028's recheck record missing; the same-arm control cannot be formed")
        ptok = _load_npz(ptp, None, who)
        pbody = json.loads(psp.read_text(encoding="utf-8"))
        control[hid] = _same_arm_control(ptok, tok, who)
        # cross figures, this mapper vs 0029's, by the same arithmetic on both records
        row = {"n_pairs": n, "bridge_r2": {a: float(body[f"{a}_r2_layer_mean"]) for a in SAME_ARMS[:2] + CROSS_ARMS},
               "prior_bridge_r2": {a: float(pbody[f"{a}_r2_layer_mean"]) for a in SAME_ARMS[:2] + CROSS_ARMS}}
        for arm in CROSS_ARMS:
            part, key = arm.split("_")
            dt = token_mean(centered_delta(tok[arm], _sst(body, part, key), n))
            pdt = token_mean(centered_delta(ptok[arm], _sst(pbody, part, key), n))
            row[arm] = {"fstar_tau_reg": f_star(dt, tau_reg[key]), "fstar_tau_tag": f_star(dt, tau_tag[key]),
                        "prior_fstar_tau_reg": f_star(pdt, tau_reg[key]),
                        "ladder": {_tau_key(t): f_star(dt, t) for t in ladder},
                        "prior_ladder": {_tau_key(t): f_star(pdt, t) for t in ladder},
                        "median_delta": float(np.median(dt)), "prior_median_delta": float(np.median(pdt))}
            if key == "K":
                row[arm]["fstar_tau_agent"] = f_star(dt, tau_agent)
                row[arm]["prior_fstar_tau_agent"] = f_star(pdt, tau_agent)
        per[hid] = row

    hids = sorted(per)
    def stat(fn):
        return summary([fn(per[h]) for h in hids])
    rng = make_rng(int(cfg.amendment["bootstrap_seed"]))
    reps = int(cfg.amendment["bootstrap_reps"])
    agg = {"n_handoffs": len(hids), "tau": {"registered_0023": tau_reg, "tagged_mapper": tau_tag, "agent_K_0025": tau_agent},
           "cross_K": {"fstar_tau_reg": stat(lambda r: r["cross_K"]["fstar_tau_reg"]),
                       "fstar_tau_tag": stat(lambda r: r["cross_K"]["fstar_tau_tag"]),
                       "prior_fstar_tau_reg": stat(lambda r: r["cross_K"]["prior_fstar_tau_reg"]),
                       "fstar_tau_agent": stat(lambda r: r["cross_K"]["fstar_tau_agent"]),
                       "prior_fstar_tau_agent": stat(lambda r: r["cross_K"]["prior_fstar_tau_agent"]),
                       "bootstrap_median_fstar_tau_reg": bootstrap_median_interval(
                           [per[h]["cross_K"]["fstar_tau_reg"] for h in hids], rng, reps, quantile),
                       "band_word_descriptive": {"tau_reg": band_outcome(stat(lambda r: r["cross_K"]["fstar_tau_reg"])["median"], rule),
                                                 "tau_tag": band_outcome(stat(lambda r: r["cross_K"]["fstar_tau_tag"])["median"], rule)}},
           "cross_V": {"fstar_tau_reg": stat(lambda r: r["cross_V"]["fstar_tau_reg"]),
                       "fstar_tau_tag": stat(lambda r: r["cross_V"]["fstar_tau_tag"]),
                       "prior_fstar_tau_reg": stat(lambda r: r["cross_V"]["prior_fstar_tau_reg"])},
           "bridge_r2": {a: stat(lambda r, a=a: r["bridge_r2"][a]) for a in SAME_ARMS[:2] + CROSS_ARMS},
           "prior_bridge_r2": {a: stat(lambda r, a=a: r["prior_bridge_r2"][a]) for a in SAME_ARMS[:2] + CROSS_ARMS},
           "ladder": {_tau_key(t): {"cross_K": stat(lambda r, t=t: r["cross_K"]["ladder"][_tau_key(t)]),
                                    "prior_cross_K": stat(lambda r, t=t: r["cross_K"]["prior_ladder"][_tau_key(t)])} for t in ladder},
           "same_arm_control": {arm: {"max_rel_square": max(control[h][arm]["max_rel_square"] for h in hids),
                                      "min_bit_identical_frac": min(control[h][arm]["bit_identical_frac"] for h in hids)}
                                for arm in SAME_ARMS}}
    figures = {"amendment": rep["amendment"], "mapper": rep["mapper"], "prior": rep["prior"],
               "e8_report": {"path": _rel(cfg.e8_report), "sha256": sha256_file_bytes(cfg.e8_report)},
               "aggregate": agg, "per_handoff": per, "control_per_handoff": control,
               "note": ("DESCRIPTIVE (entry {e}): the H-E9 cell (0029) does not move; f* is an oracle floor (0027); "
                        "the kept subset is 0025's seeded draw, not the included set").format(e=cfg.amendment["entry"])}
    (cfg.results_dir / "summary.json").write_text(json.dumps(figures, indent=1), encoding="utf-8")
    (cfg.results_dir / "summary.md").write_text(_md(cfg, figures), encoding="utf-8")
    return figures


def _check_kept_or_raise(cfg: E9RescoreConfig, hid: str, rec: dict) -> None:
    try:
        _check_kept(cfg, hid, rec)
    except RuntimeError as e:
        raise ValueError(str(e)) from e


def _md(cfg: E9RescoreConfig, f: dict) -> str:
    a = f["aggregate"]
    def fmt(s):
        return f"{s['median']:.4f} (p10 {s['p10']:.4f}, p90 {s['p90']:.4f}; n {s['n']})"
    t = a["tau"]
    ck, cv = a["cross_K"], a["cross_V"]
    lines = [f"E9 kept-subset re-score (entry {f['amendment']['entry']}), mapper {f['mapper']['path']} -- DESCRIPTIVE; the H-E9 cell does not move",
             "",
             f"- handoffs: {a['n_handoffs']} (0025's kept draw); upstream {cfg.upstream_sha[:12]}; same-arm control PASSED on every handoff "
             f"(max relative square vs 0028's re-score: " + ", ".join(f"{arm} {v['max_rel_square']:.2e}" for arm, v in a["same_arm_control"].items()) + ")",
             f"- tau_K registered (0023) {t['registered_0023']['K']:.4f}; tau_K under this mapper {t['tagged_mapper']['K']:.4f}; tau_agent_K (0025) {t['agent_K_0025']:.4f}",
             f"- cross K f*(tau_K 0023): this mapper {fmt(ck['fstar_tau_reg'])} vs 0029's mapper on the same handoffs {fmt(ck['prior_fstar_tau_reg'])}",
             f"- cross K f*(tau_K of this mapper): {fmt(ck['fstar_tau_tag'])}",
             f"- cross K f*(tau_agent_K): this mapper {fmt(ck['fstar_tau_agent'])} vs 0029's {fmt(ck['prior_fstar_tau_agent'])}",
             f"- cross V f*(tau_V 0023): this mapper {fmt(cv['fstar_tau_reg'])} vs 0029's {fmt(cv['prior_fstar_tau_reg'])}",
             f"- bridge R^2 cross K: this mapper {fmt(a['bridge_r2']['cross_K'])} vs 0029's {fmt(a['prior_bridge_r2']['cross_K'])}; "
             f"same K (control, mapper-independent) {fmt(a['bridge_r2']['same_K'])} vs {fmt(a['prior_bridge_r2']['same_K'])}",
             f"- band word, descriptive only (0023's edges): tau_K {ck['band_word_descriptive']['tau_reg']} / tau_K(this mapper) {ck['band_word_descriptive']['tau_tag']}",
             f"- bootstrap of the median cross-K f*(tau_K), seed {ck['bootstrap_median_fstar_tau_reg'].get('seed', cfg.amendment['bootstrap_seed'])}: "
             f"{ck['bootstrap_median_fstar_tau_reg']}",
             "", "| tau (ladder) | cross K f*, this mapper | cross K f*, 0029's mapper |", "|---|---|---|"]
    for key, row in a["ladder"].items():
        lines.append(f"| {key} | {fmt(row['cross_K'])} | {fmt(row['prior_cross_K'])} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.e9_rescore")
    ap.add_argument("mode", choices=["check", "run", "summarize"])
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9c.toml"))
    a = ap.parse_args(argv)
    cfg = load_e9_rescore_config(Path(a.config), REPO_ROOT)
    try:
        if a.mode == "check":
            assert_ready(cfg, REPO_ROOT)
            print(f"E9 rescore ready: mapper {cfg.mapper_tag}/k{cfg.mapper_k}, upstream {cfg.upstream_sha[:12]}, entries "
                  f"{', '.join(m.strip('# ').strip() for m in REQUIRED_ENTRIES)} + {cfg.amendment['entry']}")
        elif a.mode == "run":
            print(run(cfg))
        else:
            f = summarize(cfg)
            print((cfg.results_dir / "summary.md").read_text(encoding="utf-8"))
            print(f"wrote {cfg.results_dir / 'summary.json'}")
    except (RuntimeError, ValueError) as e:
        msg = str(e)
        print(msg if msg.startswith("E9 rescore REFUSED") else f"E9 rescore REFUSED: {msg}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
