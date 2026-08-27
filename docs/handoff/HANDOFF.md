# Handoff index

Pointers only — no evidence lives here. Entries are immutable: a later session writes a new
dated brief, never edits an old one. Run `/rigor:pickup` against the newest entry; it
re-verifies the brief's claims rather than trusting them.

| date | brief | describes commit | one-line |
|---|---|---|---|
| 2026-08-26 | [w1-scaffold](2026-08-26-w1-scaffold.md) | `2361c72` (ledger + E0 rule only; everything else is uncommitted) | **W1 complete.** E0 ran on all six pairs — ladder verdict **SAME**, so G1 degrades to Variant 3 — with the rule verifiably committed before any weight was read; entry 0004 records it and H-S2's first clause is `NOT CONFIRMED`. Suite 108, all four gates green. Two caveats carried forward: nothing but `2361c72` is in history, and 0004 records the medians but not the per-layer structure (§2.3), which lives only in untracked `results/`. |
