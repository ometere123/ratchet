# Cross-contract integration

Deployment order:

1. Deploy `contracts/ratchet.py` to **stable StudioNet chain 61999** using local CLI 0.39.1.
2. Create a policy and register one or more tracks; keep genesis values short and atomic.
3. Call `seal_policy`, record policy ID, track ID, resulting immutable **track genesis hash**.
4. Deploy `contracts/ratchet_consumer_example.py` passing the Ratchet contract address, track ID, immutable genesis hash, and minimum version `2`.
5. Consumer `perform_protected_action` fails before a qualifying tightening and succeeds after the first accepted tightening.
6. A rejected weaker candidate never unlocks the consumer.
7. Any new consumer should independently pin the **Ratchet contract address**. Do not trust a caller-supplied Ratchet address or arbitrary policy ID at execution time.

Typed consumer interface:

```python
@gl.contract_interface
class IRatchet:
    class View:
        def is_track_at_least(self, track_id: u256, minimum_version: u32, expected_genesis_hash: str) -> bool: ...
```

The consumer example performs only a harmless counter increment; **not** a real asset transfer. It illustrates API composability, not a claimed live proof.

## Exact hash or monotonic acceptance?

- `is_track_at_least` checks inclusion in an immutable semantic-evolution track, conditional on correctness of consensus judgements.
- `matches_policy_head` ensures the exact current full policy is pinned; any accepted change makes an older pin false.
- `current_track_hash` retrieves the latest hash for optimistic concurrency control in a proposer.

A consumer that requires specific concrete numeric rules (e.g. three actual signatures before paying) should still implement that deterministic condition itself. Merely achieving version 2 does not enforce the approvals.
