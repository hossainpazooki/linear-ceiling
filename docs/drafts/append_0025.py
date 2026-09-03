"""Append the E9 pre-prefill amendment (0025 by default): the descriptive tau ladder and the
keep-subset size -- ordering-guarded, every figure read from config or recomputed in-process.

Refuses unless: entry 0024 is in the ledger and the target number is free; `e9.REQUIRED_ENTRIES`
names the target number (the gate and the entry must agree, or the run could start without it);
`config/e9.toml` loads with `tau_ladder` and the new keep `n` (the loader validates the ladder);
NO prefill has happened (`results/e9/report.json` and `results/e9/scores/` absent -- 0023: nothing
in the rule section is revisited after the first score file exists). The previous keep `n` is
read from `HEAD:config/e9.toml`, never typed. The keep draws (old n and new n) and the retained
dump volume are recomputed here from the raw traces and the receiver's config (alignment is
read-only: nothing is written under results/). After appending it runs `ledger_check.check` and
restores the previous file if anything fails.

    .venv/Scripts/python.exe docs/drafts/append_0025.py --preview      # print the text, touch nothing (~15 s CPU)
    .venv/Scripts/python.exe docs/drafts/append_0025.py                # append as 0025
    .venv/Scripts/python.exe docs/drafts/append_0025.py --number 26    # only after e9.REQUIRED_ENTRIES says 0026

Delete this script once the entry is appended (docs/drafts/README.md convention).
"""
import argparse
import json
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

from linear_ceiling import REPO_ROOT, e9
from linear_ceiling.config import load_e7_config, load_e9_config
from linear_ceiling.e8_text import qwen_encoder
from linear_ceiling.e9 import keep_subset, pair_models, submission_dirs
from linear_ceiling.e9_align import align, load_handoffs
from linear_ceiling.ledger_check import chain_hash, check, committed_manifest_sha, parse_ledger
from linear_ceiling.weights import snapshot

LEDGER = REPO_ROOT / "ledger" / "ledger.md"
CONFIG = REPO_ROOT / "config" / "e9.toml"


def committed_keep_n() -> int:
    r = subprocess.run(["git", "show", "HEAD:config/e9.toml"], cwd=REPO_ROOT, capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("cannot read HEAD:config/e9.toml")
    return int(tomllib.loads(r.stdout)["e9"]["keep"]["n"])


def bytes_per_token(model_id: str) -> tuple[int, dict]:
    """fp16 K+V per token as upstream dump_kv writes it: n_layers x n_kv x d_h x 2 (K,V) x 2 bytes."""
    c = json.loads((Path(snapshot(model_id)) / "config.json").read_text(encoding="utf-8"))
    d_h = c.get("head_dim") or c["hidden_size"] // c["num_attention_heads"]
    shape = {"n_layers": int(c["num_hidden_layers"]), "n_kv": int(c["num_key_value_heads"]), "d_h": int(d_h)}
    return shape["n_layers"] * shape["n_kv"] * shape["d_h"] * 2 * 2, shape


def recon(cfg, e7):
    """Included handoffs with |S|, |R| -- the alignment of 0019, computed and NOT written."""
    src_id, tgt_id = pair_models(cfg.pair)
    enc = qwen_encoder(snapshot(src_id))
    counter = lambda t, ct="assistant": 0  # noqa: E731
    included, observed = {}, 0
    for h in load_handoffs(submission_dirs(e7, cfg), counter):
        observed += 1
        rec, _s, _r, _p = align(h, enc, cfg.context_cap)
        if not rec.excluded:
            included[h.handoff_id] = (rec.n_sender, rec.n_receiver)
    bpt_src, shape_src = bytes_per_token(src_id)
    bpt_tgt, shape_tgt = bytes_per_token(tgt_id)
    return included, observed, (bpt_src, shape_src), (bpt_tgt, shape_tgt)


def volume(included, ids, bpt_src, bpt_tgt) -> float:
    # three dumps per handoff (0019): receiver on S, receiver on R, source on S
    return sum((included[h][0] + included[h][1]) * bpt_tgt + included[h][0] * bpt_src for h in ids)


def render(number: int, cfg, old_n: int, included, observed, src, tgt) -> str:
    (bpt_src, sh_src), (bpt_tgt, sh_tgt) = src, tgt
    ids = sorted(included)
    old = keep_subset(ids, cfg.keep_seed, old_n)
    new = keep_subset(ids, cfg.keep_seed, cfg.keep_n)
    shared = sorted(set(old) & set(new))
    vol_old, vol_new = volume(included, old, bpt_src, bpt_tgt), volume(included, new, bpt_src, bpt_tgt)
    tau_k, tau_v = float(cfg.rule["tau_K"]), float(cfg.rule["tau_V"])
    ladder = [float(t) for t in cfg.rule["tau_ladder"]]
    lad_k = ", ".join(f"{t:.4g}" for t in [tau_k, *ladder])
    lad_v = ", ".join(f"{t:.4g}" for t in [tau_v, *ladder])
    short = lambda h: h.split("/", 1)[1] if "/" in h else h  # noqa: E731
    new_lines = "\n".join(f"  - `{h}` ({volume(included, [h], bpt_src, bpt_tgt) / 1e9:.2f} GB)" for h in new)
    return f"""### {number:04d} — {date.today().isoformat()} — E9 amended before any prefill: descriptive τ ladder registered; keep-subset size {old_n} → {cfg.keep_n}; no verdict changes

**Why before the box.** Two additions carried over from the E-RL design
(`docs/2026-09-02-e-rl-design.md`, unregistered), both descriptive, both cheap, and both of the kind
0023 forbids after the first score file exists. No prefill has happened: `results/e9/report.json`
is absent at append and this script refuses otherwise.

**τ ladder (descriptive; decides nothing).** `summarize_e9` now ALSO states f*(τ) at
τ_K ∈ {{{lad_k}}} and τ_V ∈ {{{lad_v}}} -- the registered value first, then the ladder from
`config/e9.toml` `[e9.rule] tau_ladder` -- for every arm (E9-same and E9-cross, K and V), per handoff
and as the same median / p10 / p90 statistics, from the same per-token record (a re-sort, no new
tensor). **The band and every cell are computed at the registered τ_K = {tau_k:.4f} only**, exactly as
0023 wrote them. What the ladder adds is a reading of *how far inside* the tolerance the re-render
sits: a HOLDS with f*({ladder[-1]:.4g}) ≈ 0 and a HOLDS with f*({tau_k:.4g}) = 0.14 are different findings, and the
E-RL lane, which inherits τ unchanged, reads its lags on the same ladder so the two experiments share
one table. The loader refuses a ladder that is not strictly decreasing inside (0, τ_K). Ladder values
are proposed in the E-RL design, not cited; f* at every τ remains an oracle LOWER BOUND (0023, both
reasons).

**Keep subset: n = {old_n} → {cfg.keep_n} (seed {cfg.keep_seed} unchanged).** 0019 retains a seeded subset of handoffs
with full dumps so a CPU summarizer can re-score from tensors; 0023 registers a `[STRETCH]` partial-
prefill experiment (the one that would make f* an achieved number) and names it as needing injection
code; the E-RL design proposes a behavioral control (stale vs fresh greedy continuation) of the same
shape. Both can only ever run on retained dumps -- they are the only tensors that survive the GPU
day -- and enlarging the subset costs disk and sync time, not GPU. Same seed, larger draw:
`numpy` choice without replacement is NOT nested across sizes, so this is a different set, not the
old {old_n} plus {cfg.keep_n - old_n}. Recomputed here from the raw traces (0019's alignment, {len(included)} included of {observed} observed at cap
{cfg.context_cap}): the n = {old_n} draw was {', '.join(f'`{short(h)}`' for h in old)} ({vol_old / 1e9:.1f} GB); the n = {cfg.keep_n} draw is
{new_lines}
{len(shared)} of the {old_n} carried over ({', '.join(f'`{short(h)}`' for h in shared) if shared else 'none'}). Retained volume {vol_new / 1e9:.1f} GB of fp16 stride-1 dumps
(three per handoff: receiver on S, receiver on R, source on S; {bpt_tgt:,} B per token on the receiver
[{sh_tgt['n_layers']} × {sh_tgt['n_kv']} × {sh_tgt['d_h']} × 2 × 2 B], {bpt_src:,} B on the source), against {vol_old / 1e9:.1f} GB before; the box
needs that much free beside the transient dumps, and the sync off the box scales with it. The
GPU runbook's named keep handoffs and volumes predate this entry and are superseded by the list
above; the driver draws from config, so the run cannot disagree with it.

**Instrument and enforcement.** `config/e9.toml` carries `tau_ladder` and the new `n`;
`load_e9_config` refuses a config without the ladder; `e9.assert_ready` requires THIS entry beside
0019 and 0023 (`REQUIRED_ENTRIES`), so no prefill can start on a ledger that lacks it; `summarize_e9`
writes `tau_ladder`, `fstar_ladder` and `fstar_ladder_per_handoff` to `summary.json` and states them
in `summary.md` under a line that says DESCRIPTIVE. Tests: ladder monotone down the τ axis and the
band unchanged by it; malformed ladders refused; the non-nesting of the keep draw pinned.

**Scope.** All of 0019's and 0023's limits. No hypothesis cell changes with this entry; no
`verdict:` line. The verdict on H-E9 still enters only by its own numbered entry after the run.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--number", type=int, default=None, help="entry number (default: next free >= 25)")
    ap.add_argument("--preview", action="store_true", help="print the entry text; touch nothing")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    text = LEDGER.read_text(encoding="utf-8")
    entries = parse_ledger(text)["entries"]
    number = a.number or max(max(entries) + 1, 25)
    if f"### {number:04d} " not in e9.REQUIRED_ENTRIES:
        print(f"REFUSED: e9.REQUIRED_ENTRIES does not name {number:04d}; the gate and the entry must agree")
        return 2
    if not a.preview:
        if 24 not in entries:
            print("REFUSED: entry 0024 is not in the ledger; appends are sequential")
            return 2
        if number in entries:
            print(f"REFUSED: entry {number:04d} already exists; pass --number for the next free one")
            return 2
    cfg = load_e9_config(CONFIG, REPO_ROOT)          # validates tau_ladder
    e7 = load_e7_config(REPO_ROOT / "config" / "e7.toml", REPO_ROOT)
    if (cfg.results_dir / "report.json").exists() or (cfg.results_dir / "scores").exists():
        print("REFUSED: results/e9 already holds a report or scores -- a prefill has happened; 0023 forbids "
              "amending the rule section after the first score file")
        return 2
    old_n = committed_keep_n()
    if old_n == cfg.keep_n:
        print(f"REFUSED: keep n in config/e9.toml ({cfg.keep_n}) equals the committed value; nothing to register")
        return 2
    included, observed, src, tgt = recon(cfg, e7)
    body = render(number, cfg, old_n, included, observed, src, tgt)
    if a.preview:
        print(body)
        return 0
    entries_start = re.search(r"^## Entries\s*$", text, re.M).start()
    new = text.rstrip("\n") + "\n\n"
    chain = chain_hash(new, len(new), entries_start)
    new += body.rstrip("\n") + f"\n\nprior-entries-sha256: {chain}\n"
    LEDGER.write_text(new, encoding="utf-8", newline="\n")
    problems = check(new, committed_manifest_sha())
    if problems:
        LEDGER.write_text(text, encoding="utf-8", newline="\n")
        print("REFUSED after append (ledger restored):\n  " + "\n  ".join(problems))
        return 1
    print(f"appended entry {number:04d}; ledger_check ok. Commit it WITH config/e9.toml and the e9/summarize_e9/"
          "config changes (the gate reads all three), no header/README edits in the same commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
