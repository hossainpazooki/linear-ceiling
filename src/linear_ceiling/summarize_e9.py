"""Recompute every E9 figure and refuse on any disagreement (entries 0019 and 0023).

What can be recomputed on CPU is recomputed on CPU: the alignments of every handoff are
re-derived from the raw traces and compared record-for-record and array-for-array; every R² is
recomputed from the recorded per-layer, per-head SSE/SST moments; the per-token record of
every handoff is checked to SUM to those moments; the keep-subset's moments and per-token
record are recomputed from its fingerprinted tensors by re-running the upstream scorer; tau is
recomputed from the archived mapper record (`--calibrate-tau`, re-run here under the pin) and
compared with the committed calibration and with config; the two controls are checked (identity
exactly zero; the null pairing re-derived from the seed); then f*(tau), the seam and depth
profiles, delta_null, the bridge R² medians and the band outcome are computed and STATED here
for the first time, since the driver deliberately does not compute them.

What cannot be recomputed on CPU is named, not hidden: the deleted dumps. For those handoffs
the moments and per-token squares are a GPU-run record, cross-checked by the keep-subset, and
the entry that states the verdict must carry that sentence (0019).

Refuses (ValueError) on: a missing or incomplete report; config or pin drift; an alignment
that does not re-derive; a score or per-token file missing or off-hash; an R² the moments do
not reproduce; per-token squares that do not sum to the moments; a kept dump off-fingerprint
or a keep-subset re-score that disagrees; a calibration that does not reproduce; a control
that fails.

`--calibrate-tau` (0023, before any prefill): run the upstream `score_mapper.py --per-token` on
the archived k=1 mapper and generic dumps, cross-check the held-out R² against the archived
`r2.json` AND `results/e8/report.json` arm (a), verify the exact bridge (centered per-token
mean == 1 - R² per head), write `results/e9/calibration/tau.json` with tau_X = 1 - R²_X and the
labelled diagnostics 0023 records (pooled-over-heads R²; the own-norm deviation's tail; the
mapper's own f* under a median tau, which is NOT zero).
"""
import argparse
import json
import math
import subprocess
from dataclasses import asdict
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.config import E9Config, load_e7_config, load_e9_config
from linear_ceiling.e7_stats import summary
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.e9 import UPSTREAM_PATHS, _stem, dump_fingerprint, keep_subset, run_upstream, submission_dirs
from linear_ceiling.e9_align import align, load_handoffs
from linear_ceiling.e9_pertoken import (
    SEAM_BIN_EDGES, SEAM_BIN_LABELS, band_outcome, centered_delta, f_star, layer_mean, null_pairs,
    own_norm_delta, seam_bin, seam_distance, token_mean,
)
from linear_ceiling.hashing import sha256_file_bytes
from linear_ceiling.pairs import pair_models
from linear_ceiling.rng import make_rng
from linear_ceiling.upstream_gate import check_upstream
from linear_ceiling.weights import snapshot

_TOL = 1e-6
_SUM_TOL = 1e-5          # float32 per-token squares vs the float64 SSE they were summed into
_TAU_TOL = 1e-9
ARMS = ("same_K", "same_V", "cross_K", "cross_V")


def _close(a, b, tol=_TOL):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def _walk_nan(obj, path="$"):
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        raise ValueError(f"NaN/inf at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_nan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_nan(v, f"{path}[{i}]")


def _r2_from_moments(part: dict) -> dict:
    """Recompute per-layer head-mean R² and the layer mean from recorded SSE/SST."""
    out = {}
    for key in ("K", "V"):
        layers = []
        for i, layer in enumerate(part[key]):
            r2 = [1.0 - e / t for e, t in zip(layer["sse"], layer["sst"])]
            mean = float(np.mean(r2))
            if not _close(mean, layer["r2_head_mean"]):
                raise ValueError(f"{key} layer {i}: r2_head_mean {layer['r2_head_mean']} does not "
                                 f"follow from the recorded SSE/SST ({mean})")
            layers.append(mean)
        out[key] = float(np.mean(layers))
    return out


def _sst(body: dict, part: str, key: str) -> np.ndarray:
    return np.asarray([layer["sst"] for layer in body[part][key]], dtype=np.float64)       # [L, H]


def _check_tokens(body: dict, tokens: dict, n: int, who: str, arms=ARMS) -> None:
    """The per-token squares must have the recorded shape and SUM to the recorded per-head SSE."""
    for arm in arms:
        part, key = arm.split("_")
        if arm not in tokens:
            raise ValueError(f"{who}: per-token record lacks {arm}")
        arr = np.asarray(tokens[arm], dtype=np.float64)
        sse = np.asarray([layer["sse"] for layer in body[part][key]], dtype=np.float64)
        if arr.shape != (n,) + sse.shape:
            raise ValueError(f"{who}: {arm} has shape {arr.shape}, expected {(n,) + sse.shape}")
        if not np.isfinite(arr).all() or (arr < 0).any():
            raise ValueError(f"{who}: {arm} carries a non-finite or negative square")
        got = arr.sum(0)
        if not np.allclose(got, sse, rtol=_SUM_TOL, atol=0):
            worst = float(np.max(np.abs(got - sse) / np.maximum(np.abs(sse), 1e-300)))
            raise ValueError(f"{who}: {arm} per-token squares do not sum to the recorded SSE (worst rel {worst:.2e})")
    for ref in ("ref_K", "ref_V"):
        if ref not in tokens or not (np.asarray(tokens[ref]) > 0).all():
            raise ValueError(f"{who}: reference norms {ref} missing or not positive")


def _load_tokens(path: Path, want_sha: str, who: str) -> dict:
    if not path.exists() or sha256_file_bytes(path) != want_sha:
        raise ValueError(f"{who}: per-token file missing or does not match the hash recorded at run time")
    with np.load(path) as z:
        return {k: z[k] for k in z.files}


def _stats(values) -> dict:
    return summary([float(v) for v in values])


# ---------------------------------------------------------------- tau calibration (0023)

def calibrate_tau(cfg: E9Config, runner=subprocess.run, *, allow_dirty_upstream: bool = False,
                  out_dir: Path | None = None, e8_report: Path | None = None) -> dict:
    up = cfg.upstream_path
    out_dir = Path(out_dir) if out_dir else cfg.results_dir / "calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    dirty = []
    try:
        check_upstream(up, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 tau calibration")
    except RuntimeError as e:
        if not allow_dirty_upstream:
            raise ValueError(str(e)) from e
        dirty = [str(e)]
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=up, capture_output=True, text=True).stdout.strip()
    mapper = up / "mappers" / cfg.pair / f"k{cfg.mapper_k}"
    src, tgt = up / "data" / "kv" / cfg.pair / "source", up / "data" / "kv" / cfg.pair / "target"
    archived = up / "results" / "mapper" / cfg.pair / "r2.json"
    e8_report = Path(e8_report) if e8_report else Path(REPO_ROOT) / "results" / "e8" / "report.json"
    for p in (mapper.with_suffix(".json"), mapper.with_suffix(".safetensors"), src / "meta.json",
              tgt / "meta.json", archived, e8_report):
        if not p.exists():
            raise ValueError(f"tau calibration: {p} does not exist")
    e8 = json.loads(e8_report.read_text(encoding="utf-8"))
    fps = e8.get("dumps", {}).get("generic", {})
    dumps_match = {name: dump_fingerprint(d) == fps.get(name) for name, d in (("source", src), ("target", tgt))}
    if not all(dumps_match.values()):
        raise ValueError(f"tau calibration: archived generic dumps do not match the fingerprints E8 recorded ({dumps_match})")
    r2_path, pt_path = out_dir / "r2.json", out_dir / "heldout.tokens.npz"
    try:
        run_upstream(cfg, ["scripts/score_mapper.py", "--mapper", str(mapper), "--src", str(src), "--tgt", str(tgt),
                           "--holdout-frac", "0.2", "--out", str(r2_path.resolve()),
                           "--per-token", str(pt_path.resolve())], runner)
    except RuntimeError as e:
        raise ValueError(str(e)) from e
    rec = json.loads(r2_path.read_text(encoding="utf-8"))
    if rec.get("per_token", {}).get("sha256") != sha256_file_bytes(pt_path):
        raise ValueError("tau calibration: r2.json does not name the per-token file it was written with")
    arch = json.loads(archived.read_text(encoding="utf-8"))["k"][str(cfg.mapper_k)]
    e8_generic = e8["per_k"][str(cfg.mapper_k)]["generic"]
    held = {}
    for key in ("K", "V"):
        mine = rec[f"{key}_r2_heldout_layer_mean"]
        if not _close(mine, arch[f"{key}_r2_heldout_layer_mean"]) or not _close(mine, e8_generic[key]):
            raise ValueError(f"tau calibration: held-out {key} R² {mine} disagrees with the archived r2.json "
                             f"({arch[f'{key}_r2_heldout_layer_mean']}) or E8 arm (a) ({e8_generic[key]})")
        held[key] = float(mine)
    with np.load(pt_path) as z:
        tok = {k: z[k] for k in z.files}
    n = int(tok["n_heldout"])
    if n != rec["n_heldout_tokens"]:
        raise ValueError("tau calibration: per-token n disagrees with r2.json")
    diag, bridge_worst = {}, 0.0
    for key in ("K", "V"):
        sq, sst, ref = tok[f"{key}_sq"], tok[f"sst_{key}"], tok[f"ref_{key}"]
        d_c = centered_delta(sq, sst, n)
        r2_head = 1.0 - np.asarray(sq, dtype=np.float64).sum(0) / sst
        bridge_worst = max(bridge_worst, float(np.max(np.abs(d_c.mean(0) - (1.0 - r2_head)))))
        if not _close(float(r2_head.mean()), held[key], 1e-5):
            raise ValueError(f"tau calibration: per-token squares do not reproduce held-out {key} R²")
        dt = token_mean(d_c)
        own = own_norm_delta(sq, ref).mean(1)                      # layer-mean own-norm deviation per token
        tau_mean = 1.0 - held[key]
        diag[key] = {
            "tau": tau_mean,
            "centered_delta_token_mean": {"mean": float(dt.mean()), "median": float(np.median(dt)),
                                          "p90": float(np.quantile(dt, 0.9)), "p99": float(np.quantile(dt, 0.99))},
            "mapper_own_fstar": {"at_tau_mean": f_star(dt, tau_mean),
                                 "at_centered_median": f_star(dt, float(np.median(dt))),
                                 "at_own_norm_median": f_star(own, float(np.median(own)))},
            "own_norm_delta": {"median": float(np.median(own)), "mean": float(own.mean()),
                               "p90": float(np.quantile(own, 0.9)), "p99": float(np.quantile(own, 0.99)),
                               "max": float(own.max()), "frac_gt_1": float((own > 1).mean())},
            "min_ref_norm_over_layer_median": float(np.min(np.asarray(ref, dtype=np.float64).sum(2).min(0)
                                                           / np.median(np.asarray(ref, dtype=np.float64).sum(2), 0))),
            "pooled_over_heads_r2_layer_mean": float(rec[f"{key}_r2_heldout_pooled_over_heads_layer_mean"]),
            "head_averaged_r2_layer_mean": held[key],
        }
    out = {
        "pair": cfg.pair, "mapper": {"path": f"mappers/{cfg.pair}/k{cfg.mapper_k}", "k": cfg.mapper_k,
                                     "json_sha256": sha256_file_bytes(mapper.with_suffix(".json")),
                                     "safetensors_sha256": sha256_file_bytes(mapper.with_suffix(".safetensors"))},
        "archived_r2_sha256": sha256_file_bytes(archived), "e8_report_sha256": sha256_file_bytes(e8_report),
        "generic_dumps_match_e8_fingerprints": dumps_match,
        "upstream_head": head, "upstream_pin_check": "held" if not dirty else dirty[0],
        "heldout": {"n_tokens": n, "K_r2_layer_mean": held["K"], "V_r2_layer_mean": held["V"],
                    "definition": "A5 per head, averaged over heads then layers (kvt.mapper.mapper_r2)"},
        "tau": {"K": 1.0 - held["K"], "V": 1.0 - held["V"],
                "definition": "1 - held-out R^2 per read-out; the mean centered per-token deviation of the k=1 mapper"},
        "bridge_check_max_abs": bridge_worst,
        "diagnostics": diag,
        "per_token_file": pt_path.name, "per_token_sha256": sha256_file_bytes(pt_path),
        "r2_file": r2_path.name, "r2_sha256": sha256_file_bytes(r2_path),
    }
    _walk_nan(out, "tau")
    (out_dir / "tau.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def _check_calibration(cfg: E9Config, runner) -> dict:
    cal_path = cfg.results_dir / "calibration" / "tau.json"
    if not cal_path.exists():
        raise ValueError(f"{cal_path} does not exist; run `summarize_e9 --calibrate-tau` before the GPU run (0023)")
    cal = json.loads(cal_path.read_text(encoding="utf-8"))
    fresh = calibrate_tau(cfg, runner, out_dir=cfg.results_dir / "recheck" / "calibration")
    for key in ("K", "V"):
        if not _close(cal["tau"][key], fresh["tau"][key], _TAU_TOL):
            raise ValueError(f"tau_{key}: recorded calibration {cal['tau'][key]} != recomputed {fresh['tau'][key]}")
        if not _close(float(cfg.rule[f"tau_{key}"]), fresh["tau"][key], _TAU_TOL):
            raise ValueError(f"config tau_{key} {cfg.rule[f'tau_{key}']} != recomputed {fresh['tau'][key]}")
    if list(cfg.controls["seam_bins"]) != list(SEAM_BIN_EDGES):
        raise ValueError("config seam_bins differ from the registered edges (0023)")
    return fresh


# ---------------------------------------------------------------- the summary

def summarize(cfg: E9Config, runner=subprocess.run, encoder=None, e7=None) -> str:
    rp = cfg.results_dir / "report.json"
    if not rp.exists():
        raise ValueError(f"{rp} does not exist; E9 has not run")
    rep = json.loads(rp.read_text(encoding="utf-8"))
    _walk_nan(rep, "report")
    if not rep.get("complete"):
        raise ValueError("report is a per-handoff checkpoint, not a complete run; finish or rerun E9")
    if rep.get("config_sha256") != sha256_file_bytes(cfg.config_path):
        raise ValueError("config/e9.toml changed since the run (config_sha256 mismatch)")
    if rep.get("upstream_sha") != cfg.upstream_sha:
        raise ValueError("report's upstream_sha differs from config; the pin moved")
    try:
        check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 summary")
    except RuntimeError as e:
        raise ValueError(str(e)) from e
    cal = _check_calibration(cfg, runner)
    tau = {"K": float(cfg.rule["tau_K"]), "V": float(cfg.rule["tau_V"])}

    # 1. Re-derive every alignment from the raw traces and compare, records and arrays.
    e7 = e7 or load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    enc = encoder or qwen_encoder(snapshot(pair_models(cfg.pair)[0]))
    counter = lambda t, ct="assistant": 0     # noqa: E731
    handoffs = {h.handoff_id: h for h in load_handoffs(submission_dirs(e7, cfg), counter)}
    recorded = {a["handoff_id"]: a for a in rep.get("alignments") or []}
    if set(handoffs) != set(recorded):
        raise ValueError(f"handoff set differs: recomputed {len(handoffs)}, recorded {len(recorded)}")
    included, pairs_of, n_recv = [], {}, {}
    for hid, h in sorted(handoffs.items()):
        rec, s_ids, r_ids, pairs = align(h, enc, cfg.context_cap)
        if asdict(rec) != recorded[hid]:
            raise ValueError(f"{hid}: alignment record does not re-derive from the raw trace")
        if not rec.excluded:
            z = np.load(cfg.results_dir / "align" / f"{_stem(hid)}.npz")
            if not (np.array_equal(z["sender"], s_ids) and np.array_equal(z["receiver"], r_ids)
                    and np.array_equal(z["pairs"], pairs)):
                raise ValueError(f"{hid}: stored alignment arrays do not match the recomputation")
            included.append(hid)
            pairs_of[hid], n_recv[hid] = pairs, len(r_ids)
    cov = {"observed": len(handoffs), "included": len(included), "excluded": len(handoffs) - len(included)}
    if cov != rep["coverage"]:
        raise ValueError(f"coverage recomputed {cov} != recorded {rep['coverage']}")
    if keep_subset(included, cfg.keep_seed, cfg.keep_n) != rep["keep_subset"]:
        raise ValueError("keep_subset does not re-derive from the seed and the included set")
    if set(rep.get("scores") or {}) != set(included):
        raise ValueError("scored handoff set differs from the included set")

    # 2. Every R² from moments; score + per-token files by hash; squares sum to moments;
    #    kept dumps by fingerprint + re-score (moments AND per-token).
    per_handoff, tokens_of, bodies = {}, {}, {}
    for hid in included:
        rec = rep["scores"][hid]
        sf = cfg.results_dir / "scores" / rec["score_file"]
        if not sf.exists() or sha256_file_bytes(sf) != rec["score_sha256"]:
            raise ValueError(f"{hid}: score file missing or does not match the hash recorded at run time")
        body = json.loads(sf.read_text(encoding="utf-8"))
        same, cross = _r2_from_moments(body["same"]), _r2_from_moments(body["cross"])
        for label, mine in (("same", same), ("cross", cross)):
            for key in ("K", "V"):
                stored = body[f"{label}_{key}_r2_layer_mean"]
                if not _close(mine[key], stored):
                    raise ValueError(f"{hid}: {label} {key} layer mean {stored} != moments ({mine[key]})")
                if not _close(rec[f"{label}_{key}_r2_layer_mean"], stored):
                    raise ValueError(f"{hid}: report copy of {label} {key} differs from the score file")
        if body.get("per_token", {}).get("sha256") != rec["tokens_sha256"]:
            raise ValueError(f"{hid}: score file and report disagree on the per-token file hash")
        tok = _load_tokens(cfg.results_dir / "tokens" / rec["tokens_file"], rec["tokens_sha256"], hid)
        n = int(body["n_pairs"])
        if n != len(pairs_of[hid]):
            raise ValueError(f"{hid}: n_pairs {n} != alignment pairs {len(pairs_of[hid])}")
        _check_tokens(body, tok, n, hid)
        per_handoff[hid] = {"same": same, "cross": cross, "n_pairs": n}
        tokens_of[hid], bodies[hid] = tok, body
        if "kept_dumps" in rec:
            hdir = cfg.results_dir / rec["kept_dir"]
            for name, fp in rec["kept_dumps"].items():
                if dump_fingerprint(hdir / name) != fp:
                    raise ValueError(f"{hid}: kept dump {name} does not match its fingerprint")
            rdir = cfg.results_dir / "recheck"
            rdir.mkdir(parents=True, exist_ok=True)
            out, out_tok = rdir / f"{_stem(hid)}.json", rdir / f"{_stem(hid)}.tokens.npz"
            mapper = cfg.upstream_path / "mappers" / cfg.pair / f"k{cfg.mapper_k}"
            try:
                run_upstream(cfg, ["scripts/score_positions.py",
                                   "--same-src", str((hdir / "same_src").resolve()),
                                   "--same-tgt", str((hdir / "same_tgt").resolve()),
                                   "--cross-src", str((hdir / "cross_src").resolve()),
                                   "--mapper", str(mapper),
                                   "--pairs", str((cfg.results_dir / "align" / f"{_stem(hid)}.npz").resolve()),
                                   "--out", str(out.resolve()), "--per-token", str(out_tok.resolve())], runner)
            except RuntimeError as e:
                raise ValueError(str(e)) from e
            re_body = json.loads(out.read_text(encoding="utf-8"))
            for label in ("same", "cross"):
                for key in ("K", "V"):
                    if not _close(re_body[f"{label}_{key}_r2_layer_mean"], body[f"{label}_{key}_r2_layer_mean"]):
                        raise ValueError(f"{hid}: keep-subset re-score disagrees on {label} {key}")
            with np.load(out_tok) as z:
                for arm in ARMS:
                    if not np.allclose(z[arm], tok[arm], rtol=_SUM_TOL, atol=0):
                        raise ValueError(f"{hid}: keep-subset per-token re-score disagrees on {arm}")

    # 3. Controls (0023): identity exactly zero; null pairing re-derived from the seed.
    ctl = rep.get("controls")
    if not ctl or ctl["handoff_id"] not in included:
        raise ValueError("controls missing from the report, or run on a handoff that is not included")
    c_hid = ctl["handoff_id"]
    cdir = cfg.results_dir / "controls"
    for which in ("identity", "null"):
        c = ctl[which]
        for f, sha in ((c["score_file"], c["score_sha256"]), (c["tokens_file"], c["tokens_sha256"]),
                       (c["pairs_file"], c["pairs_sha256"])):
            if not (cdir / f).exists() or sha256_file_bytes(cdir / f) != sha:
                raise ValueError(f"control {which}: {f} missing or off-hash")
    id_tok = _load_tokens(cdir / ctl["identity"]["tokens_file"], ctl["identity"]["tokens_sha256"], "identity")
    if float(np.abs(id_tok["same_K"]).max()) != 0.0 or float(np.abs(id_tok["same_V"]).max()) != 0.0:
        raise ValueError("identity control: a per-token square is nonzero; the GPU record is not trustworthy")
    n_s = int(np.load(cdir / ctl["identity"]["pairs_file"])["pairs"].shape[0])
    if n_s != recorded[c_hid]["n_sender"]:
        raise ValueError("identity control did not cover every sender position")
    want_null = null_pairs(pairs_of[c_hid], make_rng(int(cfg.controls["null_seed"])))
    if not np.array_equal(np.load(cdir / ctl["null"]["pairs_file"])["pairs"], want_null):
        raise ValueError("null control pairs do not re-derive from the alignment and the seed")
    null_body = json.loads((cdir / ctl["null"]["score_file"]).read_text(encoding="utf-8"))
    null_tok = _load_tokens(cdir / ctl["null"]["tokens_file"], ctl["null"]["tokens_sha256"], "null")
    _check_tokens(null_body, null_tok, len(want_null), "null control")
    delta_null = {}
    for arm in ARMS:
        part, key = arm.split("_")
        d = centered_delta(null_tok[arm], _sst(null_body, part, key), len(want_null))
        delta_null[arm] = {"median_token_mean": float(np.median(token_mean(d))),
                           "median_per_layer": [float(x) for x in np.median(layer_mean(d), 0)]}

    # 4. Per handoff: centered delta, f*(tau), cross/same ratio, own-norm diagnostic, seam, depth.
    fstar = {arm: {} for arm in ARMS}
    ratio = {"K": {}, "V": {}}
    own_gt1 = {"K": {}, "V": {}}
    seam_tokens = {arm: [[] for _ in SEAM_BIN_LABELS] for arm in ("same_K", "same_V")}
    seam_per_handoff = {}
    depth_tokens = {arm: [] for arm in ARMS}
    for hid in included:
        tok, body, n = tokens_of[hid], bodies[hid], per_handoff[hid]["n_pairs"]
        dt = {}
        for arm in ARMS:
            part, key = arm.split("_")
            d = centered_delta(tok[arm], _sst(body, part, key), n)
            dt[arm] = token_mean(d)
            depth_tokens[arm].append(layer_mean(d))
            fstar[arm][hid] = f_star(dt[arm], tau[key])
        for key in ("K", "V"):
            ratio[key][hid] = float(np.median(dt[f"cross_{key}"]) / np.median(dt[f"same_{key}"]))
            own_gt1[key][hid] = float((own_norm_delta(tok[f"same_{key}"], tok[f"ref_{key}"]).mean(1) > 1).mean())
        b = seam_distance(pairs_of[hid], n_recv[hid])
        bins = seam_bin(b)
        seam_per_handoff[hid] = {}
        for arm in ("same_K", "same_V"):
            row = []
            for i in range(len(SEAM_BIN_LABELS)):
                sel = dt[arm][bins == i]
                seam_tokens[arm][i].append(sel)
                row.append(None if len(sel) == 0 else float(np.median(sel)))
            seam_per_handoff[hid][arm] = row
    seam_pooled = {}
    for arm in ("same_K", "same_V"):
        seam_pooled[arm] = []
        for i, label in enumerate(SEAM_BIN_LABELS):
            allv = np.concatenate(seam_tokens[arm][i]) if seam_tokens[arm][i] else np.zeros(0)
            seam_pooled[arm].append({"bin": label, "n_tokens": int(len(allv)),
                                     "median": None if len(allv) == 0 else float(np.median(allv))})
    depth = {arm: [float(x) for x in np.median(np.concatenate(depth_tokens[arm], 0), 0)] for arm in ARMS}

    # 5. Verdict statistic, band, medians -- stated here for the first time.
    f_same_k = _stats(fstar["same_K"].values())
    outcome = band_outcome(f_same_k["median"], cfg.rule)
    same_k = _stats(per_handoff[h]["same"]["K"] for h in included)
    same_v = _stats(per_handoff[h]["same"]["V"] for h in included)
    cross_k = _stats(per_handoff[h]["cross"]["K"] for h in included)
    cross_v = _stats(per_handoff[h]["cross"]["V"] for h in included)
    matched = _stats(recorded[h]["n_matched"] / recorded[h]["n_receiver"] for h in included)
    figures = {
        "coverage": cov, "tau": tau, "rule": dict(cfg.rule), "band_outcome": outcome,
        "fstar": {arm: _stats(fstar[arm].values()) for arm in ARMS},
        "fstar_per_handoff": fstar,
        "cross_over_same_median_delta": {k: _stats(v.values()) for k, v in ratio.items()},
        "own_norm_delta_gt_1_fraction": {k: _stats(v.values()) for k, v in own_gt1.items()},
        "delta_null": delta_null, "delta_null_handoff": c_hid,
        "seam_profile_pooled": seam_pooled, "seam_profile_per_handoff": seam_per_handoff,
        "seam_bins": list(SEAM_BIN_LABELS), "depth_profile_median_per_layer": depth,
        "bridge_r2": {"same_K": same_k, "same_V": same_v, "cross_K": cross_k, "cross_V": cross_v},
        "matched_fraction": matched, "keep_subset": rep["keep_subset"],
        "calibration": {"tau": cal["tau"], "heldout": cal["heldout"]},
    }
    _walk_nan(figures, "figures")
    (cfg.results_dir / "summary.json").write_text(json.dumps(figures, indent=1), encoding="utf-8")

    def fmt(s, d=4):
        return f"{s['median']:.{d}f} (p10 {s['p10']:.{d}f}, p90 {s['p90']:.{d}f})"

    seam_line = " · ".join(f"{r['bin']}: {'—' if r['median'] is None else f'{r['median']:.3f}'} (n={r['n_tokens']})"
                           for r in seam_pooled["same_K"])
    md = ("E9 summary -- alignments re-derived from raw traces; every R² recomputed from recorded "
          "moments; per-token squares summed against the moments; keep-subset re-scored from "
          "fingerprinted tensors; tau recomputed from the archived mapper; controls checked\n\n"
          f"pair {cfg.pair} | upstream {cfg.upstream_sha[:12]} | config {rep['config_sha256'][:12]} | "
          f"coverage: {cov['included']} included / {cov['excluded']} excluded (cap {cfg.context_cap}) "
          f"of {cov['observed']} observed handoffs\n\n"
          "Units: centered per-token deviation = the token's share of unexplained variance, in R²'s own "
          "units (token mean == 1 - R²); NOT a per-token percent error (0023).\n\n"
          f"- matched fraction |M|/|R| (a FLOOR; blocks method, entry 0019): {fmt(matched)}\n"
          f"- **f*(tau_K = {tau['K']:.4f}) E9-same K per handoff: {fmt(f_same_k)}**  <- verdict-bearing "
          "(oracle LOWER BOUND: restored-exactly assumption; no error propagation through reused KV)\n"
          f"- f*(tau_V = {tau['V']:.4f}) E9-same V per handoff: {fmt(figures['fstar']['same_V'])} (alongside)\n"
          f"- f* E9-cross K / V per handoff: {fmt(figures['fstar']['cross_K'])} / {fmt(figures['fstar']['cross_V'])} "
          "(the k=1 mapper across the handoff; never merged with same)\n"
          f"- cross/same median-delta ratio K / V: {fmt(figures['cross_over_same_median_delta']['K'], 3)} / "
          f"{fmt(figures['cross_over_same_median_delta']['V'], 3)}\n"
          f"- delta_null (uninformative scale, handoff {c_hid}) same K / V token-mean median: "
          f"{delta_null['same_K']['median_token_mean']:.3f} / {delta_null['same_V']['median_token_mean']:.3f}\n"
          f"- seam profile, E9-same K, pooled tokens, median centered delta by b(t): {seam_line}\n"
          f"- own-norm diagnostic: fraction of tokens with delta_own > 1, same K / V: "
          f"{fmt(figures['own_norm_delta_gt_1_fraction']['K'], 4)} / {fmt(figures['own_norm_delta_gt_1_fraction']['V'], 4)}\n"
          f"- bridge R² (A5 per head, head- and layer-averaged; decides nothing): same K {fmt(same_k)}, "
          f"same V {fmt(same_v)}, cross K {fmt(cross_k)}, cross V {fmt(cross_v)}\n\n"
          f"rule (entry 0023): HOLDS if median f*(tau_K) <= {cfg.rule['holds_max']}, DEGRADES if >= "
          f"{cfg.rule['degrades_min']}, else UNRESOLVED -> **{outcome}**\n\n"
          f"keep-subset ({len(rep['keep_subset'])} handoffs) recomputed from tensors; the remaining "
          "handoffs' moments and per-token squares are a GPU-run record cross-checked by that subset "
          "(0019). Every figure is trace-visible-only (0012). Depth profile and per-handoff seam rows are "
          "in summary.json.\n\n"
          "The verdict on H-E9 is NOT stated here; it enters by a numbered entry.\n")
    (cfg.results_dir / "summary.md").write_text(md, encoding="utf-8")
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m linear_ceiling.summarize_e9")
    ap.add_argument("--config", default=str(REPO_ROOT / "config" / "e9.toml"))
    ap.add_argument("--calibrate-tau", action="store_true",
                    help="0023: derive tau from the archived k=1 mapper record; writes results/e9/calibration/tau.json")
    ap.add_argument("--allow-dirty-upstream", action="store_true",
                    help="calibration only, before the upstream re-pin is committed; recorded in tau.json")
    a = ap.parse_args(argv)
    cfg = load_e9_config(Path(a.config), REPO_ROOT)
    try:
        if a.calibrate_tau:
            out = calibrate_tau(cfg, allow_dirty_upstream=a.allow_dirty_upstream)
            print(json.dumps({"tau": out["tau"], "heldout": out["heldout"], "upstream_head": out["upstream_head"],
                              "upstream_pin_check": out["upstream_pin_check"],
                              "diagnostics": out["diagnostics"]}, indent=1))
            return 0
        print(summarize(cfg))
    except (ValueError, RuntimeError) as e:
        print(f"E9 SUMMARY REFUSED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
