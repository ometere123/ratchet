"""GenLayer Direct Mode scenarios — run with `gltest direct_tests -v -s`.

Not validated by the offline pytest suite. Requires genlayer-test==0.29.0
and matching GenLayer Python runtime installed on the developer machine.
"""

BASE = 'All treasury withdrawals require two approvals from independent signers.'
THREE = 'All treasury withdrawals require three approvals from independent signers.'
FOUR = 'All treasury withdrawals require four approvals from independent signers.'
DOMAIN = 'Treasury withdrawals by treasury operators for all recipients and amounts.'


def assessment(current='STRICTER', genesis='STRICTER', scope=True, witness='one extra independent signature'):
    return {'current_relation':current,'genesis_relation':genesis,'same_frozen_scope':scope,
            'reason_code':'MATERIAL_SCOPE_TEST','weakening_witness':'','tightening_witness':witness}


def open_track(direct_deploy):
    c=direct_deploy('contracts/ratchet.py')
    p=c.create_policy('Finance', 'Only stricter transaction-approval constraints are admissible.')
    t=c.register_track(p,'approvals',DOMAIN,BASE)
    root=c.seal_policy(p)
    return c,p,t,root


def with_leader(direct_vm, value=None):
    direct_vm.mock_llm(r'RATCHET / LEADER ASSESSMENT', value or assessment())


def test_genesis_and_consumer_pinning(direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    track=c.get_track(t)
    assert c.get_policy(p)['sealed'] is True
    assert len(root)==64
    assert c.is_track_at_least(t,1,track['genesis_hash']) is True
    assert c.is_track_at_least(t,2,track['genesis_hash']) is False
    assert c.is_policy_at_least(p,0,root) is True


def test_one_stricter_amendment(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    before=c.get_track(t)
    with_leader(direct_vm)
    aid=c.propose_revision(t,THREE,before['head_hash'])
    a=c.get_amendment(aid)
    assert a['status']=='ACCEPTED'
    assert a['relation_to_head']=='STRICTER'
    assert a['relation_to_genesis']=='STRICTER'
    assert c.get_track(t)['version']==2
    assert c.get_track(t)['genesis_hash']==before['genesis_hash']
    assert c.is_policy_at_least(p,1,root)


def test_independent_validator_approves_when_substantive_analysis_agrees(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm)
    c.propose_revision(t,THREE,c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT', assessment())
    direct_vm.mock_llm(r'RATCHET / ADVERSARIAL COUNTEREXAMPLE AUDIT',
        {'weakened':False,'incomparable':False,'ambiguous':False})
    assert direct_vm.run_validator() is True


def test_independent_validator_vetoes_malicious_stricter(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm)
    c.propose_revision(t,'Approvals may be bypassed for emergency payments.',c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT',assessment('WEAKER','WEAKER',witness=''))
    assert direct_vm.run_validator() is False


def test_validator_rejects_leader_wrong_status_even_when_validator_is_correct(direct_vm, direct_deploy):
    c, p, t, root = open_track(direct_deploy)
    # The leader claims a strengthening is weaker. The independent validator
    # derives the correct material relation from the frozen inputs.
    with_leader(direct_vm, assessment('WEAKER', 'WEAKER', witness=''))
    c.propose_revision(t, THREE, c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT', assessment())
    assert direct_vm.run_validator() is False


def test_validator_rejects_leader_scope_substitution(direct_vm, direct_deploy):
    c, p, t, root = open_track(direct_deploy)
    with_leader(direct_vm, assessment(scope=False))
    c.propose_revision(t, THREE, c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT', assessment())
    assert direct_vm.run_validator() is False


def test_adversarial_witness_vetoes_false_positive(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm)
    c.propose_revision(t,THREE,c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT',assessment())
    direct_vm.mock_llm(r'RATCHET / ADVERSARIAL COUNTEREXAMPLE AUDIT',
        {'weakened':True,'incomparable':False,'ambiguous':False})
    assert direct_vm.run_validator() is False


def test_validator_rejects_malformed_attack_result(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm)
    c.propose_revision(t,THREE,c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT',assessment())
    direct_vm.mock_llm(r'RATCHET / ADVERSARIAL COUNTEREXAMPLE AUDIT',
        {'weakened':'false','incomparable':False,'ambiguous':False})
    assert direct_vm.run_validator() is False


def test_disagreement_on_genesis_is_veto(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm)
    c.propose_revision(t,THREE,c.current_track_hash(t))
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'RATCHET / INDEPENDENT ASSESSMENT',assessment('STRICTER','WEAKER',witness=''))
    assert direct_vm.run_validator() is False


def test_weakening_remains_audit_record_without_head_change(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    before=c.current_track_hash(t)
    with_leader(direct_vm,assessment('WEAKER','WEAKER',witness=''))
    aid=c.propose_revision(t,'Only large withdrawals need one approval.',before)
    assert c.get_amendment(aid)['status']=='REJECTED'
    assert c.current_track_hash(t)==before
    assert c.get_track(t)['version']==1


def test_equivalence_is_rejected(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm,assessment('EQUIVALENT','EQUIVALENT',witness=''))
    aid=c.propose_revision(t,'Two independent approvals are mandatory for all withdrawals.',c.current_track_hash(t))
    assert c.get_amendment(aid)['status']=='REJECTED'


def test_incomparable_is_rejected(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm,assessment('INCOMPARABLE','INCOMPARABLE',witness=''))
    aid=c.propose_revision(t,'One approval for small withdrawals and four for large.',c.current_track_hash(t))
    assert c.get_amendment(aid)['status']=='REJECTED'


def test_changed_domain_is_rejected(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm,assessment('STRICTER','STRICTER',scope=False))
    aid=c.propose_revision(t,'Three approvals for domestic withdrawals only.',c.current_track_hash(t))
    assert c.get_amendment(aid)['status']=='REJECTED'


def test_ambiguous_is_rejected(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with_leader(direct_vm,assessment('AMBIGUOUS','AMBIGUOUS',witness=''))
    aid=c.propose_revision(t,'More approvals when appropriate.',c.current_track_hash(t))
    assert c.get_amendment(aid)['status']=='REJECTED'


def test_only_owner_can_evolve(direct_vm,direct_deploy,direct_alice):
    c,p,t,root=open_track(direct_deploy)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert('ONLY_OWNER'):
            c.propose_revision(t,THREE,c.current_track_hash(t))


def test_stale_head_rejected(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    before=c.current_track_hash(t)
    with_leader(direct_vm)
    c.propose_revision(t,THREE,before)
    with direct_vm.expect_revert('STALE_HEAD'):
        c.propose_revision(t,FOUR,before)


def test_no_new_track_after_seal(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    with direct_vm.expect_revert('SEALED_NO_NEW_TRACKS'):
        c.register_track(p,'new',DOMAIN,BASE)


def test_genesis_hash_must_match(direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    assert c.is_track_at_least(t,1,'fake') is False
    assert c.is_policy_at_least(p,0,'fake') is False


def test_policy_head_advances_only_when_accepted(direct_vm,direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    head=c.current_policy_hash(p)
    with_leader(direct_vm,assessment('WEAKER','WEAKER',witness=''))
    c.propose_revision(t,'Only one signature required.',c.current_track_hash(t))
    assert c.current_policy_hash(p)==head
    direct_vm.clear_mocks()
    with_leader(direct_vm)
    c.propose_revision(t,THREE,c.current_track_hash(t))
    assert c.current_policy_hash(p)!=head


def test_no_unchecked_undefined_policy(direct_deploy):
    c,p,t,root=open_track(direct_deploy)
    assert not c.is_policy_at_least(999999,0,root)
    assert not c.is_track_at_least(999999,1,'X')


def test_bound_on_number_of_tracks(direct_vm,direct_deploy):
    c=direct_deploy('contracts/ratchet.py')
    p=c.create_policy('B','purpose')
    for i in range(8):c.register_track(p,f'R{i}',DOMAIN,BASE)
    with direct_vm.expect_revert('TRACK_LIMIT'):
        c.register_track(p,'R8',DOMAIN,BASE)
