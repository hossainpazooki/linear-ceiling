# The submission manuscript's source and any LaTeX toolchain are absent from this machine: claims can be checked against the ledger here, but the .bib entries cannot be checked and nothing compiles

kills: (nothing)
ts: 2026-09-14T09:27:59.436Z
commit: a5053b2f1d453235c87ce07e9f30f95524a2a590
session: model-context-window-comparison (transcript C:\Users\hossa\.claude\projects\C--Users-hossa-dev\2f2c397b-6f7c-4aee-84c4-1509767d1a1b.jsonl)
status: verified
fact: The operator's manuscript names `neurips/main.tex` and `neurips/references.bib`. A search of the home directory
to depth 7, excluding AppData and node_modules, finds no `neurips/references.bib`, and none of `pdflatex`, `latexmk`
or `tectonic` is on PATH. The only TeX in this repo is the untracked scaffold `docs/paper/tex/`, which that manuscript
has superseded. A session here checks the manuscript by pasted text against the ledger and summaries. It cannot check
the bibliography entries, the workshop style option, or whether the document compiles.
basis: `find ~ -maxdepth 7 -path "*neurips/references.bib" -not -path "*/AppData/*" -not -path "*/node_modules/*" | head -1`
  printed nothing; `command -v pdflatex latexmk tectonic` printed nothing, `toolchain rc=1`.
re-verify: find ~ -maxdepth 7 -path "*neurips/references.bib" -not -path "*/AppData/*" -not -path "*/node_modules/*" 2>/dev/null | head -1; command -v pdflatex latexmk tectonic   # both print nothing
