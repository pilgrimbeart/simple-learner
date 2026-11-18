"""D83 neutral one-life trace. No run before frozen hook review.
Run with an external 240 s timeout and three maths-thread environment variables at 1.
The observer never draws from live RNGs, calls predict, or changes learning decisions.
"""
from __future__ import annotations
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path
import pickle
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
BASE=ROOT/'lab/v/allocation_trace'
BASELINE=ROOT/'lab/v/issued_credit_compare.json'


def leaves(n,exclude=None):
    return [k for k,x in n.units.items() if x['sym'] is None and not x['kids'] and k!=exclude]


def allocator_rng(room):
    found=[c.cell_contents for c in (getattr(room,'__closure__',None) or ()) if isinstance(c.cell_contents,np.random.Generator)]
    assert len(found)==1, 'Expected one directly captured W allocator RNG'
    return found[0]


def reconstruct(n,nets,st,rng,t):
    """Clone-and-replay exact W candidate/leaf draws before the native room call."""
    clone=np.random.Generator(type(rng.bit_generator)(0))
    clone.bit_generator.state=copy.deepcopy(rng.bit_generator.state)
    row=dict(full=st['fixed']+st['grown']>=st['cap'],due=False,opponent=None,won=False,
             draws=[],leaf_draws=[],victim=None)
    deep=n._deep
    row['due']=deep is not None and deep in n.units and min(n.units[deep]['n'])>=1
    if row['full'] and row['due']:
        for _ in range(200):
            j=int(clone.integers(len(nets)));row['draws'].append(j)
            c=nets[j]
            if c is not n and any(x['sym'] is None and not x['kids'] for x in c.units.values()):
                row['opponent']=j
                row['opponent_w']=float(getattr(c,'w',1.))
                row['requester_w']=float(getattr(n,'w',1.))
                row['opponent_leaves']=len(leaves(c))
                row['won']=row['opponent_w']<row['requester_w']
                if row['won']:
                    ks=leaves(c)
                    row['leaf_draws']=[ks[int(clone.integers(len(ks)))] for _ in range(4)]
                    row['victim']=min(row['leaf_draws'],key=lambda k:c._trace(c.units[k],t))
                break
    return row,clone.bit_generator.state


class AllocationTrace:
    def __init__(self,lf,issued):
        import grownet as GN
        self.b,self.issued=lf.brain,issued
        self.fade=GN.FADE
        assert all(type(n).says in (GN.Net.says,GN.Net2.says) for n in self.b.nets)
        self.index={id(n):j for j,n in enumerate(self.b.nets)}
        self.rngs=[allocator_rng(n._room) for n in self.b.nets]
        assert all(r is self.rngs[0] for r in self.rngs)
        self.contests,self.removals,self.learns=[],[],[]
        self.counters=Counter()
        self.taste=None
        self.current_learn=None
        self.room=None
        self.tidy_depth=0
        self.removal_stack=[]
        self.next_taste=0
        for j,n in enumerate(self.b.nets):self._wrap(n,j,self.rngs[j])
        original=self.b.taste
        def taste(value,at):
            assert self.taste is None
            self.taste=dict(id=self.next_taste,t=float(self.b.t+at),letter=None,completed=set())
            self.next_taste+=1
            try:return original(value,at)
            finally:self.taste=None
        self.b.taste=taste

    def forecast(self,n):
        k,_=n.says(self.b.place(n)-1)
        if k is None:return dict(speaker=None,p0=None,p1=None,choice=None)
        return dict(speaker=int(k),p0=float(self.b._pk(n,k,0)),p1=float(self.b._pk(n,k,1)),
                    choice=int(n.units[k]['n'][1]>n.units[k]['n'][0]))

    def stage(self,n):
        j=self.index[id(n)]
        if self.taste is None:return 'outside_taste'
        if j in self.taste['completed']:return 'completed_learning'
        if self.current_learn is not None and self.current_learn['stream']==j:return 'current_learning'
        return 'not_yet_learned'

    def unit(self,n,k):
        x=n.units[k];t=float(self.b.t)
        return dict(id=int(k),span=x['span'],counts=list(x['n']),age_s=t-x['born'],
                    use_stored=float(x['use']),use_decayed=float(n._trace(x,t)),own_stored=float(x['own']),
                    own_decayed=float(x['own']*math.exp(-(t-x['to'])/self.fade)),parents=[x['u'],x['v']],
                    children=len(x['kids']),is_leaf=not x['kids'],is_fixed=x['sym'] is not None)

    def _wrap(self,n,j,rng):
        import grownet as GN
        original_room,original_remove,original_learn,original_add,original_tidy=n._room,n._remove,n.learn,n._add,n.tidy
        ob=self
        # IMPORTANT: rng remains a directly captured Generator, as in native _room.
        # D82's fingerprint enumerates these direct cells; one per stream is preserved.
        def room():
            t=float(ob.b.t)
            expected,poststate=reconstruct(n,ob.b.nets,ob.b._alloc,rng,t)
            if expected['full'] and expected['due']:
                expected.update(id=len(ob.contests),t=t,requester=j,
                    learn=None if ob.current_learn is None else ob.current_learn['id'],
                    requester_stage=ob.stage(n),requester_leaves=len(leaves(n,n._deep)),
                    actual_removals=[])
                ob.contests.append(expected)
                if ob.current_learn is not None:ob.current_learn['contests'].append(expected['id'])
                if expected['opponent'] is not None:
                    expected['opponent_stage']=ob.stage(ob.b.nets[expected['opponent']])
                    expected['leaf_candidate_details']=[ob.unit(ob.b.nets[expected['opponent']],k) for k in expected['leaf_draws']]
                ob.room=expected
            else:ob.room=None
            c0,w0=ob.b._alloc['contests'],ob.b._alloc['won']
            try:answer=original_room()
            finally:ob.room=None
            assert rng.bit_generator.state==poststate, 'Allocator RNG clone differs from actual post-state'
            assert ob.b._alloc['contests']-c0==int(expected['opponent'] is not None)
            assert ob.b._alloc['won']-w0==int(expected['won'])
            if expected['full'] and expected['due']:
                victims=expected['actual_removals']
                target=[] if not expected['won'] else [(expected['opponent'],expected['victim'])]
                assert [(ob.removals[i]['stream'],ob.removals[i]['unit']['id']) for i in victims]==target, 'Replayed victim differs'
                assert bool(answer)==expected['won']
                expected['verified']=True
                ob.counters['verified_contest_attempts']+=1
            ob.counters['verified_room_rng_states']+=1
            return answer
        def remove(k):
            if k not in n.units:return original_remove(k)
            root=not ob.removal_stack
            before=ob.forecast(n) if root else None
            group=len(ob.removals) if root else ob.removal_stack[0]
            reason=('contest_transfer' if ob.room is not None else 'tidy' if ob.tidy_depth else
                    'own_recycling' if ob.current_learn is not None and ob.current_learn['stream']==j else 'other')
            issued=ob.issued.last
            cached=issued[j+1] if issued is not None else None
            row=dict(id=len(ob.removals),group=group,t=float(ob.b.t),stream=j,reason=reason,
                unit=ob.unit(n,k),stage=ob.stage(n),before=before,after=None,
                stream_weight=float(getattr(n,'w',1.)),stream_saved=float(getattr(n,'saved',0.)),
                default_weight=float(getattr(ob.b,'w_def',1.)),
                stored_weight_total=float(getattr(ob.b,'w_def',1.))+sum(float(getattr(m,'w',1.)) for m in ob.b.nets),
                current_speaker=(before['speaker']==k) if root else None,
                issued_speaker=cached is not None and cached.speaker==k,
                learn=None if ob.current_learn is None else ob.current_learn['id'],
                taste=None if ob.taste is None else ob.taste['id'],
                letter=None if ob.taste is None else ob.taste['letter'],
                completed_streams=[] if ob.taste is None else sorted(ob.taste['completed']),
                learning_stream=None if ob.current_learn is None else ob.current_learn['stream'],
                leaf_count=len(leaves(n)))
            ob.removals.append(row)
            if ob.room is not None:ob.room['actual_removals'].append(row['id'])
            if ob.current_learn is not None:ob.current_learn['removals'].append(row['id'])
            ob.removal_stack.append(group)
            try:answer=original_remove(k)
            finally:ob.removal_stack.pop()
            if root:
                row['after']=ob.forecast(n)
                row['default_p1']=float(ob.b._pdef(1))
            ob.counters['removed_units']+=1
            return answer
        def add(*a,**kw):
            result=original_add(*a,**kw)
            if ob.current_learn is not None:
                ob.current_learn['adds'].append(dict(stream=j,id=int(result),parents=[n.units[result]['u'],n.units[result]['v']],span=n.units[result]['span']))
            ob.counters['add_calls']+=1
            return result
        def learn(i,letter,t,speaker,firing):
            assert ob.current_learn is None
            if ob.taste is not None:
                assert ob.taste['letter'] in (None,letter)
                ob.taste['letter']=int(letter)
            row=dict(id=len(ob.learns),t=float(t),stream=j,i=i,letter=int(letter),speaker=speaker,
                     taste=None if ob.taste is None else ob.taste['id'],
                     firing_count=len(firing),removals=[],adds=[],contests=[],deep=None)
            ob.learns.append(row)
            ob.current_learn=row
            try:answer=original_learn(i,letter,t,speaker,firing)
            finally:
                ob.current_learn=None
                if ob.taste is not None:ob.taste['completed'].add(j)
            if row['removals'] and not row['adds']:
                # All predicates here are read-only diagnostics after the native learn call.
                # No random partner choice is probed or consumed.
                if type(n).learn is GN.Net.learn:
                    d=row['deep']
                    if d is not None and d in n.units:
                        span=n.units[d]['span']
                        candidates,_=n.firing(i-span)
                        if not candidates:reason='no_partner_at_i_minus_span'
                        elif all(n.units[k]['span']+span>GN.HIST//2 for k in candidates):reason='all_available_partners_too_long'
                        elif len(n.units)>=n.P:reason='no_capacity_after_removal'
                        else:reason='partner_exists_no_birth_draw_not_recorded'
                    else:reason='deep_missing_or_unrecorded'
                else:reason='non_Net_growth_path_not_diagnosed'
                row['no_birth_diagnostic']=reason
            return answer
        def tidy(i,t):
            ob.tidy_depth+=1
            try:return original_tidy(i,t)
            finally:ob.tidy_depth-=1
        # Capture the native allocation wrapper's chosen deep at _room entry, when tallies are updated.
        native_room=room
        def noted_room():
            if ob.current_learn is not None:ob.current_learn['deep']=n._deep
            # Direct RNG closure retained in this final installed wrapper too.
            assert rng is ob.rngs[j]
            return native_room()
        n._room,n._remove,n._add,n.learn,n.tidy=noted_room,remove,add,learn,tidy

    def raw(self):
        return dict(names=[n.kind for n in self.b.nets],contests=self.contests,removals=self.removals,
                    learns=self.learns,counters=dict(self.counters))


def provenance():
    paths=('lab/allocation_trace.py','lab/allocation_trace_checks.py','lab/issued_credit.py',
           'lab/issued_credit_compare.py','lab/alloc_rules.py','lab/alloc_compare.py','lab/grownet.py','lab/teach.py')
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                baseline_sha256=hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
                command='timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/allocation_trace.py run')


def run():
    import alloc_compare as C
    from issued_credit import install
    from active_mixture_audit import fingerprint
    from stage2_lang import arms as S
    start=time.monotonic();out=dict(provenance=provenance(),config=dict(seed=177000,first='red',seconds=300.,dt=.0025,cap=3042,rule='W',mode='issued'))
    baseline=next(r for r in json.loads(BASELINE.read_text())['lives'] if
        (r['world'],r['rule'],r['mode'],r['seed'],r['first'])==('seq','W','issued',177000,'red'))
    original=S.live
    trace=None
    def live(lf,seconds):
        nonlocal trace
        issued=install(lf,True)
        trace=AllocationTrace(lf,issued)
        lived=original(lf,seconds)
        out['fingerprint']=fingerprint(lf)[0]
        out['issued_credit']=issued.summary()
        return lived
    S.live=live;C.G=1000
    try:
        result=C.one(('seq','W',560,177000,'red'))
        out['result']=json.loads(json.dumps(result['result']))
        out['alloc']=result['alloc']
        out['identity']=dict(fingerprint=out['fingerprint']==baseline['fingerprint'],result=out['result']==baseline['result'],
                             allocation=result['alloc']==baseline['alloc'])
        assert all(out['identity'].values()), 'D82 identity failed'
        print('IDENTITY PASS',out['identity'],flush=True)
    except Exception as e:
        out['failure']=dict(type=type(e).__name__,message=str(e))
        raise
    finally:
        S.live=original
        out['wall_s']=time.monotonic()-start
        raw={} if trace is None else trace.raw()
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(summary=out,raw=raw)))
        out['raw_pickle']=str(BASE.with_suffix('.pkl'))
        if trace is not None:out['counters']=dict(trace.counters)
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':
    assert sys.argv[1:]==['run'], 'Only explicit reviewed run mode is supported'
    run()
