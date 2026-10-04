# Recompute the registered E9 key-error statistic and tokenwise exceedances.
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
TAU = 0.3186442653116294
TAUS = (TAU, 0.10, 0.03)
STUDIES = {
    "e9": "Native short",
    "e9s": "Scaled short",
    "e9l": "Scaled long",
}


def sha256(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def artifact_path(base, category, name):
    path = Path(name)
    if path.parts and path.parts[0] == category:
        return base / path
    return base / category / path


def fstar(values, tau):
    # Fewest-largest-token removal fraction leaving a passing remaining mean.
    ordered = np.sort(values)
    means = np.cumsum(ordered) / np.arange(1, len(ordered) + 1)
    passing = np.flatnonzero(means <= tau * (1 + 1e-9) + 1e-15)
    return 1 - (int(passing[-1]) + 1) / len(ordered) if len(passing) else 1.0


def main():
    rows = []
    for study, label in STUDIES.items():
        base = ROOT / "records" / study
        report = json.loads((base / "report.json").read_text())
        for handoff, record in sorted(report["scores"].items()):
            score_path = artifact_path(base, "scores", record["score_file"])
            token_path = artifact_path(base, "tokens", record["tokens_file"])
            for path, expected, name in (
                (score_path, record["score_sha256"], "score"),
                (token_path, record["tokens_sha256"], "token"),
            ):
                observed = sha256(path)
                if observed != expected:
                    raise ValueError(f"{name} SHA-256 mismatch: {path}")

            score = json.loads(score_path.read_text())
            n = int(score["n_pairs"])
            variance = np.asarray(
                [layer["sst"] for layer in score["same"]["K"]], dtype=np.float64
            ) / n
            with np.load(token_path, allow_pickle=False) as archive:
                error = archive["same_K"].astype(np.float64)
            if error.shape[0] != n or error.shape[1:] != variance.shape:
                raise ValueError(f"Token shape mismatch: {handoff}")
            per_token = (error / variance).mean(axis=(1, 2))
            rows.append({
                "study": study,
                "condition": label,
                "handoff": handoff,
                "tokens": n,
                "mean_key_error": float(per_token.mean()),
                "above_registered_tolerance": int((per_token > TAU).sum()),
                "fstar": {str(tau): fstar(per_token, tau) for tau in TAUS},
                "score_sha256": record["score_sha256"],
                "tokens_sha256": record["tokens_sha256"],
            })

    summary = {}
    for study, label in STUDIES.items():
        group = [row for row in rows if row["study"] == study]
        summary[study] = {
            "condition": label,
            "observations": len(group),
            "tokens": sum(row["tokens"] for row in group),
            "tokens_above_tau": sum(row["above_registered_tolerance"] for row in group),
            "tokenwise_rate": sum(row["above_registered_tolerance"] for row in group)
            / sum(row["tokens"] for row in group),
            "median_fstar": {
                str(tau): statistics.median(row["fstar"][str(tau)] for row in group)
                for tau in TAUS
            },
            "all_registered_fstar_zero": all(row["fstar"][str(TAU)] == 0 for row in group),
        }
    result = {
        "source_revisions": {
            study: json.loads((ROOT / "records" / study / "source.json").read_text())["revision"]
            for study in STUDIES
        },
        "registered_tau_k": TAU,
        "observations": rows,
        "summary": summary,
        "distinct_handoffs": len({row["handoff"] for row in rows}),
    }
    out = ROOT / "archive-audit.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result["summary"], indent=2))
    print(f"{len(rows)} observations; {result['distinct_handoffs']} distinct handoffs; wrote {out.name}")


if __name__ == "__main__":
    main()
