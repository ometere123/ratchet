# Stable StudioNet deployment and live proof

Current canonical deployment is on stable StudioNet (`studionet`, chain `61999`, RPC `https://studio.genlayer.com/api`) using repository-local `genlayer@0.39.1`.

## Current deployment

- Ratchet: `0x34fc30232010E499e76F9A5F25Fb358Da6b98a2e`
- Ratchet deployment tx: `0x50946449d78aaa7b072c81ede4ea1e782a11460c405b2fcf9c68eda16f8d1537`
- Ratchet source SHA-256: `e5e9e2eefcb8ae1a0d789c20ce06df9727097cb9c2eb06967618d6f2e45df0a5`
- Consumer: `0xEb45842c9DB9A64e573e987077659756506e52fA`
- Consumer deployment tx: `0x157ef60fc2f2b66bab0b47fc4de9d19ac32b8315d40c4d64d9309572c8f2f0ca`
- Consumer source SHA-256: `63a9ea986555c6b4c6598bb553b9d41e3d760700fe30ed373ea36c20bbd83e75`
- Consumer binding: Ratchet above, track `1`, track genesis `88996c8e2ac61e4877ed1b09be4fd7ce55584635670e4221a0f15b4e53793282`, required version `4`.

Both deployment receipts were `FINALIZED`, `MAJORITY_AGREE`, with successful deployment execution. `gen_getContractCode` returned bytes whose SHA-256 exactly matched the local source files. The previous Ratchet and consumer deployments remain historical and are not current evidence.

## Fresh live lifecycle evidence

All writes below were sent to the current addresses and independently polled to `FINALIZED`; no accepted-only state was treated as final.

| Proof | Transaction | Result and readback |
|---|---|---|
| Policy create | `0x473145f6c0d14e9982e174577edd32d7bc7f4f5339f18b9f1e1b01973679807c` | `FINALIZED / MAJORITY_AGREE`; policy `1` created |
| Track 1 register | `0x19f6a97f4eef401d6dcb60b47902b39d1da8f6eeefc80e65e858dc27450714fd` | `FINALIZED`; genesis `88996c8e...93282` |
| Track 2 register | `0x368ff58b19ce39df0e3bc100e84e91158117f8d6244c7600d979fff5a27209fa` | `FINALIZED` |
| Policy seal | `0x6af7ae1d938b9fed15e8a1867cf40cff797d8b4f356114214109beb8e81f578d` | `FINALIZED`; sealed with tracks `1,2` |
| Hidden emergency exception | `0x9ff69e69c8d771710fb163aa818230c1346414d2a7256c8c5dfede0815e3223f` | `FINALIZED`; `REJECTED`, `EXCEPTION_CARVEOUT_WEAKENS`, head unchanged |
| Scope substitution | `0xd09cb14c7aec4300ec27123df3369cb42d7ede341be316d3842c93432fe9ed39` | `FINALIZED`; `REJECTED`, `DOMESTIC_CARVEOUT_WEAKENS_SCOPE`, head unchanged |
| Accepted tightening v2 | `0x741cb099ea37b22184475e82591f53d2e677e05aa50ecdbd672099e65beb3ec8` | `FINALIZED`; `ACCEPTED`, version `2` |
| Accepted tightening v3 | `0xa0c6eebd0d3911d2dc5d5d8c2b7c1837327e12ce427b1ec94802173f80df0108` | `FINALIZED`; `ACCEPTED`, version `3` |
| Consumer denial before v4 | `0xc5c38072138929cfc9406139a92a2dfb43de22aff54e422fa2e0db9e9c78542f` | `FINALIZED / MAJORITY_AGREE`; execution `ERROR`, rollback `RATCHET_REQUIREMENT_NOT_MET`; action count remained `0` |
| Accepted tightening v4 | `0x26600fee936c53830876034503c8c63ddf55fc792e6e3555be5639ceb21f0078` | `FINALIZED`; `ACCEPTED`, version `4`, head `4cc64128059f513e3b6fcb4ac5a99751a44ec7d15876b9c991182ba9d0aca913` |
| Consumer success after v4 | `0xcacdffa082c4e88f4689913b0f109daeccfc5a1ae890c1f404490792d2cde43a` | `FINALIZED / MAJORITY_AGREE`; execution `SUCCESS`; `get_action_count()` read back `1` |

The policy gate now counts distinct qualified tracks, not revisions: repeated accepted tightening of track 1 does not satisfy `is_policy_at_least(policy, 2, genesis)` while track 2 remains at version 1. Direct Mode covers this distinction; the live consumer proof pins one exact track and minimum version.

## Verification commands

```bash
npm ci
npm run cli:version
node scripts/assert_studionet.mjs
python scripts/preflight.py
python -m pytest tests/test_offline.py -q
gltest direct_tests/test_ratchet_direct.py -q
```

The current verified local counts are: offline `14 passed`, preflight `14/14`, Direct Mode `24 passed`, AST lint `3/3` for each contract, and source parity for both deployed files. The semantic GenVM check remains blocked by the pinned linter’s SDK resolver: `genvm-lint check` returns `E101` because it cannot load `runners/py-genlayer/1j/b45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6.tar`, even though that member exists in the downloaded `genvm-universal-v0.2.12.tar.xz` archive. This is reported as unresolved; it is not claimed as a semantic lint pass.

## Historical evidence

The superseded Ratchet `0xbd1cf148872dD396d06437859B4Bd4c8c0862A86` and consumer `0x0176AD19a6968a1D1F4Dd3db5F1833ECe247Ab0f`, including their transactions and source hashes, are historical only. They must not be used as evidence for the current deployment.
