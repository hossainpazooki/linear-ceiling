"""DRAFT append script for linear-ceiling: entry 0071 (PROVISIONAL number; the drafts README allocates it at staging) --
E-TRUNC's L32-native cell RAN (registered by 0062): the figures, written ONLY from files pinned below by sha256.
DESCRIPTIVE: no `verdict:` line, no hypothesis row; the band word the reader prints is quoted, not read as a verdict.

Why no summarizer runs here. 0062: "Then `summarize_e9_native`: `summarize_e9` on the native cell and on the L32 level
(fail-closed, the gate; ...), the paired comparison, `results/e9tn/compare.{json,md}`. The figures enter by their own
entry, every number read from those files." That run was made once, on the arm64 home, from an export of the tree at
the run's commit (its second attempt, rc 0), and its files were backed up to a private Hub dataset and verified both
ways. This script reads those files by digest and refuses on any other, as 0068's script read its summary. It does NOT
run `summarize_e9_native` in-process, which departs from the drafts README's convention: `summarize_e9` calls
`check_upstream` on the upstream clone ("E9 summary"), and the Windows tree's clone of `../kv-transfer-replication`,
read-only by AGENTS.md, has moved past the pin on paths E9 invokes, so that gate refuses there. The operator ruled
2026-11-13 that this entry reads those files by digest, as 0068's did.

Run facts the reader cannot know are recounted from the sitting's records, each pinned by sha256 (EVIDENCE): the launch,
driver-up and finish times, the run's commit and the card's name; the mirror's counts (the repair seed, the close guard,
the fingerprint verify, the 500-file listing both homes hashed) and the puller's start during the run; the calibration and
summary times and return codes, and the calibration's command as the sitting log records it; the links the summary ran
with; the export's blob list against `git ls-tree` of the run's commit; the L32 summary's digest before and after the
re-run; the upstream record's two renderings (--r2-probe). The alignment files of the home side before the first pull are
compared here with the mirror's, file by file. NOT asserted here, resting on records outside the repository: "RunPod
community"; "after that run had been pulled home and verified" (0061's verify, in 0061's sitting log); "the archived
generic dumps" and "no artifact of this run" (what the calibration read); that the puller's home ran Windows; which two
files `mac/r2-diff.out` compared (it names neither; the sitting log does). "What this does NOT touch" holds by
construction: the script writes only `ledger/ledger.md`.

  --evidence <dir>     the sitting folder (2026-11-11-pod-sitting-0062-l32-native): launch-3b.out, workspace/kit-0062/,
                       root/, pull.log, seed-state.out, guard3-small-files.out, verify-mirror.out, minute-log-2026-11-11.md,
                       mac/ and home-align-before-the-first-pull/; the backup's staging record is read from the sibling
                       folder ../2026-11-12-0062-hub-backup/
  --r2-probe <file>    the line-ending probe of the upstream `r2.json` at the pin: the committed blob's sha, the working
                       file's CR and line counts, and its sha with the CRs removed
  --backup-log <file>  the log of the backup's verified push (tools/hf_backup.sh), ending "BACKUP VERIFIED"
  --dataset <repo_id>  optional; names the backup in the entry and must be the log's repository. Omitted, the entry says
                       "a private Hub dataset".
  --date YYYY-MM-DD    the heading's date: the day the entry is written and appended (entry 0021), not the run day;
                       it must be today's date in UTC, and not before the backup's verify or the last entry's date
  --repo-root <path>   required: the clone this script reads and writes. It must be the current directory and the top of
                       its git work tree; there is no default.
  --preview
Before a preview or the append, the five summary files FILES names under results/e9tn/ and results/e9t-l32n/ are copied
from the arm64 home's mirror (CLAUDE.md, "Previews on Windows"); the others are on the Windows mirror already. The
preview's last line must read `[ordering guard: ok]`. Ordering guard: 0062 present, the ledger's last entry is PREV, NUM
absent. Before the write: `ledger/ledger.md` equals HEAD's and `ledger_check` passes (the chain included). After it:
the new ledger is the old one with this entry appended, and `ledger_check` passes, else the old bytes are written back.
Every guard is an `assert`, so the script refuses to run under `python -O`; a refusal prints the guard's line. Run from
the repo root with `.venv/Scripts/python.exe` (numpy reads the `.npz` files). Delete once appended, chained with `&&`.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tomllib
import traceback
from pathlib import Path

import numpy as np

if not __debug__ or sys.flags.optimize:
    raise SystemExit("REFUSED: python runs with -O or PYTHONOPTIMIZE set, which strips every guard (assert) in this script")


def _refused(et, ev, tb):
    """Any exception is a refusal: print the guard's line so the output shows which one fired; exit status 1."""
    fr = [f for f in traceback.extract_tb(tb) if Path(f.filename).resolve() == Path(__file__).resolve()] or traceback.extract_tb(tb)
    sys.stderr.write(f"REFUSED: {et.__name__} at line {fr[-1].lineno}: {ev}\n  guard: {fr[-1].line}\n")


sys.excepthook = _refused
ap = argparse.ArgumentParser()
ap.add_argument("--evidence", type=Path, required=True)
ap.add_argument("--r2-probe", type=Path, required=True)
ap.add_argument("--backup-log", type=Path, required=True)
ap.add_argument("--dataset", default=None)
ap.add_argument("--date", required=True)
ap.add_argument("--preview", action="store_true")
ap.add_argument("--repo-root", type=Path, required=True)
a = ap.parse_args()
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD (the ledger heading's form)"
dt.date.fromisoformat(a.date)                    # a real calendar date, or ValueError
assert a.date == dt.datetime.now(dt.timezone.utc).date().isoformat(), "--date is the day of writing: it must be today's date (UTC)"
R = a.repo_root.resolve()
assert R == Path.cwd().resolve(), f"--repo-root {R} is not the current directory {Path.cwd().resolve()}"
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=R, capture_output=True, text=True)
assert _top.returncode == 0 and Path(_top.stdout.strip()).resolve() == R, f"--repo-root {R} is not the top of a git work tree"
assert (R / "ledger" / "ledger.md").is_file(), f"no ledger/ledger.md under {R}"
sys.path.insert(0, str(R / "src"))
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file    # noqa: E402  (text = LF-normalized, for tracked files on a CRLF checkout)
from linear_ceiling import ledger_check as _lc                             # noqa: E402
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash        # noqa: E402
assert Path(_lc.__file__).resolve().is_relative_to((R / "src").resolve()), f"imported {_lc.__file__}, not the tree's"

NUM, PREV, REG = "0071", "0070", "0062"
OUT = R / "results"
E = a.evidence.resolve()
CFG = "config/e9t-l32n.toml"
RUNBOOK = "docs/runbooks/2026-10-04-e-trunc-gpu-runbook.md"
FILES = {   # results/<path>: full sha256 of raw bytes
    "e9tn/compare.json": "8a7bc89ceac641ddd035d7838c10e1b5f68e3a6f77809c57411b872f5dc1d41f",
    "e9tn/compare.md": "587b14455ac751950732c597d1358b477b4c60f5761582e4bd42ffbcadf2f001",
    "e9t-l32n/summary.json": "e6a88722b0dcb37b5a6a510e59e831e15ca52f8ec57d5a27b17901343e4b3f79",
    "e9t-l32n/summary.md": "048949dc87d18056b3e8dfecaac9265b9887682741fbd977f229f4991cf9cdec",
    "e9t-l32n/calibration/tau.json": "cc7a69220da666ffdf5dde30efeff087681637ee9d6b56c6e74203a997b45d1a",
    "e9t-l32n/report.json": "f11742a01190ae2068faba6673359f0c3e6a0c5e9b266e66f35bd4b90538cdd7",
    "e9t-l32n/align/coverage.json": "a3e17b0f6763f6cec6f6eb5a2139044b8fb0c8d6c688f0998b5d4eca4cf33ce0",
    "e9t-l32/calibration/tau.json": "8b00952a0067bac696b3aaaef78e9ae30e0bbee0b1154b720fd6a4b436b33482",
    "e9s/compare.json": "a0699a826f1f87ef64fae90757985028c1b0b5425c45c529c8602a417f5767df",
    "e9t/compare.json": "0572662307f3fd60ea9961323336ef573e0110877ab6a6bdedd8dd62f6d96986",
}
PIN = {     # full sha256 of raw bytes; home_align = sha256 of the sorted "sha256  name" lines of that folder's files
    "backup_log": "2f99bb99c641e1eb09d7f5b05e07681af84db302bdfd71833ad611c6da8fb407",
    "r2_probe": "dc77d1243a536b1fb627c314349b82289d9bbf0c638a9bd132a1e3e875bebf0f",
    "home_align": "c79abceaae4f79694444758d4305e8b530a555e2dfe32092949341ca624b6471",
}
EVIDENCE = {   # relative to --evidence; full sha256 of raw bytes
    "launch-3b.out": "714c28bb417a4a3a121a29fa3720e1fd7a212d4c02db052d0d15f8f2cae7e624",
    "workspace/kit-0062/chain.log": "fcd3871b20bb6d6c13eec6432e4ca6a60e0ab904d9d367792a85fba5c6f5751c",
    "workspace/kit-0062/chain.rc": "418a5c17f33c70e99b0cc0a07fce69191489cfedc94164bfa903785777c5bd4b",
    "root/launches.log": "7c3b434419f1504a541cc31a58f821f2e7d64d117018639f0426a520abba84f8",
    "root/e9t-l32n.log": "82ec55c1833e7ef74f08c80b8c7674b9422b1484505029e4143dd295afa71f83",
    "root/setup.log": "a28c9ab0b057215fad78fcc542a4c75756c3ebd14d417fa037ecf29498daecd9",
    "minute-log-2026-11-11.md": "34711928c320b5bd654c6bb930a8c56b938481f599f81b1f88108b09fe3555fb",
    "pull.log": "3705f2f4d3537a65547d80ead983c2ecc6091fd81eb06134a6bd6df6a21176d0",
    "seed-state.out": "4fe63e61292202a2c7d00a0918f1cda6319705010ff7b9d7ba337d22ff5f5d7c",
    "guard3-small-files.out": "9660233ac89bd87e6e2482b99f23dda19f85fccb2268e6a259cd773efa92c0a3",
    "verify-mirror.out": "77356d9952ca899c3acc13cc889c17a9775e9c073be03cffc707ed74ae3ac288",
    "mac/mac-verify-mirror.out": "74f47c08b7aa37cfb05813f284004bc073715ff942ebe3afc6de1f8088a2d40d",
    "mac/hash-compare.out": "59a7019d29eba805910236dd07bf1878127945f90bfd7f558be37c8099fd3ea0",
    "mac/win.sha256": "211326e34612697974a37e906615526bb8cff4891d1a89935a69094576f67e62",
    "mac/mac.sha256": "211326e34612697974a37e906615526bb8cff4891d1a89935a69094576f67e62",
    "mac/calibrate.out": "261c1f4c76b2d223f6ca46bbbc8dc86a540d9a274322212f432e39ff3fb1c139",
    "mac/summary-log-copy.txt": "7446bb1d9623243098022e0394ba9917b2526759aac030c440a4bbf50eaab4d5",
    "mac/summary2-log-copy.txt": "ca74db5bc757dc41149b62a695ab6c4d1ada4973a496dc7d22f1ab12d38c5f1c",
    "mac/summary2-launch.out": "1db6b0e620c59e842e6acc513baa5f6dc3d0eca4a71b1a272a04ccc95b3f6a30",
    "mac/export-tree.blobs": "5496469d6a09b648859ac3f5cd0d0d75c96c57042faaf17213ff3ca3f751f884",
    "mac/export-mac.blobs": "5496469d6a09b648859ac3f5cd0d0d75c96c57042faaf17213ff3ca3f751f884",
    "mac/after-summary-guards.out": "f7634045a5f0f60b5dce5f4f69cd1b6bd29bc02172341e3cb1eea48b2b9dcb93",
    "mac/e9t-l32-recheck-jsondiff.out": "637fe1e515ccadf236fd685899b51bb692307ed73025143ba97761f1fc8620b7",
    "mac/r2-diff.out": "2aceecc44be1627440832186061939773cca81041c347dc6697fd5f46057f7b8",
    "mac/prep-link.out": "518ada099afcda26bf99f2d93fa889c9aebafcc093b332430735433c966603b0",
    "../2026-11-12-0062-hub-backup/stage-0062.out": "f935867952d917bbc9091750d1c529fd7a249588b324d7c45453121d5f9ec262",
}
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")


def lines_of(p: Path) -> list:
    return re.split(r"\r\n|\r|\n", p.read_text(encoding="utf-8", errors="replace"))


def one(lines: list, pattern: str) -> re.Match:
    hits = [mm for mm in (re.fullmatch(pattern, ln.strip()) for ln in lines) if mm]
    assert len(hits) == 1, f"expected exactly one line matching {pattern!r}, found {len(hits)}"
    return hits[0]


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=R, capture_output=True, text=True, check=True, env=ENV).stdout.strip()


def leaves(v, pre=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from leaves(x, f"{pre}/{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from leaves(x, f"{pre}/{i}")
    else:
        yield pre, v


# --- the ledger: ordering, and the pins 0062 states ------------------------------------------------------------------------
LEDGER = R / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
heads = re.findall(r"^### (\d{4}) ", text, re.M)
assert heads.count(REG) == 1, f"entry {REG} must be on the ledger exactly once"
last_date = re.search(rf"^### {heads[-1]} — (\d{{4}}-\d\d-\d\d) — ", text, re.M).group(1)
assert a.date >= last_date, f"--date is before the last entry's date ({heads[-1]}, {last_date})"


def block(t: str, entry: str) -> str:
    s = t.index(f"\n### {entry} ") + 1
    nxt = re.search(r"^### \d{4} ", t[s + 4:], re.M)
    return t[s: s + 4 + nxt.start()] if nxt else t[s:]


flat = lambda s: re.sub(r"\s+", " ", s)  # noqa: E731
b62 = flat(block(text, REG))
ordering_ok = NUM not in heads and bool(heads) and heads[-1] == PREV and heads.count(PREV) == 1
pin62 = {"config": re.search(r"`config/e9t-l32n\.toml` \(`([0-9a-f]{12})…`\)", b62).group(1),
         "l32": re.search(r"`config/e9t-l32\.toml` \(`([0-9a-f]{12})…`, 0055's, unchanged\)", b62).group(1),
         "full": re.search(r"\(`config/e9t-full\.toml` `([0-9a-f]{12})…`, whose `\[e9\.trunc\]` defines M_cap", b62).group(1),
         "summarize_e9.py": re.search(r"\(i\) `summarize_e9` \(`([0-9a-f]{12})…`\)", b62).group(1),
         "config.py": re.search(r"\(ii\) `\[e9\.native\]` in `config\.py` \(`([0-9a-f]{12})…`\)", b62).group(1),
         "summarize_e9_native.py": re.search(r"\(iii\) `summarize_e9_native` \(`([0-9a-f]{12})…`\), the paired reader", b62).group(1),
         "coverage": re.search(r"`results/e9t-l32n/align/coverage\.json` \(`([0-9a-f]{12})…`\): 68 observed", b62).group(1),
         "upstream": re.search(r"Same pair, pin `([0-9a-f]{12})`", b62).group(1),
         "e9s": re.search(r"\(`results/e9s/compare\.json` `([0-9a-f]{12})…`, `median_native`\)", b62).group(1),
         "e9t": re.search(r"\(read from `results/e9t/compare\.json` `([0-9a-f]{12})…`\)", b62).group(1)}
lv62 = re.search(r"NATIVE-short far-from-seam median, (0\.\d{4}) .* YaRN-L32 median on M_cap, (0\.\d{4}), recomputed", b62)
mc62 = re.search(r"\*\*(\d+) enter, (\d+) void\*\* under the floor, ([\d,]+) common tokens", b62)
for phrase in ("on the same card as entry 0061's (ruling F)", "the margin (±0.005, as 0055 ruling 1)", "the bootstrap (seed 62, 2,000 reps)",
               'the native-window control on basis "dumped_length"', "The figures enter by their own entry, every number read from those files.",
               "every existing cell's summary is unchanged", "mirrored home, verified and backed up before the figures entry",
               "68 observed · 35 included · 33 excluded"):
    assert phrase in b62, f"{REG} no longer reads {phrase!r}"
b23, b38, b59 = flat(block(text, "0023")), flat(block(text, "0038")), flat(block(text, "0059"))
assert "**Two departures from 0037's text, neither moving a figure.** (i) The cell's τ calibration" in b38, "0038 reads otherwise"
h57 = block(text, "0057").split("\n", 1)[0]
b55, b57 = flat(block(text, "0055")), flat(block(text, "0057"))
assert "speaks for the handoffs whose receiver re-renders enough of the late sender context to survive" in b55, "0055 states no such limitation"
assert "against the scaled-short level" in b57 and "and the long level" in b57, "0057 did not read the YaRN L32 level against the scaled-short and long levels"

# --- the tree: the reader and configs at the run's commit, unmodified -----------------------------------------------------
ch = lines_of(E / "workspace/kit-0062/chain.log")
st = one(ch, r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) CHAIN setup start \(LC_SHA ([0-9a-f]{40}), coverage ([0-9a-f]{12})\)")
RUN_COMMIT = st.group(2)
USED = ["src/linear_ceiling/", "config/e9t-l32n.toml", "config/e9t-l32.toml", "config/e9t-full.toml", RUNBOOK]
assert git("status", "--porcelain", "--", *USED) == "", "a file this entry reads is modified or untracked in the working tree"
assert subprocess.run(["git", "merge-base", "--is-ancestor", RUN_COMMIT, "HEAD"], cwd=R, env=ENV).returncode == 0, \
    "the run's commit is not an ancestor of HEAD"
assert subprocess.run(["git", "diff", "--quiet", RUN_COMMIT, "HEAD", "--", *USED], cwd=R, env=ENV).returncode == 0, \
    "the reader, the package, a config or the runbook changed since the commit the run used"
cfg_sha = sha256_text_file(R / CFG)
assert cfg_sha.startswith(pin62["config"]) and sha256_text_file(R / "config/e9t-l32.toml").startswith(pin62["l32"]) \
    and sha256_text_file(R / "config/e9t-full.toml").startswith(pin62["full"]), f"a config is not {REG}'s pin"
for n in ("summarize_e9.py", "config.py", "summarize_e9_native.py"):
    assert sha256_text_file(R / "src/linear_ceiling" / n).startswith(pin62[n]), f"{n} is not {REG}'s pin"
cfg = tomllib.loads((R / CFG).read_text(encoding="utf-8"))
nat_cfg, UPSTREAM, TAU_K = cfg["e9"]["native"], cfg["e9"]["upstream_sha"], cfg["e9"]["rule"]["tau_K"]
assert UPSTREAM.startswith(pin62["upstream"]) and nat_cfg["margin_abs"] == 0.005 \
    and nat_cfg["bootstrap_seed"] == 62 and nat_cfg["bootstrap_reps"] == 2000
e9_src = (R / "src/linear_ceiling/summarize_e9.py").read_text(encoding="utf-8")
assert "does not exist; run `summarize_e9 --calibrate-tau` before the GPU run (0023)" in e9_src, "the summarizer no longer refuses without the file"
assert 'check_upstream(cfg.upstream_path, cfg.upstream_sha, UPSTREAM_PATHS, who="E9 summary")' in e9_src
nat_src = (R / "src/linear_ceiling/summarize_e9_native.py").read_text(encoding="utf-8")
assert "from linear_ceiling.e7_stats import" in e9_src and "from linear_ceiling.e7_stats import" in nat_src, "the medians are not e7_stats'"
rb_lines = lines_of(R / RUNBOOK)
l32sum = one(rb_lines, r"- \d\d:\d\d:\d\d–\d\d:\d\d:\d\d \*\*L32 summary: rc 0\*\* \(`summary\.json` `([0-9a-f]{12})…`\).*").group(1)

# --- the files read, by digest -----------------------------------------------------------------------------------------------
for rel, want in FILES.items():
    assert sha256_file_bytes(OUT / rel) == want, f"results/{rel} is not the pinned file"
for rel, want in EVIDENCE.items():
    assert sha256_file_bytes(E / rel) == want, f"{rel} is not the pinned file"
ld = lambda rel: json.loads((OUT / rel).read_text(encoding="utf-8"))  # noqa: E731
c, s, t, t32 = ld("e9tn/compare.json"), ld("e9t-l32n/summary.json"), ld("e9t-l32n/calibration/tau.json"), ld("e9t-l32/calibration/tau.json")
report, e9s, e9t = ld("e9t-l32n/report.json"), ld("e9s/compare.json"), ld("e9t/compare.json")
md = (OUT / "e9t-l32n/summary.md").read_text(encoding="utf-8").replace("\r", "").split("\n")


def md_line(prefix):
    hits = [ln for ln in md if ln.startswith(prefix)]
    assert len(hits) == 1, f"{prefix!r}: {len(hits)} lines"
    return hits[0].lstrip("- ").rstrip()


rd, ref, by = c["reading"], c["references"], c["by_cell"]
nat, yarn = by["NATIVE"], by["L32768"]
pair = c["paired_native_minus_yarn_mean_delta_K"]
N = len(report["run_order"])
assert report["complete"] and report["resumed_from"] is None and report["config_sha256"] == cfg_sha \
    and report["upstream_sha"] == UPSTREAM == c["upstream_sha"] and report["order_by"] == "n_sender_desc"
assert c["cells"]["NATIVE"] == {"config_sha256": cfg_sha, "report_sha256": FILES["e9t-l32n/report.json"],
                                "upstream_sha": UPSTREAM, "partial": False}
assert c["yarn_level"] == "L32768" and c["tau_K"] == TAU_K and c["margin_abs"] == nat_cfg["margin_abs"]
assert c["n_scored_everywhere"] == N and all(v == [] for v in c["unscored_by_cell"].values())
assert (c["n_used"], c["n_void"], f"{c['n_common_total']:,}") == (int(mc62.group(1)), int(mc62.group(2)), mc62.group(3)), "M_cap is not 0062's"
assert sorted(c["void"]) == sorted(ref["yarn"]["void"]) == sorted(e9t["void"]), "the void set is not 0057's"
assert c["n_used"] == ref["yarn"]["n_used"] == e9t["n_used"] and c["min_common_matched"] == ref["yarn"]["min_common_matched"]
assert rd["yarn_level"] == rd["yarn_level_on_the_record"] == ref["yarn"]["far_median"] == yarn["far_from_seam_pooled"]["median"]
assert rd["far_from_seam_median_on_M_cap"] == nat["far_from_seam_pooled"]["median"] and rd["complete_coverage"] is True
assert rd["short_native_level"] == ref["short_native"]["far_median"] and rd["margin_abs"] == c["margin_abs"] == 0.005
# the two reference levels, read again from their records as the reader reads them (summarize_e9_native._references)
bin_ = ref["seam_far_bin"]
assert bin_ == "16+" and e9t["reading"]["level"] == "L32768" and e9t["by_level"]["L32768"]["far_from_seam_pooled"]["bin"] == bin_
assert next(r_["median_native"] for r_ in e9s["seam_profile_left_pooled"] if r_["bin"] == bin_) == ref["short_native"]["far_median"]
assert e9t["reading"]["far_from_seam_median_on_M_cap"] == ref["yarn"]["far_median"] and e9s["n_handoffs"] == ref["short_native"]["n_handoffs"]
assert ref["short_native"]["path"] == nat_cfg["short_native_compare"] and ref["yarn"]["path"] == nat_cfg["trunc_compare"]
assert ref["short_native"]["sha256"] == FILES["e9s/compare.json"] and FILES["e9s/compare.json"].startswith(pin62["e9s"])
assert ref["yarn"]["sha256"] == FILES["e9t/compare.json"] and FILES["e9t/compare.json"].startswith(pin62["e9t"])
assert (f"{rd['short_native_level']:.4f}", f"{rd['yarn_level']:.4f}") == lv62.groups(), "the reference levels are not the ones 0062 states"
assert f'reads "{rd["reads_as"]}"' in h57, "0057's heading does not print the same word"
assert s["coverage"] == {"observed": 68, "included": N, "excluded": 33, "scored": N, "registered": N, "unscored": []}
assert s["partial"] is None and s["dump_rope"]["window"]["basis"] == "dumped_length" and s["dump_rope"]["window"]["demand"] == c["max_dumped_length"] == 32769
assert s["tau"]["K"] == c["tau_K"] and t["upstream_head"] == t32["upstream_head"] == UPSTREAM
v, lo, hi = rd["far_from_seam_median_on_M_cap"], rd["short_native_level"], rd["yarn_level"]
assert lo + rd["margin_abs"] < v < hi - rd["margin_abs"] and rd["reads_as"] == "unattributed"
assert pair["bootstrap"]["upper_97.5"] < 0 and pair["bootstrap"]["seed"] == 62 and pair["bootstrap"]["reps"] == 2000 and pair["n"] == c["n_used"]
diffs = [x["paired_native_minus_yarn"]["mean_diff"] for x in c["per_handoff"].values() if not x["void"]]
assert len(diffs) == c["n_used"] and all(d < 0 for d in diffs)
idc = report["controls"]["identity"]
assert report["controls"]["handoff_id"] == report["run_order"][0], "the identity control is not on the largest handoff"
fstar_line = md_line('- **f*(tau_K = 0.3186) E9-same K per handoff').split(':', 1)[1].split('<-')[0].strip().strip('*')

# --- the coverage file and the alignment passes: the home side before the first pull against the mirror ---------------------
cov = (OUT / "e9t-l32n/align/coverage.json").read_bytes()
assert bytes([13]) not in cov, "the mirror's coverage.json carries CR bytes"
cov_lf = hashlib.sha256(cov).hexdigest()
cov_crlf = hashlib.sha256(cov.replace(bytes([10]), bytes([13, 10]))).hexdigest()
assert cov_crlf.startswith(pin62["coverage"]) and cov_lf == FILES["e9t-l32n/align/coverage.json"] and cov_lf.startswith(st.group(3))
HA, MA = E / "home-align-before-the-first-pull", OUT / "e9t-l32n/align"
names = sorted(p.name for p in HA.iterdir())
assert names == sorted(p.name for p in MA.iterdir()), "the home side's alignment files and the mirror's are not the same names"
listing = "".join(f"{sha256_file_bytes(HA / n)}  {n}\n" for n in names)
assert hashlib.sha256(listing.encode()).hexdigest() == PIN["home_align"], "the home side's alignment files are not the pinned ones"
assert sha256_file_bytes(HA / "coverage.json") == cov_crlf, "the home side's coverage.json is not the CRLF rendering"
W = {}
for ln in lines_of(E / "mac/win.sha256"):
    if ln.strip():
        h_, p_ = re.fullmatch(r"([0-9a-f]{64})  (\./\S+)", ln).groups()
        W[p_] = h_
n_json = n_npz = 0
for n in names:
    hb, mb = (HA / n).read_bytes(), (MA / n).read_bytes()
    assert hashlib.sha256(mb).hexdigest() == W[f"./align/{n}"], f"align/{n} is not the file both homes hashed"
    if n.endswith(".json"):
        assert bytes([13]) in hb and bytes([13]) not in mb and hb.replace(bytes([13, 10]), bytes([10])) == mb, f"{n}: not one content in two renderings"
        n_json += 1
    else:
        assert n.endswith(".npz") and len(hb) == len(mb), n
        za, zb = np.load(io.BytesIO(hb)), np.load(io.BytesIO(mb))
        assert sorted(za.files) == sorted(zb.files) and all(za[k].dtype == zb[k].dtype and np.array_equal(za[k], zb[k]) for k in za.files), \
            f"{n}: the arrays differ"
        cdir, j = set(), hb.find(b"PK\x01\x02")
        while j >= 0:
            cdir.add(j)
            j = hb.find(b"PK\x01\x02", j + 1)
        dpos = np.flatnonzero(np.frombuffer(hb, np.uint8) != np.frombuffer(mb, np.uint8)).tolist()
        assert dpos and all((i - 5) in cdir for i in dpos), f"{n}: a byte differs outside the central directory's creating-system byte"
        n_npz += 1
assert n_json > 0 and n_npz > 0, "the alignment passes hold no JSON file or no .npz file"

# --- the sitting's records, by line --------------------------------------------------------------------------------------------
STAMP = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"
t_launch = one(lines_of(E / "launch-3b.out"), rf"== 3b ({STAMP})").group(1)
up = one(ch, rf"({STAMP}) CHAIN DRIVER_UP pid (\d+); liveness is .+")
one(ch, rf"{STAMP} CHAIN CHAIN_END rc 0")
assert (E / "workspace/kit-0062/chain.rc").read_text().strip() == "EXIT=0"
assert one(lines_of(E / "root/launches.log"), rf"launched pid (\d+) at ({STAMP}) args: .*").group(1) == up.group(2)
t_up = up.group(1)
ml = lines_of(E / "minute-log-2026-11-11.md")
one(ml, rf"- {STAMP} STATE AT THE START\. Pod \w+ \(0061's; created {STAMP}\)\..*")
dn = one(ml, rf"- ({STAMP}) 0062 RUN DONE\. By the (\d\d:\d\d:\d\d) poll: \"\[{N}/{N}\] (\S+)\", \"E9 report: \S+/results/e9t-l32n/report\.json\", "
             rf"\"driver\.rc EXIT=0\"; the monitor ended .*")
assert dn.group(3) == report["run_order"][-1] and dn.group(2) <= dn.group(1)[11:19], "the minute log's finish line names another handoff or a poll after its stamp"
t_done = f"{dn.group(1)[:11]}{dn.group(2)}Z"
prog = [mm for mm in (re.fullmatch(r"\[(\d+)/(\d+)\] (\S+): same K [\d.]+ in \d+s", ln.strip()) for ln in lines_of(E / "root/e9t-l32n.log")) if mm]
assert [(int(mm.group(1)), int(mm.group(2)), mm.group(3)) for mm in prog] == [(i + 1, N, h) for i, h in enumerate(report["run_order"])], \
    "the driver's log does not run the report's order"
one(lines_of(E / "root/e9t-l32n.log"), r"E9 report: \S+/results/e9t-l32n/report\.json")
setup = lines_of(E / "root/setup.log")
gpu = one(setup, r"(NVIDIA [^,]+), \d+ MiB, [\d.]+").group(1)
assert one(setup, r"torch \S+ cuda True (.+)").group(1) == gpu
assert t_launch < st.group(1) < t_up < t_done, "the launch, setup, driver-up and finish times are out of order"
# the mirror: a failed first copy, the repair seed, the close guard, the fingerprint verify, both homes' listing
pl = lines_of(E / "pull.log")
first = next(i for i, ln in enumerate(pl) if re.match(r"== \d\d:\d\d:\d\d ", ln))
assert re.match(r"== \d\d:\d\d:\d\d mirror failed \(RuntimeError: stream failed ", pl[first]), "the puller's first round is not the failed copy"
one(pl, rf"{STAMP} PULLER exit rc 0")
p_start = [mm.group(1) for mm in (re.fullmatch(rf"({STAMP}) PULLER start \d+", ln.strip()) for ln in pl) if mm]
assert p_start and t_up < p_start[0] < t_done, "the puller did not start during the run"
seed = lines_of(E / "seed-state.out")
n_rep = int(one(seed, r"L1 listed (\d+) by top folder \{'align': \d+, 'controls': \d+\}").group(1))
assert int(one(seed, r"sha256 pod == home: (\d+) \| not matching or missing: 0 \[\]").group(1)) == n_rep
one(seed, "SEED_DONE")
g3 = lines_of(E / "guard3-small-files.out")
n_small = int(one(g3, r"small files under results/e9t-l32n: pod files (\d+) \| pod hashes read \1 \| equal \1 \| differ 0 \[\] \| missing at home 0 \[\]").group(1))
n_box = int(one(g3, r"box files \(home logs/box/\): pod files (\d+) \| pod hashes read \1 \| equal \1 \| differ 0 \[\] \| missing at home 0 \[\]").group(1))
one(g3, "GUARD3_OK")
fp = {}
for h in report["run_order"]:
    rec = report["scores"][h]
    fp[f"./scores/{rec['score_file']}"] = rec["score_sha256"]
    fp[f"./tokens/{rec['tokens_file']}"] = rec["tokens_sha256"]
    for d, files in (rec.get("kept_dumps") or {}).items():
        for rel, hh in files.items():
            fp[f"./{rec['kept_dir']}/{d}/{rel}"] = hh
assert report["bridge"] is None and all(W.get(p_) == hh for p_, hh in fp.items()), "a fingerprinted file is not the one both homes hashed"
ctl = {}
for rec in report["controls"].values():
    for k_ in ("score", "tokens", "pairs"):
        if isinstance(rec, dict) and f"{k_}_file" in rec:
            p_ = f"./controls/{rec[f'{k_}_file']}"
            assert ctl.setdefault(p_, rec[f"{k_}_sha256"]) == rec[f"{k_}_sha256"], f"{p_}: two fingerprints"
assert ctl and sorted(ctl) == sorted(p_ for p_ in W if p_.startswith("./controls/")) and all(W[p_] == hh for p_, hh in ctl.items()), \
    "a control file is not the one report.json fingerprints"
for vm in ("verify-mirror.out", "mac/mac-verify-mirror.out"):
    vl = lines_of(E / vm)
    one(vl, rf"report\.json sha256 {FILES['e9t-l32n/report.json']}\s+complete=True\s+scored={N}/{N}")
    assert int(one(vl, r"(\d+)/\1 fingerprinted files verified from raw bytes, [\d,]+ B; ALL VERIFIED").group(1)) == len(fp)
kept = report["keep_subset"]
unfp = [p_ for p_ in W if any(p_.startswith(f"./{report['scores'][h]['kept_dir']}/") for h in kept) and p_ not in fp]
assert sorted(Path(p_).name for p_ in unfp) == sorted(["R.npy", "S.npy"] * len(kept)) \
    and all(f"./{report['scores'][h]['kept_dir']}/{x}" in unfp for h in kept for x in ("S.npy", "R.npy")), "the unfingerprinted kept files are not S.npy and R.npy"
assert W["./report.json"] == FILES["e9t-l32n/report.json"] and W["./align/coverage.json"] == FILES["e9t-l32n/align/coverage.json"]
hc = lines_of(E / "mac/hash-compare.out")
n_all = int(one(hc, r"COMPARE windows (\d+) mac \1 identical_lines \1 windows_only 0 mac_only 0").group(1))
wsha = one(hc, r"win\.sha256 sha256 ([0-9a-f]{64})").group(1)
assert wsha == one(hc, r"mac\.sha256 sha256 ([0-9a-f]{64})").group(1) == sha256_file_bytes(E / "mac/win.sha256") == sha256_file_bytes(E / "mac/mac.sha256")
one(hc, "HASH_EQUAL")
assert n_all == len(W)
# the home side: the calibration, then the summary's two attempts, from an export of the run's commit
cal = lines_of(E / "mac/calibrate.out")
t_cal0, t_cal = one(cal, rf"CAL_START ({STAMP})").group(1), one(cal, rf"CAL_END ({STAMP}) rc 0").group(1)
CAL_CMD = f"summarize_e9 --calibrate-tau --config {CFG}"
one(ml, rf"- mac/calibrate\.out: \"CAL_START {t_cal0}\", \"CAL_END {t_cal} rc 0\"\. It ran `{re.escape(CAL_CMD)}` from the {RUN_COMMIT[:7]} export .*")
lk = lines_of(E / "mac/prep-link.out")
one(lk, r"results -> \S+/linear-ceiling/results \| results\.tracked: .*")
one(lk, rf"linear_ceiling \S+/linear-ceiling-{RUN_COMMIT[:7]}/src/linear_ceiling/__init__\.py")
for cl_ in ("e9t-l32n", "e9t-l32"):
    one(lk, rf"{cl_} \| results_dir -> \S+/linear-ceiling/results/{cl_} \| report True \| upstream \S+ True")
one(lk, "load rc 0")
s1, s2 = lines_of(E / "mac/summary-log-copy.txt"), lines_of(E / "mac/summary2-log-copy.txt")
t_s1, t_s1e = one(s1, rf"SUM_START ({STAMP})").group(1), one(s1, rf"SUM_END ({STAMP}) rc 1").group(1)
t_s2, t_s2e = one(s2, rf"SUM2_START ({STAMP})").group(1), one(s2, rf"SUM2_END ({STAMP}) rc 0").group(1)
one(s1, r"\[NATIVE\] summarize_e9 --config e9t-l32n\.toml")
assert not any("[L32768]" in ln for ln in s1) and any("load_handoffs(submission_dirs(e7, cfg)" in ln for ln in s1), \
    "the first summary attempt reached the L32 level or did not stop in loading the handoffs"
one(s1, r"FileNotFoundError: \[Errno 2\] No such file or directory: '\S+/traces/swe-bench'")
one(s2, r"\[NATIVE\] summarize_e9 --config e9t-l32n\.toml")
one(s2, r"\[L32768\] summarize_e9 --config e9t-l32\.toml")
assert not any("Traceback" in ln for ln in s2)
one(lines_of(E / "mac/summary2-launch.out"), r"traces -> \S+/traces \| swe-bench entries \d+")
assert t_done < t_cal0 < t_cal < t_s1 < t_s1e < t_s2 < t_s2e, "the calibration and the summary are out of order"
lt = git("ls-tree", "-r", RUN_COMMIT)
tree = [f"{x.split()[2]}  {x.split(chr(9), 1)[1]}" for x in lt.split("\n")]
assert [ln for ln in lines_of(E / "mac/export-tree.blobs") if ln] == tree == [ln for ln in lines_of(E / "mac/export-mac.blobs") if ln], \
    "the export the summary ran from is not the run's commit"
# (6) the L32 level's summary before and after the re-run, and the recheck files that changed
ag = lines_of(E / "mac/after-summary-guards.out")
l32b = one(ag, r"e9t-l32-small-before\.sha256:([0-9a-f]{64})  e9t-l32/summary\.json").group(1)
assert l32b == one(ag, r"e9t-l32-small-after\.sha256:([0-9a-f]{64})  e9t-l32/summary\.json").group(1) and l32b.startswith(l32sum), \
    "the L32 summary changed in the re-run, or is not the one its runbook records"
i0 = next(i for i, ln in enumerate(ag) if re.fullmatch(r"e9t-l32 small: \d+ identical lines; changed:", ln.strip()))
changed = []
for ln in ag[i0 + 1:]:
    if not ln.startswith("    "):
        break
    changed.append(ln.strip())
assert changed and all(x.startswith("e9t-l32/recheck/") for x in changed)
jd = [ln for ln in lines_of(E / "mac/e9t-l32-recheck-jsondiff.out") if ln.strip()]
assert sorted(ln.split(" | ")[0] for ln in jd) == sorted(Path(x).name for x in changed)
for ln in jd:
    nm = re.fullmatch(r"\S+ \| leaves \d+ \| differ 1 \(float [01], max rel \S+\) \| names \['(\w+)'\]", ln.strip())
    assert nm and nm.group(1) in ("seconds", "r2_sha256"), f"a recheck file differs in another field: {ln[:90]}"
# (1) the two calibrations, and (2) the upstream record's two renderings
la, lb = dict(leaves(t)), dict(leaves(t32))
assert set(la) == set(lb)
tau_diff = sorted(k for k in la if la[k] != lb[k])
assert tau_diff == ["/r2_sha256"], tau_diff
assert t["tau"] == t32["tau"] and t["mapper"] == t32["mapper"] and t["e8_report_sha256"] == t32["e8_report_sha256"]
r2d = [ln for ln in lines_of(E / "mac/r2-diff.out") if ln.strip()]
assert [x for x in r2d if x.startswith(("<", ">"))] and all('"seconds":' in x for x in r2d if x.startswith(("<", ">"))) \
    and "NPZ_SAME" in r2d, "the calibration's r2.json differs in another field"
assert sha256_file_bytes(a.r2_probe) == PIN["r2_probe"], "the r2.json line-ending probe is not the pinned file"
cr = lines_of(a.r2_probe)
n_cr = int(one(cr, r"CR bytes in the working file: (\d+)").group(1))
assert int(one(cr, r"lines: (\d+)").group(1)) == n_cr, "the probe's CR count is not one per line"
committed = one(cr, r"committed blob sha256:\s+([0-9a-f]{64})").group(1)
assert one(cr, r"working file with CRs removed, sha256: ([0-9a-f]{64})").group(1) == committed
arch = t["archived_r2_sha256"]
assert f"sha256 `{arch[:12]}`" in b23 and f"(`{committed[:12]}…`) and at home as its CRLF checkout rendering (`{arch[:12]}…`" in b59
stage = lines_of(E / "../2026-11-12-0062-hub-backup/stage-0062.out")
for rel in ("e9t-l32n/calibration/tau.json", "e9t-l32n/report.json", "e9t-l32n/summary.json", "e9t-l32n/summary.md", "e9tn/compare.json", "e9tn/compare.md"):
    one(stage, rf"{FILES[rel]}  \./results/{re.escape(rel)}")
one(stage, rf"{arch}  \./results/mapper/qwen3-0\.6b-to-1\.7b/r2\.json")
one(stage, rf"kept directories: {len(kept)} \| files without a fingerprint name \(S\.npy, R\.npy\): {len(unfp)}")

# --- the backup ----------------------------------------------------------------------------------------------------------------
assert sha256_file_bytes(a.backup_log) == PIN["backup_log"], "the backup log is not the pinned file"
bl = lines_of(a.backup_log)
one(bl, r"\S+Z\s+dataset exists and is private")
rv = one(bl, r"repo (\S+) @ ([0-9a-f]{8}) \| remote (\d+) files \| local (\d+) files")
assert rv.group(3) == rv.group(4), "remote and local file counts differ"
one(bl, r"lfs-compared \d+, downloaded\+hashed \d+, problems 0")
one(bl, r"BACKUP VERIFIED")
bv = one(bl, r"(\d{4}-\d\d-\d\d)T\d\d:\d\d:\d\dZ\s+BACKUP VERIFIED: (\S+) matches \S+ in both directions\..*")
assert bv.group(2) == rv.group(1)
assert t_s2e[:10] <= bv.group(1) <= a.date, "the backup was verified before the summary or after the entry's date (\"before this entry\")"
if a.dataset is not None:
    assert a.dataset == bv.group(2), "--dataset is not the repository the backup log verified"
backup_txt = f"`{a.dataset}`" if a.dataset else "a private Hub dataset"


def cell(label, d):
    f = d["fstar_median_over_handoffs"]
    p = d["far_from_seam_pooled"]
    return (f"- **{label}**: median over handoffs of mean δ_K {d['mean_delta_K_median_over_handoffs']:.4f}, of the fraction over τ_K "
            f"{d['frac_over_tau_K_median_over_handoffs']:.4f}; f*(0.3186) {f['0.3186']:.4f}, f*(0.1) {f['0.1']:.4f}, f*(0.03) {f['0.03']:.4f}; "
            f"far-from-seam (16+) pooled median {p['median']:.4f}, mean {p['mean']:.4f} over {p['n_tokens']:,} tokens.")


WORD = {3: "three"}
nth = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"  # noqa: E731
assert t_up[:10] == t_launch[:10], "the driver came up on another day than the launch"
ENTRY = f"""### {NUM} — {a.date} — E-TRUNC, the L32-native cell ran `[BASELINE, DESCRIPTIVE]`: 0055's L32 level with both models under their native RoPE, paired with 0057's YaRN L32 level on the same tokens; the registered reading reads "{rd['reads_as']}"; descriptive, no cell moves

**Setup, as registered ({REG}).** RunPod community, 1x {gpu}, the card entry 0061's run used (as entry {REG} registers), after that run
had been pulled home and verified; chain launched {t_launch}, driver up {t_up[11:]}, the {nth(N)} handoff and driver exit 0 by
{t_done}; {s['coverage']['scored']} of {s['coverage']['registered']} registered handoffs, no partial close, no resume. Upstream pin `{c['upstream_sha'][:12]}…`; config
`{cfg_sha[:12]}…`, report `{FILES['e9t-l32n/report.json'][:12]}…`; run at linear-ceiling `{RUN_COMMIT[:7]}`. Backup: {backup_txt} (R8, verified both ways before this
entry). Pinned: `results/e9t-l32n/summary.json` `{FILES['e9t-l32n/summary.json'][:12]}…`, `results/e9tn/compare.json` `{FILES['e9tn/compare.json'][:12]}…`, `compare.md` `{FILES['e9tn/compare.md'][:12]}…`,
the files of the `summarize_e9_native` run that exited 0 (item 5), which this entry reads by digest rather than running it at append.

**Coverage file, two renderings of one content.** Entry {REG} pins `results/e9t-l32n/align/coverage.json` by the sha of the home file's raw
bytes at registration, `{cov_crlf[:12]}…` (CRLF). The box wrote the same lines with LF endings and the mirror carries that rendering,
`{cov_lf[:12]}…`; both shas are derived from the mirror's file here. The other files of the alignment passes compare as follows: the JSON
files are equal once line endings are normalized, and the `.npz` files hold equal arrays and differ only in the zip header's
creating-system byte.

**Home side, stated before any figure.** (1) A departure from 0023's order that moves no figure, as entry 0038 records for its cell: the
τ calibration (`{CAL_CMD}`; `results/e9t-l32n/calibration/tau.json` `{FILES['e9t-l32n/calibration/tau.json'][:12]}…`) was written
at home at {t_cal}, after the GPU run (done {t_done[11:]}) and before the summary, not before the run; the summarizer refuses without the file. The calibration reads only the upstream mapper
(`{t['mapper']['json_sha256'][:12]}…` / `{t['mapper']['safetensors_sha256'][:12]}…`), the archived generic dumps, the archived `r2.json` and E8's report (`{t['e8_report_sha256'][:12]}…`), no artifact of
this run. It gave τ_K, τ_V and τ_agent_K equal to the L32 level's calibration at the same pin: {len(la) - len(tau_diff)} of the file's {len(la)} fields are equal, and
the other is the hash of the calibration's own `r2.json`, which differs in a timing field. The summarizer recomputed it
({md_line('tau recomputation')}). (2) The calibration reads the upstream mapper record
`results/mapper/qwen3-0.6b-to-1.7b/r2.json` in the CRLF rendering of the arm64 home's clone, `{arch[:12]}…`, the sha 0023 registers and
0059 names beside the bytes committed at the pin, `{committed[:12]}…`. The two differ by line endings only. (3) In each of the {WORD[len(kept)]} kept
directories, `S.npy` and `R.npy` carry no fingerprint in `report.json` ({len(unfp)} files); every other kept file does. (4) The mirror was pulled
to a Windows home during the run. After a failed first copy, the small files were re-copied and hashed against the box's own listing
({n_rep} at the repair; at the close {n_small} small files and {n_box} box files equal, none differing), and the {len(fp)} score, token and
kept-dump files `report.json` fingerprints all match it, as do its {len(ctl)} control files. The mirror was then copied to the
arm64 home that ran the summary; all {n_all} files hashed equal on both. (5) The summary
ran on the arm64 home from an export of the tree at `{RUN_COMMIT[:7]}` with the mirror and the traces linked in; its second attempt exited 0, the
first having stopped on a missing link before any scoring. (6) `summarize_e9_native` re-ran `summarize_e9` on the L32 level, as
registered: that level's `summary.json` came out byte for byte the one its runbook records (`{l32sum}…`,
`{RUNBOOK}`), which is {REG}'s "every existing cell's summary is unchanged" checked on the one cell
the pairing reads. Its recheck scratch was rewritten; the files that changed differ in a wall-time field or a hash over one.

**Controls.** Pipeline identity on the largest handoff, from `report.json`: {idc['n_pairs']:,} pairs, maximum squared deviation {idc['max_abs_square']}. As the reader
printed them (`summarize_e9` on the native cell, the gate): {md_line('per-dump RoPE record')}. {md_line('keep-subset re-score')}.
{md_line('- prefix-invariance control')}. The cell's own f*(τ_K), the oracle removal fraction (0058), on the same-model keys over its {N} scored
handoffs: {fstar_line}; the reader prints the 0023 band word for it, {s['band_outcome']}, which this entry does not read as a verdict: the
cell has no hypothesis row.

**Coverage and the void gate.** {c['n_scored_everywhere']} handoffs scored at the native cell and at every E-TRUNC level. Under the registered floor of
{c['min_common_matched']:,} common matched tokens, {c['n_void']} are void, the same {c['n_void']} that 0057 names, and {c['n_used']} are compared on {c['n_common_total']:,} common
tokens: 0057's used set and token count, as {REG} registered. Stated limitation (0055): the
comparison speaks for the handoffs whose receiver re-renders enough of the late sender context to survive head truncation, not for the
long cohort as a whole.

**Figures on M_cap (`summarize_e9_native`: `summarize_e9` passed on the native cell and on the L32 level first; medians over the
{c['n_used']} compared handoffs, `e7_stats` convention; δ in R²'s units, 0023; the config's registered τ_K = {c['tau_K']}; f* is the oracle removal fraction, 0058).**

{cell('NATIVE (S[−32,768:], both models under native RoPE)', nat)}
{cell('L32768 (S[−32,768:], the YaRN receiver of 0057, recomputed on the same tokens)', yarn)}
- **Paired, native − YaRN, mean δ_K over M_cap per handoff**: median {pair['median']:.4f} (p10 {pair['p10']:.4f}, p90 {pair['p90']:.4f}; bootstrap 95 % of the median [{pair['bootstrap']['lower_2.5']:.4f}, {pair['bootstrap']['upper_97.5']:.4f}], seed {pair['bootstrap']['seed']}, {pair['bootstrap']['reps']:,} reps); negative on {sum(d < 0 for d in diffs)} of {len(diffs)} handoffs, the one nearest zero {max(diffs):.4f}.

**The registered reading (ruling A, {REG}).** The far-from-seam (16+) pooled median δ_K of the native level on M_cap is **{v:.4f}**,
against the native-short level {lo:.4f} (0038, read from `{ref['short_native']['path']}` `{ref['short_native']['sha256'][:12]}…`, {ref['short_native']['n_handoffs']} handoffs)
and the YaRN L32 level {hi:.4f} on the same tokens (0057, `{ref['yarn']['path']}` `{ref['yarn']['sha256'][:12]}…`; the reader recomputed it and it
equals the record's), margin ±{rd['margin_abs']}: **the L32 excess reads as "{rd['reads_as']}"**. The label alone does not say where the value
sits: it is {v - lo:.4f} above the native-short level and {hi - v:.4f} below the YaRN level, with {hi - lo:.4f} between the two. The label is the
registered reading; this entry reads no share of the gap from it. Entry 0057's reading printed the same word on the same {c['n_used']} compared
and {c['n_void']} void handoffs, the set being the same by registration; it read the YaRN L32 level against the scaled-short and long levels, which
is another reading.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0036, 0038, 0055, 0057 and their records;
`config/e9t-{{full,l65,l49,l32}}.toml`; `results/e9t/` and `results/e9t-{{full,l65,l49,l32}}/` as they stand, item 6 aside; the E9
driver; `summarize_e9_trunc`.

**Scope.** One receiver, one pair, one corpus, the {N} long handoffs at one truncation level, compared on the {c['n_used']} above the floor; M_cap
sits at late sender positions; the native-short reference is a different cohort (0038's {ref['short_native']['n_handoffs']} handoffs, pooled over their full matched sets) while the YaRN-L32 reference is
the same tokens; both models native, so the cell says nothing about a sender-native / receiver-scaled pairing; f* is read as the oracle
removal fraction (0058); generation quality after reuse not measured; descriptive.

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    print(f"[ordering guard: {'ok' if ordering_ok else f'NOT satisfied — the last entry is {heads[-1]}, want {PREV}; {NUM} must be absent'}]")
    raise SystemExit(0)
assert ordering_ok, f"ordering: the ledger's last entry must be {PREV}, and {NUM} absent"
# --- before the write: the ledger is HEAD's and passes ledger_check, the chain included ----------------------------------------
LEDGER_OK = "ledger ok (blocks unchanged vs HEAD)"


def ledger_check():
    return subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=R, capture_output=True, text=True,
                          env=dict(ENV, PYTHONPATH=str(R / "src")))


at_head = subprocess.run(["git", "show", "HEAD:ledger/ledger.md"], cwd=R, capture_output=True, check=True, env=ENV).stdout
assert text == at_head.decode("utf-8").replace("\r\n", "\n"), "ledger/ledger.md is not HEAD's: an uncommitted edit"
assert git("status", "--porcelain", "--", "ledger/ledger.md") == "", "ledger/ledger.md is modified in the working tree"
r0 = ledger_check()
assert r0.returncode == 0 and r0.stdout.strip().endswith(LEDGER_OK), f"ledger_check before the write: {(r0.stdout + r0.stderr).strip()[-400:]}"
assert "prior-entries-sha256: PLACEHOLDER" not in text, "the ledger already holds a placeholder chain line"
base = text + ("" if text.endswith("\n") else "\n") + "\n"
digest = chain_hash(base + ENTRY, len(base), _ENTRIES_HEAD.search(base).start())
new = base + ENTRY.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
assert new.startswith(text) and new.count(f"\n### {NUM} ") == 1 and new.index(f"\n### {NUM} ") + 1 == len(base), "the new ledger is not the old one plus this entry"
# --- the write, and after it: ledger_check, else the old bytes go back -----------------------------------------------------------
orig = LEDGER.read_bytes()
LEDGER.write_text(new, encoding="utf-8", newline="\n")
r = ledger_check()
if not (r.returncode == 0 and r.stdout.strip().endswith(LEDGER_OK) and LEDGER.read_text(encoding="utf-8") == new):
    LEDGER.write_bytes(orig)
    raise SystemExit(f"REFUSED after the write: ledger_check failed, so the old ledger bytes were written back.\n{(r.stdout + r.stderr).strip()[-600:]}")
print(f"appended {NUM}; chain {digest[:12]}")
print(r.stdout.strip())
