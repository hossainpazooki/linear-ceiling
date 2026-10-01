# Exploratory seam-proximity pilot

This preserves the four-case prompt-intervention driver used before the A100
model extension. It changes which parts of a token block's preceding context
are retained, then compares cached representations. It does not inject a cache
into generation and is not E-BEH or a task-quality result.

`source.json` pins the original driver and 154,817-byte input artifact at the
completed fork revision. The artifact contains tokenized public trajectory
text, so it stays outside upstream git history. The archived fork commit remains
the immutable download source; a hash mismatch stops restoration.

From the repository root, using the existing PyTorch 2.14 / Transformers 5.17
experiment environment:

```bash
python tools/seam_pilot/fetch_inputs.py
python tools/seam_pilot/run.py --check
# Only when a new exploratory replay is intended:
python tools/seam_pilot/run.py --device cuda --output results/seam-pilot/new-cuda
```

No replay is needed to migrate the code. Existing outputs remain in the
Carryover evidence bundle. The original inputs, comparison calculations,
thresholds and exploratory quantile convention are unchanged. Migration fixes
the missing default input filename and the old workspace-specific import path,
and adds a model-free input check. The historical result's recorded script hash
continues to refer to the original script, not this packaging revision.
