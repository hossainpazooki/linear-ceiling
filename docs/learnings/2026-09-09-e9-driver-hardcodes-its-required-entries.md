# The E9 driver hard-codes its required ledger entries, so a second E9 configuration cannot pass its own gate

kills: (nothing)
ts: 2026-09-09T03:57:39.466Z
commit: 4eafe40290a1b6525fe747532a768e15a0ca73c3
session: linear-ceiling-lcfm (018R4BNzaMfGpTZaCSocf8Sc)
status: verified
fact: `e9 --config <toml>` reads `results_dir`, `scratch_dir`, `context_cap`, `[e9.keep]` and `[e9.rule]`
from the config, which looks like enough to run a second E9 experiment (the long half, `config/e9l.toml`)
from a new file. It is not: `e9.assert_ready` checks a module-level `REQUIRED_ENTRIES` tuple naming
0019/0023/0025/0026/0027 and its refusal text names `config/e9.toml` by string, so a second configuration
would be gated on the FIRST experiment's entries and never on its own registration entry. The E8 family
already solved this shape (e8a/e8c carry their own required entries); E9 did not, because until now there
was one E9. Building E9-long starts with making the required-entry list per config and the refusal text
read `cfg.config_path`, with a test that a config naming a missing entry refuses by that entry's number.
basis: `grep -n "^REQUIRED_ENTRIES = " src/linear_ceiling/e9.py` at 4eafe40 ->
  `49:REQUIRED_ENTRIES = ("### 0019 ", "### 0023 ", "### 0025 ", "### 0026 ", "### 0027 ")`; the refusal at
  lines 66–67 reads `"... entries 0019/0023/0025/0026/0027 and config/e9.toml must be committed before any prefill"`.
re-verify: grep -n "^REQUIRED_ENTRIES = (" src/linear_ceiling/e9.py   # one module-level tuple until it is made per-config
