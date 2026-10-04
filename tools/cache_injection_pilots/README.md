# Historical cache-injection pilots

Migrated from [neuriv/cache-injection](https://github.com/neuriv/cache-injection/tree/8e8417a6a6186d4a4164c3477836e25892fdf046),
commit `8e8417a6a6186d4a4164c3477836e25892fdf046`. All 26 tracked files are retained
under this directory. [migration-manifest.json](migration-manifest.json) maps every
original path and SHA-256 to its migrated path and SHA-256, including scoped corrections.

The [overview](docs/index.html), [results](docs/results.html),
[replication steps](docs/replicate.html), [protocols](docs/protocols.html), and
[archive review](docs/refutations.html) document the earlier exploratory work.
`results/historical-summary.json` is preserved byte-for-byte and is NOT evidence ([label](results/README.md)). Its aggregates are
historical reports: the original per-example outputs, prompt caches, and downloaded
models were deleted. They cannot be independently regenerated from that summary.
Fresh runs can use the pinned public inputs but cannot restore the deleted outputs.
This migration adds no GPU measurements and does not close a registered experiment.

Run the model downloader to completion before the pilots; missing local models
fail in the loader instead of waiting indefinitely for a log message. Archive-alias
setup refuses to replace existing files or directories; the downloader restores the
pinned archive files and overwrites its previous downloads.

Run the documented commands from this directory, with a separate environment:

```bash
cd tools/cache_injection_pilots
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The Transformers 4.57.6 pin is historical, not a requirement for the new E-BEH
driver or the main project. No rationale for that original version choice was
recorded. Keep its dependencies separate; compatibility with the main project's
5.x archive environment requires an explicit comparison, not an assumed identity.

`practical.py` retains the native-position Qwen pilot: three short handoffs, an
extraction-question wrapper, and newly aligned blocks of at least 32 tokens. It is
not the long-cohort E-BEH protocol, which must use the archived alignments and
explicit YaRN configuration. Its copied keys use a pure relative rotation under
one fixed rotary schedule; changing schedules or amplitudes requires a different
transform. The migrated timing helper synchronizes the selected CUDA or MPS device.

Offline helper checks, from the main repository root:

```bash
python -m pytest -q tests/test_cache_injection_pilots.py
```
