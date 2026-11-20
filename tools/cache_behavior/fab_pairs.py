"""Inputs, cohort accounting and the pair summary for the cache reading of the Finance Agent run's paired helper
sub-calls (`config/cache-behavior-fab.toml`; the registering ledger entry is the authority on every rule here).

The unit is a PAIR of `retrieve_information` sub-calls of one trajectory: B, a sub-call carrying at least one
document token that an earlier sub-call carried, and A, the latest earlier sub-call carrying at least one of B's
document tokens. Sub-calls, document tokens and their keys are entry 0075's, derived by 0075's own code
(`linear_ceiling.fab_reuse`), and a trajectory gives pairs only if 0075 measures it; this module refuses unless its
own walk reproduces 0075's counts for the trajectory. The matched set M is B's document tokens whose key occurs
exactly once in A and once in B, minus those at the same index inside A's and B's common token prefix (their
reused and fresh states coincide under causal attention), so the reader reads B fresh and reads it with M's states
taken from A and re-placed at B's positions (`run.py`). A is prefilled only up to the first prefill-chunk boundary
at or after its last matched token (capped at A's length), which leaves every state read at A's matched positions
bit-identical; nothing is truncated, and a pair that does not fit the reader's cap, or whose host memory predicted
from its matched count exceeds the stated requirement, is excluded and counted. The scored continuation is the
serving model's logged response to B, read with no chat template. Nothing of the logs' text is written anywhere but
the token-id inputs, which go to the GPU machine that runs the reading and nowhere else.
"""
import hashlib
import json
import math
import re
import statistics
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from linear_ceiling.e7_stats import summary
from linear_ceiling.e9_pertoken import f_star
from linear_ceiling.fab_reuse import (_numbered, _present, document_tokens, load_config, measure_trajectory,
                                      read_json, reader_encoder, rebuild)
from linear_ceiling.hashing import sha256_text_file
from linear_ceiling.rng import make_rng

CELL = "fab-pairs"
FAB_CONFIG = "config/fab-reuse.toml"
SOURCES = ("src/linear_ceiling/fab_reuse.py", "tools/cache_behavior/fab_pairs.py", "tools/cache_behavior/run.py",
           "tools/cache_behavior/core.py")
STAMP = "%Y-%m-%dT%H:%M:%SZ"
CLASSES = ("same_offset", "different_offset")
EXCLUSIONS = ("prefix", "repeated keys only", "below the matched-token floor", "no logged response",
              "fewer than two continuation tokens", "over the cap", "over host memory", "beyond the ceiling")
ARRAYS = ("sender", "receiver", "pairs", "continuation")
STATS = ("mean_kl", "p90_kl", "top1_agreement")
LABEL = ("next-token sensitivity of the reader (Qwen3-1.7B, YaRN 2.5) to reading B with its matched document states "
         "taken from an earlier sub-call A of the same agent; teacher-forced on the serving model's logged response "
         "to B, not the reader's own generation; the harness sent B as one user message through a chat interface, "
         "and the reader reads the logged text with no chat template; f* is the oracle removal fraction (0058), "
         "computed by this driver on the logged pairs, not by the E9 instrument")
CROSS_CHECK_LABELS = {"run": "checked per token against the E9-long archive on one handoff",
                      "not staged": "not cross-checked per token"}
# Every field of summary.json's `fab` block, by level; the registering entry names each, and a test holds the
# summary to these lists.
FAB_FIELDS = ("label", "cross_check_label", "cross_check", "read", "selected", "not_read", "stop_at", "stopped",
              "ended_in_flight", "probe_pair", "built", "candidates", "eligible", "exclusions", "excluded",
              "over_the_cap_matched_share", "reused_within_cap_0075", "questions", "all", *CLASSES, "per_pair")
BLOCK_FIELDS = ("pairs", "trajectories", "pair_level", "trajectory_level")
PAIR_STATS = ("f_star_K", *(f"{arm}_{k}" for arm in ("reuse", "random", "scrambled") for k in STATS))
# Copied into each per-pair row from the pair's manifest record (A is `sender_tokens` through the cut, of `a_tokens`).
PAIR_RECORD_FIELDS = ("ended_by_itself", "matched", "matched_in_common_prefix", "repeated_key_tokens",
                      "matched_share_of_reused", "different_offset_share", "sender_tokens", "a_tokens",
                      "receiver_tokens", "continuation_tokens")
PER_PAIR_FIELDS = ("handoff", "task_id", "class", "probe", *PAIR_STATS, *PAIR_RECORD_FIELDS, "tokens_over_tau_K",
                   "max_token_mean_K")
WITHIN_CAP_0075 = ("reused_in_capped_prompts", "reused_in_capped_pairs")    # 0075's two counts at the cap
CROSS_CHECK_FIELDS = ("matched", "tokens_outside_tolerance", "max_gap", "max_gap_over_bound", "f_star_driver",
                      "f_star_archive", "tokens_over_tau_K_driver", "tokens_over_tau_K_archive", "passed",
                      "handoff", "identity", "archived_mean", "minutes")


def parse_stamp(text: str) -> datetime:
    return datetime.strptime(text, STAMP).replace(tzinfo=timezone.utc)


def sources(root: Path) -> dict:
    return {rel: sha256_text_file(root / rel) for rel in SOURCES}


def assert_registered(root: Path, entries) -> None:
    """Refuse unless the committed ledger holds every entry named (e.g. 0075 before any log is read)."""
    shown = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=root, capture_output=True, text=True,
                           encoding="utf-8")
    if shown.returncode != 0:
        raise RuntimeError("FAB-PAIRS REFUSED: cannot read HEAD:ledger/ledger.md")
    for num in entries:
        if f"### {num} " not in shown.stdout:
            raise RuntimeError(f"FAB-PAIRS REFUSED: the committed ledger has no entry {num}")


def _lcp(a, b) -> int:
    n = min(len(a), len(b))
    diff = np.flatnonzero(np.asarray(a[:n]) != np.asarray(b[:n]))
    return int(diff[0]) if len(diff) else n


def _record(path: Path):
    """A launch record and its `end`, or None if it does not decode (the wrapper has not finished writing it)."""
    try:
        body = json.loads(path.read_bytes().decode("utf-8"))
        return body, parse_stamp(body["end"])
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return None


def _launches(runs_root: Path, tid: str, suffix: str) -> dict[int, Path]:
    """The question's `runs/<task id>-<k><suffix>` files by k (names only; nothing is opened here)."""
    pat = re.compile(re.escape(tid) + r"-(\d+)" + re.escape(suffix))
    return {int(m.group(1)): p for p in (runs_root / "runs").glob(f"{tid}-*{suffix}")
            if (m := pat.fullmatch(p.name))}


def window(runs_root: Path, fab, end: datetime) -> tuple[dict, dict]:
    """Per task id of the cohort: its status, and its launch records if it is in the window: every launch ended
    (the wrapper creates `<task id>-<k>.out` when launch k starts and writes `<task id>-<k>.json` once, when it
    ends; only the two names are looked at), every launch record decodes and every `end` is at or before `end`."""
    status, launches = {}, {}
    for row in range(1, fab.cohort + 1):
        tid = fab.task_id_format.format(row=row)
        recs, outs = _launches(runs_root, tid, ".json"), _launches(runs_root, tid, ".out")
        paths = [recs[k] for k in sorted(recs)]
        read = [(p, _record(p)) for p in paths]
        if set(outs) - set(recs):
            status[tid] = "a launch with no end record at the build"
            continue
        if not paths:
            status[tid] = "no launch record"
            continue
        if any(r is None for _, r in read) or any(r[1] > end for _, r in read):
            status[tid] = "outside the window"
            continue
        status[tid] = "in the window"
        launches[tid] = [(p, r[0]) for p, r in read]
    return status, launches


def _walk(qdir: Path, encode, root: Path, files: dict) -> list[dict]:
    """The trajectory's sub-calls in (turn, tool) order by 0075's rules: ids, document tokens (`document_tokens`)
    and the logged response. Called only on a trajectory 0075 measures, so a failure here is a disagreement with
    0075 and refuses."""
    turns = qdir / "turns"
    turn_dirs = _numbered(turns, "turn")
    if turn_dirs and not _present(qdir / "result.json"):
        turn_dirs = turn_dirs[:-1]          # 0075: without the final record the last turn is set aside, unread
    last = read_json(turns / "init" / "state.json", files, root)
    context = {}
    for n, tdir in turn_dirs:
        res = read_json(tdir / "result.json", files, root, required=False)
        if res is None:                      # a turn whose query failed; no tool ran
            continue
        after = read_json(tdir / "state.json", files, root)
        context[n] = (res["tool_call_records"], after, last)
        last = after
    out = []
    for n, tdir in turn_dirs:
        for i, hdir in _numbered(tdir / "helper_queries", "tool"):
            rec = read_json(hdir / "result.json", files, root)
            sent = read_json(hdir / "history.json", files, root)[0]["text"]
            recs, after, before = context[n]
            spans = rebuild(rec["tool_call"]["parsed_args"], sent, recs, i, after, before)
            ids, offsets = encode(sent)
            toks = document_tokens(sent, spans, ids, [(int(a), int(b)) for a, b in offsets])
            if toks is None:
                raise ValueError(f"{hdir}: a span edge 0075 placed cannot be placed here")
            qr = rec.get("query_result")
            response = qr.get("output_text") if isinstance(qr, dict) else None
            out.append({"turn": n, "tool": i, "ids": np.asarray(ids, dtype=np.int64),
                        "doc": [(p, (sha, a, b, tid)) for p, sha, a, b, tid in toks],
                        "response": response if isinstance(response, str) else None})
    return out


def _reproduce(subs: list[dict], row: dict, qdir: Path) -> None:
    """0075's counts from this walk; refuse on any difference. Sets each sub-call's reused count as 0075 counts it."""
    seen: dict = {}
    got = Counter(subcalls=len(subs))
    for s in subs:
        reused = 0
        for p, key in s["doc"]:
            before = seen.get(key)
            kind = "new" if before is None else ("same_offset" if p in before else "different_offset")
            got[kind] += 1
            reused += kind != "new"
        s["reused"] = reused
        got["prompt_tokens"] += len(s["ids"])
        got["document_tokens"] += len(s["doc"])
        for p, key in s["doc"]:
            seen.setdefault(key, set()).add(p)
    for k in ("subcalls", "prompt_tokens", "document_tokens", "same_offset", "different_offset", "new"):
        if got[k] != row[k]:
            raise ValueError(f"{qdir}: {k} {got[k]} here, {row[k]} in 0075's count; refusing")


def a_cut(last_matched: int, a_len: int, chunk: int) -> int:
    """A's prefill length: through the end of the prefill chunk holding its last matched token, or all of A."""
    return min(a_len, math.ceil((last_matched + 1) / chunk) * chunk)


def host_gib(matched: int, cfg: dict) -> float:
    """A pair's predicted host memory: the fixed part plus the stated bytes per matched token (four float32 copies
    of M's keys and values on the host at once: FRESH's, A's, the relocated ones and one arm's)."""
    return cfg["host_fixed_GiB"] + matched * cfg["host_bytes_per_matched_token"] / 2**30


def candidate_pairs(task_id: str, subs: list[dict], encode, cfg: dict) -> list[dict]:
    """One candidate per B, with its exclusion reason (None if eligible) and, if eligible, its arrays."""
    out = []
    keysets = [{k for _, k in s["doc"]} for s in subs]
    for j, b in enumerate(subs):
        if not b["reused"]:
            continue
        i = max(x for x in range(j) if keysets[x] & keysets[j])
        a = subs[i]
        ca, cb = Counter(k for _, k in a["doc"]), Counter(k for _, k in b["doc"])
        pos_a = {k: p for p, k in a["doc"]}
        lcp = _lcp(a["ids"], b["ids"])
        pairs, repeated, in_prefix = [], 0, 0
        for p, k in b["doc"]:
            if k not in ca:
                continue
            if ca[k] != 1 or cb[k] != 1:
                repeated += 1
            elif pos_a[k] == p and p < lcp:
                in_prefix += 1
            else:
                pairs.append((pos_a[k], p))
        pairs = np.asarray(pairs, dtype=np.int64).reshape(-1, 2)
        moved = int(np.sum(pairs[:, 0] != pairs[:, 1]))
        row = {"handoff": f"{task_id}/t{b['turn']:03d}.{b['tool']:03d}<t{a['turn']:03d}.{a['tool']:03d}",
               "task_id": task_id, "b": [b["turn"], b["tool"]], "a": [a["turn"], a["tool"]],
               "a_tokens": len(a["ids"]), "receiver_tokens": len(b["ids"]), "common_prefix_tokens": lcp,
               "matched": len(pairs), "matched_in_common_prefix": in_prefix, "repeated_key_tokens": repeated,
               "reused_document_tokens": b["reused"], "matched_share_of_reused": len(pairs) / b["reused"],
               "different_offset_share": moved / len(pairs) if len(pairs) else None,
               "class": None if not len(pairs) else ("different_offset" if moved else "same_offset"),
               "predicted_host_GiB": host_gib(len(pairs), cfg), "sender_tokens": None, "continuation_tokens": None,
               "reason": None}
        if not len(pairs):
            row["reason"] = "prefix" if in_prefix else "repeated keys only"
        elif len(pairs) < cfg["min_matched_tokens"]:
            row["reason"] = "below the matched-token floor"
        elif b["response"] is None:
            row["reason"] = "no logged response"
        else:
            cont = np.asarray(encode(b["response"])[0][:cfg["continuation_tokens"]], dtype=np.int64)
            cut = a_cut(int(pairs[:, 0].max()), len(a["ids"]), cfg["chunk_tokens"])
            row.update(sender_tokens=cut, continuation_tokens=len(cont))
            if len(cont) < 2:
                row["reason"] = "fewer than two continuation tokens"
            elif cut > cfg["context_cap"] or len(b["ids"]) + len(cont) - 1 > cfg["context_cap"]:
                row["reason"] = "over the cap"
            elif row["predicted_host_GiB"] > cfg["host_memory_limit_GiB"]:
                row["reason"] = "over host memory"
            else:
                row["_arrays"] = {"sender": a["ids"][:cut], "receiver": b["ids"], "pairs": pairs,
                                  "continuation": cont}
        out.append(row)
    return out


def registered_order(eligible: dict[str, list[dict]], seed: int) -> list[dict]:
    """Round robin over a seeded permutation of the trajectories (sorted by task id), each trajectory's pairs in a
    seeded permutation of their (B turn, B tool) order. It depends only on which pairs are eligible, keyed by task
    id and B's turn and tool; lengths and counts decide eligibility before this, and no length or text enters it."""
    rng = make_rng(seed)
    tasks = sorted(eligible)
    tasks = [tasks[i] for i in rng.permutation(len(tasks))]
    ranked = {}
    for t in tasks:
        ps = sorted(eligible[t], key=lambda r: tuple(r["b"]))
        ranked[t] = [ps[i] for i in rng.permutation(len(ps))]
    depth = max((len(v) for v in ranked.values()), default=0)
    return [ranked[t][r] for r in range(depth) for t in tasks if r < len(ranked[t])]


def arrays_sha256(arrays) -> str:
    """Digest of the four arrays' int64 values and shapes, independent of the npz container's bytes."""
    h = hashlib.sha256()
    for name in ARRAYS:
        x = np.ascontiguousarray(arrays[name], dtype=np.int64)
        h.update(f"{name}:{x.shape}:".encode())
        h.update(x.tobytes())
    return h.hexdigest()


def prepare(args, cfg, root: Path, digest, write) -> dict:
    """Build the inputs and the manifest from the run's ended, in-window questions. No model; no reading."""
    assert_registered(root, cfg["gate"]["prepare_entries"])
    fab = load_config(root / FAB_CONFIG, root)
    end = parse_stamp(cfg["window_end"])
    if datetime.now(timezone.utc) < end:
        raise ValueError(f"the window ends {cfg['window_end']}; the inputs are built after it")
    args.inputs.mkdir(parents=True, exist_ok=True)
    if (args.inputs / "manifest.json").exists():
        raise ValueError("prepared manifest already exists; check it instead of overwriting")
    base = reader_encoder(args.tokenizer_json, fab.reader["tokenizer_json_sha256"])
    cache: dict = {}

    def encode(text):
        key = hashlib.sha256(text.encode("utf-8", "surrogatepass")).digest()
        if key not in cache:
            cache[key] = base(text)
        return cache[key]
    runs_root = Path(args.runs_root)
    built = datetime.now(timezone.utc).strftime(STAMP)
    status, launches = window(runs_root, fab, end)
    questions, candidates, logs = {}, [], {}
    for tid, st in status.items():
        questions[tid] = {"status": st}
        if st != "in the window":
            continue
        recorded = {}
        for _, body in launches[tid]:
            recorded.update(body["files"])
        dirs = [runs_root / d for _, body in launches[tid] for d in body["log_dirs"]]
        done = [d for d in dirs if any(_present(t / "result.json") for _, t in _numbered(d / "turns", "turn"))]
        questions[tid].update(launches={p.name: digest(p) for p, _ in launches[tid]},
                              failed_launches=len(dirs) - len(done))
        if len(done) > 1:
            raise ValueError(f"{tid}: more than one trajectory; one run per question")
        if not done:
            questions[tid]["status"] = "no trajectory in its launch records"
            continue
        cache.clear()                        # one trajectory's tokenizations at a time
        row = measure_trajectory(done[0], encode, runs_root, cap=fab.reader["context_cap"])
        if row["serving_model"] is not None and row["serving_model"] != fab.harness["model"]:
            raise ValueError(f"{tid} was served by {row['serving_model']!r}, not {fab.harness['model']!r}")
        files = dict(row["files"])
        if row["measurable"]:
            walked: dict = {}
            subs = _walk(done[0], encode, runs_root, walked)
            if any(files.get(k) != v for k, v in walked.items()):
                raise ValueError(f"{tid}: a file changed between two reads")
            _reproduce(subs, row, done[0])
        for path, sha in files.items():
            if recorded.get(path) != sha:
                raise ValueError(f"{path}: the bytes read differ from the launch record, or it lists no such file")
        logs.update(files)
        if not row["measurable"]:
            questions[tid]["status"] = f"not measured by 0075: {row['reason']}"
            continue
        rows = candidate_pairs(tid, subs, encode, cfg)
        for r in rows:
            r["ended_by_itself"] = row["ended_by_itself"]   # 0075's value for the pair's trajectory
        questions[tid].update(status="measured", subcalls=len(subs), b_subcalls=len(rows),
                              ended_by_itself=row["ended_by_itself"], **{k: row[k] for k in WITHIN_CAP_0075})
        candidates += rows
    cache.clear()
    eligible: dict = {}
    for r in candidates:
        if r["reason"] is None:
            eligible.setdefault(r["task_id"], []).append(r)
    order = registered_order(eligible, cfg["seed"])
    for r in order[cfg["max_pairs"]:]:
        r["reason"] = "beyond the ceiling"
    for r in candidates:
        r["excluded"] = r["reason"] is not None
        arrays = r.pop("_arrays", None)
        r["file"] = r["sha256"] = r["arrays_sha256"] = None
        if not r["excluded"]:
            stem = r["handoff"].replace("/", "__").replace("<", "_from_").replace(".", "-")
            path = args.inputs / f"{stem}.npz"
            np.savez_compressed(path, **arrays)
            r.update(file=path.name, sha256=digest(path), arrays_sha256=arrays_sha256(arrays))
    ranked = {r["handoff"]: k for k, r in enumerate(order)}
    records = sorted(candidates, key=lambda r: (ranked.get(r["handoff"], len(ranked)), r["handoff"]))
    over = [r for r in candidates if r["reason"] == "over the cap"]
    matched_all = sum(r["matched"] for r in candidates)
    measured = [q for q in questions.values() if q["status"] == "measured"]
    manifest = {"cell": CELL, "built": built, "config_sha256": sha256_text_file(args.config),
                "fab_reuse_config_sha256": sha256_text_file(root / FAB_CONFIG), "sources": sources(root),
                "tokenizer_json_sha256": fab.reader["tokenizer_json_sha256"], "window_end": cfg["window_end"],
                "logs_sha256": hashlib.sha256(json.dumps(sorted(logs.items())).encode()).hexdigest(),
                "files_read": len(logs), "questions": questions, "registered_order": [r["handoff"] for r in order],
                "candidates": len(candidates), "eligible": len(order),
                "selected": sum(1 for r in records if not r["excluded"]),
                "exclusions": {k: sum(1 for r in candidates if r["reason"] == k) for k in EXCLUSIONS},
                "over_the_cap_matched_share": sum(r["matched"] for r in over) / matched_all if matched_all else None,
                "reused_within_cap_0075": {"trajectories": len(measured),
                                           **{k: sum(q[k] for q in measured) for k in WITHIN_CAP_0075}}
                if measured else None,
                "records": records}
    write(args.inputs / "manifest.json", manifest)
    return manifest


def check_manifest(manifest: dict, cfg: dict, config_path: Path, root: Path) -> None:
    if (manifest.get("cell") != CELL or manifest["config_sha256"] != sha256_text_file(config_path)
            or manifest["fab_reuse_config_sha256"] != sha256_text_file(root / FAB_CONFIG)
            or manifest["sources"] != sources(root)):
        raise ValueError("configuration or code changed after preparation")
    selected = [r for r in manifest["records"] if not r["excluded"]]
    if len(selected) != manifest["selected"] or len(selected) > cfg["max_pairs"]:
        raise ValueError("selected pairs differ from the manifest's count or exceed the ceiling")
    if [r["handoff"] for r in selected] != manifest["registered_order"][:len(selected)]:
        raise ValueError("selected pairs are not the registered order's first pairs")


def check_arrays(arrays, row: dict) -> None:
    if arrays_sha256(arrays) != row["arrays_sha256"]:
        raise ValueError(f"input arrays differ from the manifest: {row['handoff']}")
    if (len(arrays["sender"]) != row["sender_tokens"] or len(arrays["receiver"]) != row["receiver_tokens"]
            or len(arrays["pairs"]) != row["matched"] or len(arrays["continuation"]) != row["continuation_tokens"]):
        raise ValueError(f"input lengths differ from the manifest: {row['handoff']}")


def probe_size(row: dict) -> int:
    return max(row["sender_tokens"], row["receiver_tokens"] + row["continuation_tokens"] - 1)


def removal(token_means: np.ndarray, deviation: dict, tau: float) -> dict:
    """f* and the tail at tau_K from per-token means, after the identity check against deviation_means' K."""
    if abs(float(token_means.mean()) - deviation["K"]) > 1e-9 * abs(deviation["K"]):
        raise ValueError(f"per-token deviation mean {token_means.mean()} differs from deviation_means K "
                         f"{deviation['K']}")
    return {"f_star_K": f_star(token_means, tau), "tokens_over_tau_K": int((token_means > tau).sum()),
            "max_token_mean_K": float(token_means.max()), "matched": len(token_means),
            "deviation_means": deviation}


def cross_check_compare(driver_means: np.ndarray, archive_means: np.ndarray, cfg: dict) -> dict:
    """0047's bridge tolerance applied per token, and f* within one token; the tail count is recorded."""
    tau, n = cfg["tau_K"], len(archive_means)
    if driver_means.shape != archive_means.shape:
        raise ValueError("cross-check token sets differ")
    bound = cfg["bridge_absolute_tolerance"] + cfg["bridge_relative_tolerance"] * archive_means
    gap = np.abs(driver_means - archive_means)
    f_driver, f_archive = f_star(driver_means, tau), f_star(archive_means, tau)
    return {"matched": n, "tokens_outside_tolerance": int((gap > bound).sum()), "max_gap": float(gap.max()),
            "max_gap_over_bound": float((gap / bound).max()), "f_star_driver": f_driver, "f_star_archive": f_archive,
            "tokens_over_tau_K_driver": int((driver_means > tau).sum()),
            "tokens_over_tau_K_archive": int((archive_means > tau).sum()),
            "passed": bool((gap <= bound).all() and abs(f_driver - f_archive) <= 1 / n)}


def pair_summary(report: dict, manifest: dict, rows: list[dict]) -> dict:
    """Pair-level medians (the headline) and the median over trajectories of each trajectory's median, pooled and
    per class, with the per-pair rows."""
    meta = {r["handoff"]: r for r in manifest["records"]}
    flat = []
    for r in rows:
        m = meta[r["handoff"]]
        flat.append({"handoff": r["handoff"], "task_id": m["task_id"], "class": m["class"], "probe": r["probe"],
                     "f_star_K": r["removal"]["f_star_K"],
                     **{f"{arm}_{k}": v[k] for arm, v in r["arms"].items() for k in STATS}})
    stats = list(PAIR_STATS)
    if rows and set(rows[0]["arms"]) != {"reuse", "random", "scrambled"}:
        raise ValueError(f"the fab cell reads three arms, not {sorted(rows[0]['arms'])}")

    def block(sel):
        if not sel:
            return None
        by_t: dict = {}
        for x in sel:
            by_t.setdefault(x["task_id"], []).append(x)
        return {"pairs": len(sel), "trajectories": len(by_t),
                "pair_level": {s: summary([x[s] for x in sel]) for s in stats},
                "trajectory_level": {s: summary([statistics.median([x[s] for x in v]) for v in by_t.values()])
                                     for s in stats}}
    cross = report.get("cross_check") or {}
    read = {r["handoff"] for r in rows}
    # Every step started and not finished: those a resume found (`ended_in_flight`), then the one under way when the
    # report was last written, if any.
    in_flight = report.get("ended_in_flight", []) + ([report["in_flight"]] if report.get("in_flight") else [])
    questions: dict = {}
    for tid, q in sorted(manifest["questions"].items()):
        questions.setdefault(q["status"], []).append(tid)
    return {"label": LABEL, "cross_check_label": CROSS_CHECK_LABELS.get(cross.get("branch")),
            "cross_check": cross, "read": len(rows), "selected": manifest["selected"],
            "not_read": [h for h in report["run_order"] if h not in read], "stop_at": report.get("stop_at"),
            "stopped": report.get("stopped"), "ended_in_flight": in_flight,
            "probe_pair": report["run_order"][0] if report["run_order"] else None, "built": manifest["built"],
            "candidates": manifest["candidates"], "eligible": manifest["eligible"],
            "exclusions": manifest["exclusions"],
            "excluded": {k: [r["handoff"] for r in manifest["records"] if r["reason"] == k] for k in EXCLUSIONS},
            "over_the_cap_matched_share": manifest["over_the_cap_matched_share"],
            "reused_within_cap_0075": manifest["reused_within_cap_0075"], "questions": questions,
            "all": block(flat), **{c: block([x for x in flat if x["class"] == c]) for c in CLASSES},
            "per_pair": [{**x, **{k: meta[x["handoff"]][k] for k in PAIR_RECORD_FIELDS},
                          "tokens_over_tau_K": r["removal"]["tokens_over_tau_K"],
                          "max_token_mean_K": r["removal"]["max_token_mean_K"]}
                         for x, r in zip(flat, rows)]}
