"""DRAFT append script for linear-ceiling: REGISTER, before any pair is built, the cache reading of the Finance Agent
run's paired helper sub-calls (`config/cache-behavior-fab.toml`, `tools/cache_behavior/fab_pairs.py`). DESCRIPTIVE: no
hypothesis row, no band, no `verdict:` line, no cell moves. The number is the ledger's next, 0076 after 0075,
PROVISIONAL until the drafts README stages this script.

Every line number and hash in the entry is computed here, read-only: the cited sentences of this ledger, located by
search; the pinned files, tracked, unmodified and hashed newline-normalized, with their git blob ids.

    python -I docs/drafts/append_0076.py --repo-root . --date YYYY-MM-DD [--case-file F] [--preview]

--date must be today's date in UTC (entry 0021: the day of writing). --repo-root is required. It must be the current
directory and the top of its git work tree, and the imported `linear_ceiling` and `tools` must be that tree's. The
script refuses under -O. Outside `--preview` it refuses until the cell's five files are committed as-is, 0075's module
and config are committed as they landed with 0075, the cell's config gate names 0075 and this number, the shared
settings equal `config/cache-behavior.toml`'s, nothing exists under `results/cache-behavior-fab/` and the drafts README
stages this script with the next number. Every field the summary's `fab` block writes must be named in the entry.
With --case-file (0049's prepared input for its probe handoff, outside the repository) it recomputes the three
archive figures the entry states from that file and refuses on a difference. Before the write, the ledger must equal
HEAD's, be unmodified and pass `ledger_check`. After the write `ledger_check`
runs again, and on a failure the old bytes go back. The script writes only ledger/ledger.md.
"""
import argparse
import datetime as dt
import hashlib
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
ap.add_argument("--case-file", type=Path, help="0049's prepared input for the probe handoff: recompute the archive figures")
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
sys.path.insert(0, str(R))
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling.fab_reuse import load_config                          # noqa: E402
from linear_ceiling.hashing import sha256_text_file                       # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
from tools.cache_behavior import fab_pairs as FP                         # noqa: E402
assert Path(_lc.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_lc.__file__}, not the tree's"
assert Path(FP.__file__).resolve().is_relative_to(R), f"imported {FP.__file__}, not the tree's"

LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"
OWN = ("config/cache-behavior-fab.toml", "tools/cache_behavior/fab_pairs.py", "tools/cache_behavior/run.py",
       "tools/cache_behavior/core.py", "tests/test_cache_behavior_fab.py")
FROM_0075 = ("src/linear_ceiling/fab_reuse.py", "config/fab-reuse.toml")
# The driver 0069 ran, at f98d53b (0074): the test in this commit set builds it from these blobs.
DRIVER_0069 = {"tools/cache_behavior/run.py": "a80fbc28a2d50ecca5c7ac0164aeffee4167cb4f",
               "tools/cache_behavior/core.py": "04fab278e7d1772b0b822d1523af59bdfcd4d5df"}
# 0049's probe handoff and its prepared inputs (0049: manifest `2aeee5769c0a…`; 0073: the probe handoff).
CROSS = {"handoff": "20241016_composio_swekit/django__django-11087_traj#152",
         "manifest_sha256": "2aeee5769c0a3b557e1fecd43c2a745abe9f29c37af66b0eabb54358b4c35b22",
         "file_sha256": "3f79826e8a0168d79d8e37072472e3d8022d4dc0b9db010c1511b5ff3fbab6bd"}
# On that handoff, from its case file (`3f79826e8a01…`, delta_K [23155, 28, 8]): the mean of the token means 0.11203,
# f* 0 at tau_K, 878 tokens over tau_K. The file is not in the repository (results/ is not committed); with
# --case-file this script recomputes the three from it, and the cross-instrument control recomputes them on the pod.
ARCHIVE_MEAN, ARCHIVE_MATCHED, ARCHIVE_OVER = "0.1120", 23155, 878
CITED = {  # key: (entry, the sentence quoted or pointed at, which must occur exactly once in that entry)
    "0013": ("0013", "repository's one convention (`e7_stats`"),
    "0014": ("0014", "never a zero (entry 0006's rule, generalized from Lane A to every class)."),
    "0045": ("0045", "the per-token tail counted per cell with the per-handoff maximum"),
    "0047_tau": ("0047", "τ_K = 0.3186442653116294 used only to name the archived high-error tail"),
    "0047_arms": ("0047", "**Arms.** FRESH: the receiver's own prefill of R."),
    "0047_repeat": ("0047", "Fresh repeat: a second FRESH pass must reproduce the first's logits exactly."),
    "0047_bridge": ("0047", "Archive bridge: the current runtime's same-model centered K/V mean deviation per handoff "
                            "within 0.001 + 0.01 × |archived|"),
    "0047_probe": ("0047", "The largest sender is scored first as the retained memory probe."),
    "0047_claim": ("0047", "The standing sentence \"No downstream task-quality number is claimed\""),
    "0049_row": ("0049", "**REUSE-ALL (assembled same-model cache)**"),
    "0058": ("0058", "(1) f* is read as the **oracle removal fraction**"),
    "0073": ("0073", "\"on the probe handoff, the only one that carries the two controls\""),
    "0074": ("0074", "needs a driver that stops on any nonzero fresh-repeat error"),
    "0075_subcall": ("0075", "A sub-call is one logged helper record"),
    "0075_identity": ("0075", "Its identity is the retrieved document's sha256, the token's character span in that "
                              "document and its token id"),
    "0075_offset": ("0075", "Each document token is SAME OFFSET if an earlier sub-call of the trajectory carried its "
                            "identity at the same token index"),
    "0075_setaside": ("0075", "so it is SET ASIDE"),
    "0075_cap": ("0075", "(e) WITHIN THE CAP, in the reader's tokens"),
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


def heading_line(t: str, entry: str) -> int:
    start, _ = block(t, entry)
    return t.count("\n", 0, start) + 1


def preview_note(msg: str) -> None:
    print(f"[preview] {msg}; the append refuses until it is", file=sys.stderr)


# --- this ledger: the ordering, the cited sentences ------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert len(heads) == len(set(heads)), "the ledger's headings are not unique"
PREV = heads[-1]
assert PREV == max(heads) == "0075", f"the ledger's last entry is {PREV}, not 0075"
NUM = f"{int(PREV) + 1:04d}"
NEXT = f"{int(NUM) + 1:04d}"
L = {k: once(text, e, p) for k, (e, p) in CITED.items()}
HL = {e: heading_line(text, e) for e in ("0036", "0047", "0049", "0075")}


def lines(*keys) -> str:
    ns = sorted({L[k] for k in keys})
    return f"line {ns[0]}" if len(ns) == 1 else "lines " + ", ".join(str(n) for n in ns)


# --- the pinned files: the cell's own, and 0075's as they landed with 0075 -------------------------------------------------
def committed_as_is(rel: str) -> bool:
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=R, capture_output=True, env=ENV).returncode == 0
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=R, env=ENV).returncode == 0
    return tracked and clean


BLOB = {}
for rel in (*OWN, *FROM_0075):
    assert (R / rel).is_file(), f"{rel} missing"
    if committed_as_is(rel):
        BLOB[rel] = git("rev-parse", f"HEAD:{rel}").decode().strip()
    else:
        assert a.preview, f"{rel} is not committed as-is"
        preview_note(f"{rel} is not committed as-is (its blob id below is the working file's)")
        BLOB[rel] = git("hash-object", f"--path={rel}", str(R / rel)).decode().strip()
H = {rel: sha256_text_file(R / rel) for rel in (*OWN, *FROM_0075)}
_landed = git("log", "--format=%H", "-S", "### 0075 —", "--", "ledger/ledger.md").decode().split()
if _landed:
    C0075 = _landed[-1]
    for rel in FROM_0075:
        assert git("rev-parse", f"{C0075}:{rel}").decode().strip() == BLOB[rel], f"{rel} is not the blob that landed with 0075"
else:
    assert a.preview, "no commit adds 0075 to the ledger"
    preview_note("no commit adds 0075 to the ledger (the blobs of 0075's files are the working files')")
for rel, blob in DRIVER_0069.items():
    assert git("rev-parse", f"f98d53b:{rel}").decode().strip() == blob, f"{rel} at f98d53b is not blob {blob[:12]}"

# --- the configs ---------------------------------------------------------------------------------------------------------
cfg = tomllib.loads((R / "config/cache-behavior-fab.toml").read_text(encoding="utf-8"))
beh = tomllib.loads((R / "config/cache-behavior.toml").read_text(encoding="utf-8"))
fab = load_config(R / "config/fab-reuse.toml", R)
SHARED = ("model", "revision", "transformers", "torch", "seed", "context_cap", "chunk_tokens", "continuation_tokens",
          "continuation_chunk", "prefix_control_tokens", "control_max_logit_error", "bridge_absolute_tolerance",
          "bridge_relative_tolerance", "tau_K", "attention_query_chunk", "oracle_fractions", "rope")
for k in SHARED:
    assert cfg[k] == beh[k], f"cache-behavior-fab.toml {k} = {cfg[k]!r}, not 0047's {beh[k]!r}"
assert cfg["cell"] == FP.CELL and cfg["attention_queries"] == 0 and "expected_handoffs" not in cfg
assert cfg["gate"] == {"prepare_entries": ["0075", NUM], "run_entries": ["0075", NUM]}, f"the cell's gate is {cfg['gate']}"
assert cfg["cross_check"] == CROSS, "the cross-check is not 0049's probe handoff and prepared inputs"
WINDOW, FLOOR, CEILING = cfg["window_end"], cfg["min_matched_tokens"], cfg["max_pairs"]
assert (WINDOW, FLOOR, CEILING) == ("2026-11-20T12:00:00Z", 64, 60), "window, floor or ceiling differs from this entry's text"
CAP, CHUNK, CONT = cfg["context_cap"], cfg["chunk_tokens"], cfg["continuation_tokens"]
assert (CAP, CHUNK, CONT) == (81920, 256, 256) and cfg["rope"]["factor"] == 2.5
HOSTLIM, HOSTFIX, HOSTB = cfg["host_memory_limit_GiB"], cfg["host_fixed_GiB"], cfg["host_bytes_per_matched_token"]
assert (HOSTLIM, HOSTFIX, HOSTB) == (88, 12, 4 * 28 * 8 * 128 * 2 * 4), "the host-memory rule differs from this entry's text"
HOST_AT_CAP = FP.host_gib(CAP, cfg)
assert HOST_AT_CAP <= HOSTLIM, "the host-memory rule would exclude pairs the cap admits; the entry says it does not"
if a.case_file is not None:     # the three archive figures, recomputed from the case file
    import numpy as np
    from linear_ceiling.e9_pertoken import f_star, token_mean
    assert hashlib.sha256(a.case_file.read_bytes()).hexdigest() == CROSS["file_sha256"], "--case-file is not 0049's probe input"
    with np.load(a.case_file, allow_pickle=False) as _z:
        _tm = token_mean(_z["delta_K"])
    _got = (f"{_tm.mean():.4f}", len(_tm), int((_tm > cfg["tau_K"]).sum()), f_star(_tm, cfg["tau_K"]))
    assert _got == (ARCHIVE_MEAN, ARCHIVE_MATCHED, ARCHIVE_OVER, 0.0), f"the case file gives {_got}, not the entry's figures"
    print(f"[case file] mean {_got[0]}, matched {_got[1]}, over tau_K {_got[2]}, f* {_got[3]}: as stated", file=sys.stderr)
assert fab.reader["context_cap"] == CAP and (fab.reader["model"], fab.reader["revision"]) == (cfg["model"], cfg["revision"])
assert fab.required_entries == ("0075",) and fab.cohort == 27
MODEL, HARNESS = fab.harness["model"], fab.harness["commit"]
assert MODEL == "anthropic/claude-opus-5-5-no-fallback" and HARNESS.startswith("25b6cab9bcb4")
assert FP.EXCLUSIONS == ("prefix", "repeated keys only", "below the matched-token floor", "no logged response",
                         "fewer than two continuation tokens", "over the cap", "over host memory", "beyond the ceiling"), \
    "the entry names the exclusions in order"
assert set(FP.CROSS_CHECK_LABELS) == {"run", "not staged"}
OUT = R / "results" / "cache-behavior-fab"
assert not (OUT.exists() and any(OUT.rglob("*"))), "results/cache-behavior-fab/ holds something: the entry comes before any reading"

# --- the drafts README stages this script ----------------------------------------------------------------------------------
readme = (R / "docs/drafts/README.md").read_text(encoding="utf-8")
free = re.findall(r"Next free number:?\s*\*\*(\d{4})\*\*", readme)
if not (f"`append_{NUM}.py`" in readme and free and free[-1] == NEXT):
    assert a.preview, f"the drafts README does not stage append_{NUM}.py with its last allocator line at {NEXT}"
    preview_note(f"the drafts README does not stage append_{NUM}.py at {NEXT}")


def h(rel: str) -> str:
    return f"`{rel}` (blob `{BLOB[rel][:12]}…`, sha256 `{H[rel][:12]}…`)"


def q(key: str) -> str:
    return CITED[key][1]


FIELDS_FAB = ", ".join(f"`{f}`" for f in FP.FAB_FIELDS)
FIELDS_BLOCK = ", ".join(f"`{f}`" for f in FP.BLOCK_FIELDS)
FIELDS_PAIR = ", ".join(f"`{f}`" for f in FP.PER_PAIR_FIELDS if f not in FP.PAIR_STATS)
FIELDS_CROSS = ", ".join(f"`{f}`" for f in FP.CROSS_CHECK_FIELDS)
STATS = ", ".join(f"`{s}`" for s in FP.STATS)
EXCL = "; ".join(f'"{x}"' for x in FP.EXCLUSIONS)

# --- the entry -------------------------------------------------------------------------------------------------------------
RAW = f"""### {NUM} — {a.date} — Cache reading of the Finance Agent run's paired helper sub-calls registered before any pair is built: next-token sensitivity of Qwen3-1.7B to reading a logged helper sub-call with its matched document states taken from one earlier sub-call of the same trajectory, fresh vs reused with RANDOM and CYCLIC controls, and the oracle removal fraction at τ_K; the pairs derived by 0075's code; descriptive, no band, no hypothesis row, no cell moves

**Why.** 0049 (line {HL['0049']}) reads an assembled same-model cache from one agent to another: on 0036's 35 long handoffs the receiver reads the sender's states for the tokens they share. 0075 (line {HL['0075']}) counts, in the helper sub-calls of the Finance Agent Benchmark v2 run, the document tokens a sub-call carries that an earlier sub-call of the same trajectory already carried: an upper bound on the reuse opportunity, with no carryover effect read. This entry registers the reading of that opportunity by 0049's reader, on 0049's axis: for a pair of sub-calls of one trajectory, B and an earlier A, how much reading B with A's states for their shared document tokens changes the reader's next-token predictions on B's logged response, and the oracle removal fraction of those states at τ_K. It measures prediction sensitivity on fixed logged text, not task quality, free generation or speed; 0047's standing sentence (line {L['0047_claim']}) "No downstream task-quality number is claimed" stands. **No band, no hypothesis row, no `verdict:` line, no cell moves.**

**What was seen before this text.** Every rule here was fixed before any content of the run's logs was read: the window, the pair rule, the floor, the ceiling and its order, what is scored, and the length rule, which was chosen before any length was seen. Until this entry was committed, the work for it read no log's content: only synthetic logs, and at most the layout of row 1's logs (file names and record schemas). The inputs are built after this entry's commit: the build refuses until the committed ledger holds 0075 and {NUM}, so nothing the build shows can change this text. The build's counts are carried by its manifest, not here: this entry states no expected count. The driver reads no pair until the committed ledger holds {NUM}.

**The trajectories, by 0075's code.** The run is the one 0075 registers on the 27 public questions of Finance Agent Benchmark v2 at `{HARNESS[:12]}`, served by `{MODEL}`. This cell's pairs are derived by 0075's own code, imported and not copied: {h('src/linear_ceiling/fab_reuse.py')} with {h('config/fab-reuse.toml')}, both as they landed with 0075. Its sub-calls (0075, {lines('0075_subcall')}), their order, the rebuilt prompts, the document tokens and their identities ({lines('0075_identity')}: "{q('0075_identity')}"), SAME and DIFFERENT OFFSET ({lines('0075_offset')}), and the last turn SET ASIDE when a trajectory ended without its final record ({lines('0075_setaside')}) are all 0075's. A trajectory gives pairs only if 0075 measures it. A trajectory with no final record (the wrapper ended it, or its process ended) has its last turn set aside by 0075 and is measured over the turns before it; this cell reads it the same way: no sub-call of the set-aside turn is an A or a B, and the earlier turns' pairs are built and read like any other trajectory's. A trajectory that did not end by itself but wrote its final record is read over every turn it completed, as 0075 reads it. The summary does not split pairs by how their trajectory ended: each per-pair row carries its `task_id` and `ended_by_itself`, 0075's value for that trajectory, and the pairs of a trajectory that did not end by itself lie in turns it completed; 0075's summary lists those trajectories with their stop reasons. The build refuses a trajectory served by another model; one whose serving model cannot be read is one 0075 does not measure (an unreadable record), so it gives no pair. The adapter derives each sub-call's document tokens again with 0075's `document_tokens`, and refuses unless its totals equal those of 0075's `measure_trajectory` for the trajectory (sub-calls, prompt tokens, document tokens, SAME OFFSET, DIFFERENT OFFSET and NEW). A trajectory 0075 does not measure gives no pair and is named under 0075's reason.

**The window: one run, one window.** A question is read only if every one of its launches has ended, each with its launch record written and its `end` at or before {WINDOW}. The run's wrapper writes a launch's record once, when it ends, and creates the launch's output file when it starts; a launch with that file and no record has not ended, and it bars its question whatever the question's earlier records say: the question is not read, and is named under "a launch with no end record at the build". Only the two names are looked at. Only the log directories an in-window record lists are read, and every file read must have the sha256 that the record gives it, or the build refuses. Every other question is named with its status: no launch record; a launch with no end record at the build; outside the window (an `end` after it, or a record that does not decode); no trajectory in its launch records (failed launches only); or not measured by 0075, with 0075's reason. If the run has ended by then, the window holds the whole run. The run goes on after the window closes, and no later trajectory is read under this entry.

**Pairs.** B is a sub-call carrying at least one document token whose identity an earlier sub-call of its trajectory carried. A is the latest earlier sub-call of that trajectory carrying at least one of B's document-token identities: one pair per B. A is a single writer, so B's reused document tokens that only other earlier sub-calls carried are recomputed, not taken from A; each pair reports the matched set's size over B's reused document tokens as 0075 counts them (`matched_share_of_reused`). The matched set M is B's document tokens whose identity occurs exactly once in A and once in B, as position pairs (p_A, p_B) in B's order, less those with p_A = p_B inside the longest common token prefix of A and B: under causal attention their reused and fresh states coincide, so they are recomputed and counted (`matched_in_common_prefix`). An identity repeated within A or within B is recomputed and counted too (`repeated_key_tokens`). A pair whose M is empty is not read: it is "prefix" if the common-prefix rule removed at least one of its tokens (an exact prefix cache serves those, so there is no carryover to read), else "repeated keys only". A read pair is SAME-OFFSET if p_A = p_B over all of M, and DIFFERENT-OFFSET otherwise, which includes pairs where only part of M moved; each pair reports the share of M at a different offset (`different_offset_share`). The two classes are reported apart and pooled.

**The length rule, chosen before any length was seen: exclude, never truncate.** The cap is 0047's, {CAP:,} tokens under YaRN 2.5. A is prefilled only through the end of the {CHUNK}-token prefill chunk that holds its last matched token (the first chunk boundary after that token), or all of A if A ends sooner. With the driver's {CHUNK}-token chunks under causal attention, the states read at A's matched positions are then bit-identical to those of a prefill of all of A, which a test in this commit set shows on a synthetic case; nothing that is read is cut. A pair is read only if that prefill of A is at most {CAP:,} tokens, and so is B with its continuation less one token (the continuation's positions follow B's); otherwise it is "over the cap". B is never cut, so the scored response is the response to the prompt that is read. The host memory a pair needs is fixed now as well, from the manifest alone: a pair is read only if its predicted host memory, {HOSTFIX} GiB plus {HOSTB:,} bytes per token of M, is at most {HOSTLIM} GiB, otherwise it is "over host memory". The bytes are four float32 copies of M's keys and values on the host at once (FRESH's, A's, the relocated ones and one arm's, over 28 layers, 8 KV heads and 128 dimensions); the fixed part covers the runtime, the logits and the per-layer work. Each candidate's manifest record carries its prediction (`predicted_host_GiB`). At these settings the rule excludes no pair the cap admits: M is shorter than the cap, and {CAP:,} tokens predict {HOST_AT_CAP:.1f} GiB. The reading needs a machine with at least {HOSTLIM} GiB of host memory. The outcome reports the pairs the cap leaves out, their share of all candidate pairs' matched tokens (`over_the_cap_matched_share`), and 0075's two counts at the cap ({lines('0075_cap')}).

**Exclusions, in order, each counted and named.** A candidate pair takes the first of these that applies: {EXCL}. "Below the matched-token floor" is |M| < {FLOOR}; "beyond the ceiling" is a pair after the registered order's first {CEILING}. 0014 (line {L['0014']}): "{q('0014')}" An excluded pair carries no reading and no zero.

**Order and ceiling.** Fixed with `make_rng({cfg['seed']})`. It depends only on which pairs are eligible, keyed by task id and by B's turn and tool: lengths and counts decide eligibility, before the order, and no length or text enters it. The in-window trajectories with an eligible pair, sorted by task id, are permuted; each one's eligible pairs, sorted by B's turn and tool, are permuted; the pairs are taken round robin, one from each trajectory before any trajectory's second. The first {CEILING} are selected. The adapter's manifest records every candidate with its reason, the registered order and the selection, with each input's digest. The driver refuses a selection that is not the order's first pairs or that exceeds {CEILING}, and the outcome reports the counts with the manifest's digest.

**What is scored.** The continuation C is B's logged helper response (its record's `query_result.output_text`) in the reader's tokenizer: its first {CONT} tokens, including the unscored conditioning token C[0], teacher-forced after B, as 0047 scores the recorded continuation. The harness sent B as one user message through a chat interface; the reader reads the logged text with no chat template. FRESH is the reader's chunked prefill of all of B. REUSE takes A's states at p_A for every token of M, keys relocated to p_B under the same fixed schedule and values unrotated, and computes the rest of B in B's order against the cache assembled so far: 0047's REUSE-ALL ({lines('0047_arms')}) with this M. RANDOM and CYCLIC are 0047's controls, unchanged. Per pair: the mean of KL(p_FRESH ‖ p_ARM) over the scored tokens, its p90, and top-1 agreement. Every figure carries the label "{FP.LABEL}".

**The oracle removal fraction, computed in this driver.** For each token of M, layer and KV head, δ_K is ‖K_REUSE − K_FRESH‖² over SST_K / |M|, where SST_K is the layer-head's centered sum of squares of the fresh keys over M, with keys unrotated to position 0 and in float64: `deviation_means`' arithmetic kept per token (`token_deviation`, `tools/cache_behavior/core.py`), then averaged per token over layers and heads. The normalisation is per pair: SST_K is taken over the pair's own M, so f* depends on which tokens M holds. The driver stops unless the mean of those token means equals `deviation_means`' K to 1e-9 relative. f* is `e9_pertoken.f_star` of the token means at τ_K = {cfg['tau_K']!r}, 0047's τ_K (line {L['0047_tau']}), which there names the archived tail only and here also sets f*. f* is the oracle removal fraction (0058, line {L['0058']}), reported per pair beside the tokens over τ_K and the largest token mean (0045, line {L['0045']}). It is computed by this driver on the logged pairs, not by the E9 instrument.

**The cross-instrument control, before any finance pair.** On 0049's probe handoff, `{CROSS['handoff']}`, from 0049's prepared inputs (manifest `{CROSS['manifest_sha256'][:12]}…`, case file `{CROSS['file_sha256'][:12]}…`), the driver computes its per-token δ_K as above and compares it with the E9-long archive's for the same matched tokens. It passes if every token's |driver − archive| ≤ {cfg['bridge_absolute_tolerance']} + {cfg['bridge_relative_tolerance']} × the archive's value, which is 0047's registered archive-bridge tolerance ({lines('0047_bridge')}) applied per token, and if the two f* differ by at most one token's share of M; the two counts over τ_K are recorded, not gated. On that handoff the archive's f* is 0: the mean of its token means, {ARCHIVE_MEAN}, is under τ_K, while {ARCHIVE_OVER:,} of its {ARCHIVE_MATCHED:,} matched tokens are over it. These three are computed from the case file's `delta_K` (shape [{ARCHIVE_MATCHED}, 28, 8]) with `e9_pertoken.token_mean` and `f_star` at τ_K; the case file is not in the repository, and `docs/drafts/append_{NUM}.py --case-file` recomputes them from it and refuses on a difference. The per-token comparison is therefore the informative part of the check. A failure stops the run before any finance pair is read. The branch and the wall-time limit are fixed once per manifest: the first launch writes them beside the manifest (`launch.json`, created only if absent), before the control runs; a first launch on a manifest that has one is refused, in a new output folder too, and a resume must match it. A failed control therefore ends this reading: a resume refuses it and no other launch on the manifest is accepted. The lock binds the copy of the inputs it sits beside, so the inputs are prepared once: no second manifest is built or read under this entry, and a manifest whose lock has no report beside it is not replaced. The outcome names every manifest built, its lock and every launch. If the control runs and passes, every f* carries "{FP.CROSS_CHECK_LABELS['run']}". If its inputs cannot be staged for the sitting, it is recorded as not run and every f* carries "{FP.CROSS_CHECK_LABELS['not staged']}".

**Controls, the probe and the stop.** The controls are 0047's ({lines('0047_repeat')}), on the probe pair only, as 0073 ({lines('0073')}) states for both earlier runs. The fresh repeat must reproduce the first FRESH pass's logits exactly, and the driver now stops on any nonzero error under every config, the condition 0074 sets ({lines('0074')}). The prefix copy over 128 tokens stays at most 0.0005. TF32 is off, algorithms are deterministic, and `CUBLAS_WORKSPACE_CONFIG=:4096:8`. There is no archive bridge, since no archive holds these pairs; the identity check and the cross-instrument control stand in its place. There is no attention slice (`attention_queries = 0`): it needs the deviation before the fresh pass, which only an archive supplied. The report records both as not computed. The largest selected pair, by the larger of A's prefill and B with its continuation less one, is read first as the memory probe, as in 0047 ({lines('0047_probe')}: "{q('0047_probe')}"). It is selected by size, not by the order, and flagged in the per-pair rows (`probe`); the rest follow in the registered order. The sitting's wall-time limit is a UTC time fixed at its first launch, before the probe pair is read, and recorded in the report and in `launch.json`; a resume keeps it and the cross-check branch, and the driver starts no pair after it. Between the probe and the rest, only the controls, the cross-check, peak memory and minutes are read off the report: no pair's reading is inspected before the sitting stops. The read set is therefore the probe pair plus a prefix of the registered order; the summary states the read count and names the selected pairs not read. The stopping rule is 0047's: a failed control, identity check or hash, or an out-of-memory, stops the run; the completed prefix is kept; a resume needs unchanged code, inputs, config and runtime. Before each step, the cross-instrument control and then each pair, the driver records the step as under way (`in_flight`, with its start time) and clears it when the step's result is written. A resume moves a step it finds under way to `ended_in_flight`, with the time it found it, and reads that step again, since the read set stays a prefix of the order; so a process that ends during a step, by a kill or an error, is attributed to that step.

**Summary, fixed now.** Over the read pairs, each pair one unit, the headline as the 35-handoff row's unit is a handoff: the median with p10 and p90, by the repository's one convention (0013, line {L['0013']}), of f* and of each arm's three statistics. Beside it, a trajectory-level summary, since the pairs of one trajectory share documents and are not independent: the same convention over trajectories, of each trajectory's median. Both are given for all read pairs and for each class, with the number of trajectories the pairs come from. No interval is reported: p10 and p90 are the spread of the pairs' or of the trajectories' values, not an interval on the median. `results/cache-behavior-fab/summary.json` holds the driver's report fields, with the attention slice as not computed, and a `fab` block holding {FIELDS_FAB}. `all`, `same_offset` and `different_offset` each hold {FIELDS_BLOCK}; each of `pair_level` and `trajectory_level` holds `n`, `median`, `p10` and `p90` of `f_star_K` and of {STATS} for each arm, as `reuse_…`, `random_…` and `scrambled_…` (CYCLIC). `per_pair` holds, for each read pair, the same statistics with {FIELDS_PAIR}; in it A is `sender_tokens` (A's prefill through the cut, of `a_tokens` in all), B is `receiver_tokens`, and CYCLIC's statistics are the `scrambled_…` ones. `excluded` names the candidates under each reason, `questions` the task ids under each status, `not_read` the selected pairs not read and `stopped` the time and the read count if the limit stopped the sitting. `ended_in_flight` lists each step started and not finished, with its start time and, if a resume found it, that time. `built` is the manifest's build time (UTC), and `reused_within_cap_0075` holds 0075's two counts at the cap, `reused_in_capped_prompts` and `reused_in_capped_pairs`, summed over the measured in-window trajectories, with their number. `cross_check` holds `branch`, `label` and `result`: null until the control has run, then {FIELDS_CROSS}. A field with nothing to report is null, never a zero.

**What stands beside what.** This cell is on the same axis as 0049's 35-handoff REUSE-ALL row (line {L['0049_row']}) and stands beside it, never pooled with it. These differences remain: the text, a finance agent's helper prompts holding filings and web pages, against coding agents' handoffs; the pairing rule, sub-call to sub-call inside one agent's trajectory, not agent to agent; the single writer, A being one earlier sub-call; the matched set, 0075's exact document-token identities against 0036's archived alignment pairs (line {HL['0036']}); the continuation, the serving model's logged response read with no chat template, against the recorded receiver response; the window, questions that ended by {WINDOW}; and the cap, pairs within {CAP:,} tokens, against 0049's receivers of at most 25,073. There is no attention slice and no archive bridge here, and f* is this driver's.

**The logs' text.** The logs hold the text of filings and web pages. The adapter writes its inputs, as token ids, into a private folder outside this repository; the logged prompts go to the pod as token ids, and nowhere else, and they are removed from the pod before it is released. The outputs hold no token of the logs (each continuation is kept as its length and the sha256 of its ids), and the manifest holds digests, counts, task ids and turn and tool numbers. The outputs do hold the reader's outputs on the logged text: per-token KL, top-1 agreement and deviations, and on the probe pair the witness, the reader's logits at up to four continuation positions for FRESH and each arm. They are kept private with the output tree, which is copied from the pod into a private folder and verified there by digest; for this sitting it is not backed up to the Hub. Nothing of the logs is committed or republished.

**The earlier runs.** Every driver change is selected by this cell's config except two, which make every config stricter: the exact fresh repeat (0074), and a guard refusing a prompt and its continuation past the cap (0049's receivers are at most 25,073 tokens). Tests in this commit set show both committed configs passing the driver's check, and an earlier run's summary byte-identical under this driver and under the one 0069 ran (`tools/cache_behavior/run.py` blob `{DRIVER_0069['tools/cache_behavior/run.py'][:12]}…` and `core.py` blob `{DRIVER_0069['tools/cache_behavior/core.py'][:12]}…`, at `f98d53b`); 0049's and 0069's own output trees, outside the repository, also re-summarise byte-identical under this driver. 0049 and 0069 stay pinned by their commits.

**Gate and enforcement.** `tools/cache_behavior/run.py --prepare --config config/cache-behavior-fab.toml` builds the inputs with no model. It refuses before the window ends, until the committed ledger holds 0075 and {NUM}, on an existing manifest, on a tokenizer other than 0075's, on a file read whose bytes differ from its launch record, on a walk that does not reproduce 0075's counts, on two trajectories for one question, and on another serving model. The driver refuses until the committed ledger holds 0075 and {NUM}; on a manifest whose config or code digests differ from the tree's; on a selection other than the order's first pairs; on any input whose digest or lengths differ from the manifest; on a first launch without a wall-time limit and one cross-check branch, or on a manifest that already has a `launch.json`; and on a resume that changes either or differs from `launch.json`. This script refuses unless the cell's files are committed as-is, 0075's module and config are the blobs that landed with 0075, the cell's gate names 0075 and {NUM}, its shared settings equal `config/cache-behavior.toml`'s, and nothing exists under `results/cache-behavior-fab/`. Pinned at append: {h('config/cache-behavior-fab.toml')}, {h('tools/cache_behavior/fab_pairs.py')}, {h('tools/cache_behavior/run.py')}, {h('tools/cache_behavior/core.py')}, {h('tests/test_cache_behavior_fab.py')}.

**What this does NOT touch.** Every cell and verdict; τ, the rule and the bands; entries 0047, 0049, 0061, 0069 and 0075, their configs and records; every other output tree; the figure set 0072 lists.

**Consequences in this commit set.** `config/cache-behavior-fab.toml`, `tools/cache_behavior/fab_pairs.py`, `tests/test_cache_behavior_fab.py`, the changes to `tools/cache_behavior/run.py` and `tools/cache_behavior/core.py`, a section in `docs/agent/experiment-commands.md`, a line in `docs/agent/repo-architecture.md`, and the drafts README's allocator. Nothing under `results/`.

**Scope.** One reader, Qwen3-1.7B at YaRN 2.5, cap {CAP:,}; one run of one serving model, on the public questions in the window; pairs within a trajectory; fixed logged text, so KL and top-1 agreement are not task outcomes; same-model only; no second reader; a registration, not a result.

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
assert "UNVERIFIED" not in ENTRY
for _f in (*FP.FAB_FIELDS, *FP.BLOCK_FIELDS, *(f for f in FP.PER_PAIR_FIELDS if f not in FP.PAIR_STATS),
           *FP.CROSS_CHECK_FIELDS, *FP.STATS, "f_star_K", "pair_level", "trajectory_level"):
    assert f"`{_f}`" in ENTRY, f"the entry does not name the summary field {_f!r}"
assert all(f"`{arm}_…`" in ENTRY for arm in ("reuse", "random", "scrambled"))
for _f in ("launch.json", "in_flight", "ended_in_flight", "result", "branch", "label", "predicted_host_GiB",
           *FP.WITHIN_CAP_0075):
    assert f"`{_f}`" in ENTRY, f"the entry does not name {_f!r}"
for _x in FP.EXCLUSIONS:
    assert f'"{_x}"' in ENTRY, f"the entry does not name the exclusion {_x!r}"
for _label in (FP.LABEL, *FP.CROSS_CHECK_LABELS.values()):
    assert " ".join(_label.split()) in " ".join(ENTRY.split()), "a label the summary writes is not in the entry"

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
