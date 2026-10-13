"""Draw the README's seam-profile figure from the four same-model summary files.

Reads `seam_profile_left_pooled.same_K` (pooled median per-token deviation by causal distance b^-(t) to the nearest seam,
in R^2's units, entries 0023/0025; the profile the ledger prints at 0029:1786) from each cell's summary.json, refuses if a file's sha256 prefix is not the one the ledger pins, and writes
docs/assets/seam-profile-same-model.png. No number is typed here; the legend's n comes from the file.

    .venv/Scripts/python.exe tools/readme_figure.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELLS = [  # (label, summary path, ledger-pinned sha256 prefix, tau label or None)
    ("Qwen3-1.7B, short handoffs (0029)", "results/e9/summary.json", "ae461db872f2", "tau_K, Qwen pair"),
    ("Qwen3-1.7B under YaRN, long handoffs (0036)", "results/e9l/summary.json", "64e64e9318d4", None),
    ("Llama-3.1-8B, short handoffs (0044)", "results/e9f/summary.json", "e1e5feb8aadd", "tau_K, Llama pair"),
    ("Llama-3.1-8B, long handoffs (0051)", "results/e9fl/summary.json", "1ac712b3897e", None),
]
OUT = ROOT / "docs" / "assets" / "seam-profile-same-model.png"


def main() -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=160)
    for label, rel, pin, tau_label in CELLS:
        p = ROOT / rel
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if not digest.startswith(pin):
            print(f"refuse: {rel} sha256 {digest[:12]} != pinned {pin}", file=sys.stderr)
            return 1
        d = json.loads(p.read_text(encoding="utf-8"))
        prof = d["seam_profile_left_pooled"]["same_K"]
        bins = [row["bin"] for row in prof]
        med = [row["median"] for row in prof]
        n = d["fstar"]["same_K"]["n"]
        (line,) = ax.plot(range(len(bins)), med, marker="o", label=f"{label}, n = {n}")
        if tau_label:
            tau = d["tau"]["K"]
            ax.axhline(tau, color=line.get_color(), linestyle="--", linewidth=1, label=f"{tau_label} = {tau:.4f}")
    ax.set_xticks(range(len(bins)))
    ax.set_xticklabels(bins)
    ax.set_xlabel("causal distance to the nearest seam (tokens)")
    ax.set_ylabel("pooled median per-token deviation, K")
    ax.set_title("Same-model arm: per-token K deviation by distance to the seam (median profile; means in each cell's tail.json)", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
