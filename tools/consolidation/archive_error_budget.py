# Diagnostic deletion of near-seam tokens; no claim about practical cache repair.
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
from linear_ceiling.e9_pertoken import centered_delta, token_mean, seam_distance_left


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def summarize(evidence):
    # The evidence manifest also pins alignments, which score reports do not hash.
    hashes = {name: sha for sha, name in (
        line.split("  ", 1) for line in (evidence / "SHA256SUMS").read_text().splitlines()
    )}

    def verified(path, expected=None):
        recorded = hashes[str(path.relative_to(evidence))]
        if digest(path) != recorded or (expected is not None and recorded != expected):
            raise ValueError(f"SHA-256 mismatch: {path}")
        return path

    results = {}
    for cohort in ["e9s", "e9l"]:
        folder = evidence / "archive/records" / cohort
        report = json.loads(verified(folder / "report.json").read_text())
        rows = []
        for hid, entry in report["scores"].items():
            token_file = verified(folder / "tokens" / entry["tokens_file"], entry["tokens_sha256"])
            score = json.loads(verified(folder / "scores" / entry["score_file"], entry["score_sha256"]).read_text())
            alignment = verified(folder / "align" / (Path(entry["score_file"]).stem + ".npz"))
            with np.load(alignment, allow_pickle=False) as data:
                far = seam_distance_left(data["pairs"], len(data["receiver"])) >= 16
            with np.load(token_file, allow_pickle=False) as data:
                sst = np.array([layer["sst"] for layer in score["same"]["K"]])
                delta = token_mean(centered_delta(data["same_K"], sst, len(far)))
            if not far.any():
                raise ValueError(f"No far-span tokens: {hid}")
            rows.append({"handoff": hid, "far_token_share": float(far.mean()),
                         "far_error_share": float(delta[far].sum() / delta.sum()),
                         "retained_far_mean": float(delta[far].mean())})
        results[cohort] = {
            "handoffs": len(rows),
            "far_mean_above_0.03": sum(row["retained_far_mean"] > .03 for row in rows),
            "median": {key: float(np.median([row[key] for row in rows]))
                       for key in ["far_token_share", "far_error_share", "retained_far_mean"]},
            "per_handoff": rows,
        }
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=Path.home() / "Desktop/Carryover-evidence")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = summarize(args.evidence)
    output = args.output or args.evidence / "archive/error-budget.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({key: {k: v for k, v in value.items() if k != "per_handoff"}
                      for key, value in results.items()}, indent=2))


if __name__ == "__main__":
    main()
