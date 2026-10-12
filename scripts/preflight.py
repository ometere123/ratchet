#!/usr/bin/env python3
"""Offline structural preflight. Does not simulate GenVM or attest live state."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
main=(ROOT/'contracts/ratchet.py').read_text()
consumer=(ROOT/'contracts/ratchet_consumer_example.py').read_text()
checks=[]
def ck(expr,msg):
    assert expr,msg
    checks.append(msg)
ast.parse(main);ast.parse(consumer)
ck(True,'contract and companion Python syntax parses')
ck(main.count('gl.vm.run_nondet_unsafe(')==1,'one custom independent validator boundary')
ck('INDEPENDENT ASSESSMENT' in main,'independent validator has its own prompt')
ck('RATCHET / ADVERSARIAL COUNTEREXAMPLE AUDIT' in main,'validator searches for weakening counterexample')
ck('genesis' in main and 'current' in main,'compares both genesis and head')
ck('REL_INCOMPARABLE' in main and 'REL_WEAKER' in main and 'REL_AMBIGUOUS' in main,'fail-closed semantic outcomes')
ck('ALREADY_SEALED' in main and 'SEALED_NO_NEW_TRACKS' in main,'irreversible sealing')
ck('STALE_HEAD' in main,'stale-head guard')
ck('len(t.history)>=MAX_ATTEMPTS' in main,'per-track consensus cost bounded')
ck('def is_track_at_least' in main and 'def is_policy_at_least' in main,'typed consumer-gating surface')
ck('ratchet.view().is_track_at_least' in consumer,'sample consumer actively checks Ratchet state')
config=(ROOT/'gltest.config.yaml').read_text()
ck('https://studio.genlayer.com/api' in config and 'studio-dev' not in config,'correct stable studio RPC only')
pkg=(ROOT/'package.json').read_text()
ck('"genlayer": "0.39.1"' in pkg,'CLI pinned locally at 0.39.1')
ck('61997' not in main and 'studio-dev' not in main,'core contract contains no preview marker')
print('Ratchet offline structural preflight: %d/%d checks passed'%(len(checks),len(checks)))
for item in checks:print('  OK',item)
