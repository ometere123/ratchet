# Standalone Intelligent Contract submission draft

**Title:** Ratchet — consensus-enforced non-weakening natural-language policies

**Contract category:** reusable standalone GenLayer Intelligent Contract primitive. No frontend, no backend.

**Summary:** Ratchet lets an organisation seal natural-language policy controls whose future revisions may become stricter, but may never be loosened through the same canon. Each candidate is independently assessed against both its immediate predecessor and the immutable genesis for strict permitted-behaviour subset, with a separate adversarial counterexample audit. Only unanimous *semantic agreement requirements as enforced by GenLayer custom equivalence* and deterministic `STRICTER/STRICTER/same_scope` checks can advance an append-only hash-linked policy. Weaker, equivalent, incomparable and ambiguous amendments remain recorded attempts but do not replace operative policy state. Consumer ICs may pin genesis/track identity and check minimum monotonic versions.

**Why this is reusable:** privacy non-weakening, treasury approval hardening, security baseline tightening, disclosure requirements, permission attenuation, sustainability safeguards, agent mandates, and irreversible governance promises.

**Consensus boundary:** one `gl.vm.run_nondet_unsafe` with independent validator re-analysis and adversarial weakening witness search; it compares full frozen texts, not just enum shape.

**Mechanics:** immutable genesis, one-way owner authority, irreversible seal, per-track version history, audit receipts including refusals, optimistic concurrency hashes, bounded attempts, consumer read gates.

**Demonstration:** tests include malicious leader, hidden exception, scope loss, genesis-erosion, owner restrictions, stale-head replay and accepted/rejected versioning. Live StudioNet proof is recorded below with finalized receipts and canonical readbacks.

**Live deployment:** Ratchet `0xbd1cf148872dD396d06437859B4Bd4c8c0862A86`; deploy tx `0xaa10c92091637f7baf036ad10f17f1f46411a1c3f0fc600e4f3159c07ebe0d70`; source SHA-256 `e30e6487d23ab73abe7b5924ede8fe10744069dd49322c50ad53970ea225ebd0`. Optional correctly bound consumer `0x0176AD19a6968a1D1F4Dd3db5F1833ECe247Ab0f`; consumer source SHA-256 `63a9ea986555c6b4c6598bb553b9d41e3d760700fe30ed373ea36c20bbd83e75`; successful protected action tx `0xfc82998dddfbe30b030c0f3278dff750e29c775be606eb46de20f02833827b8b`, final `get_action_count=1`. Full evidence and limitations are in [DEPLOYMENT.md](DEPLOYMENT.md).

**Verification state:** offline `14 passed`; structural preflight `14/14`; Direct Mode `21 passed` (including malicious-leader and scope-substitution regressions). Local CLI is `0.39.1`, and the exact stable StudioNet guard passed for chain `61999`. AST lint passed `3/3` for each contract; semantic GenVM SDK validation remains unresolved because the pinned SDK artifact was unavailable to the local linter.

The rejected stale-head receipt finalized at the lifecycle level but its execution reverted with `STALE_HEAD`; it is not represented as a successful state transition. The optional consumer evidence uses the corrected track-genesis binding; the earlier mis-bound consumer deployment is superseded.

**Status:** deployed on stable StudioNet 61999 with the live evidence and local verification listed above. The repository remains a standalone contract-only submission; semantic GenVM SDK lint validation is unresolved because the pinned runner artifact was unavailable to the linter cache.
