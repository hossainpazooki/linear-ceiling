"""Append entry 0049 -- the cache-behavior comparison RAN (registered by 0047); figures only, written ONLY from
`tools.cache_behavior.run.summarize` run in-process over the operator's verified output. DESCRIPTIVE: no `verdict:`
line, no hypothesis row, no band, no cell moves. "No downstream task-quality number is claimed" stands.

Ordering guard: 0048 on the ledger, 0049 absent; the reader must PASS (it re-hashes every case record, checks the
scored set is exactly the registered one, the continuation lengths, the witness, and rebuilds every statistic). The
inputs manifest asserted is the OPERATOR's (`2aeee576…`, prepared on Linux 2026-10-07) with its pinned fields checked
against the pilot's freeze record, per the operator ruling of 2026-10-07 quoted in the entry (the pilot's frozen
`9a6f2923…` embeds the sha of a private file). Run facts the reader cannot know come as arguments and are refused
when missing:

  --box "<instance type, GPU, region, instance id>"   --launched <UTC>   --finished <UTC>
  --dataset <repo_id>       the R8 backup, verified by tools/hf_verify_backup.py (exit 0) before this runs
  --output <path>           default results/cache-behavior (report.json, case .npz, inputs/)
  --date <YYYY-MM-DD>       defaults to --finished's date
  --preview                 print, do not append
Runs `ledger_check` after appending. Delete once appended, chained to the append with `&&`.
The reader imports torch and transformers at module level: run this from the WSL venv that has them (torch-cpu suffices).
"""
import argparse
import datetime as dt
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from linear_ceiling.hashing import sha256_file_bytes, sha256_text_file   # noqa: E402  (text = LF-normalized, for tracked files on a CRLF checkout)
from linear_ceiling.ledger_check import _ENTRIES_HEAD, chain_hash  # noqa: E402

NUM, PREV, REG = "0049", "0048", "0047"
# The pilot's frozen manifest (0047) embeds `evidence_sha256_manifest`, the sha256 of the pilot author's private
# SHA256SUMS file, so no operator prepare can reproduce it byte-for-byte. Operator ruling 2026-10-07 (verbatim in the
# entry text): the clause is read on the manifest's PINNED fields, and the operator's manifest is the one asserted.
PILOT_MANIFEST_SHA = "9a6f2923d3beda90cebde009ba80a12c5363c43a440fc19a356d6b3f11d4e2dc"   # frozen with 0047, for the text
INPUT_MANIFEST_SHA = "2aeee5769c0a3b557e1fecd43c2a745abe9f29c37af66b0eabb54358b4c35b22"   # the operator's, prepared on Linux 2026-10-07
FREEZE = REPO_ROOT / "docs" / "2026-10-01-cache-behavior-freeze.json"                     # the pilot's freeze record
RULING = ("0047's byte-for-byte clause is read as: every field of the operator's manifest that is pinned to the "
          "repository or the verified archive equals the pilot's freeze record; the evidence-file digest, which pins a "
          "private file, is excluded. The operator's manifest 2aeee576… is the one 0049 asserts.")
ARMS = {"reuse": "REUSE-ALL (assembled same-model cache)", "random": "RANDOM (norm-matched perturbation)",
        "scrambled": "CYCLIC (matched states permuted, keys relocated)"}

ap = argparse.ArgumentParser()
ap.add_argument("--box", required=True)
ap.add_argument("--launched", required=True)
ap.add_argument("--finished", required=True)
ap.add_argument("--dataset", required=True)
ap.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "cache-behavior")
ap.add_argument("--date", default=None)
ap.add_argument("--preview", action="store_true")
a = ap.parse_args()
a.date = a.date or a.finished[:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.date), "--date must be YYYY-MM-DD"
LEDGER = REPO_ROOT / "ledger" / "ledger.md"
text = LEDGER.read_text(encoding="utf-8").replace("\r\n", "\n")
assert f"### {PREV} " in text and f"### {NUM} " not in text, f"ordering: {PREV} present, {NUM} absent"
assert f"### {REG} " in text, "the registration entry is not on the ledger"

cfg_sha = sha256_text_file(REPO_ROOT / "config" / "cache-behavior.toml")
core_sha = sha256_text_file(REPO_ROOT / "tools" / "cache_behavior" / "core.py")
run_path = REPO_ROOT / "tools" / "cache_behavior" / "run.py"
run_sha = sha256_text_file(run_path)
sys.path.insert(0, str(REPO_ROOT))                      # run.py does `from .core import …`: import it as the package module
mod = importlib.import_module("tools.cache_behavior.run")
assert Path(mod.__file__).resolve() == run_path.resolve(), f"imported {mod.__file__}, expected {run_path}"

report = json.loads((a.output / "report.json").read_text(encoding="utf-8"))
assert report["complete"], "the run is not complete; a partial close is not registered for this cell"
identity = report["identity"]                                  # run.py nests the run identity (hashes, runtime, GPU) here
assert identity["code_sha256"] == {"run.py": run_sha, "core.py": core_sha}, "the run's driver hashes are not the committed driver's (0047)"
assert identity["config_sha256"] == cfg_sha, "the run's config is not the registered config"
assert identity["manifest_sha256"] == INPUT_MANIFEST_SHA, "the run's prepared inputs are not the operator's manifest (ruling 2026-10-07)"
assert identity["cublas_workspace_config"] == ":4096:8", "the run did not pin CUBLAS_WORKSPACE_CONFIG"
assert len(report["run_order"]) == 35 and list(report["scores"]) == report["run_order"], "scored set is not the registered run order"
assert sha256_file_bytes(a.output / "inputs" / "manifest.json") == INPUT_MANIFEST_SHA
# The ruling's pinned fields. The freeze record pins only config_sha256 and input_manifest_sha256; the config digest is
# checked against it, the other three against the committed bytes and the verified e9l mirror.
manifest = json.loads((a.output / "inputs" / "manifest.json").read_text(encoding="utf-8"))
freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
assert manifest["config_sha256"] == freeze["config_sha256"] == cfg_sha, "manifest config digest differs from the pilot's freeze record"
assert manifest["corpus_manifest_sha256"] == sha256_text_file(REPO_ROOT / "config" / "e7-manifest.json"), "manifest corpus digest is not the committed corpus manifest"
assert manifest["archive_config_sha256"] == sha256_text_file(REPO_ROOT / "config" / "e9l.toml"), "manifest archive-config digest is not the committed e9l config"
assert manifest["archive_report_sha256"] == sha256_file_bytes(REPO_ROOT / "results" / "e9l" / "report.json"), "manifest archive-report digest is not the verified e9l report"
assert freeze["input_manifest_sha256"] == PILOT_MANIFEST_SHA, "the freeze record's manifest hash is not the one this entry names"
assert len(manifest["records"]) == 35 and not any(r["excluded"] for r in manifest["records"]), "the prepared cohort is not the registered 35"
result = mod.summarize(a.output, a.output / "inputs")          # fail-closed; raises on any disagreement
assert result["complete"] and result["scored"] == 35 and result["excluded"] == [], f"scored {result['scored']}, excluded {result['excluded']}"
summary_sha = sha256_file_bytes(a.output / "summary.json")
report_sha = sha256_file_bytes(a.output / "report.json")

s = lambda d, nd=4: f"{d['median']:.{nd}f} (p10 {d['p10']:.{nd}f}, p90 {d['p90']:.{nd}f})"  # noqa: E731
arm_lines = []
for arm, label in ARMS.items():
    if arm not in result["arms"]:
        continue
    r = result["arms"][arm]
    arm_lines.append(f"- **{label}**: mean KL per handoff {s(r['mean_kl'])} nats; p90 KL {s(r['p90_kl'])}; top-1 agreement {s(r['top1_agreement'])}.")
att = result.get("attention") or {}
att_txt = "; ".join(f"{k} {s(v)}" for k, v in att.items()) if att else "not reported"
scored_tokens = sum(int(e.get("scored_continuation_tokens", 0)) for e in report["scores"].values())
peak = max((float(e.get("peak_allocated_GiB", 0)) for e in report["scores"].values()), default=0.0)
ctrl_max = {name: max(e["controls"][name]["max_logit_error"] for e in report["scores"].values() if name in e["controls"])
            for name in ("fresh_repeat", "prefix_copy")}
ctrl_txt = (f"fresh-repeat maximum logit error {ctrl_max['fresh_repeat']:.2e}, prefix-copy maximum logit error "
            f"{ctrl_max['prefix_copy']:.2e} (limit 5e-4), over all scored handoffs")
rt = {k: identity.get(k) for k in ("gpu", "torch", "transformers", "cuda")}
assert all(rt.values()), f"run identity is missing a runtime field: {rt}"
commit = report["git_commit"]

ENTRY = f"""### {NUM} — {a.date} — Cache-behavior comparison ran `[BASELINE, DESCRIPTIVE]`: next-token sensitivity of Qwen3-1.7B to reading an assembled same-model cache on the 35 long handoffs, fresh vs reused with two controls; no band, no cell moves

**Setup, as registered ({REG}).** {a.box}; launched {a.launched}, finished {a.finished}; GPU `{rt['gpu']}`, PyTorch {rt['torch']},
Transformers {rt['transformers']}, CUDA {rt['cuda']}; config `{cfg_sha[:12]}…`, driver `core.py` `{core_sha[:12]}…` / `run.py` `{run_sha[:12]}…` as committed,
run at commit `{commit[:7]}`.
35 of 35 handoffs scored, {scored_tokens:,} continuation tokens, none excluded; peak allocation {peak:.2f} GiB. Backup: `{a.dataset}` (R8,
verified both ways before this entry). Pinned: `report.json` `{report_sha[:12]}…`, `summary.json` `{summary_sha[:12]}…`.

**Inputs and the manifest clause of {REG}.** The inputs were prepared by the registered `--prepare` on Linux from the verified
E9-long mirror and the manifest-pinned traces; their manifest is `{INPUT_MANIFEST_SHA[:12]}…`. Its config digest equals the
pilot's freeze record; its corpus-manifest, archive-config and archive-report digests equal the committed bytes and the verified
e9l mirror (the freeze record pins no field beyond the config and the manifest hash itself; all checked by this script), and
every record's trace, alignment, score and token digest matches the corpus manifest and the e9l archive. It is NOT byte-identical
to the pilot's frozen `{PILOT_MANIFEST_SHA[:12]}…`: that manifest's `evidence_sha256_manifest` field is the sha256 of the pilot
author's evidence `SHA256SUMS` file, which is in neither the repository nor the archive, so the frozen hash cannot be reproduced
without that file; whether that field is the only one that differs is unknown until the pilot's manifest arrives (regenerated
`SHA256SUMS` layouts over the same archive files were tried against the frozen hash with no hit; a Windows prepare additionally
differs on every record sha by the zip `create_system` byte, members identical). {REG}'s clause "or the run refuses" was never
the driver's: the frozen `run.py` compares no manifest hash, so the only refusal was this script's, and the ruling below —
made on 2026-10-07 after the run had finished — moved it. Operator ruling, verbatim: "{RULING}" The pilot author's `SHA256SUMS`
and `manifest.json` were requested (issue #20) for a field-level confirmation, which enters as a dated note if it arrives.

**Numerical controls (registered limits in {REG}):** {ctrl_txt}. Every per-handoff archive bridge passed, or the reader would have
refused.

**Figures (`run.summarize` in-process: every case record re-hashed, the scored set checked against the registered 35,
the logit witness re-checked; medians with p10 / p90 over handoffs, `e7_stats` convention, handoffs weighted equally).**
KL is KL(fresh ‖ candidate) per scored token, averaged per handoff.

{chr(10).join(arm_lines)}

Fresh attention at the last 32 receiver queries (descriptive; medians over handoffs): {att_txt}.

**Reading.** Reading the assembled same-model cache changes the receiver's predictions on the recorded continuation by
a measurable amount, and by far less than a norm-matched random perturbation of the same states; the cyclic
permutation sits between them. **Top-1 agreement is not task accuracy and no acceptance threshold exists**; the result
does not validate τ_K as a quality threshold, does not establish unchanged free generation, and measures no speed.
"No downstream task-quality number is claimed" stands.

**What this does NOT touch.** Every cell and verdict; τ, the rule, the bands; entries 0029, 0036, 0038, 0044, 0045 and
their records; the Qwen3 short cells (Condition 1).

prior-entries-sha256: PLACEHOLDER
"""

if a.preview:
    sys.stdout.reconfigure(encoding="utf-8")
    print(ENTRY)
    raise SystemExit(0)
new = text + ("" if text.endswith("\n") else "\n") + "\n" + ENTRY
head = _ENTRIES_HEAD.search(new)
digest = chain_hash(new, new.index(f"### {NUM} "), head.start())
new = new.replace("prior-entries-sha256: PLACEHOLDER", f"prior-entries-sha256: {digest}")
LEDGER.write_text(new, encoding="utf-8", newline="\n")
print(f"appended {NUM}; chain {digest[:12]}")
r = subprocess.run([sys.executable, "-m", "linear_ceiling.ledger_check"], cwd=REPO_ROOT, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
raise SystemExit(r.returncode)
