# Editing a gate string changes the config sha, so every alignment pass under it is stale and the coverage pin refuses the draft

ts: 2026-10-04T09:45:00Z
commit: a2742b9
session: d4f6aa2f (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\d4f6aa2f-529e-4861-9322-e476f4693f66.jsonl)
status: verified
fact: Renumbering the E-TRUNC registration from 0052 to 0055 changed one line in each of `config/e9t-*.toml` (`[e9.gate] required_entries`). The four `e9 --align-only` passes on disk had been written under the old shas, so `append_0055.py --preview` refused with "FULL: coverage.json under another config" until the passes were re-run (~5 min CPU). The alignment itself does not read the gate, so the arrays were byte-identical — the pin is about provenance, not content, and it is right to refuse: a coverage file is a claim about one config's bytes.
basis: the refusal at ~09:0xZ (`AssertionError: FULL: coverage.json under another config`), then `summarize_e9_trunc --shrinkage` after the re-run printing the same distribution (median 0.4470, pooled 0.4090, 14 void).
re-verify: .venv/Scripts/python.exe -c "import json; from linear_ceiling.hashing import sha256_text_file; c=json.load(open('results/e9t-full/align/coverage.json')); print(c['config_sha256']==sha256_text_file('config/e9t-full.toml'))"   # True only while the committed config and the pass agree
