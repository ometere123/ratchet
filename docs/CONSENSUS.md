# Consensus and equivalence strategy

The contract has **one custom `gl.vm.run_nondet_unsafe` boundary** per candidate. The *leader* reads three immutable policy texts and a frozen domain: genesis G, head H, candidate C, domain D. Its normalized output is:

```json
{
  "current": 1,
  "genesis": 1,
  "same_scope": true,
  "reason": "APPROVAL_BOUND_TIGHTENED",
  "weakening_witness": "",
  "tightening_witness": "one additional independent approval required"
}
```

Exact relation enum: `1 STRICTER`, `2 EQUIVALENT`, `3 WEAKER`, `4 INCOMPARABLE`, `5 AMBIGUOUS`.

The validator separately calls an **independent** reasoning prompt containing the same immutable texts. It demands equality on `current`, `genesis`, and `same_scope`, not formatting or textual witness equality. If the leader requests an affirmative `STRICTER/STRICTER` verdict, the validator makes an **additional independent falsification call** searching for carve-outs, reduced duties, changed actor/scope, missing protected cases and newly permitted conduct. Any positive or ambiguous finding vetoes.

There is no fallthrough that treats unavailable or malformed LLM data as acceptance. Invalid JSON maps to `AMBIGUOUS`. Invalid return structure and exceptions reject the custom validator. `gl.vm.Return` is required. Model-provided reason and witness are bounded to prevent resource abuse; accepted positive results require a nonempty concrete strengthening witness and no admitted weakening witness.

**Trust limit:** independent validators may share correlated model errors. A semantic consensus majority is not a mathematical proof of logical subset containment. Do not describe a `STRICTER` classification as formally verified or universally enforceable. For mission-critical clauses, supplement with a bounded formal DSL, more restrictive input language, manual approval, or dedicated external auditors.

## Test matrix

- legitimate `2 approvals → 3 approvals` accepted;
- new carve-out considered weaker;
- domestic-only narrowing considered scope change;
- equivalence rejected without changing head;
- incomparable tradeoff rejected;
- ambiguity rejected;
- candidate stricter than head but weaker than genesis blocked;
- malicious leader `STRICTER` vs validator `WEAKER` fails;
- leader affirmative vs validator adverse counterexample fails;
- malformed independent result fails;
- malformed second-stage audit result fails;
- stale head hash blocks replay;
- immutable seal, owner, track limits and attempts.

Offline tests directly exercise the deterministic state logic through a deliberately labelled Python mock. Direct Mode tests use the actual SDK/VM adapter and explicitly run the captured validator callback. A live **multi-validator StudioNet** transaction must still be separately proved.
