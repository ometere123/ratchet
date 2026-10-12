# Architecture — irreversible semantic policy ratchets

## Invariant model

For a frozen subject/activity/resource domain `D`, let `Allow(P, D)` denote the behaviours permitted by policy `P`. A valid strictly-tightening transition from P to Q requires `Allow(Q,D)` to be a **proper subset** of `Allow(P,D)`. Equivalently every old prohibition/condition/duty still applies and at least one previously allowed behaviour is newly excluded. Changes that introduce new exceptions, broaden permissions, remove protections, reduce thresholds, or redefine the domain are not admissible.

The protocol does not pretend to establish this property formally for unrestricted natural language. Consensus returns a bounded conservative determination. `AMBIGUOUS`, `INCOMPARABLE`, and `EQUIVALENT` cannot advance a version. The validator must separately compare with the sealed genesis anchor to resist slow semantic erosion.

## State machine

```text
Policy DRAFT -- owner registers frozen tracks --> DRAFT
DRAFT -- seal, at least one track --> SEALED (irreversible)
SEALED -- propose candidate, compare --> ACCEPTED AMENDMENT -- new head/version
                             └-------> REJECTED AMENDMENT -- unchanged head/version
```

A Policy never returns to draft, can never add/remove tracks after sealing, and has no admin override. Tracks are immutable in name, actor domain, and initial rule. Amendments are append-only receipts. Accepted heads hash `parent_hash`, exact `track_id`, `version`, candidate `text_hash`, and unchangeable track `genesis_hash`. Policy canonical head hashes the entire ordered track set, roots, versions, and current hashes.

## Responsibility split

| Consensus handles | Deterministic code handles |
|---|---|
| Subset relation vs current | ownership |
| Subset relation vs genesis | irreversible sealing |
| Domain-preservation judgement | immutable roots, bounds |
| Bounded relation, scope and adversarial-audit facts | witness length, shape and explicit leader-reported provenance |
| Independent re-analysis | strictly-positive admission predicate |
| Adversarial counterexample search | version/attempt counters, hash lineage |

## Existing primitive differentiation

Concord maintains a rule conflict/precedence graph; it does not forbid the owner from weakening the next approved policy version. SemanticWatcher and drift oracles identify change, not strict partial-order admissibility. PolicyGate validates an action under a current policy, not the allowed-set inclusion relationship between successive policy revisions. RATCHET is intentionally narrower but stronger in its monotone-invariant focus.

## Consumer categories

Use `is_track_at_least` when a consumer requires a minimum *admitted* version under a pinned immutable genesis. Use `matches_policy_head` when any new revision requires the consumer to reapprove/review the policy. Neither API proves that all real-world actions comply with the policy: a consumer must enforce that separately.
