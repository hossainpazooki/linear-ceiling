# Original cache-behavior preparation inputs

2026-10-10 · Response to [issue #20](https://github.com/hossainpazooki/linear-ceiling/issues/20).

These are the two original files requested for the operator's comparison with the
October 1 pilot. Both are copied byte-for-byte from the retained evidence bundle:

| File | Original location, relative to `~/Desktop/Carryover-evidence/` | Bytes | SHA-256 |
|---|---|---:|---|
| `SHA256SUMS` | `SHA256SUMS` | 97,134 | `eb3500f1224d48c82103b73abf452eff00201b8b69778d37f7e6b1b1a5629129` |
| `inputs/manifest.json` | `cache-behavior/inputs/manifest.json` | 35,013 | `9a6f2923d3beda90cebde009ba80a12c5363c43a440fc19a356d6b3f11d4e2dc` |

The manifest matches `input_manifest_sha256` in the committed
[freeze record](../../2026-10-01-cache-behavior-freeze.json). Its
`evidence_sha256_manifest` matches the exact `SHA256SUMS` bytes provided here.
The latter indexes 799 files across the original evidence bundle, including the
A100 study and manuscript artifacts; it was not an E9-long-only listing.
Reordering or narrowing that listing changes its digest. The local `.gitattributes`
preserves both files' bytes on checkouts with automatic line-ending conversion.

Preparation ran locally on **macOS, arm64**, using the fork's Python environment;
the H100 was used for inference afterward. The retained execution transcript records
the local `--prepare` invocation at **2026-10-01 22:55:23 UTC**, with the bundle's
root `SHA256SUMS`, `archive/records/e9l`, and `cache-behavior/traces`. Its output
was `Prepared 35 handoffs; run --check before GPU use.` The prepare log does not
record the macOS release, so no historical release number is asserted here.

On October 10, the retained 35 prepared input files and all 105 alignment/score/token
witnesses matched the manifest. The archive witnesses also matched the original
`SHA256SUMS`. Re-running `--prepare` from `e73e7b8c8a1f9bfbb4411fef4bdc1d4717c452f4`
on macOS arm64 reproduced the manifest and all 35 prepared files byte-for-byte,
using Python 3.12.14, PyTorch 2.14.0, Transformers 5.17.0 and NumPy 2.5.3.
No GPU inference was run; no ledger entry changed.

From the repository root, verify the two supplied files against each other and the
freeze record with Python 3.12:

```bash
python - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('docs/provenance/2026-10-01-cache-behavior-inputs')
manifest_bytes = (root / 'inputs/manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
freeze = json.loads(Path('docs/2026-10-01-cache-behavior-freeze.json').read_bytes())
assert hashlib.sha256(manifest_bytes).hexdigest() == freeze['input_manifest_sha256']
assert hashlib.sha256((root / 'SHA256SUMS').read_bytes()).hexdigest() == manifest['evidence_sha256_manifest']
print('Both original files match the frozen pins.')
PY
```

For a new `--prepare`, restore `SHA256SUMS` at an evidence root and the verified
archive under `<evidence-root>/archive/records/e9l`; its paths are relative to the
checksum file's parent. Use a new output directory and the pinned environment in
the [runbook](../../2026-10-01-cache-behavior-runbook.md). The October 10 check used:

```bash
PYTHONPATH=src .venv/bin/python -m tools.cache_behavior.run --prepare \
  --inputs /tmp/carryover-issue20.IR0Mug/inputs \
  --archive ~/Desktop/Carryover-evidence/archive/records/e9l \
  --traces ~/Desktop/Carryover-evidence/cache-behavior/traces \
  --evidence-sha256 ~/Desktop/Carryover-evidence/SHA256SUMS
```

The rest of the indexed bundle is not shipped here. Running a whole-bundle
`sha256sum --check` in this provenance directory would therefore be inappropriate.

The operator's `2aeee576…` manifest is not available in this checkout. These checks
do not establish which fields differ from it; that comparison can now use the
original pilot manifest. The operator's October 7 ruling and ledger entry 0049
remain unchanged.
