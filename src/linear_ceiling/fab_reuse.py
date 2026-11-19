"""Document-reuse OPPORTUNITY in the helper sub-calls of FAB v2 trajectories (ledger entry 0075).

The Finance Agent Benchmark v2 harness (`config/fab-reuse.toml` pins its commit) gives its agent a document store:
`parse_html_page` saves a page's text under a key, and `retrieve_information` sends a prompt to a helper model with
each `{{key}}` replaced, in one `re.sub` pass, by that document's whole text or by `doc[start:end]` when the call
names a character range for the key. The result is one user message with no system prompt and no tools, and the
harness sends it with prompt caching OFF. A document's text reaches a model only inside these sub-calls.

This module counts, per trajectory, the tokens of document text that a sub-call carries and that an EARLIER sub-call
of the same trajectory already carried. That count is the reuse OPPORTUNITY: an UPPER BOUND on the document KV that a
cache keyed on the retrieved document could have reused across the trajectory's sub-calls. A cache keyed on content
could reuse more, since identical text inside a different document is not counted. Prefix-shared tokens are
reported beside the count and are not bounded by it. The sub-calls were sent with prompt caching off, so nothing
here is a realized saving. No carryover effect, key statistic or KL is read. Counts are in the registered READER's tokenizer
(Qwen3-1.7B, `[fab_reuse.reader]`), not the serving model's.

Beside it, from the same logs and each under its own label, it describes where the input goes (the helper sub-calls'
share of the input tokens), the main loop's realized caching (both in the provider's own token counts) and the time
between a document's carryings (estimated from the logs' times). None of these is compared with the reuse counts:
they are in another tokenizer or another unit.

Definitions, as registered:

- Trajectory: one harness run on one public question: a log directory holding `turns/init/` and at least one
  answered turn, a `turns/turn_NNN/` holding `result.json` (the harness writes it when the turn's query succeeds,
  before any tool runs, and rewrites it after each tool). Its task id is `task_id_format` filled with the question's
  1-based row in the pinned `public.csv`. A directory with `turns/init/` and no answered turn (no turn, or only
  turns whose query failed, which hold the harness's `error.json` alone) is a FAILED LAUNCH (no answer of the model
  was recorded); it is counted and named, and it is not a trajectory. A directory WITHOUT `turns/init/` is not
  seen at all: it is neither a trajectory nor a failed launch, and it is not refused even when its name is outside
  the cohort (the run's private wrapper record counts every launch). One trajectory per question; a question with
  none is NOT RUN, and a question with two refuses the summary, as does a trajectory whose `turns/init/config.json`
  names a serving model other than `[fab_reuse.harness] model`.
- Sub-call: one `turns/turn_NNN/helper_queries/tool_NNN/` record, i.e. a `retrieve_information` call whose helper
  response the harness logged. A call the tool refused before sending (a missing key, a bad range) and a call whose
  helper query failed leave no record and are not sub-calls. Sub-calls are ordered by (turn, tool index); the tools
  of a turn run one at a time, in the order of the turn's `tool_call_records`.
- Rebuilt prompt: from the record's `tool_call.parsed_args` (`prompt`, `input_character_ranges`) and, for each key
  it names, the document the store held when the call ran, fixed by the turn's ordered tool records. If a
  successful `parse_html_page` call earlier in the same turn wrote the key, it is the key's value in the turn's
  `state.json`, unless another wrote it later in that turn too: then the value is in no snapshot, and the trajectory
  is NOT MEASURABLE ("reconstruction"). Otherwise it is the key's value in the latest earlier snapshot (`init`, or
  the last earlier answered turn's `state.json`; a turn whose query failed holds `error.json` alone, runs no
  tool and changes nothing). The
  harness's own substitution must then give, byte for byte, the text the record's `history.json` logs as sent, or
  the trajectory is NOT MEASURABLE ("reconstruction"). The sent text itself is what is tokenized; the rebuild only
  locates the inserted spans and their documents.
- Document token: a token of the sent prompt whose character span is non-empty and lies wholly inside one inserted
  span (a token with empty offsets carries no text and is none). Its
  IDENTITY is (the retrieved document's sha256, the token's start and end character in that document, its token
  id); a page parsed again with changed text is another document. A token that straddles a span edge is template
  text. A span's edges are its first character and the character just after its end. If the tokenizer's offsets
  leave an edge character covered by no token, or it has a nonzero canonical combining class (normalization can
  fold either into a neighbouring token), the edge cannot be placed and the trajectory is NOT MEASURABLE
  ("tokenization"). An empty span has no edge to place.
- Same offset: an earlier sub-call of the trajectory carried the same identity at the same token index, the index
  in the logged prompt, template text included. Different offset: an earlier sub-call carried the identity, only
  at other indices. New: no earlier sub-call carried it. Two places of one identity within one sub-call never
  count as reuse of each other: each is compared with the earlier sub-calls only.
- Within the cap (descriptive): of the SAME and DIFFERENT OFFSET tokens, those in a sub-call whose prompt is at most
  `[fab_reuse.reader] context_cap` reader tokens (the reader's registered context cap), and those for which the
  latest earlier sub-call that carried a document token of the same document is within the cap too. Each is
  reported as a count and as a share of the trajectory's SAME plus DIFFERENT OFFSET tokens.
- Prefix-shared (descriptive): the longest common token-id prefix of a sub-call's prompt with any earlier
  sub-call's prompt of the trajectory, over all its tokens. It is what an exact prefix cache could serve, before
  block granularity.
- NOT MEASURABLE, never a zero: no sub-call read (none logged, or all in a set-aside turn); no document token over all
  sub-calls; a sub-call not rebuilt; a sent
  prompt the reader's tokenizer cannot encode or whose span edges it cannot place; a record that is missing,
  truncated or not JSON, a turn that holds neither its result record nor the error record alone, turn numbers that
  do not run 1, 2, 3 without a gap, or a sub-call record its turn's tool records do not yet list (the process ended
  between the two writes) ("unreadable record"). A trajectory with one sub-call is measured (no earlier sub-call, so
  its reuse is zero by construction) and its sub-call count is reported.
- Ended without its final record: a log directory with no root `result.json` (the wrapper ended the process at its
  wall-time end or its token ceiling, `[fab_reuse.run]`, or the process died). Its LAST turn directory is the turn
  under way when it ended, whose records may be cut short: that turn is SET ASIDE. None of its records is read, its
  sub-calls are counted as `cut_subcalls`, and every measure is taken over the turns before it, by the same rules
  as any trajectory. A trajectory that ends with its final record has nothing set aside.
- Ended by itself: the final record's `stop_reason` is `done_tool` or `should_stop`, the two ends no limit or error
  made (at the pin the harness never stops on `should_stop`). Any other trajectory (the harness's own `max_time`,
  which writes a final record, `max_turns` or `error`, or `absent`) is read over the turns it completed before it
  was stopped. Every aggregate is reported over all trajectories and, beside it, over those that ended by
  themselves; the others are listed with their stop reasons.
- Input share (descriptive, the provider's tokens): a call's input tokens are its usage record's `in_tokens +
  cache_read_tokens + cache_write_tokens`, as the provider reports them for the call's successful attempt. The
  share is the helper sub-calls' input tokens over those of the helper sub-calls and the main agent's turn queries
  together. Compaction calls (none is configured at the pin) are on neither side; their usage, as the final record
  lists it, is reported apart. A failed query and a failed helper call leave no usage and are not counted. Reported
  for every trajectory whose records are readable, whatever its reuse reason; null when any record, a helper's
  included, cannot be read.
- Realized caching on the main loop (descriptive, the provider's tokens): the main agent's turn queries'
  `cache_read_tokens` over their input tokens. At the pin the main loop keeps the library's default prompt caching
  (five minutes) and the helper runs with it off. With questions run at once, which share one system prompt and
  tool set, a turn query's cache read can include a prefix another question wrote. Reported as the input share is.
- Reuse gap (descriptive, an estimate in seconds): a sub-call's start is estimated as its turn's `timestamp`
  (written when the turn's query returned, before its tools ran) plus the `duration_seconds` of the turn's tool
  records before it; the estimate leaves out the harness's own log writes between tools. For each sub-call of a
  measured trajectory and each document with a SAME or DIFFERENT OFFSET token in it, the gap is the sub-call's
  estimated start minus that of the latest earlier sub-call carrying a document token of that document, in
  seconds to the millisecond. Reported: the gaps' median, p10 and p90, and the share of gaps at most each of
  `[fab_reuse.timing] cache_lifetimes_seconds`, the provider's two published prompt-cache lifetimes. A trajectory
  whose turn records lack a time-zone-aware `timestamp` or a tool record's `duration_seconds` is UNTIMED: it has
  no gap and is named.
- Question type: `public.csv`'s `[fab_reuse.run] question_type_column`; the summary lists every row under its type.

Not counted, and said so wherever a figure is used: text that reaches a sub-call by any other route (the agent
copying document text into its prompt, an answer quoting a document), identical text inside a different document,
reuse across trajectories, the main agent's own calls (in the reuse counts; the input share and the realized
caching read only their usage), and helper calls that failed. Character offsets are used to locate tokens and are
not reported.

Files: every JSON file is read as `NAME.json` or `NAME.json.gz` (the run's wrapper may gzip `state.json` after
hashing it); exactly one of the two must exist. The summary records the sha256 of every file's decompressed
bytes, so the run's own manifest can be compared with what was read, and the sha256 of this module, its test and
its config. The command reads `config/fab-reuse.toml` and no other config.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
import subprocess
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from linear_ceiling import REPO_ROOT
from linear_ceiling.e7_stats import summary
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file

PLACEHOLDER = re.compile(r"{{([^{}]+)}}")      # finance_agent/tools.py at the pinned commit, both uses
TOOL = "retrieve_information"
WRITER = "parse_html_page"
# parse_html_page's success text at the pin; an overwrite puts a WARNING line before it
WRITTEN = "SUCCESS: The result has been saved to the data storage under the key:"
SOURCES = ("src/linear_ceiling/fab_reuse.py", "tests/test_fab_reuse.py")
REASONS = ("no sub-call", "no document token", "reconstruction", "tokenization", "unreadable record")
ENDED = ("done_tool", "should_stop")             # model-library's AgentStopReason values that no limit or error sets
COUNTS = ("prompt_tokens", "document_tokens", "same_offset", "different_offset", "new", "prefix_shared",
          "reused_in_capped_prompts", "reused_in_capped_pairs")
FRACTIONS = ("reused_fraction", "same_offset_fraction", "different_offset_fraction", "new_fraction",
             "prefix_shared_fraction", "capped_prompt_share", "capped_pair_share")
LABEL = ("reuse OPPORTUNITY: an upper bound on the document KV a cache keyed on the retrieved document's sha256 "
         "could reuse across a trajectory's logged sub-calls, which the harness sent with prompt caching off; not a "
         "realized saving; a cache keyed on content "
         "could reuse more, and prefix_shared is not bounded by it; no carryover, key or KL statistic; counts in the "
         "reader's tokenizer (Qwen3-1.7B), not the serving model's; a trajectory that did not end by itself is read "
         "over the turns it completed, and aggregates_ended_by_itself leaves it out")
LABELS = {
    "input_share": "input SHARE: the helper sub-calls' input tokens over those of the helper sub-calls and the main "
                   "agent's turn queries, in the provider's counts; descriptive; not compared with the reuse counts "
                   "(another tokenizer)",
    "main_loop_caching": "REALIZED caching on the main loop: cache-read input tokens over all input tokens of the main "
                         "agent's turn queries, in the provider's counts; the main loop only; the helper sub-calls, "
                         "which carry the documents, were sent with prompt caching off; with questions run at once, a "
                         "cache read can include a prefix another question wrote",
    "reuse_gap": "reuse GAP: the estimated start-to-start time from the latest earlier sub-call that carried the same "
                 "document (turn timestamps plus tool durations, leaving out the harness's log writes); descriptive; "
                 "not a cache hit",
    "by_question_type": "the trajectories under their question type; listed, not compared",
}
USAGE = ("main_input_tokens", "main_cache_read_tokens", "helper_input_tokens", "compaction_input_tokens",
         "input_share_helper", "main_cache_read_fraction")
# Every field summary.json holds, by level; the entry names each, and a test holds the summary to these lists.
ROW_FIELDS = ("task_id", "row", "question_type", "stop_reason", "ended_by_itself", "serving_model", "turns",
              "error_turns", "final_record", "set_aside_turn", "cut_subcalls", "subcalls", *COUNTS, "documents", "measurable",
              "reason", *FRACTIONS, *USAGE, "reuse_gaps_seconds", "files")
SUMMARY_FIELDS = ("label", "labels", "harness_commit", "model", "reader", "cohort", "run", "not_run", "measured",
                  "not_measurable", "failed_launches", "trajectories", "by_question_type", "per_trajectory",
                  "pooled", "input_share", "main_loop_caching", "reuse_gap", "aggregates_ended_by_itself",
                  "not_ended_by_itself", "sources")
AGGREGATES = ("per_trajectory", "pooled", "input_share", "main_loop_caching", "reuse_gap")
NESTED_FIELDS = {
    "aggregates_ended_by_itself": ("trajectories", "measured", *AGGREGATES),
    "not_ended_by_itself": ("task_id", "stop_reason"),
    "reader": ("model", "revision", "tokenizer_json_sha256", "context_cap", "tokenizers_version"),
    "per_trajectory": ("reused_fraction", "same_offset_fraction", "different_offset_fraction", "new_fraction",
                       "subcalls"),
    "pooled": (*COUNTS, *FRACTIONS),
    "input_share": ("trajectories", "main_input_tokens", "helper_input_tokens", "pooled", "per_trajectory",
                    "compaction_input_tokens", "compaction_unknown"),
    "main_loop_caching": ("trajectories", "main_cache_read_tokens", "main_input_tokens", "pooled", "per_trajectory"),
    "reuse_gap": ("trajectories", "untimed", "gaps", "seconds", "share_within"),
    "summary": ("n", "median", "p10", "p90"),
}


@dataclass(frozen=True)
class FabReuseConfig:
    config_path: Path
    results_dir: Path
    cohort: int
    task_id_format: str
    required_entries: tuple[str, ...]
    harness: dict
    reader: dict
    run: dict = field(default_factory=dict)
    timing: dict = field(default_factory=dict)


def load_config(path: Path, repo_root: Path = REPO_ROOT) -> FabReuseConfig:
    path = Path(path)
    raw = tomllib.loads(path.read_text(encoding="utf-8"))["fab_reuse"]
    req = tuple(str(x) for x in raw["gate"]["required_entries"])
    if not req or not all(re.fullmatch(r"\d{4}", r) for r in req):
        raise ValueError(f"{path.name} [fab_reuse.gate] required_entries must be four-digit entry numbers")
    for k in ("commit", "tarball_sha256", "questions_csv_sha256", "model_library", "model", "max_time_seconds"):
        if k not in raw["harness"]:
            raise ValueError(f"{path.name} [fab_reuse.harness] lacks {k}")
    for k in ("model", "revision", "tokenizer_json_sha256"):
        if k not in raw["reader"]:
            raise ValueError(f"{path.name} [fab_reuse.reader] lacks {k}")
    fmt = str(raw["task_id_format"])
    if fmt.format(row=1) == fmt.format(row=2):
        raise ValueError("task_id_format must depend on the row")
    cohort = int(raw["cohort"])
    run, timing = dict(raw["run"]), dict(raw["timing"])
    if sorted(run["order"]) != list(range(1, cohort + 1)):
        raise ValueError(f"{path.name} [fab_reuse.run] order must list rows 1..{cohort}, each once")
    ceiling = run["token_ceiling"]
    if not (ceiling == "UNSET" or (isinstance(ceiling, int) and not isinstance(ceiling, bool) and ceiling > 0)):
        raise ValueError(f"{path.name} [fab_reuse.run] token_ceiling must be a positive integer or UNSET")
    par = run["max_parallel"]
    if not (par == "UNSET" or (isinstance(par, int) and not isinstance(par, bool) and par > 0)):
        raise ValueError(f"{path.name} [fab_reuse.run] max_parallel must be a positive integer or UNSET")
    dt.datetime.strptime(run["last_start_utc"], "%Y-%m-%dT%H:%M:%SZ")
    for k in ("wall_seconds", "disk_floor_gb", "poll_seconds"):
        if not (isinstance(run[k], int) and not isinstance(run[k], bool) and run[k] > 0):
            raise ValueError(f"{path.name} [fab_reuse.run] {k} must be a positive integer")
    if not isinstance(run["question_type_column"], str):
        raise ValueError(f"{path.name} [fab_reuse.run] question_type_column must be a string")
    cap = raw["reader"]["context_cap"]
    if not (isinstance(cap, int) and not isinstance(cap, bool) and cap > 0):
        raise ValueError(f"{path.name} [fab_reuse.reader] context_cap must be a positive integer")
    life = timing["cache_lifetimes_seconds"]
    if not (isinstance(life, list) and life and all(isinstance(x, int) and x > 0 for x in life)):
        raise ValueError(f"{path.name} [fab_reuse.timing] cache_lifetimes_seconds must be positive integers")
    return FabReuseConfig(config_path=path, results_dir=Path(repo_root) / raw["results_dir"], cohort=cohort,
                          task_id_format=fmt, required_entries=req, harness=dict(raw["harness"]),
                          reader=dict(raw["reader"]), run=run, timing=timing)


def _pinned(cfg: FabReuseConfig, root: Path) -> tuple[str, ...]:
    return ("ledger/ledger.md", cfg.config_path.resolve().relative_to(root).as_posix(), *SOURCES)


def assert_ready(cfg: FabReuseConfig, repo_root: Path) -> None:
    """Refuse before any log is opened unless the ledger, this config, this module and its test are committed as-is,
    the committed ledger holds every entry `[fab_reuse.gate]` names, and the serving model, the per-question token
    ceiling and the number of questions run at once are set (not UNSET)."""
    root = Path(repo_root).resolve()
    for rel in _pinned(cfg, root):
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=root, capture_output=True)
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=root)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise RuntimeError(f"FAB-REUSE REFUSED: {rel} is not committed as-is")
    committed = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=root, capture_output=True,
                               text=True, encoding="utf-8")
    if committed.returncode != 0:
        raise RuntimeError("FAB-REUSE REFUSED: cannot read HEAD:ledger/ledger.md")
    for num in cfg.required_entries:
        if f"### {num} " not in committed.stdout:
            raise RuntimeError(f"FAB-REUSE REFUSED: committed ledger has no entry {num}; register before measuring")
    if cfg.harness["model"] == "UNSET":
        raise RuntimeError("FAB-REUSE REFUSED: [fab_reuse.harness] model is UNSET")
    for k in ("token_ceiling", "max_parallel"):
        if cfg.run.get(k, "UNSET") == "UNSET":
            raise RuntimeError(f"FAB-REUSE REFUSED: [fab_reuse.run] {k} is UNSET")


class _Unbuilt(Exception):
    pass


class _Unreadable(Exception):
    pass


def read_json(path: Path, files: dict, root: Path, required: bool = True):
    """Read `path` or `path.gz`; record the decompressed bytes' sha256 under the plain name in `files`. Both
    present refuses (ValueError); a missing required file, bad gzip, bad UTF-8 or bad JSON is _Unreadable."""
    gz = path.with_name(path.name + ".gz")
    plain, packed = path.is_file(), gz.is_file()
    if plain and packed:
        raise ValueError(f"both {path.name} and {gz.name} exist under {path.parent}")
    if not (plain or packed):
        if required:
            raise _Unreadable(f"{path} is missing")
        return None
    try:
        raw = path.read_bytes() if plain else gzip.decompress(gz.read_bytes())
        files[path.relative_to(root).as_posix()] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw.decode("utf-8"))
    except (OSError, EOFError, ValueError) as e:      # BadGzipFile is an OSError; JSON and UTF-8 errors ValueErrors
        raise _Unreadable(f"{path}: {type(e).__name__}") from None


def _present(path: Path) -> bool:
    """`path` or `path.gz` exists (read_json's two forms)."""
    return path.is_file() or path.with_name(path.name + ".gz").is_file()


def _numbered(parent: Path, prefix: str) -> list[tuple[int, Path]]:
    if not parent.is_dir():
        return []
    out = []
    for d in parent.iterdir():
        m = re.fullmatch(prefix + r"_(\d{3,})", d.name)
        if d.is_dir() and m:
            out.append((int(m.group(1)), d))
    return sorted(out)


def _doc_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()


def _usage(md) -> tuple[int, int] | None:
    """(input tokens, cache-read tokens) from a usage record (QueryResultMetadata as dumped), or None if it is not one."""
    if not isinstance(md, dict):
        return None
    parts = [md.get("in_tokens"), md.get("cache_read_tokens") or 0, md.get("cache_write_tokens") or 0]
    if not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in parts):
        return None
    return sum(parts), parts[1]


def _query_usage(rec) -> tuple[int, int] | None:
    qr = rec.get("query_result") if isinstance(rec, dict) else None
    return _usage(qr.get("metadata")) if isinstance(qr, dict) else None


def _times(res, recs) -> tuple[float, list[float]] | None:
    """(the turn's timestamp in POSIX seconds, its tool records' durations), or None if either is not logged."""
    ts = res.get("timestamp") if isinstance(res, dict) else None
    durs = [r.get("duration_seconds") if isinstance(r, dict) else None for r in recs]
    if not isinstance(ts, str) or not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in durs):
        return None
    try:
        t = dt.datetime.fromisoformat(ts)
    except ValueError:
        return None
    if t.tzinfo is None:
        return None
    return t.timestamp(), [float(x) for x in durs]


def _call(record) -> tuple[str | None, object]:
    tc = record.get("tool_call") if isinstance(record, dict) else None
    return (tc.get("name"), tc.get("parsed_args")) if isinstance(tc, dict) else (None, None)


def _writes(record, key: str) -> bool:
    """True if this tool record is a parse_html_page call that saved `key` to the store."""
    name, args = _call(record)
    out = record.get("tool_output") if isinstance(record, dict) else None
    return (name == WRITER and isinstance(args, dict) and args.get("key") == key and isinstance(out, dict)
            and not out.get("error") and isinstance(out.get("output"), str) and WRITTEN in out["output"])


def rebuild(args, sent: str, records: list, index: int, after, before) -> list[tuple[int, int, str, int]]:
    """Inserted spans of the sent prompt as (prompt start, prompt end, document sha256, document start). Each key's
    document is the store's value when tool `index` of the turn ran: `after` (the turn's snapshot) if a successful
    write of the key came earlier in the turn and none later, `before` (the latest earlier snapshot) if none came
    earlier. Raises _Unbuilt if that cannot be fixed or the harness's substitution does not give `sent`."""
    if not (0 <= index < len(records) and _call(records[index]) == (TOOL, args)):
        raise _Unbuilt("the turn's tool records do not place this sub-call")
    template = args.get("prompt") if isinstance(args, dict) else None
    if not isinstance(template, str):
        raise _Unbuilt("no prompt in the tool call's args")
    ranges = {}
    try:
        for spec in args.get("input_character_ranges") or []:   # later specs for a key win, as in the harness's dict
            ranges[spec["key"]] = (spec["start"], spec["end"])
    except (TypeError, KeyError, AttributeError) as e:
        raise _Unbuilt(f"input_character_ranges not as the harness reads them: {e}") from None
    keys = list(dict.fromkeys(PLACEHOLDER.findall(template)))
    if not keys:
        raise _Unbuilt("no placeholder in the prompt")
    doc = {}
    for k in keys:
        writes = [j for j, r in enumerate(records) if _writes(r, k)]
        if any(j < index for j in writes) and any(j > index for j in writes):
            raise _Unbuilt(f"key {k!r} written both before and after the sub-call in its turn")
        store = after if any(j < index for j in writes) else before
        v = store.get(k) if isinstance(store, dict) else None
        if not isinstance(v, str):
            raise _Unbuilt(f"key {k!r} is not in the snapshot the call saw")
        doc[k] = v
    parts, spans, pos, last = [], [], 0, 0
    try:
        for m in PLACEHOLDER.finditer(template):
            lit = template[last:m.start()]
            parts.append(lit)
            pos += len(lit)
            content = doc[m.group(1)]
            if m.group(1) in ranges:
                s, e = ranges[m.group(1)]
                piece = content[s:e]
                d0 = slice(s, e).indices(len(content))[0]
            else:
                piece, d0 = content, 0
            spans.append((pos, pos + len(piece), _doc_sha(content), d0))
            parts.append(piece)
            pos += len(piece)
            last = m.end()
    except (TypeError, ValueError):
        raise _Unbuilt("a range the harness could not have sliced") from None
    parts.append(template[last:])
    if "".join(parts) != sent:
        raise _Unbuilt("the rebuilt text differs from the sent text")
    return spans


def document_tokens(sent: str, spans, ids, offsets) -> list[tuple[int, str, int, int, int]] | None:
    """The document tokens of one sent prompt, in prompt order: (token index in the prompt, document sha256, start and
    end character in the document, token id). `spans` is `rebuild`'s list of inserted spans; `ids` and `offsets` are
    the reader's encoding of `sent` (code-point offsets, no special tokens). A token is a document token if its offsets
    are non-empty and lie wholly inside one span. None if a span edge cannot be placed: an edge character (a span's
    first character or the one just after its end) that no token's offsets cover, or that has a nonzero canonical
    combining class."""
    covered = np.zeros(len(sent), dtype=bool)
    for a, b in offsets:
        covered[a:b] = True
    if any(x < len(sent) and (not covered[x] or unicodedata.combining(sent[x]))
           for s0, s1, _, _ in spans if s1 > s0 for x in (s0, s1)):
        return None
    out = []
    si = 0
    for p, (tid, (a, b)) in enumerate(zip(ids, offsets)):
        while si < len(spans) and spans[si][1] <= a:
            si += 1
        if not (si < len(spans) and a < b and spans[si][0] <= a and b <= spans[si][1]):
            continue
        s0, _, sha, d0 = spans[si]
        out.append((p, sha, d0 + a - s0, d0 + b - s0, int(tid)))
    return out


def _lcp(a: np.ndarray, b: np.ndarray) -> int:
    n = min(len(a), len(b))
    diff = np.flatnonzero(a[:n] != b[:n])
    return int(diff[0]) if len(diff) else n


def measure_trajectory(qdir: Path, encode, root: Path, cap: int | None = None) -> dict:
    """One trajectory's counts. `encode(text) -> (ids, offsets)` with code-point offsets, no special tokens; `cap`, the
    reader's context cap in tokens (None: the within-cap counts are not taken)."""
    files: dict = {}
    turns_dir = qdir / "turns"
    init = turns_dir / "init"
    if not init.is_dir():
        raise ValueError(f"{qdir} has no turns/init")
    turn_dirs = _numbered(turns_dir, "turn")
    final = _present(qdir / "result.json")
    cut = turn_dirs[-1][0] if (turn_dirs and not final) else None     # the turn under way when the process ended
    helpers = [(n, i, hdir) for n, tdir in turn_dirs if n != cut
               for i, hdir in _numbered(tdir / "helper_queries", "tool")]
    row = {"stop_reason": "absent", "ended_by_itself": False, "serving_model": None, "turns": len(turn_dirs),
           "error_turns": 0,
           "final_record": final, "set_aside_turn": cut,
           "cut_subcalls": len(_numbered(turn_dirs[-1][1] / "helper_queries", "tool")) if cut else 0,
           "subcalls": len(helpers), **{k: 0 for k in COUNTS}}
    reason = None
    context: dict = {}
    times: dict = {}
    use = {"main": [0, 0], "helper": 0, "ok": True}
    compaction = None
    try:
        end = read_json(qdir / "result.json", files, root, required=False)
        row["stop_reason"] = (end or {}).get("stop_reason", "absent") if isinstance(end, dict) else "absent"
        row["ended_by_itself"] = final and row["stop_reason"] in ENDED
        if final:
            comps = end.get("compactions") if isinstance(end, dict) else None
            compaction = 0
            for c in comps or []:                # a failed attempt has no metadata and no usage
                md = c.get("metadata") if isinstance(c, dict) else False
                if md is None:
                    continue
                u = _usage(md)
                if u is None:
                    compaction = None
                    break
                compaction += u[0]
        conf = read_json(init / "config.json", files, root)
        llm = conf.get("llm") if isinstance(conf, dict) else None
        key = llm.get("_registry_key") if isinstance(llm, dict) else None
        if not isinstance(key, str):
            raise ValueError(f"{init}/config.json names no serving model (llm._registry_key)")
        row["serving_model"] = key
        last = read_json(init / "state.json", files, root)
        if [n for n, _ in turn_dirs] != list(range(1, len(turn_dirs) + 1)):
            raise _Unreadable(f"{turns_dir}: turn numbers do not run 1..{len(turn_dirs)} without a gap")
        for n, tdir in turn_dirs:
            if n == cut:                         # set aside: none of its records is read
                continue
            res = read_json(tdir / "result.json", files, root, required=False)
            if res is None:                      # a turn whose query failed: error.json alone, no tool, no store change
                err = read_json(tdir / "error.json", files, root, required=False)
                if err is None or _present(tdir / "state.json") or _numbered(tdir / "helper_queries", "tool"):
                    raise _Unreadable(f"{tdir} holds neither result.json nor the error record alone")
                row["error_turns"] += 1
                continue
            if _present(tdir / "error.json"):
                raise _Unreadable(f"{tdir} holds both result.json and error.json")
            after = read_json(tdir / "state.json", files, root)
            recs = res.get("tool_call_records") if isinstance(res, dict) else None
            if not isinstance(recs, list):
                raise _Unreadable(f"{tdir}/result.json holds no tool_call_records")
            context[n] = (recs, after, last)
            last = after
            u = _query_usage(res)
            if u is None:
                use["ok"] = False
            else:
                use["main"][0] += u[0]
                use["main"][1] += u[1]
            times[n] = _times(res, recs)
    except _Unreadable:
        reason = "unreadable record"
    seen: dict = {}
    doc_idx: dict = {}
    prior_ids: list = []
    last_start: dict = {}                        # document index -> estimated start of the latest sub-call carrying it
    last_len: dict = {}                          # document index -> prompt tokens of the latest sub-call carrying it
    gaps: list | None = []
    for n, i, hdir in helpers:
        try:
            rec = read_json(hdir / "result.json", files, root)
            hist = read_json(hdir / "history.json", files, root)
        except _Unreadable:                      # its usage cannot be read either: (a) and (b) are null
            reason = reason or "unreadable record"
            use["ok"] = False
            continue
        name, args = _call(rec)
        if name is None:
            reason = reason or "unreadable record"
            use["ok"] = False
            continue
        if name != TOOL:
            raise ValueError(f"{hdir}: a helper record of tool {name!r}; the pinned harness has one, {TOOL}")
        u = _query_usage(rec)
        if u is None:
            use["ok"] = False
        else:
            use["helper"] += u[0]
        if reason:
            continue
        if not (isinstance(hist, list) and hist and isinstance(hist[0], dict) and hist[0].get("kind") == "text"
                and isinstance(hist[0].get("text"), str)):
            reason = "reconstruction"
            continue
        sent = hist[0]["text"]
        recs, after, before = context[n]
        if i >= len(recs):                       # the helper was written, the turn's record not yet rewritten
            reason = "unreadable record"
            continue
        try:
            spans = rebuild(args, sent, recs, i, after, before)
        except _Unbuilt:
            reason = "reconstruction"
            continue
        try:
            ids, offsets = encode(sent)
            ids = np.asarray(ids, dtype=np.int64)
            offsets = [(int(a), int(b)) for a, b in offsets]
            if len(offsets) != len(ids):
                raise ValueError("ids and offsets differ in length")
        except Exception:
            reason = "tokenization"
            continue
        toks = document_tokens(sent, spans, ids.tolist(), offsets)
        if toks is None:
            reason = "tokenization"
            continue
        row["prompt_tokens"] += len(ids)
        row["prefix_shared"] += max((_lcp(ids, p) for p in prior_ids), default=0)
        prior_ids.append(ids)
        tm = times.get(n)
        start = tm[0] + sum(tm[1][:i]) if tm else None
        carried, reused = set(), set()
        fits = cap is not None and len(ids) <= cap
        pending = []
        for p, sha, c0, c1, tid in toks:
            di = doc_idx.setdefault(sha, len(doc_idx))
            ident = (di, c0, c1, tid)
            before_at = seen.get(ident)
            carried.add(di)
            if before_at is None:
                row["new"] += 1
            elif p in before_at:
                row["same_offset"] += 1
                reused.add(di)
            else:
                row["different_offset"] += 1
                reused.add(di)
            if before_at is not None and fits:
                row["reused_in_capped_prompts"] += 1
                row["reused_in_capped_pairs"] += last_len[di] <= cap
            pending.append((ident, p))
        row["document_tokens"] += len(pending)
        for ident, p in pending:                 # this sub-call's places join `seen` only after all are compared
            seen.setdefault(ident, set()).add(p)
        for d in carried:
            last_len[d] = len(ids)
        if start is None or gaps is None:
            gaps = None
        else:
            gaps += [round(start - last_start[d], 3) for d in sorted(reused)]
            for d in carried:
                last_start[d] = start
    if reason is None and row["subcalls"] == 0:
        reason = "no sub-call"
    if reason is None and row["document_tokens"] == 0:
        reason = "no document token"
    row["measurable"] = reason is None
    row["reason"] = reason
    row["documents"] = len(doc_idx) if reason is None else None
    if reason != "unreadable record" and use["ok"]:
        mi, mc, hi = use["main"][0], use["main"][1], use["helper"]
        row.update({"main_input_tokens": mi, "main_cache_read_tokens": mc, "helper_input_tokens": hi,
                    "compaction_input_tokens": compaction,
                    "input_share_helper": hi / (hi + mi) if hi + mi else None,
                    "main_cache_read_fraction": mc / mi if mi else None})
    else:
        row.update({k: None for k in USAGE})
    row["reuse_gaps_seconds"] = gaps if reason is None else None
    if reason:                                   # an unmeasurable trajectory carries no partial counts
        row.update({k: None for k in (*COUNTS, *FRACTIONS)})
    else:
        d = row["document_tokens"]
        rz = row["same_offset"] + row["different_offset"]
        if cap is None:
            row.update({"reused_in_capped_prompts": None, "reused_in_capped_pairs": None})
        row.update({"capped_prompt_share": row["reused_in_capped_prompts"] / rz if cap is not None and rz else None,
                    "capped_pair_share": row["reused_in_capped_pairs"] / rz if cap is not None and rz else None})
        row.update({"reused_fraction": (row["same_offset"] + row["different_offset"]) / d,
                    "same_offset_fraction": row["same_offset"] / d,
                    "different_offset_fraction": row["different_offset"] / d,
                    "new_fraction": row["new"] / d,
                    "prefix_shared_fraction": row["prefix_shared"] / row["prompt_tokens"]})
    row["files"] = files
    return row


def find_trajectories(runs: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    """(trajectories, failed launches) under `runs`, by directory name (the harness's question id): a directory
    holding `turns/init/` is a trajectory if it also holds an answered turn (a `turns/turn_NNN/` with `result.json`),
    else a failed launch."""
    traj: dict[str, list[Path]] = {}
    failed: dict[str, list[Path]] = {}
    for init in sorted(Path(runs).rglob("init")):
        if init.is_dir() and init.parent.name == "turns":
            q = init.parent.parent
            done = any(_present(t / "result.json") for _, t in _numbered(q / "turns", "turn"))
            (traj if done else failed).setdefault(q.name, []).append(q)
    return traj, failed


def summarize(cfg: FabReuseConfig, runs: Path, questions_csv: Path, encode) -> dict:
    """The cohort summary. Refuses on a questions file that is not the pinned one, on a task id that is not a cohort
    row, on two trajectories for one question, and on a trajectory of another serving model."""
    if sha256_file_bytes(questions_csv) != cfg.harness["questions_csv_sha256"]:
        raise ValueError("questions file is not the pinned public.csv")
    import csv
    col = cfg.run["question_type_column"]
    with open(questions_csv, encoding="utf-8", newline="") as fh:
        qrows = list(csv.DictReader(fh))
    n_rows = len(qrows)
    if n_rows != cfg.cohort:
        raise ValueError(f"public.csv has {n_rows} questions, the cohort is {cfg.cohort}")
    if any(col not in q for q in qrows):
        raise ValueError(f"public.csv has no column {col!r}")
    qtype = {r: qrows[r - 1][col] for r in range(1, cfg.cohort + 1)}
    ids = {cfg.task_id_format.format(row=r): r for r in range(1, cfg.cohort + 1)}
    found, failed = find_trajectories(runs)
    stray = sorted((set(found) | set(failed)) - set(ids))
    if stray:
        raise ValueError(f"log directories outside the cohort: {stray}")
    twice = sorted(k for k, v in found.items() if len(v) > 1)
    if twice:
        raise ValueError(f"more than one trajectory for {twice}; one run per question")
    rows, not_run = [], []
    for tid, r in ids.items():
        if tid not in found:
            not_run.append(tid)
            continue
        row = measure_trajectory(found[tid][0], encode, Path(runs), cap=cfg.reader["context_cap"])
        if row["serving_model"] is not None and row["serving_model"] != cfg.harness["model"]:
            raise ValueError(f"{tid} was served by {row['serving_model']!r}, "
                             f"not the registered {cfg.harness['model']!r}")
        rows.append({"task_id": tid, "row": r, "question_type": qtype[r], **row})
    meas = [x for x in rows if x["measurable"]]
    out = {"label": LABEL, "labels": LABELS, "harness_commit": cfg.harness["commit"], "model": cfg.harness["model"],
           "reader": {k: cfg.reader[k] for k in ("model", "revision", "tokenizer_json_sha256", "context_cap")},
           "cohort": cfg.cohort, "run": len(rows), "not_run": not_run, "measured": len(meas),
           "not_measurable": {k: sum(1 for x in rows if x["reason"] == k) for k in REASONS},
           "failed_launches": {k: len(v) for k, v in sorted(failed.items())},
           "trajectories": rows}
    by_type: dict = {}
    for tid, r in ids.items():
        by_type.setdefault(qtype[r], {"run": [], "not_run": []})["run" if tid in found else "not_run"].append(tid)
    out["by_question_type"] = by_type
    out.update(_aggregates(rows, cfg))
    own = [x for x in rows if x["ended_by_itself"]]
    out["aggregates_ended_by_itself"] = {"trajectories": len(own), "measured": sum(1 for x in own if x["measurable"]),
                                         **_aggregates(own, cfg)}
    out["not_ended_by_itself"] = [{"task_id": x["task_id"], "stop_reason": x["stop_reason"]}
                                  for x in rows if not x["ended_by_itself"]]
    return out


def _aggregates(rows: list, cfg: FabReuseConfig) -> dict:
    """`per_trajectory`, `pooled`, `input_share`, `main_loop_caching` and `reuse_gap` over `rows`."""
    out: dict = {"per_trajectory": None, "pooled": None, "input_share": None, "main_loop_caching": None}
    meas = [x for x in rows if x["measurable"]]
    used = [x for x in rows if x["main_input_tokens"] is not None]
    if used:
        mi = sum(x["main_input_tokens"] for x in used)
        mc = sum(x["main_cache_read_tokens"] for x in used)
        hi = sum(x["helper_input_tokens"] for x in used)
        out["input_share"] = {"trajectories": len(used), "main_input_tokens": mi, "helper_input_tokens": hi,
                              "pooled": hi / (hi + mi) if hi + mi else None,
                              "per_trajectory": _summ([x["input_share_helper"] for x in used
                                                       if x["input_share_helper"] is not None]),
                              "compaction_input_tokens": sum(x["compaction_input_tokens"] or 0 for x in used),
                              "compaction_unknown": [x["task_id"] for x in used if x["compaction_input_tokens"] is None]}
        out["main_loop_caching"] = {"trajectories": len(used), "main_cache_read_tokens": mc, "main_input_tokens": mi,
                                    "pooled": mc / mi if mi else None,
                                    "per_trajectory": _summ([x["main_cache_read_fraction"] for x in used
                                                             if x["main_cache_read_fraction"] is not None])}
    timed = [x for x in meas if x["reuse_gaps_seconds"] is not None]
    allg = [g for x in timed for g in x["reuse_gaps_seconds"]]
    out["reuse_gap"] = {"trajectories": len(timed), "untimed": [x["task_id"] for x in meas if x["reuse_gaps_seconds"] is None],
                        "gaps": len(allg), "seconds": None, "share_within": None, **({"seconds": summary(allg),
                        "share_within": {str(s): sum(1 for g in allg if g <= s) / len(allg)
                                        for s in cfg.timing["cache_lifetimes_seconds"]}} if allg else {})}
    if meas:
        per = {k: [x[k] for x in meas] for k in ("reused_fraction", "same_offset_fraction",
                                                 "different_offset_fraction", "new_fraction")}
        tot = {k: sum(x[k] for x in meas) for k in COUNTS}
        out["per_trajectory"] = {k: summary(v) for k, v in per.items()}
        out["per_trajectory"]["subcalls"] = summary([x["subcalls"] for x in meas])
        d = tot["document_tokens"]
        rz = tot["same_offset"] + tot["different_offset"]
        out["pooled"] = {**tot,
                         "capped_prompt_share": tot["reused_in_capped_prompts"] / rz if rz else None,
                         "capped_pair_share": tot["reused_in_capped_pairs"] / rz if rz else None,
                         "reused_fraction": (tot["same_offset"] + tot["different_offset"]) / d,
                         "same_offset_fraction": tot["same_offset"] / d,
                         "different_offset_fraction": tot["different_offset"] / d,
                         "new_fraction": tot["new"] / d,
                         "prefix_shared_fraction": tot["prefix_shared"] / tot["prompt_tokens"]}
    return out


def provenance(res: dict, cfg: FabReuseConfig, root: Path) -> dict:
    """What the command adds to a summary: `sources`, the newline-normalized sha256 of the config, this module and its
    test, and the reader's `tokenizers_version`, the version of the library that encodes with its tokenizer."""
    import tokenizers
    res["sources"] = {rel: sha256_text_file(Path(root) / rel) for rel in _pinned(cfg, Path(root).resolve())[1:]}
    res["reader"]["tokenizers_version"] = tokenizers.__version__
    return res


def _summ(values) -> dict | None:
    return summary(values) if values else None


def reader_encoder(tokenizer_json: Path, sha256: str):
    if sha256_file_bytes(tokenizer_json) != sha256:
        raise ValueError("tokenizer.json is not the registered reader's")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(tokenizer_json))

    def encode(text: str):
        enc = tok.encode(text, add_special_tokens=False)
        return enc.ids, enc.offsets
    return encode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", type=Path, default=REPO_ROOT / "config" / "fab-reuse.toml")
    ap.add_argument("--runs", type=Path, required=True, help="the run's log root (private, outside the repository)")
    ap.add_argument("--questions", type=Path, required=True, help="data/public.csv at the pinned harness commit")
    ap.add_argument("--tokenizer-json", type=Path, required=True, help="the reader's tokenizer.json")
    a = ap.parse_args(argv)
    if Path(a.config).resolve() != (REPO_ROOT / "config" / "fab-reuse.toml").resolve():
        raise SystemExit(f"FAB-REUSE REFUSED: --config {a.config} is not config/fab-reuse.toml")
    cfg = load_config(a.config, REPO_ROOT)
    assert_ready(cfg, REPO_ROOT)
    out_path = cfg.results_dir / "summary.json"
    if out_path.exists():
        raise SystemExit(f"FAB-REUSE REFUSED: {out_path} exists; one summary per registration")
    res = provenance(summarize(cfg, a.runs, a.questions,
                               reader_encoder(a.tokenizer_json, cfg.reader["tokenizer_json_sha256"])), cfg, REPO_ROOT)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print(f"wrote {out_path.relative_to(REPO_ROOT).as_posix()}: run {res['run']}, measured {res['measured']}, "
          f"not measurable {sum(res['not_measurable'].values())}, not run {len(res['not_run'])}, "
          f"failed launches {sum(res['failed_launches'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
