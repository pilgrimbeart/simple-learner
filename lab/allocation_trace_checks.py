"""D83 deterministic allocator fixtures; zero simulated steps, known removal/birth cases."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
import numpy as np
import alloc_compare  # establishes frozen bank environment before grownet import
import alloc_rules as A
import grownet as GN
from issued_credit import Forecast
from allocation_trace import AllocationTrace,allocator_rng,reconstruct
from active_mixture_audit import fingerprint
BASE=ROOT/'lab/v/allocation_trace_checks'


def fixture(extra=False):
    rng=np.random.default_rng(101)
    nets=[GN.Net(k,20,rng,prune=False,fade=False,dup=False) for k in ('a','b','c')]
    b=SimpleNamespace(nets=nets,t=1.,taste=lambda *a:None,
        place=lambda n:1,_pk=lambda n,k,l:(n.units[k]['n'][l]+.5)/(sum(n.units[k]['n'])+1.))
    st=A.install(b,'W',4 if extra else 3,7)
    for n in nets:
        k=n._add(0,1,2,0.);n.units[k]['n']=[3,1];n._deep=k
        n.hist[0]=0
        def says(i,_n=n):
            k=2 if 2 in _n.units else 0
            return k,[k]
        n.says=says
    if extra:
        k=nets[0]._add(0,1,2,0.);nets[0].units[k]['n']=[1,1]
    b._pdef=lambda letter:.5
    for n in nets:
        n.w=1.
        n.ondemand=True
    lf=SimpleNamespace(brain=b,meals=[],scored=[],firings=[])
    issued=SimpleNamespace(last=(Forecast(None,0,.5,.5),)+tuple(Forecast(2,0,.7,.3) for _ in nets))
    return lf,issued


def main():
    started=time.monotonic();checks=[]
    try:
        lf,issued=fixture();b=lf.brain;n=b.nets[0];n.w=3.
        rng=allocator_rng(n._room);state=copy.deepcopy(rng.bit_generator.state)
        expected,post=reconstruct(n,b.nets,b._alloc,rng,b.t)
        assert rng.bit_generator.state==state,'Clone consumed live randomness'
        # Independent first candidate draw: seed [7,91], reject requester index0.
        reference=np.random.default_rng([7,91]);draws=[]
        while True:
            j=int(reference.integers(3));draws.append(j)
            if j!=0:break
        assert expected['draws']==draws and expected['opponent']==j
        checks.append(dict(name='clone_does_not_touch_live_rng_and_candidate_draw_matches',passed=True))
        trace=AllocationTrace(lf,issued)
        assert n._room() is True
        assert rng.bit_generator.state==post and b._alloc['won']==1
        assert len(trace.removals)==1 and trace.removals[0]['current_speaker'] and trace.removals[0]['issued_speaker']
        assert trace.contests[0]['verified'] and trace.removals[0]['before']['p1']!=trace.removals[0]['after']['p1']
        checks.append(dict(name='won_contest_actual_leaf_and_forecast_change',passed=True))

        lf,issued=fixture();b=lf.brain;n=b.nets[0];n.w=.1
        trace=AllocationTrace(lf,issued)
        assert n._room() is False and len(trace.contests)==1 and trace.contests[0]['verified']
        assert not trace.removals and b._alloc['contests']==1 and b._alloc['won']==0
        checks.append(dict(name='failed_contest_observed_without_removal',passed=True))

        # Native Net.learn deletes its spare leaf, then finds no past partner: no birth.
        fingerprints=[]
        for observe in (False,True):
            lf,issued=fixture(extra=True);b=lf.brain;n=b.nets[0];n.w=.1
            trace=AllocationTrace(lf,issued) if observe else None
            n.learn(0,1,1.,2,[2])
            assert 3 not in n.units and n.births==0 and b._alloc['grown']==3
            fingerprints.append(fingerprint(lf)[0])
            if trace:
                row=trace.learns[0]
                assert len(row['removals'])==1 and not row['adds']
                assert row['no_birth_diagnostic']=='no_partner_at_i_minus_span'
                assert trace.removals[0]['reason']=='own_recycling'
                assert allocator_rng(n._room) is trace.rngs[0]
        assert fingerprints[0]==fingerprints[1]
        checks.append(dict(name='actual_removal_no_birth_and_exact_neutral_fingerprint',passed=True,fingerprint=fingerprints[0]))

        # Recursive non-leaf removal cannot be safely probed mid-cascade; only root is probed.
        lf,issued=fixture(extra=True);n=lf.brain.nets[0]
        # Free one place before adding a child, keeping native cap invariant.
        lf.brain.nets[1]._remove(2)
        child=n._add(2,0,3,0.)
        n.units[child]['n']=[2,1]
        trace=AllocationTrace(lf,issued)
        n._remove(2)
        assert len(trace.removals)==2 and trace.removals[0]['after'] is not None and trace.removals[1]['before'] is None
        checks.append(dict(name='cascade_probe_only_on_complete_graph',passed=True))
    except Exception as e:
        out=dict(checks=checks,failure=repr(e),wall_s=time.monotonic()-started)
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        raise
    out=dict(checks=checks,simulated_steps=0,wall_s=time.monotonic()-started,
             source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                 ('lab/allocation_trace.py','lab/allocation_trace_checks.py','lab/alloc_rules.py','lab/grownet.py')})
    BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
