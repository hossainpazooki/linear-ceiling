"""DRAFT append script for linear-ceiling: REGISTER, before any trajectory exists, the document-reuse OPPORTUNITY in
the helper sub-calls of Finance Agent Benchmark v2 trajectories (`config/fab-reuse.toml`, `linear_ceiling.fab_reuse`).
DESCRIPTIVE: no hypothesis row, no `verdict:` line, no cell moves. The number is the ledger's next, 0075 after 0074,
PROVISIONAL until the drafts README stages this script.

Every line number and hash in the entry is computed here, read-only: the cited sentences of this ledger, located by
search; the three pinned files, tracked, unmodified and hashed newline-normalized.

    python -I docs/drafts/append_0075.py --repo-root . --date YYYY-MM-DD [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root is required. It must be the current
directory and the top of its git work tree, and the imported `linear_ceiling` must be that tree's. The script refuses
under -O. Outside `--preview` it refuses until the three files are committed as-is, the config's gate names this
number, the serving model is the pinned one (always), the run's limits in `[fab_reuse.run]` are set, nothing exists under
`results/fab-reuse/` and the drafts README stages this script with the next number. Every field the summary writes must be
named in the entry. Before the write, the ledger must equal HEAD's, be unmodified and pass `ledger_check`.
After the write `ledger_check` runs again, and on a failure the old bytes go back. The script writes only
ledger/ledger.md.
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import textwrap
import tomllib
import traceback
from pathlib import Path

if not __debug__ or sys.flags.optimize:
    raise SystemExit("REFUSED: python runs with -O or PYTHONOPTIMIZE set, which strips every guard (assert) in this script")


def _refused(et, ev, tb):
    """Any exception is a refusal: print the guard's line so the output shows which one fired; exit status 1."""
    fr = [f for f in traceback.extract_tb(tb) if Path(f.filename).resolve() == Path(__file__).resolve()] or traceback.extract_tb(tb)
    sys.stderr.write(f"REFUSED: {et.__name__} at line {fr[-1].lineno}: {ev}\n  guard: {fr[-1].line}\n")


sys.excepthook = _refused
ap = argparse.ArgumentParser()
ap.add_argument("--date", required=True)
ap.add_argument("--repo-root", type=Path, required=True)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True, env=ENV)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
sys.path.insert(0, str(R / "src"))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling.fab_reuse import (LABEL, LABELS, NESTED_FIELDS, REASONS, ROW_FIELDS,  # noqa: E402
                                     SUMMARY_FIELDS, load_config)
from linear_ceiling.hashing import sha256_text_file                       # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
assert Path(_lc.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_lc.__file__}, not the tree's"

LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
PINNED_MODEL = "anthropic/claude-opus-5-5-no-fallback"
PINNED = ("config/fab-reuse.toml", "src/linear_ceiling/fab_reuse.py", "tests/test_fab_reuse.py")
CITED = {  # entry: the sentence quoted or pointed at, which must occur exactly once in that entry
    "0011": "A trajectory is one agent run on one task instance.",
    "0012": "every trace-only cost figure is a lower bound",
    "0013": "repository's one convention (`e7_stats`",
    "0014": "never a zero (entry 0006's rule, generalized from Lane A to every class).",
    "0047": "receiver `Qwen/Qwen3-1.7B@70d244cc86cc`",
}


def git(*args) -> bytes:
    return subprocess.run(["git", "-C", str(R), *args], capture_output=True, check=True, env=ENV).stdout


def block(t: str, entry: str) -> tuple:
    hits = [m.start() for m in re.finditer(rf"^### {entry} ", t, re.M)]
    assert len(hits) == 1, f"{entry}: {len(hits)} heading lines"
    nxt = re.compile(r"^### \d{4} ", re.M).search(t, hits[0] + 1)
    return hits[0], t[hits[0]:(nxt.start() if nxt else len(t))]


def once(t: str, entry: str, phrase: str) -> int:
    """The line of the phrase (any whitespace between its words), which must occur exactly once in the entry."""
    start, b = block(t, entry)
    hits = list(re.finditer(r"\s+".join(re.escape(w) for w in phrase.split()), b))
    assert len(hits) == 1, f"{entry}: {len(hits)} hits for {phrase[:60]!r}"
    return t.count("\n", 0, start + hits[0].start()) + 1


def preview_note(msg: str) -> None:
    print(f"[preview] {msg}; the append refuses until it is", file=sys.stderr)


# --- this ledger: the ordering, the cited sentences ------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0074", f"the ledger's last entry is {PREV}, not 0074"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
L = {e: once(text, e, p) for e, p in CITED.items()}
assert REASONS == ("no sub-call", "no document token", "reconstruction", "tokenization", "unreadable record"), \
    "the entry names the module's reasons"

# --- the pinned files, the config, the results tree --------------------------------------------------------------------------------------
for rel in PINNED:
    assert (R / rel).is_file(), f"{rel} missing"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=R, capture_output=True, env=ENV).returncode == 0
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=R, env=ENV).returncode == 0
    if not (tracked and clean):
        assert a.preview, f"{rel} is not committed as-is"
        preview_note(f"{rel} is not committed as-is")
H = {rel: sha256_text_file(R / rel) for rel in PINNED}
cfg = load_config(R / "config/fab-reuse.toml", R)
raw = tomllib.loads((R / "config/fab-reuse.toml").read_text(encoding="utf-8"))["fab_reuse"]
assert cfg.required_entries == (NUM,), f"[fab_reuse.gate] names {cfg.required_entries}, not ({NUM!r},)"
assert cfg.cohort == 27 and cfg.task_id_format == "row{row:02d}" and raw["results_dir"] == "results/fab-reuse"
HN = cfg.harness
assert HN["commit"] == "25b6cab9bcb4f8f9857f2e1a6721732c85511c5c" and HN["max_time_seconds"] == 7200
MODEL = HN["model"]
assert MODEL == PINNED_MODEL, f"[fab_reuse.harness] model {MODEL!r} is not the pinned {PINNED_MODEL!r}"
RD = cfg.reader
beh = tomllib.loads((R / "config/cache-behavior.toml").read_text(encoding="utf-8"))
assert (RD["model"], RD["revision"]) == (beh["model"], beh["revision"]), "the reader is not 0047's receiver"
assert RD["revision"].startswith("70d244cc86cc")
OUT = R / "results" / "fab-reuse"
assert not (OUT.exists() and any(OUT.rglob("*"))), "results/fab-reuse/ holds something: the entry comes before any count"

# --- the drafts README stages this script ----------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if not (f"`append_{NUM}.py`" in readme and free and free[-1] == NEXT):
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    preview_note(f"the drafts README does not stage append_{NUM}.py at {NEXT}")


def h(rel: str) -> str:
    return f"`{rel}` (`{H[rel][:12]}…`)"


SMOKE = ("A one-question smoke on row 1 ran before this entry's text was fixed, under the wall-time end, the disk floor and "
         "the spend limit below. Set after it: from it, the token ceiling and the number of questions run at once; and "
         f"the last start time (planned before the smoke as 2026-11-20 12:00Z, now {cfg.run['last_start_utc']}), the "
         "poll interval, and the in-flight spend estimate below, which counts every running question at its ceiling (the "
         "plan before the smoke counted the spend so far and the costliest question so far). Its trajectory is row 1's "
         "one run. The other questions started after this entry's text, but for the date in its heading, and the three "
         f"files it pins ({h('config/fab-reuse.toml')}, {h('src/linear_ceiling/fab_reuse.py')} and "
         f"{h('tests/test_fab_reuse.py')}) were fixed, without waiting for its commit; the outcome entry says which "
         "questions had started before the commit. Before the commit, the logs were "
         "read for this entry only to plan and enforce the run. From the smoke: its turn count and its helper-record "
         "count, which is its sub-call count (the summary reports both, as `turns` and `subcalls`); the bytes it wrote; "
         "its wall time; and the provider's usage summed over all its calls, its spend and its input tokens split into "
         "uncached, cache-read and cache-write tokens. The helper runs with prompt caching off, so that cache-read count "
         "is row 1's main-loop cache-read count, the numerator of (b) below for row 1; the main loop's input tokens, its "
         "denominator, were not separated from the helper calls'. The split therefore bounds row 1's (a) from above and "
         "its (b) from both sides; those bounds, from the split alone, were worked out before the commit and are not "
         "given here. From every question: the run's wrapper parses each turn and helper record for its usage and cost "
         "and keeps two totals for the question, its spend (the cost of its turn and helper calls and of any compaction) "
         "and its input tokens (the input, cache-read and cache-write tokens of its turn and helper calls, summed into one "
         "count), to "
         "enforce the limits below; it hashes every log file for its manifest and reads a failed launch's output. The "
         "summarizer opened no log before the commit. Beyond those bounds for row 1, no reuse, prefix, "
         "input-share, cache-share, gap or within-cap figure was computed before it, by the summarizer or by any other "
         "reading of the logs.")
RUN = cfg.run
ORDER = ", ".join(str(r) for r in RUN["order"])
assert RUN["order"] == [1] + [r for k in (1, 2, 0) for r in range(2, cfg.cohort + 1) if r % 3 == k], "the order is not its rule"
for k in ("token_ceiling", "max_parallel"):
    if RUN[k] == "UNSET":
        assert a.preview, f"[fab_reuse.run] {k} is UNSET"
        preview_note(f"[fab_reuse.run] {k} is UNSET")
CEIL = RUN["token_ceiling"] if RUN["token_ceiling"] == "UNSET" else f"{RUN['token_ceiling']:,}"
LIFE = cfg.timing["cache_lifetimes_seconds"]
assert LIFE == [300, 3600], "the entry states five minutes and one hour"


# --- the entry -------------------------------------------------------------------------------------------------------------
RAW = f"""### {NUM} — {a.date} — FAB v2 document-reuse opportunity registered before any reuse count: the document tokens a logged helper sub-call of a Finance Agent Benchmark v2 trajectory carries that an earlier sub-call of the same trajectory already carried, at the same or a different offset, in the reader's tokenizer; an upper bound for a cache keyed on the retrieved document's sha256, with the input split, the main loop's realized caching and the reuse gap described beside it; no hypothesis row, no cell moves

**Why.** The Finance Agent Benchmark v2 harness is one agent whose helper calls carry whole documents: a page the agent parses is stored under a key, and each `retrieve_information` call sends the helper model a prompt with each `{{{{key}}}}` replaced by that document's text, or by a character slice of it. The harness sends these sub-calls with prompt caching off. Its trajectories therefore bound, from above, how much document KV a cache keyed on the retrieved document's sha256 could reuse across one trajectory's logged sub-calls; a cache keyed on content could reuse more. This entry registers that measure, and four descriptions beside it, BEFORE any of their figures was computed, but for the row 1 counts named below, and decides nothing: **no hypothesis row, no `verdict:` line, no cell moves.** {SMOKE}

**The harness.** `vals-ai/finance-agent-v2` at `{HN['commit']}`, fetched without git as the codeload tarball (sha256 `{HN['tarball_sha256'][:12]}…`), with model-library {HN['model_library']} as its lockfile pins. It runs locally in single-task mode, one question per process, in UTF-8 mode so that each question is read as UTF-8, at the harness's defaults: {HN['max_time_seconds']:,} s per question, no turn cap. The harness checks that budget at the start of each turn, against wall time less the retry overhead of queries that succeeded (each one's wall time less the provider's reported duration), so a question can run past it. Serving model: `{MODEL}`, at the registry's default effort; the helper model is the same, with the library's prompt caching off, and the main loop keeps the library's default five-minute caching. One local change is allowed before any question runs: the page fetcher's User-Agent header, which at the commit carries another party's contact, takes the run's own contact from the environment instead. The outcome entry states that change by its diff, with any contact elided. The logs stay in a private run folder outside this repository. Nothing from them is committed, and no document or web text is republished. The benchmark's grading is its owner's, so this run carries no score.

**Cohort and unit.** The {cfg.cohort} public questions of `data/public.csv` at the commit (sha256 `{HN['questions_csv_sha256'][:12]}…`), one trajectory each, one run. 0011 (line {L['0011']}): "{CITED['0011']}" Row N's task id is `row` followed by N in two digits (`row01`). The summarizer sees a log directory only if it holds `turns/init/`. Such a directory with no turn holding its result record (none, or only turns whose query failed, which hold the harness's error record alone) is a FAILED LAUNCH (no answer of the model was recorded): it is counted by question, it is not a trajectory, and its question may be launched again. A directory without `turns/init/` is not seen at all: it is neither a trajectory nor a failed launch, and it is not refused. Every launch, seen or not, is in the run's private record, and the outcome entry reports the launch count by question. A question's first trajectory is its one run: a second trajectory for it refuses the summary, as does a trajectory that names another serving model. A question with no trajectory is NOT RUN and named, never dropped.

**The measure.** A sub-call is one logged helper record: a `retrieve_information` call whose helper response the harness wrote. A call the tool refused before sending, and a call whose helper query failed, leave no record and are not sub-calls. Sub-calls are ordered by turn and tool index; a turn's tools run one at a time, in the order its tool records list. A turn whose query failed holds the harness's error record alone: no tool ran in it and the store did not change. Each sent prompt is rebuilt from the call's own arguments and, for each key, the document the store held when the call ran, with the harness's own one-pass substitution. The turn's ordered tool records fix that document: the turn's own snapshot if a successful page parse earlier in the turn wrote the key, else the latest earlier snapshot. A key written both earlier and later in the same turn is in no snapshot, and the trajectory is NOT MEASURABLE. The rebuild must reproduce, byte for byte, the text the record logs as sent; it only locates the inserted spans and their documents, and the logged text is what is tokenized. A document token is a token whose character span is non-empty and lies wholly inside one inserted span; a token
with empty offsets carries no text and is none. Its identity is the retrieved document's sha256, the token's character span in that document and its token id; a page parsed again with changed text is another document. A token across a span edge is template text. A span's edges are its first character and the character just after its end. Where the tokenizer's offsets leave an edge character covered by no token, or it has a nonzero canonical combining class (normalization can fold either into a neighbouring token), the edge cannot be placed; an empty span has no edge. Each document token is SAME OFFSET if an earlier sub-call of the trajectory carried its identity at the same token index (its index in the logged prompt, template text included), DIFFERENT OFFSET if an earlier sub-call carried it only at other indices, and NEW otherwise. Two places of one identity within one sub-call never count as reuse of each other: each is compared with the earlier sub-calls only. Described beside it, not a reuse figure: PREFIX-SHARED, the longest common token prefix of a sub-call's prompt with any earlier sub-call's prompt, which is what an exact prefix cache could serve before block granularity.

**Not measurable, never a zero.** 0014 (line {L['0014']}): "{CITED['0014']}" A trajectory is NOT MEASURABLE for one of five reasons, and then carries no partial counts: "no sub-call", none read (the question ended without one, or all its sub-calls lie in a set-aside turn); "no document token" over all its sub-calls; "reconstruction", a sub-call whose document cannot be fixed or whose sent text is not rebuilt byte for byte; "tokenization", a sent prompt the reader's tokenizer cannot encode or whose span edges it cannot place; "unreadable record", a log record that is missing, truncated or not JSON; a turn that holds neither its result record nor the error record alone; turn numbers with a gap; or a sub-call record that its turn's tool records do not yet list (the process ended between the two writes). How many trajectories each reason touches is known only after the run, and the outcome entry reports it. A trajectory with one sub-call is measured: it has no earlier sub-call, so its reuse is zero by construction, and its sub-call count is reported beside it.

**A question ended early.** A question whose process the run's wrapper ended, at its wall-time end or its token ceiling (below), or that died, leaves no final record: its stop reason is `absent`. Its last turn directory, the turn under way when it ended, may be cut short, so it is SET ASIDE: none of its records is read, its sub-calls are counted as `cut_subcalls`, and every measure is taken over the turns before it, by the same rules as any trajectory. Such a trajectory is measured, or NOT MEASURABLE for one of the five reasons, like any other. The outcome entry names each such question and the limit that ended it, from the run's private record. A trajectory ENDED BY ITSELF if its final record's stop reason is `done_tool` or `should_stop`, the two ends no limit or error made (at the pin the harness never stops on `should_stop`). Any other trajectory, whether the harness's own time budget stopped it (`max_time`, with a final record), a turn limit or an error stopped it, or it has no final record (`absent`), is read over the turns it completed before it was stopped. A token ceiling set from the smoke cuts the longest questions first, so every aggregate is reported twice, over all trajectories and over those that ended by themselves, and the others are listed with their stop reasons.

**The reader's tokenizer.** `{RD['model']}` at `{RD['revision'][:12]}`, the receiver 0047 registers (line {L['0047']}), whose `tokenizer.json` is pinned by sha256 (`{RD['tokenizer_json_sha256'][:12]}…`); the summary records the version of the library that encodes with it. Counting runs on CPU, with no special tokens and no API key after the run. Every reuse count is in this tokenizer, not the serving model's. Character offsets locate tokens and are not reported.

**Also reported, each descriptive and under its own label, none compared numerically with the reuse counts.** All are read from the same logs, with no further call. (a) INPUT SHARE, exact from the logs: a call's input tokens are its usage record's input, cache-read and cache-write tokens, in the provider's own counts for the call's successful attempt; per trajectory and pooled, the helper sub-calls' input tokens over those of the helper sub-calls and the main agent's turn queries together. A failed query or helper call leaves no usage and is not counted. Compaction calls are on neither side; their usage, as the final record lists it, is reported apart (none is configured at the pin). (b) REALIZED CACHING ON THE MAIN LOOP, exact from the logs: per trajectory and pooled, the main agent's turn queries' cache-read input tokens over their input tokens; realized, in the provider's tokens, for the main loop only. With questions run at once, which share one system prompt and tool set, a turn query's cache read can include a prefix another question wrote. (a) and (b) are reported for every trajectory whose records are readable, whatever its reuse reason, and are null when any of its records, a helper's included, cannot be read. (c) REUSE GAP, an estimate the logs define exactly but not a measured time: no helper record has a time of its own, so a sub-call's start is taken as its turn's timestamp (written when the turn's query returned, before its tools ran) plus the durations of the turn's tool records before it, which leaves out the harness's own log writes. For each sub-call of a measured trajectory and each document with a SAME or DIFFERENT OFFSET token in it, the gap is that start less the start of the latest earlier sub-call that carried a document token of the same document. Reported: the gaps' median, p10 and p90, and the share of gaps at most each of the provider's two published prompt-cache lifetimes, five minutes and one hour. A trajectory whose turn records lack a time-zone-aware timestamp or a tool duration is UNTIMED and named. (d) BY QUESTION TYPE: every row listed under its type from the questions file's `Question Type` column (nine types, three questions a type), with no comparison claimed. (e) WITHIN THE CAP, in the reader's tokens: of the SAME and DIFFERENT OFFSET tokens, those in a sub-call whose prompt is at most {RD['context_cap']:,} reader tokens (the reader's registered context cap, `config/cache-behavior.toml`), and those for which the latest earlier sub-call that carried a document token of the same document is within the cap too; each as a count and as a share of the SAME plus DIFFERENT OFFSET tokens.

**What is reported, field by field.** `results/fab-reuse/summary.json` holds `label` (the reuse label below) and `labels` (one each for `input_share`, `main_loop_caching`, `reuse_gap` and `by_question_type`), `harness_commit`, `model`, `reader` (`model`, `revision`, `tokenizer_json_sha256`, `context_cap`, `tokenizers_version`), `cohort`, `run` (the questions with a trajectory), `not_run` (their task ids), `measured`, `not_measurable` (the count by reason), `failed_launches` (the count by question), `by_question_type` (each type's task ids, run and not run), `trajectories`, `per_trajectory`, `pooled`, `input_share`, `main_loop_caching`, `reuse_gap`, `aggregates_ended_by_itself`, `not_ended_by_itself` and `sources` (the sha256 of the config, the module and its test). Each of `trajectories` holds `task_id`, `row`, `question_type`, `stop_reason` (the harness's, or `absent`), `ended_by_itself`, `serving_model`, `turns` (its turn directories, error and set-aside turns included), `error_turns`, `final_record`, `set_aside_turn`, `cut_subcalls`, `subcalls` (the sub-calls read), `prompt_tokens` and `document_tokens` (summed over its sub-calls), `same_offset`, `different_offset`, `new`, `prefix_shared`, `reused_in_capped_prompts`, `reused_in_capped_pairs`, `documents` (its distinct document sha256s), `measurable`, `reason`, the fractions `reused_fraction` (SAME plus DIFFERENT OFFSET over document tokens), `same_offset_fraction`, `different_offset_fraction` and `new_fraction` (each over document tokens), `prefix_shared_fraction` (PREFIX-SHARED over prompt tokens), `capped_prompt_share` and `capped_pair_share` (each over SAME plus DIFFERENT OFFSET), the usage figures `main_input_tokens`, `main_cache_read_tokens`, `helper_input_tokens`, `compaction_input_tokens`, `input_share_helper` (helper over helper plus main input tokens) and `main_cache_read_fraction` (main cache-read over main input tokens), `reuse_gaps_seconds` (its gaps) and `files` (the sha256 of every log file it read, so the run's own manifest can be checked against it). An unmeasurable trajectory carries none of the reuse counts or fractions, and no `documents`. `per_trajectory` holds, over the measured trajectories, the median, p10 and p90 (`n`, `median`, `p10`, `p90`, by the repository's one convention, 0013, line {L['0013']}) of `reused_fraction`, `same_offset_fraction`, `different_offset_fraction`, `new_fraction` and `subcalls`; `pooled` holds the sums of the counts over the measured trajectories and the same fractions of those sums. `input_share` holds `trajectories` (those whose usage was read), `main_input_tokens`, `helper_input_tokens`, `pooled`, `per_trajectory`, `compaction_input_tokens` and `compaction_unknown` (the trajectories without a final record, or whose final record lists a compaction usage that cannot be read); `main_loop_caching` holds `trajectories`, `main_cache_read_tokens`, `main_input_tokens`, `pooled` and `per_trajectory`; `reuse_gap` holds `trajectories` (measured and timed), `untimed`, `gaps`, `seconds` (median, p10, p90) and `share_within` (by lifetime). `aggregates_ended_by_itself` holds `trajectories` and `measured` (the trajectories that ended by themselves, and the measured among them) and `per_trajectory`, `pooled`, `input_share`, `main_loop_caching` and `reuse_gap` as above, over those trajectories alone; `not_ended_by_itself` lists every other trajectory's `task_id` and `stop_reason`. A field with nothing to report is null, never a zero. Every reuse figure carries the label "{LABEL}". It is a bound in 0012's sense (line {L['0012']}), from traces alone, labelled as one: an UPPER bound on the opportunity for a cache keyed on the retrieved document's sha256, where 0012's are lower bounds on cost. PREFIX-SHARED is reported beside it and is not bounded by it.

**Not counted.** Text that reaches a sub-call by any other route, such as the agent copying document text into its prompt or an answer quoting a document; identical text inside a different document, which a cache keyed on content could reuse; reuse across trajectories; the main agent's own calls in the reuse counts (the input share and the realized caching read only their usage records); helper calls that failed; a paged cache's block granularity; and what any serving engine does with the opportunity. No carryover effect, key statistic or KL is read here; the entry and any sentence that cites it say so.

**Gate and enforcement.** `python -m linear_ceiling.fab_reuse` refuses before it opens a log until `ledger/ledger.md`, `config/fab-reuse.toml`, `src/linear_ceiling/fab_reuse.py` and `tests/test_fab_reuse.py` are committed unmodified, the committed ledger holds {NUM}, and the serving model, the token ceiling and the number of questions run at once are set in the config. It reads `config/fab-reuse.toml` and no other config, and refuses on a questions file or `tokenizer.json` other than the pinned ones, a seen log directory outside the cohort, two trajectories for one question, a trajectory of another serving model, a helper record of another tool, and an existing summary. This script refuses unless the three files are committed as-is, the gate names {NUM}, the model is the pinned one, the run's limits are set, and nothing exists under `results/fab-reuse/`. Pinned at append: {h('config/fab-reuse.toml')}, {h('src/linear_ceiling/fab_reuse.py')}, {h('tests/test_fab_reuse.py')}.

**Run.** The other questions start in this order, fixed before the smoke ran and held in `[fab_reuse.run]`, from the time this entry's text and its pinned files were fixed, without waiting for its commit (the run's wrapper refuses to start one unless the config's sha256 is the one pinned here): {ORDER} (row 1, then the other rows by their remainder mod 3: 1, then 2, then 0, which spreads the nine question types across whatever runs). At most {RUN['max_parallel']} run at once, each its own process with the same harness, model and arguments; the order fixes which questions start first, and with several running they end in any order. Until one question has ended, one runs at a time. A question starts only while each of these holds: it is no later than {RUN['last_start_utc']}; the run's keys file is present and not empty; at least {RUN['disk_floor_gb']} GB are free on the run's drive; every usage record read so far carries its cost; and the run's spend cannot pass the spend limit by the wrapper's estimate, which counts every question in flight at its ceiling: the spend so far, plus each running question's ceiling cost less its own spend so far, plus one ceiling cost for the new question, a ceiling cost being the token ceiling times the highest spend per input token among the questions already ended. When the estimate refuses a start while a question runs, the next question waits and every check is made again at each poll, so the last start time still applies; when it refuses with nothing running, new starts stop. Any other check that fails stops new starts at once. Questions start in the registered order as far as the spend limit allows; the limit is set outside this repository, its amount is not stated, and it may be raised, never lowered, before the last start time; the outcome entry names the questions run and says whether it was raised. A failed launch stops new starts; they resume only after that question is launched again or is named NOT RUN, every launch is counted, and the outcome entry reports each stop. The wrapper can also be given a part of the order, which it starts in the order's sequence, and the run can be stopped by hand; a question in flight when the run is stopped ends like one that died (above). The outcome entry says why starts ended and whether either was used. The wrapper ends a question's process at {RUN['wall_seconds']:,} s of wall time, or once its logged calls' input tokens (the input, cache-read and cache-write tokens of its turn and helper records, in the provider's counts) reach {CEIL}; it checks every {RUN['poll_seconds']} s, so a question can pass its ceiling by the calls logged since the last check. The run's private record names, for each question that ended under the wrapper, what ended it: its own end, the wall time or the token ceiling. A question not started is NOT RUN and named. Not published: the spend limit and the spend, the wrapper, its records and the logs. The figures enter by their own entry, which runs the summarizer in-process; no figure is typed.

**What this does NOT touch.** Every cell and verdict, every other config and output tree, and the figure set 0072 lists.

**Consequences in this commit set.** `config/fab-reuse.toml`, `src/linear_ceiling/fab_reuse.py`, `tests/test_fab_reuse.py`, a section in `docs/agent/experiment-commands.md`, a line in `docs/agent/repo-architecture.md`, and the drafts README's allocator. Nothing under `results/`.

**Scope.** One harness at one commit, one serving model, {cfg.cohort} questions, one run each; the document text of one agent's logged helper sub-calls; a registration, not a result.

**Numbering.** {NUM} is the number the drafts README allocates at staging; ordering guard {PREV} present, {NUM} absent. Next free number after this entry: {NEXT}.

prior-entries-sha256: PLACEHOLDER
"""
NB = "\u0000"


def wrap(par: str) -> str:
    """One paragraph at width 120; a code span is never broken across lines."""
    par = re.sub(r"`[^`]*`", lambda m: m.group(0).replace(" ", NB), " ".join(par.split()))
    return "\n".join(ln.replace(NB, " ") for ln in textwrap.wrap(par, width=120, break_long_words=False, break_on_hyphens=False))


_paras = RAW.split("\n\n")
assert _paras[0].startswith(f"### {NUM} ") and "\n" not in _paras[0] and _paras[-1] == "prior-entries-sha256: PLACEHOLDER\n"
assert NB not in RAW, "the entry text holds the wrap's placeholder"
ENTRY = "\n\n".join([_paras[0]] + [wrap(x) for x in _paras[1:-1]] + [_paras[-1]])
assert ENTRY.endswith("prior-entries-sha256: PLACEHOLDER\n") and ENTRY.count("PLACEHOLDER") == 1, "the chain line is not the entry's last"
assert "{{key}}" in ENTRY and "UNVERIFIED" not in ENTRY
for _f in (*SUMMARY_FIELDS, *ROW_FIELDS, *(x for v in NESTED_FIELDS.values() for x in v), *LABELS):
    assert f"`{_f}`" in ENTRY, f"the entry does not name the summary field {_f!r}"

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print("[ordering guard: ok]")
    raise SystemExit(0)


# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included -----------------------------------
def ledger_check():
    code = (f"import sys; sys.path.insert(0, {str(R / 'src')!r}); "
            "from linear_ceiling.ledger_check import main; sys.exit(main())")
    return subprocess.run([sys.executable, "-I", "-c", code], cwd=R, capture_output=True, text=True, env=ENV)


at_head = git("show", "HEAD:ledger/ledger.md")
assert text == at_head.decode("utf-8").replace("\r\n", "\n"), "ledger/ledger.md is not HEAD's: an uncommitted edit"
assert git("status", "--porcelain", "--", "ledger/ledger.md").strip() == b"", "ledger/ledger.md is modified in the working tree"
r0 = ledger_check()
assert r0.returncode == 0 and r0.stdout.strip().endswith(LEDGER_OK), f"ledger_check before the write: {(r0.stdout + r0.stderr).strip()[-400:]}"
assert "prior-entries-sha256: PLACEHOLDER" not in text, "the ledger already holds a placeholder chain line"
base = text + ("" if text.endswith("\n") else "\n") + "\n"
digest = chain_hash(base + ENTRY, len(base), _ENTRIES_HEAD.search(base).start())
new = base + ENTRY.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
assert new.startswith(text) and new.count(f"\n### {NUM} ") == 1 and new.index(f"\n### {NUM} ") + 1 == len(base), "the new ledger is not the old one plus this entry"
# --- the write, and after it: ledger_check, else the old bytes go back ----------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
