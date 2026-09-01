"""TOML config -> frozen dataclasses. Seeds and thresholds live here, never in code."""
import tomllib
from dataclasses import dataclass
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
    lane_b_policy: str
    config_path: Path


_E7_PRICING_KEYS = ("provider", "read_mult", "write_mult", "write_mult_1h", "ttl_seconds")
_E7_THRESHOLD_KEYS = ("materiality_fraction", "negative_mass_fraction",
                      "min_trajectories_per_suite", "min_agents_per_suite", "min_suites")


def load_e7_config(path: Path, repo_root: Path) -> E7Config:
    path = Path(path)
    e7 = _read(path)["e7"]
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
        lane_b_policy=e7["lane_b"]["policy"],
        config_path=path,
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
