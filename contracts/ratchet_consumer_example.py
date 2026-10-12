# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Optional two-contract integration specimen; Ratchet does not depend on it."""
from genlayer import *

@gl.contract_interface
class IRatchetView:
    class View:
        def is_track_at_least(self, track_id: u256, minimum_version: u32, expected_genesis_hash: str) -> bool: ...


class VersionGatedExecutor(gl.Contract):
    ratchet_address: Address
    track_id: u256
    genesis_hash: str
    required_version: u32
    number_of_protected_actions: u256

    def __init__(self, ratchet_address: Address, track_id: u256,
                 genesis_hash: str, required_version: u32):
        self.ratchet_address = ratchet_address
        self.track_id = track_id
        self.genesis_hash = genesis_hash
        self.required_version = required_version
        self.number_of_protected_actions = u256(0)

    @gl.public.write
    def perform_protected_action(self) -> None:
        ratchet = IRatchetView(self.ratchet_address)
        if not ratchet.view().is_track_at_least(self.track_id, self.required_version, self.genesis_hash):
            raise gl.vm.UserError('RATCHET_REQUIREMENT_NOT_MET')
        self.number_of_protected_actions = u256(int(self.number_of_protected_actions)+1)

    @gl.public.view
    def get_action_count(self) -> u256:
        return self.number_of_protected_actions
