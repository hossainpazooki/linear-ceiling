"""Load every E7 corpus under `traces/` into one normalized list, with nothing dropped silently.

Three suites, three layouts, one output. The driver and the summarizer both walk the corpus
through this module, so the two can never disagree about WHICH trajectories exist; they still
disagree loudly (the summarizer refuses) if any NUMBER computed from them differs.

- `tau-bench/<agent>-<domain>.json`      agent from the filename (run-level identity)
- `tau2-bench/<...>.json`                agent from `info.agent_info.llm` inside the file
- `swe-bench/<YYYYMMDD_submission>/...`  agent = submission name with the date stripped; each
                                          trajectory is one instance (entry 0011's unit) in
                                          either the flat or the nested layout, parsed by the
                                          role/content adapter or, failing that, the LangChain
                                          adapter. A trajectory neither adapter accepts is
                                          recorded under `unparsed` with its reason -- it is
                                          never counted, and never disappears.

Composio (`composio_swekit`, two submissions of one system) is the Lane A subject and is
NOT a coverage contributor (entry 0011): `LANE_A_ONLY_AGENTS` keeps it out of the floor
arithmetic while its trajectories stay in every Lane A and headroom figure.

Serving-identity detection everywhere goes through `e7_swe.models_in` with `MODEL_KEYS`
(entry 0010); the report records that key set beside every Lane A count.
"""
import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from linear_ceiling.config import E7Config
from linear_ceiling.e7_rolecontent import load_role_content_trajectory
from linear_ceiling.e7_swe import discover_trajectories, load_composio_detailed
from linear_ceiling.e7_tau2 import agent_of, load_tau2_doc, read_tau2
from linear_ceiling.e7_tokens import make_counter, strategy_for
from linear_ceiling.e7_traces import Trajectory, load_tau_bench

LANE_A_ONLY_AGENTS = ("composio_swekit",)    # entry 0011: Lane A subject, not a coverage contributor

_DATE_PREFIX = re.compile(r"^\d{8}_")


def agent_of_submission(name: str) -> str:
    """`20241016_composio_swekit` -> `composio_swekit`; the date is a submission, not an agent."""
    return _DATE_PREFIX.sub("", name)


@dataclass
class Corpus:
    trajectories: list[Trajectory] = field(default_factory=list)
    texts: dict[str, list[str]] = field(default_factory=dict)   # traj_id -> per-message text (LangChain family only)
    unparsed: list[dict] = field(default_factory=list)          # {suite, agent, traj_id, reason}
    files: list[Path] = field(default_factory=list)             # every file read or discovered, sorted
    strategies: dict[str, str] = field(default_factory=dict)    # agent -> tokenizer strategy

    def relkey(self, traces_dir: Path, f: Path) -> str:
        return f.resolve().relative_to(Path(traces_dir).resolve()).as_posix()


def discover_files(traces_dir: Path) -> list[Path]:
    """Every file the corpus walk would touch, sorted -- the provenance set the report hashes."""
    traces_dir = Path(traces_dir)
    out: list[Path] = []
    out += sorted(traces_dir.glob("tau-bench/*.json"))
    out += sorted(traces_dir.glob("tau2-bench/*.json"))
    swe = traces_dir / "swe-bench"
    if swe.is_dir():
        for sub in sorted(p for p in swe.iterdir() if p.is_dir()):
            for _, files in discover_trajectories(sub):
                out += files
    return out


def load_corpus(cfg: E7Config) -> Corpus:
    c = Corpus()
    counters: dict[str, object] = {}

    def counter_for(agent: str):
        if agent not in counters:
            counters[agent] = make_counter(agent, cfg.tokenizer)
            c.strategies[agent] = strategy_for(agent, cfg.tokenizer)
        return counters[agent]

    for f in sorted(cfg.traces_dir.glob("tau-bench/*.json")):
        agent = f.stem.rsplit("-", 1)[0]          # gpt-4o-airline -> gpt-4o
        c.trajectories.extend(load_tau_bench(f, agent=agent, counter=counter_for(agent)))
        c.files.append(f)

    for f in sorted(cfg.traces_dir.glob("tau2-bench/*.json")):
        doc = read_tau2(f)
        c.trajectories.extend(load_tau2_doc(doc, counter_for(agent_of(doc))))
        c.files.append(f)

    swe = cfg.traces_dir / "swe-bench"
    if swe.is_dir():
        for sub in sorted(p for p in swe.iterdir() if p.is_dir()):
            agent = agent_of_submission(sub.name)
            counter = counter_for(agent)
            for tid, files in discover_trajectories(sub):
                c.files.extend(files)
                traj, texts, reason = _load_swe_trajectory(sub.name, tid, files, counter)
                if traj is None:
                    c.unparsed.append({"suite": "swe-bench", "agent": agent,
                                       "traj_id": f"{sub.name}/{tid}", "reason": reason})
                    continue
                # traj_id keeps the dated submission (unique); attempts only where the layout records them
                traj = replace(traj, agent=agent, attempts=_attempts_in(files))
                c.trajectories.append(traj)
                if texts is not None:
                    c.texts[traj.traj_id] = texts
    if not c.trajectories and not c.unparsed:
        raise ValueError(f"no trajectories under {cfg.traces_dir}; acquire traces first "
                         "(they are gitignored, never committed)")
    return c


_ATTEMPT = re.compile(r"^attempt_\d+$")


def _attempts_in(files: list[Path]) -> int | None:
    """Distinct `attempt_N` directories among a trajectory's files; None for a flat layout."""
    if len(files) == 1 and files[0].parent.name and not _ATTEMPT.match(files[0].parent.name):
        return None
    names = {part for f in files for part in f.parts if _ATTEMPT.match(part)}
    return len(names) if names else None


def _load_swe_trajectory(submission: str, tid: str, files: list[Path], counter):
    """(Trajectory, texts|None, None) on success; (None, None, reason) when no adapter accepts it."""
    reasons = []
    try:
        return load_role_content_trajectory(files, submission, tid, counter), None, None
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        reasons.append(f"role/content: {str(e)[:120]}")
    if len(files) == 1 and files[0].suffix == ".json":
        try:
            traj, texts = load_composio_detailed(files[0], submission, counter)
            return traj, texts, None
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
            reasons.append(f"langchain: {str(e)[:120]}")
    else:
        reasons.append("langchain: adapter takes a single .json file")
    return None, None, "; ".join(reasons)
