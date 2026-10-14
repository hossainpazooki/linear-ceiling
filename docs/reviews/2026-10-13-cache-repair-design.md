# Cache-repair design response

Date: 2026-10-13. Response to [issue #26](https://github.com/hossainpazooki/linear-ceiling/issues/26).
Reviewed source: `18ba359aa44de3017ca786cff602d0ccbfd08e5d`, the proposed 0061 amendment in
`exp/cache-behavior-repair`. These are recommendations for the pending draft; no entry is appended here.

1. Keep the uniform random subset at the same matched-token count. It answers whether ranking improves
   prediction agreement over spending that budget anywhere. Matching seam bins would instead ask whether
   ranking helps after controlling for seam location, which can remove part of the effect under study.
   The same seeded permutation across budgets gives nested random subsets. A single draw per handoff
   does not estimate selection variance, and equal token counts do not imply equal execution cost.

2. Keep stable descending order of the archived token-mean delta_K, averaged over heads and layers.
   This is the existing driver's ranking. `construct` performs repairs in receiver order against the
   assembled cache; the ranking stays fixed after earlier repairs. It tests this offline selection
   rule, with no guarantee that the selected subset minimizes KL or maximizes top-1 agreement.

3. Keep 5%, 10%, and 20%. The 10% and 20% points connect to 0045's removal diagnostics; 5% adds a smaller
   budget. Each selects `ceil(len(pairs) * fraction)` matched tokens. The reported `recomputed` count also
   includes unmatched receiver tokens, so compare its increase over REUSE-ALL when checking the budget
   on real handoffs. No quality band or speedup claim follows from these percentages.

4. Do not require bitwise equality between separate GPU runs. Keep exact input hashes and explicit
   runtime records, and register the numerical comparison rule before the run. The summarizer's
   `atol=rtol=1e-10` checks KL recomputed from a saved logits witness; it does not establish a tolerance
   for running the model again. Specify the fields, tolerances, and refusal behavior for comparison with
   0049, including top-1 agreement, before appending 0061. No new tolerance is chosen in this response.

The accompanying changes make the selection test inspect the rows actually passed to `construct` at
all three budgets. Previously, replacing the random draw with the oracle's rows still passed: the test
computed the expected random rows but never compared them with the driver's selection. That mutation
now fails at the selection assertion, while the unchanged driver passes.

The draft now derives the candidate-arm count from the two fraction lists: nine passes, plus FRESH and
the first-handoff controls. The old eight-pass estimate was incorrect; multiplying total runtime by
the arm ratio also overlooks the different prefill calls repair creates. Use the largest-case probe
for the estimate. The draft also drops the claimed optimality bound for the offline ranking and states
that tau_K names the archived tail; delta_K itself determines the ranking.

## Reproduction

Local checks used Python 3.12.14, PyTorch 2.14.0, Transformers 5.17.0 and NumPy 2.5.3 on macOS arm64.
The checkout had no virtualenv, so these synthetic checks used an existing environment with those
packages and this checkout's `src` on `PYTHONPATH`. The repo setup instructions create `.venv` for the
commands below; install Transformers explicitly so this test module is not skipped.

```sh
.venv/bin/python -m pip install transformers==5.17.0
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_cache_behavior.py
PYTHONPATH=src .venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m linear_ceiling.seal verify
PYTHONPATH=src .venv/bin/python -m linear_ceiling.lint_scope
PYTHONPATH=src .venv/bin/python -m linear_ceiling.ledger_check --against 18ba359aa44de3017ca786cff602d0ccbfd08e5d
```

The full suite passed 649 tests with one skipped. Seal, scope and ledger checks passed. To reproduce the
test defect in a disposable checkout, replace the random-selection expression in `run.py` with
`np.arange(budget)` and run `test_random_control_arm_matches_the_oracle_budget_and_differs_in_selection`.
At the reviewed revision it passes; with this change it fails. Restore the driver before running the
suite normally. The driver's source hashes and both experiment configs are unchanged in this commit.

No GPU experiment or 0061 append script was run. Its full preview and the comparison against 0049 still
need the operator's verified mirror; these checks establish neither baseline agreement nor repair quality.
