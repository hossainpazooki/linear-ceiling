# The scope-paraphrase guard reads a period-free markdown table as ONE sentence

kills: (nothing)
ts: 2026-09-01T22:11:01Z
commit: 151bb719e05231fdd12fc8766b1668c427655d5c
session: linear-ceiling-venue (edf43652-2973-456b-85d0-6d6dd532713a)
status: verified
fact: `lint_scope` splits text on sentence-final punctuation before scoring each chunk's
stem overlap against the scope sentence (threshold 0.45). A markdown table whose cells end
without periods is therefore ONE chunk, and its accumulated vocabulary can cross the
threshold even though no single cell paraphrases anything — the README's findings table fired
at 0.54 this way while drafting. Two mitigations, both used in the committed README: end each
table cell's prose with a period so chunks stay cell-sized, and keep the vocabulary that
`lint_scope._SCOPE_STEMS` names out of table cells (deliberately not listed here: the first
draft of THIS entry listed the stems and fired the guard at 0.62, twice — once for the list,
once for a hardcoded demo string; both replaced by references). The firing is a feature — the
guard exists so near-copies cannot drift — but a future doc editor who has never seen it fire
on a TABLE will not guess the chunking rule from the error message.
basis: reproduced read-only against the pre-fix wording as data, 2026-09-01T22:11:01Z:
  `chunks after sentence split: 1` / `fires: True | demo: sentence closely paraphrases the
  scope sentence (word overlap 0.54 >= 0.45)...` / `current README fires: False`
  (via `linear_ceiling.lint_scope.check_paraphrase` on the old findings-table text; the
  original firing occurred mid-session against an uncommitted README draft and never landed).
re-verify: .venv/Scripts/python.exe -c "from linear_ceiling.lint_scope import SCOPE_SENTENCE, check_paraphrase; demo = '| ' + SCOPE_SENTENCE.replace('.', '') + ' | extra cell |'; print('period-free table chunk fires:', bool(check_paraphrase(demo, 'demo')))"
