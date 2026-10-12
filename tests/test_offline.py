"""Offline deterministic and validator-contract tests; NOT real GenVM Direct Mode."""
import copy
import importlib.util
import sys
import types
from pathlib import Path
import hashlib
import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'contracts/ratchet.py'

class GenArray(list):
    @classmethod
    def __class_getitem__(cls, _): return cls

class GenMap(dict):
    @classmethod
    def __class_getitem__(cls, _): return cls
    def __init__(self, cls=None):
        super().__init__()
        self.cls=cls
    def get_or_insert_default(self,key):
        if key not in self:
            instance=object.__new__(self.cls)
            if self.cls.__name__=='Policy': instance.tracks=GenArray()
            if self.cls.__name__=='Track': instance.history=GenArray()
            self[key]=instance
        return self[key]

class I(int): pass
class A(str): pass
class E:
    def __init__(self,*args,**kwargs):pass
    def emit(self):pass
class NotReturn:
    def __init__(self,calldata):self.calldata=calldata
class VM:
    Return=NotReturn
    UserError=ValueError
    def __init__(self): self.last_validator=None
    def run_nondet_unsafe(self,leader,validator):
        v=leader()
        self.last_validator=validator
        return v
class Prompt:
    def __init__(self):
        self.result={}
        self.independent=None
        self.audit={'weakened':False,'incomparable':False,'ambiguous':False}
    def exec_prompt(self,prompt,response_format='json'):
        if 'ADVERSARIAL COUNTEREXAMPLE AUDIT' in prompt: return copy.deepcopy(self.audit)
        if 'INDEPENDENT ASSESSMENT' in prompt and self.independent is not None:
            return copy.deepcopy(self.independent)
        return copy.deepcopy(self.result)
class Public:
    @staticmethod
    def write(f): return f
    @staticmethod
    def view(f): return f
class GL:
    Contract=object
    Event=E
    public=Public()
    message=types.SimpleNamespace(sender_address=A('0xA'))
    vm=VM()
    nondet=Prompt()
    @staticmethod
    def contract_interface(c):return c

def keccak(data):
    # Test stub for hashing only; sha3_256 is not Keccak256 and is not parity proof.
    return types.SimpleNamespace(hexdigest=lambda:hashlib.sha3_256(data).hexdigest())

@pytest.fixture
def core():
    g=GL()
    stub=types.ModuleType('genlayer')
    stub.gl=g
    stub.allow_storage=lambda x:x
    stub.TreeMap=GenMap
    stub.DynArray=GenArray
    stub.Address=A
    stub.u8=I;stub.u32=I;stub.u256=I
    stub.Keccak256=keccak
    sys.modules['genlayer']=stub
    spec=importlib.util.spec_from_file_location('ratchet_testing',SOURCE)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    c=mod.Ratchet()
    c.policies=GenMap(mod.Policy)
    c.tracks=GenMap(mod.Track)
    c.amendments=GenMap(mod.Amendment)
    yield mod,c,g
    sys.modules.pop('genlayer',None)
    sys.modules.pop(spec.name,None)

BASE='Treasury operators must obtain two approvals before any withdrawal.'
STRONG='Treasury operators must obtain three approvals before any withdrawal.'
STRONGER='Treasury operators must obtain four approvals before any withdrawal.'
WEAK='Treasury operators may withdraw with a single approval.'
DOMAIN='treasury operators, treasury withdrawals, approvals, every amount and recipient'

def setup_policy(c):
    pid=c.create_policy('Treasury','Only tightening permitted')
    t=c.register_track(pid,'approvals',DOMAIN,BASE)
    h=c.seal_policy(pid)
    return pid,t,h

def verdict(current='STRICTER',genesis='STRICTER',scope=True,weakening='',tightening='one extra approval required'):
    return {'current_relation':current,'genesis_relation':genesis,
            'same_frozen_scope':scope,'reason_code':'APPROVAL_BOUND_TIGHTENED',
            'weakening_witness':weakening,'tightening_witness':tightening}

def test_bootstrap_and_seal(core):
    _,c,_=core
    pid,t,root=setup_policy(c)
    assert len(root)==64 and c.get_policy(pid)['sealed']
    assert c.get_track(t)['version']==1
    assert c.is_track_at_least(t,1,c.get_track(t)['genesis_hash'])
    assert c.is_policy_at_least(pid,0,root)
    assert not c.is_policy_at_least(pid,1,root)
    with pytest.raises(ValueError,match='ALREADY_SEALED'):c.seal_policy(pid)
    with pytest.raises(ValueError,match='SEALED_NO_NEW_TRACKS'):c.register_track(pid,'another',DOMAIN,BASE)

def test_cannot_seal_empty(core):
    _,c,_=core
    pid=c.create_policy('P','purpose')
    with pytest.raises(ValueError,match='NO_TRACKS'):c.seal_policy(pid)
    assert c.current_policy_hash(pid)==''

def test_unauthorized_and_stale_head(core):
    _,c,g=core
    pid,t,_=setup_policy(c)
    h=c.current_track_hash(t)
    g.message.sender_address=A('0xB')
    with pytest.raises(ValueError,match='ONLY_OWNER'):c.propose_revision(t,STRONG,h)
    g.message.sender_address=A('0xA')
    with pytest.raises(ValueError,match='STALE_HEAD'):c.propose_revision(t,STRONG,'wrong')
    with pytest.raises(ValueError,match='NO_TEXT_CHANGE'):c.propose_revision(t,BASE,h)

def test_strict_amendment_monotone_chain(core):
    _,c,g=core
    pid,t,root=setup_policy(c)
    phead0=c.current_policy_hash(pid)
    g.nondet.result=verdict()
    aid=c.propose_revision(t,STRONG,c.current_track_hash(t))
    a=c.get_amendment(aid)
    assert a['status']=='ACCEPTED'
    assert a['relation_to_genesis']=='STRICTER'
    assert c.get_track(t)['version']==2
    assert c.current_policy_hash(pid)!=phead0
    assert c.is_track_at_least(t,2,c.get_track(t)['genesis_hash'])
    assert not c.is_track_at_least(t,2,'wrong')
    assert c.is_policy_at_least(pid,1,root)
    g.nondet.result=verdict()
    b=c.propose_revision(t,STRONGER,c.current_track_hash(t))
    assert c.get_amendment(b)['prior_version']==2
    assert c.get_track(t)['version']==3
    assert len(c.get_track(t)['history'])==2
    assert c.get_amendment(aid)['resulting_head_hash']==a['resulting_head_hash']

def test_weakening_and_incomparable_rejected_without_head_change(core):
    _,c,g=core
    pid,t,_=setup_policy(c)
    old=c.current_track_hash(t);po=c.current_policy_hash(pid)
    g.nondet.result=verdict('WEAKER','WEAKER',weakening='withdraw with one approval',tightening='')
    a=c.propose_revision(t,WEAK,old)
    assert c.get_amendment(a)['status']=='REJECTED'
    assert c.current_track_hash(t)==old
    assert c.current_policy_hash(pid)==po
    g.nondet.result=verdict('INCOMPARABLE','INCOMPARABLE',tightening='')
    b=c.propose_revision(t,'Treasury operator approvals only required for large payments.',old)
    assert c.get_amendment(b)['status']=='REJECTED'
    assert c.get_track(t)['attempts']==2

def test_genesis_anchor_prevents_gradual_erosion(core):
    _,c,g=core
    pid,t,_=setup_policy(c)
    g.nondet.result=verdict()
    c.propose_revision(t,STRONG,c.current_track_hash(t))
    old=c.current_track_hash(t)
    g.nondet.result=verdict('STRICTER','WEAKER',weakening='genesis protected class removed',tightening='adds logging')
    a=c.propose_revision(t,'Four approvals required except high-risk treasury transfers.',old)
    assert c.get_amendment(a)['status']=='REJECTED'
    assert c.current_track_hash(t)==old

def test_scope_change_and_ambiguous_refused(core):
    _,c,g=core
    pid,t,_=setup_policy(c)
    root=c.current_track_hash(t)
    g.nondet.result=verdict(scope=False)
    a=c.propose_revision(t,'Three approvals for domestic treasury withdrawals.',root)
    assert c.get_amendment(a)['status']=='REJECTED'
    g.nondet.result=verdict('AMBIGUOUS','AMBIGUOUS',tightening='')
    b=c.propose_revision(t,'Three approvals whenever reasonable.',root)
    assert c.get_amendment(b)['status']=='REJECTED'
    assert c.get_track(t)['version']==1

def test_independent_validator_rejects_malicious_leader(core):
    mod,c,g=core
    p,t,_=setup_policy(c)
    g.nondet.result=verdict()
    c.propose_revision(t,STRONG,c.current_track_hash(t))
    leader=mod.canonical_assessment(verdict())
    assert g.vm.last_validator(NotReturn(leader))
    g.nondet.independent=verdict('WEAKER','WEAKER',weakening='low approval threshold',tightening='')
    assert not g.vm.last_validator(NotReturn(leader))
    g.nondet.independent=verdict()
    g.nondet.audit={'weakened':True,'incomparable':False,'ambiguous':False}
    assert not g.vm.last_validator(NotReturn(leader))
    g.nondet.audit={'weakened':False,'incomparable':False,'ambiguous':True}
    assert not g.vm.last_validator(NotReturn(leader))
    assert not g.vm.last_validator({'fake':'return'})

def test_validator_fails_closed_to_bad_payloads(core):
    mod,c,g=core
    p,t,_=setup_policy(c)
    g.nondet.result=verdict()
    c.propose_revision(t,STRONG,c.current_track_hash(t))
    orig=mod.canonical_assessment(verdict())
    for bad in [{'current':1},[],{'current':1,'genesis':1,'same_scope':True,'reason':'A','weakening_witness':'','tightening_witness':''}]:
        assert not g.vm.last_validator(NotReturn(bad))
    g.nondet.independent={'current_relation':'STRICTER','genesis_relation':'STRICTER'}
    assert not g.vm.last_validator(NotReturn(orig))

def test_no_model_json_overflow_or_weakening_witness(core):
    mod,_,_=core
    base=verdict()
    assert mod.admissible(mod.canonical_assessment(base))
    assert not mod.admissible(mod.canonical_assessment({**base,'reason_code':'x'*2000}))
    assert not mod.admissible(mod.canonical_assessment({**base,'weakening_witness':'BYPASS'}))
    assert not mod.admissible(mod.canonical_assessment({**base,'tightening_witness':''}))
    assert not mod.admissible(mod.canonical_assessment({**base,'same_frozen_scope':'true'}))
    assert not mod.admissible(mod.canonical_assessment('NOT JSON'))

def test_multi_track_and_root_pin(core):
    _,c,g=core
    p=c.create_policy('p','purpose')
    a=c.register_track(p,'A',DOMAIN,BASE)
    b=c.register_track(p,'B','user access','Users must use MFA for all access.')
    root=c.seal_policy(p)
    tA=c.get_track(a)['genesis_hash']; tB=c.get_track(b)['genesis_hash']
    old_b=c.current_track_hash(b)
    g.nondet.result=verdict()
    c.propose_revision(a,STRONG,c.current_track_hash(a))
    assert c.current_track_hash(b)==old_b
    assert c.is_track_at_least(b,1,tB)
    assert not c.is_track_at_least(b,2,tB)
    assert c.is_track_at_least(a,2,tA)
    assert c.is_policy_at_least(p,1,root)

def test_bounded_tracks_inputs(core):
    _,c,_=core
    p=c.create_policy('p','purpose')
    with pytest.raises(ValueError):c.register_track(p,'bad','x','')
    with pytest.raises(ValueError):c.register_track(p,'bad','x','X'*2100)
    for i in range(8):c.register_track(p,f'T{i}',DOMAIN,BASE)
    with pytest.raises(ValueError,match='TRACK_LIMIT'):c.register_track(p,'T8',DOMAIN,BASE)

def test_policy_owner_cannot_replace_genesis(core):
    _,c,g=core
    p,t,_=setup_policy(c)
    before=c.get_track(t)
    g.nondet.result=verdict()
    c.propose_revision(t,STRONG,c.current_track_hash(t))
    after=c.get_track(t)
    assert before['genesis_text']==after['genesis_text']
    assert before['genesis_hash']==after['genesis_hash']
    with pytest.raises(ValueError,match='SEALED_NO_NEW_TRACKS'):
        c.register_track(p,'A','other',BASE)

def test_prompt_security_boundaries(core):
    mod,_,_=core
    prompt=mod.assessment_prompt(DOMAIN,BASE,STRONG,WEAK,'LEADER ASSESSMENT')
    assert 'UNTRUSTED DATA' in prompt
    assert 'GENESIS' in prompt and 'CURRENT' in prompt
    assert 'INCOMPARABLE' in prompt and 'WEAKER' in prompt
    assert 'counterexample' in prompt
    assert 'same_frozen_scope' in prompt
    assert 'RATCHET / ADVERSARIAL COUNTEREXAMPLE AUDIT' in mod.attack_prompt(DOMAIN,BASE,STRONG,WEAK)
