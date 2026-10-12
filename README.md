# RATCHET

**A consensus-checked monotonicity protocol for natural-language policies. A policy owner can tighten a sealed rule, but even the owner cannot directly loosen it through this contract.**

**Standalone Intelligent Contract primitive · no frontend · no backend · stable StudioNet 61999 only · local CLI `genlayer@0.39.1`**

### Problem

A policy can be weakened without removing its headline restriction. Compare:

- **Genesis:** All treasury withdrawals require two independent approvals.
- **Tightening:** All treasury withdrawals require three independent approvals.
- **Hidden loosening:** All treasury withdrawals require three independent approvals, except emergency disbursements.

A string hash detects change but cannot establish whether the allowed behaviours became a subset or a superset. An administrator with an upgrade key can silently widen permission even if the organisation promised that its safety/privacy policy could only get stricter.

**RATCHET makes the monotonicity constraint a protocol invariant.** Its single custom GenLayer consensus boundary compares a candidate with **both the current rule and its sealed genesis anchor**, including attempts to expand scope or insert carve-outs. Only an independently verified, **strict** strengthening advances the immutable history. Equivalent, weaker, incomparable, changed-scope and ambiguous proposals are recorded as rejected attempts. An owner cannot repeal a sealed track, replace its genesis, or remove one to reset the baseline.

This is an executable *semantic guardrail*, not a formal proof of all conceivable meanings. An LLM can still err; independent rederivation, counterexample checks, and conservative ambiguity handling reduce—not eliminate—that risk. High-stakes policies should additionally use human or formal verification.

## One-minute protocol example

```text
create_policy("Treasury Constitution", "Operations and payments")
  └─ register_track("approvals", fixed_scope, "Two independent approvals for every withdrawal")
      └─ seal_policy()     genesis hash forever frozen
           ├─ propose "Three independent approvals for every withdrawal"
           │    ├─ comparison vs current: STRICTER
           │    ├─ comparison vs genesis: STRICTER
           │    ├─ adversarial counterexample audit: no weakening found
           │    └─ deterministic ACTIVE head advances v1 → v2
           ├─ propose "Four approvals except emergency withdrawals"
           │    └─ REJECTED; v2 unchanged (exception weakens v1)
           └─ propose "Three approvals for domestic withdrawals"
                └─ REJECTED; domain was narrowed
```

`Policy` has up to eight **independent, immutable-scope tracks** and may be sealed only once. `Track` stores its immutable genesis plus current head/version. `Amendment` stores every audited attempt (accepted or rejected) with source hashes, verdict categories, witnesses, and resulting state. An accepted revision is hash-linked to its predecessor. **There is no downgrade, repeal, genesis replacement, or change-owner method.** The owner is a fixed `gl.message.sender_address` recorded at creation.

## Why GenLayer consensus is required

For natural language, subset containment of the set of allowed behaviours is not generally decidable by a deterministic Solidity/Python parser. GenLayer is used *only* for the bounded judgement **"is the candidate strictly more restrictive under the same actor/resource/activity/scope?"**. Deterministic code controls ownership, sealing, numerical caps, acceptance predicates, hashing, version history, and consumer eligibility.

One `gl.vm.run_nondet_unsafe` custom boundary does three things:

1. **Leader assessment:** strictly bounded enum relation against current AND genesis, a scope flag, reason and concrete strengthening/weakening witness.
2. **Independent validator:** independently assesses the frozen texts; must agree on both relations and scope preservation, not just JSON shape.
3. **Adversarial counterexample audit:** validator actively searches for a formerly forbidden behaviour newly allowed by the candidate. Any weakening, incomparability, ambiguity, malformed answer, unavailable inference or validator disagreement rejects consensus.

Only a candidate with **`STRICTER` vs current AND `STRICTER` vs genesis AND `same_frozen_scope=true`** can advance state. Equivalent restatements are intentionally not accepted to prevent meaningless canon churn. Full prompt and threat analysis: [docs/CONSENSUS.md](docs/CONSENSUS.md), [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Main contract API

**Writes:**

```python
create_policy(name: str, purpose: str) -> u256
register_track(policy_id: u256, name: str, domain: str, genesis_rule: str) -> u256
seal_policy(policy_id: u256) -> str
propose_revision(track_id: u256, new_text: str, expected_head_hash: str) -> u256
```

Only the creator owns the policy and may register/seal/revise. Tracks can only be registered **before** the policy is sealed. `propose_revision` returns an amendment receipt ID; the receipt can be `ACCEPTED` or `REJECTED`. Call `get_amendment()` before interpreting a returned ID as success.

**Views:** `get_policy`, `get_track`, `get_amendment`, `current_track_hash`, `current_policy_hash`, `is_track_at_least`, `is_policy_at_least`, `matches_policy_head`.

**Composability:** A consumer pins the exact Ratchet contract address + track ID + `genesis_hash` + minimum version. The `is_track_at_least(...)` predicate can only turn from false to true **assuming each accepted semantic admission was correct**; history is irreversible. `matches_policy_head` instead implements exact invalidation whenever any sealed track changes. See [docs/INTEGRATION.md](docs/INTEGRATION.md) and the small separate [example consumer](contracts/ratchet_consumer_example.py). The consumer is not needed for the primitive and does not create a frontend.

## Bounded execution

- Up to `8` tracks/policy, immutable after sealing.
- Up to `64` attempts/track, preserving rejected attempts and bounding storage.
- `2,000` characters per rule, `360` per domain, `100` per name.
- Exactly **one** consensus boundary per revision (leader and each validator may run multiple inference calls).
- All denial outcomes leave operative policy/hash/version unchanged.
- No GEN escrow, transfers, external backend, frontend, upgrade key, or admin bypass.

## Verify locally

```bash
python -m pytest tests/test_offline.py -q
python scripts/preflight.py
```

The offline suite uses an explicitly labelled mock runtime; its SHA3-based hash stub is **not** a byte-parity check for GenVM Keccak. These tests verify deterministic transition logic and validator callback behaviour, **not** live consensus. Current recorded execution here: `14 passed`; offline structural preflight: `14/14`.

On the developer workstation (Python >=3.12), run actual GenLayer Direct Mode:

```bash
python -m pip install -r requirements-dev.txt
gltest direct_tests/test_ratchet_direct.py -v -s
```

The Direct Mode suite includes malicious leader, independent disagreement, adversarial weakening, genesis erosion, invalid scope, stale hash, ownership, immutability and consumer view scenarios. The verified local run is `21 passed`, including the Windows loader compatibility shim in `direct_tests/conftest.py`; that shim does not alter contract/runtime behaviour.

## Stable StudioNet deployment — never the preview

The workstation's global `genlayer` is not used. This repository pins `genlayer@0.39.1` as a local development dependency.

```bash
npm install
./node_modules/.bin/genlayer --version  # MUST show 0.39.1
node scripts/assert_studionet.mjs        # MUST confirm RPC chain 61999
npm run deploy:guarded                # guarded, interactive, Windows-compatible
```

The exact deployment RPC is `https://studio.genlayer.com/api` (stable `studionet`, **chain 61999**). **Do not deploy to `studio-dev`, `studio-next`, or chain `61997`**. The guarded Node script refuses an incorrect local CLI version or RPC chain ID. See [DEPLOYMENT.md](DEPLOYMENT.md) and [RATCHET_CODEX_MASTER_HANDOFF.txt](RATCHET_CODEX_MASTER_HANDOFF.txt).

### Proof status

**Current proof status:** deployed on stable StudioNet 61999 with source parity verified. Ratchet is `0xbd1cf148872dD396d06437859B4Bd4c8c0862A86` and its source SHA-256 is `e30e6487d23ab73abe7b5924ede8fe10744069dd49322c50ad53970ea225ebd0`. The correctly bound optional consumer is `0x0176AD19a6968a1D1F4Dd3db5F1833ECe247Ab0f` with source SHA-256 `63a9ea986555c6b4c6598bb553b9d41e3d760700fe30ed373ea36c20bbd83e75`. The successful consumer protected-action transaction finalized and `get_action_count()` read back `1`. These are live chain facts; Direct Mode and offline tests remain separate evidence layers. See [DEPLOYMENT.md](DEPLOYMENT.md) for transaction hashes, readbacks, and the semantic-lint limitation.

## Repository contents

```text
contracts/ratchet.py                  deployable primitive
contracts/ratchet_consumer_example.py optional integration consumer
examples/treasury.md                 ready-made scenario
scripts/preflight.py                offline structure checks
scripts/assert_studionet.mjs       chain ID network gate
scripts/deploy_studionet.mjs       cross-platform local CLI and chain gate
scripts/deploy_studionet.sh        optional Bash deployment gate
requirements-dev.txt              Direct Mode dependency
package.json                      local genlayer@0.39.1
*.md                              architecture/consensus/threat/deploy/handoff
```

## Research and official references

- [GenLayer Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [GenLayer CLI 0.39.1](https://docs.genlayer.com/api-references/genlayer-cli)
- [CLI deployment](https://docs.genlayer.com/developers/intelligent-contracts/deploying/cli-deployment)
- [Direct Mode tests](https://docs.genlayer.com/api-references/genlayer-test/direct)
- [GenLayer storage](https://docs.genlayer.com/developers/intelligent-contracts/storage)

RATCHET is a reusable infrastructure primitive. **No frontend. No hosted backend.**
