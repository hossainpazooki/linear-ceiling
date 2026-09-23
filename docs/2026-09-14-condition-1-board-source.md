# Condition 1: operator-supplied board excerpts

Received 2026-09-14 in the operator's conversation. These are verbatim excerpts from the supplied JSX, not evidence from the ledger and not a ruling. Line references to this file identify the retained excerpts; they are not claimed to be line numbers in the original full artifacts. No board was edited or posted.

Source location: Claude project **Papers**, project-context artifact `lcfm-submission-day-board.jsx`. The operator supplied its source after first supplying the separate `lcfm-extended-sprint-board-v3.jsx`. No public artifact URL was supplied.

## Submission-day board: explicit gate claim

The section **Tomorrow, by area**, following the area rows, contains:

```jsx
            <div className="text-base" style={{ fontWeight: 600 }}>The refutation is owed, not blocking</div>
            <div className="leading-7 text-sm mt-1">
              0032 admitted E9 to the paper on the condition that the co-author refutation of 0025–0029 be recorded
              first. That condition is dropped as a gate: §4.1 prints either way, and §6 carries the sentence saying
              the refutation was owed at the time of writing. Dropping the gate does not drop the work — an
              unrefuted cell in a paper that advertises adversarial reading is a debt, and it comes due before the
              MLSys draft, not after.
            </div>
```

## Submission-day board: proposed review assignment and timing

Selected fields from `AREAS`, object `id: "eval"`:

```jsx
    pair: "Samuel · Ritvik",
    name: "Re-verify 0025–0029 and record the refutation",
    done: "A written finding with both names on it, handed to Farhan for the outside read.",
    lands: "a numbered entry after the deadline; §6's owed-at-time-of-writing sentence stays or comes out",
```

The footer says:

```text
pairs are proposed, not settled · the ledger is the authority where this page and the repo disagree
```

## Extended board: different proposed assignment

Selected fields from `PAIRS`, object `id: "se"`, in the separately supplied `lcfm-extended-sprint-board-v3.jsx`:

```jsx
    pair: "Samuel · Emerson",
    closes: "A dated record under docs/reviews with both names; §6's owed-at-time-of-writing sentence resolved either way.",
```

Its `RULES` array includes:

```text
Nothing run after 0036 enters the paper. The verification pair's findings go to docs/reviews, then to an entry after the upload.
```

Both assignments are historical proposals. The operator's current signature instruction, recorded separately in the status note, takes precedence; no signature or attestation is inferred from either board.
