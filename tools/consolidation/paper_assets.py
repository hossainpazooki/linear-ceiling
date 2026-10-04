# Export the verified model comparison as a small LaTeX table; never reads GPU files directly.
from pathlib import Path
import csv
import argparse
import json
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--evidence",type=Path,default=Path.home()/"Desktop/Carryover-evidence")
parser.add_argument("--summary",type=Path)
parser.add_argument("--output",type=Path)
args = parser.parse_args()
EVIDENCE = args.evidence
output = args.output or EVIDENCE/"manuscript"
output.mkdir(parents=True,exist_ok=True)
summary = json.loads((args.summary or EVIDENCE/"a100/summary.json").read_text())
assert summary["verified"]
with (EVIDENCE/"archive/audit/handoff_metrics.csv").open() as f:
    archived = list(csv.DictReader(f))
cells = {}
for cohort in ["e9s","e9l"]:
    rows = [r for r in archived if (r["cohort"],r["kind"],r["arm"],r["subset"])==(cohort,"K","same","all")]
    cells["Qwen3-1.7B",cohort] = {"n":len(rows),**{m:float(np.median([float(r[m]) for r in rows])) for m in ["fstar","fstar_0.1","fstar_0.03"]}}
for key,label in [("qwen4","Qwen3-4B"),("smollm3","SmolLM3-3B")]:
    for cohort in ["e9s","e9l"]:
        c = summary["models"][key][cohort+"_K"]
        cells[label,cohort] = {"n":c["handoffs"],**c["median"]}
lines = [r"\begin{table}[htb]",r"\centering\small",
    r"\caption{Same-model keys on the same handoff texts. Each entry gives short/long cohort medians; $n$ gives handoff counts. The Qwen3-1.7B row reuses the archived YaRN runs. New models are evaluated on one A100 80GB with fixed YaRN settings per model. The common $\tau_K$ is the original Qwen mapper reference, not a model-specific quality threshold.}",
    r"\label{tab:additional-models}",r"\begin{tabular}{@{}lcccc@{}}",r"\toprule",
    r"Model & $n$ & $f^*(\tau_K)$ & $f^*(0.1)$ & $f^*(0.03)$ \\",r"\midrule"]
for model in ["Qwen3-1.7B","Qwen3-4B","SmolLM3-3B"]:
    a,b = cells[model,"e9s"],cells[model,"e9l"]
    line = f"{model} & {a['n']}/{b['n']}"
    for m in ["fstar","fstar_0.1","fstar_0.03"]:
        line += f" & {a[m]:.4f}/{b[m]:.4f}"
    lines.append(line+r" \\")
lines.extend([r"\bottomrule",r"\end{tabular}",r"\end{table}"])
(output/"additional-models.tex").write_text("\n".join(lines)+"\n")
print("Generated table from verified summary:")
print("\n".join(lines[8:-3]))

lines = [r"\begin{table}[H]",r"\centering\small",
    r"\caption{Additional-model sensitivity. Entries are handoff medians; brackets give 95\% trajectory-cluster bootstrap intervals (2,000 resamples). Each short/long cohort contains 25/35 handoffs. Values use the original $\tau_V=\tauV$ reference.}",
    r"\label{tab:model-sensitivity}",r"\begin{tabular}{@{}llccc@{}}",r"\toprule",
    r"Model & Cohort & $f_K^*(0.03)$ [95\% CI] & $f_V^*(\tau_V)$ & $f_V^*(0.03)$ [95\% CI] \\",r"\midrule"]
def interval(group,metric):
    lo,hi = group["cluster_bootstrap_95"][metric]
    return f"{group['median'][metric]:.4f} [{lo:.4f}, {hi:.4f}]"
for model,label in [("qwen4","Qwen3-4B"),("smollm3","SmolLM3-3B")]:
    for cohort,name in [("e9s","Short"),("e9l","Long")]:
        k,v = [summary["models"][model][cohort+"_"+kind] for kind in ["K","V"]]
        lines.append(f"{label} & {name} & {interval(k,'fstar_0.03')} & {v['median']['fstar']:.4f} & {interval(v,'fstar_0.03')}"+r" \\")
lines.extend([r"\bottomrule",r"\end{tabular}",r"\end{table}"])
(output/"model-sensitivity.tex").write_text("\n".join(lines)+"\n")
