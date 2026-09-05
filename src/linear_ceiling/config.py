"""TOML config -> frozen dataclasses. Seeds and thresholds live here, never in code."""
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

OPERATIONALIZATIONS = ("", "A", "B", "C")


@dataclass(frozen=True)
class ArtifactRoot:
    path: Path
    pattern: str


@dataclass(frozen=True)
class SealConfig:
    predictions_dir: Path
    upstream_path: Path
    artifact_roots: tuple[ArtifactRoot, ...]


@dataclass(frozen=True)
class E0Config:
    seed: int
    ladder: tuple[str, ...]
    optional: tuple[str, ...]
    operationalization: str
    results_dir: Path
    rule: dict
    reg_sweep: tuple[float, ...]
    heldout_frac: float
    config_path: Path


def _read(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _resolve(repo_root: Path, raw: str, upstream: Path | None = None) -> Path:
    if "${upstream}" in raw:
        if upstream is None:
            raise ValueError("${upstream} used before upstream_path was known")
        raw = raw.replace("${upstream}", upstream.as_posix())
        return Path(raw).resolve()
    return (repo_root / raw)


def load_seal_config(path: Path, repo_root: Path) -> SealConfig:
    d = _read(Path(path))
    repo_root = Path(repo_root)
    upstream = repo_root / d["upstream_path"]
    roots = []
    for r in d.get("artifact_roots", []):
        if "{pair}" not in r["pattern"]:
            raise ValueError(f"artifact root pattern {r['pattern']!r} has no {{pair}} placeholder; "
                             "a root that cannot be scoped to a pair would match everything or nothing")
        roots.append(ArtifactRoot(_resolve(repo_root, r["path"], upstream), r["pattern"]))
    if not roots:
        raise ValueError("seal config lists no artifact_roots; the writer would have nothing to refuse on")
    return SealConfig(predictions_dir=repo_root / d["predictions_dir"],
                      upstream_path=upstream, artifact_roots=tuple(roots))


@dataclass(frozen=True)
class E7Config:
    traces_dir: Path
    results_dir: Path
    pricing: dict
    thresholds: dict
    tokenizer: dict
    lane_b_policy: str
    config_path: Path
    # The committed corpus manifest (entry 0024); None means "beside the config" -- see
    # e7_manifest.manifest_path. Not a key in config/e7.toml, so the config's registered
    # sha256 (entries 0013-0022) still identifies the same bytes.
    manifest_path: Path | None = None
    # [e7.overlap_null]: the seed for entry 0024's null controls (e7_null); {} until registered.
    overlap_null: dict = field(default_factory=dict)


_E7_PRICING_KEYS = ("provider", "read_mult", "write_mult", "write_mult_1h", "ttl_seconds")
_E7_THRESHOLD_KEYS = ("materiality_fraction", "negative_mass_fraction",
                      "min_trajectories_per_suite", "min_agents_per_suite", "min_suites")


def load_e7_config(path: Path, repo_root: Path) -> E7Config:
    path = Path(path)
    e7 = _read(path)["e7"]
    if "tokenizer" not in e7 or "divisors" not in e7.get("tokenizer", {}):
        raise ValueError("config/e7.toml [e7.tokenizer] with measured [e7.tokenizer.divisors] is "
                         "required; the token counter must be registered (ledger entry 0009) "
                         "before any cost number is computed")
    for section, keys in (("pricing", _E7_PRICING_KEYS), ("thresholds", _E7_THRESHOLD_KEYS)):
        missing = [k for k in keys if k not in e7.get(section, {})]
        if missing:
            raise ValueError(f"config/e7.toml [e7.{section}] is missing {missing}; the registered "
                             "parameters (ledger entries 0006/0007) must be complete before E7 runs")
    return E7Config(
        traces_dir=Path(repo_root) / e7["traces_dir"],
        results_dir=Path(repo_root) / e7["results_dir"],
        pricing=dict(e7["pricing"]),
        thresholds=dict(e7["thresholds"]),
        tokenizer=dict(e7["tokenizer"]),
        lane_b_policy=e7["lane_b"]["policy"],
        config_path=path,
        manifest_path=Path(repo_root) / "config" / "e7-manifest.json",
        overlap_null=dict(e7.get("overlap_null", {})),
    )


def load_e0_config(path: Path, repo_root: Path) -> E0Config:
    path = Path(path)
    d = _read(path)
    op = d.get("operationalization", "")
    if op not in OPERATIONALIZATIONS:
        raise ValueError(f"operationalization must be one of {OPERATIONALIZATIONS}, got {op!r}")
    seed = d["seed"]
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an int")
    e0 = d["e0"]
    return E0Config(
        seed=seed,
        ladder=tuple(d["models"]["ladder"]),
        optional=tuple(d["models"].get("optional", [])),
        operationalization=op,
        results_dir=Path(repo_root) / e0["results_dir"],
        rule=dict(e0.get("rule", {})),
        reg_sweep=tuple(float(x) for x in e0["reg_sweep"]),
        heldout_frac=float(e0["heldout_frac"]),
        config_path=path,
    )


@dataclass(frozen=True)
class E8Config:
    pair: str
    results_dir: Path
    tokens_dir: Path
    upstream_path: Path
    upstream_sha: str
    verdict_k: int
    report_k: tuple[int, ...]
    generic_dumps: str          # relative to upstream_path
    agent_dumps: Path           # under this repo
    holdout_frac: float
    stride: int
    text: dict
    band: dict
    config_path: Path
    # E8 amendment (ledger entry 0030): arm (b) may score EVERY agent sequence (the mapper was never fit
    # on them); the agent dumps of the 0020 run are reused by fingerprint; per-sequence moments + bootstrap.
    agent_holdout_frac: float | None = None      # None -> holdout_frac (the 0016 protocol)
    reuse_agent_dumps_from: Path | None = None   # a prior E8 report.json whose recorded dumps/tokens are reused
    amendment: dict | None = None                # {"entry": "0030", "bootstrap_seed": int, "bootstrap_reps": int}


def load_e8_config(path: Path, repo_root: Path) -> E8Config:
    path = Path(path)
    e8 = _read(path)["e8"]
    for section, keys in (("mappers", ("verdict_k", "report_k")),
                          ("arms", ("generic_dumps", "agent_dumps", "holdout_frac", "stride")),
                          ("text", ("seed", "n_seqs", "seq_len", "suites", "window")),
                          ("band", ("holds_max_drop", "degrades_min_drop"))):
        missing = [k for k in keys if k not in e8.get(section, {})]
        if missing:
            raise ValueError(f"config/e8.toml [e8.{section}] is missing {missing}; the registered "
                             "parameters (ledger entries 0009/0016) must be complete before E8 runs")
    if e8["mappers"]["verdict_k"] not in e8["mappers"]["report_k"]:
        raise ValueError("config/e8.toml: verdict_k must be one of report_k")
    root = Path(repo_root)
    arms = e8["arms"]
    agent_frac = float(arms["agent_holdout_frac"]) if "agent_holdout_frac" in arms else None
    if agent_frac is not None and not (0.0 < agent_frac <= 1.0):
        raise ValueError("config e8 [e8.arms] agent_holdout_frac must be in (0, 1]")
    amendment = dict(e8["amendment"]) if "amendment" in e8 else None
    if amendment is not None:
        missing = [k for k in ("entry", "bootstrap_seed", "bootstrap_reps") if k not in amendment]
        if missing:
            raise ValueError(f"config e8 [e8.amendment] is missing {missing}")
        if not (isinstance(amendment["entry"], str) and len(amendment["entry"]) == 4 and amendment["entry"].isdigit()):
            raise ValueError("config e8 [e8.amendment] entry must be a four-digit ledger entry number as a string")
        if int(amendment["bootstrap_reps"]) < 1:
            raise ValueError("config e8 [e8.amendment] bootstrap_reps must be >= 1")
    return E8Config(
        pair=e8["pair"], results_dir=root / e8["results_dir"], tokens_dir=root / e8["tokens_dir"],
        upstream_path=(root / e8["upstream_path"]).resolve(), upstream_sha=str(e8["upstream_sha"]),
        verdict_k=int(e8["mappers"]["verdict_k"]), report_k=tuple(int(k) for k in e8["mappers"]["report_k"]),
        generic_dumps=arms["generic_dumps"], agent_dumps=root / arms["agent_dumps"],
        holdout_frac=float(arms["holdout_frac"]), stride=int(arms["stride"]),
        text=dict(e8["text"]), band=dict(e8["band"]), config_path=path,
        agent_holdout_frac=agent_frac,
        reuse_agent_dumps_from=(root / arms["reuse_agent_dumps_from"]) if "reuse_agent_dumps_from" in arms else None,
        amendment=amendment,
    )


@dataclass(frozen=True)
class E9Config:
    pair: str
    results_dir: Path
    scratch_dir: Path
    upstream_path: Path
    upstream_sha: str
    suite: str
    agent: str
    context_cap: int
    alignment_method: str
    mapper_k: int
    mapper_space: str
    keep_seed: int
    keep_n: int
    rule: dict          # entry 0023: statistic, holds_max, degrades_min, tau_K, tau_V
    controls: dict      # entry 0023: null_seed, seam_bins
    config_path: Path


def load_e9_config(path: Path, repo_root: Path) -> E9Config:
    path = Path(path)
    e9 = _read(path)["e9"]
    for section, keys in (("handoffs", ("suite", "agent", "context_cap")),
                          ("alignment", ("method",)), ("mapper", ("k", "space")),
                          ("keep", ("seed", "n")),
                          ("rule", ("statistic", "holds_max", "degrades_min", "tau_K", "tau_V", "tau_ladder",
                                    "tau_agent_K", "min_block_len")),
                          ("controls", ("null_seed", "seam_bins", "prefix_invariance_max_delta",
                                        "bootstrap_seed", "bootstrap_reps"))):
        missing = [k for k in keys if k not in e9.get(section, {})]
        if missing:
            raise ValueError(f"config/e9.toml [e9.{section}] is missing {missing}; the registered "
                             "parameters (ledger entries 0019/0023/0025) must be complete before E9 runs")
    ladder = e9["rule"]["tau_ladder"]
    if (not isinstance(ladder, list) or not ladder
            or any(not isinstance(t, (int, float)) or not (0 < float(t) < float(e9["rule"]["tau_K"])) for t in ladder)
            or any(float(a) <= float(b) for a, b in zip(ladder, ladder[1:]))):
        raise ValueError("config/e9.toml [e9.rule] tau_ladder must be a strictly decreasing list of values in "
                         "(0, tau_K): the ladder reads how far INSIDE the registered tolerance f* sits (entry 0025)")
    rule, ctl = e9["rule"], e9["controls"]
    if not (float(rule["tau_K"]) < float(rule["tau_agent_K"]) < 1.0):
        raise ValueError("config/e9.toml [e9.rule] tau_agent_K must sit in (tau_K, 1): it is the LOOSER agent-text "
                         "tolerance from entry 0020 arm (b), reported alongside (entry 0025)")
    if not (isinstance(rule["min_block_len"], int) and rule["min_block_len"] >= 1):
        raise ValueError("config/e9.toml [e9.rule] min_block_len must be an integer >= 1 (entry 0025)")
    if not (isinstance(ctl["prefix_invariance_max_delta"], (int, float)) and 0 < float(ctl["prefix_invariance_max_delta"]) < 1):
        raise ValueError("config/e9.toml [e9.controls] prefix_invariance_max_delta must be in (0, 1) (entry 0025)")
    if not (isinstance(ctl["bootstrap_reps"], int) and ctl["bootstrap_reps"] >= 100 and isinstance(ctl["bootstrap_seed"], int)):
        raise ValueError("config/e9.toml [e9.controls] bootstrap_seed must be an int and bootstrap_reps an int >= 100 (entry 0025)")
    root = Path(repo_root)
    return E9Config(
        pair=e9["pair"], results_dir=root / e9["results_dir"], scratch_dir=root / e9["scratch_dir"],
        upstream_path=(root / e9["upstream_path"]).resolve(), upstream_sha=str(e9["upstream_sha"]),
        suite=e9["handoffs"]["suite"], agent=e9["handoffs"]["agent"],
        context_cap=int(e9["handoffs"]["context_cap"]), alignment_method=e9["alignment"]["method"],
        mapper_k=int(e9["mapper"]["k"]), mapper_space=e9["mapper"]["space"],
        keep_seed=int(e9["keep"]["seed"]), keep_n=int(e9["keep"]["n"]),
        rule=dict(e9["rule"]), controls=dict(e9["controls"]), config_path=path,
    )
