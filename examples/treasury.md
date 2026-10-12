# Demonstration: immutable finance controls

Create and seal with one track:

- Name: `TREASURY_APPROVALS`
- Frozen domain: `All treasury operators, all treasury withdrawals, all recipients, regardless of amount or urgency.`
- Genesis: `Every treasury withdrawal requires approval from two independent authorised signers before execution.`

Candidate A: `Every treasury withdrawal requires approval from three independent authorised signers before execution.` Expected semantic result: STRICTER / STRICTER / same_scope=true.

Candidate B: `Every treasury withdrawal requires approval from three independent authorised signers, except emergency disbursements.` Expected: WEAKER or INCOMPARABLE due to an expanded exception, thus REJECTED.

Candidate C: `Every domestic treasury withdrawal requires approval from four independent authorised signers.` Expected: scope narrowed/changed, REJECTED.

Candidate D: `Withdrawals need suitable approval.` Expected: AMBIGUOUS/INCOMPARABLE, REJECTED.

These are *expected* results to test; the live run must be observed rather than reported as predetermined consensus outcomes.
