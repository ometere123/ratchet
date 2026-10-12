# Threat model and residual limitations

| Attack / failure | Mitigation | Residual issue |
|---|---|---|
| Owner silently weakens policy | cannot edit/remove sealed genesis/track; requires independently accepted STRICTER vs head and genesis | leader/validators can still misinterpret language |
| Owner resets policy | new policy has a **different** genesis hash; consumers pin Ratchet address, policy/track and root | consumers must not accept arbitrary new policy IDs |
| Gradual weakening across revisions | checks against current AND immutable genesis; multi-track gates count distinct qualified tracks rather than total revisions | correlated mistaken inclusions can still accumulate |
| Emergency carve-out disguised as hardening | explicitly called out in prompts and adversarial counterexample search | model failure possible |
| Scope/actor substitution | frozen domain comparison and same_scope gate | subtle scope changes may be missed |
| Malicious leader shapes JSON correctly but lies | independent validator analysis of same inputs and second-stage counterexample attempt; bounded consensus facts are separated from leader-reported witness prose | independent models may be correlated and witness prose is explanatory, not independently identical |
| Prompt injection in policy text | delimited untrusted data; instructions to ignore embedded directions | no natural language prompt is absolute protection |
| Validator outage | invalid, missing and malformed results fail closed | temporary inability to adopt a valid tightening |
| Unauthorized caller | immutable creator address guards all writes except views | compromised owner may spam rejected attempts |
| Stale transaction after concurrent upgrade | caller must supply exact current track hash | normal transaction ordering still required |
| Storage spam | creator-only changes, bounded 8 tracks and 64 attempts each | owner can consume their own cap |
| Runtime evolution | stable 61999 stack and pinned dependency header | must retest against hosted GenVM after updates |
| Consumer replay or mismatch | immutable genesis hash and exact contract/track pinning | consumer must enforce own action semantics |
| Irreversible acceptance wrongfully approved | no downgrade by design | remediation means creating a separate policy and opt-in migrating consumers |

## Deliberate scope omissions

- No formal theorem prover for unrestricted language.
- No retroactive repairs, emergency override, superadmin, or admin pause.
- No economic slashing or GEN escrow. Avoids accidental fund-loss mechanisms.
- No private data in prompts; every text passed to consensus is public contract data.
- No external fact/source authentication: comparison is between user-supplied frozen policy texts only.
- No automatic application of the policy to arbitrary transactions: a consumer must integrate the policy or gate.
- No frontend, wallet, hosted backend or remote signer.

The irreversible design is an intentional contract feature: a mistaken sealed policy cannot be loosened. Recommend small, precise tracks and externally reviewed genesis language rather than blindly sealing complex legal contracts.
