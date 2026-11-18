"""D84 All-Net frozen-history observer. Run only after lead source/check review.
No hypothetical units feed back into the living brain. No Net2/NetC/JointNet support.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
BASE=ROOT/'lab/v/future_evidence'
BASELINE=ROOT/'lab/v/allocation_trace.json'


def definition(x):
    return dict(sym=x['sym'],u=x['u'],v=x['v'],span=x['span'])


def write_history(hist,i,sym,keep,limit):
    """Native Net.write semantics, including skipped retention pop on keep short-circuit."""
    if keep and i in hist:return False
    old=dict(hist)
    hist[i]=sym
    hist.pop(i-limit,None)
    return hist!=old


def signature(defs,k,memo):
    """Inductive exact equivalence for Net: fixed symbols span1; composites concatenate."""
    if k in memo:return memo[k]
    d=defs[k]
    if d['sym'] is not None:
        assert d['span']==1 and d['u'] is None and d['v'] is None
        result=(d['sym'],)
    else:
        u,v=signature(defs,d['u'],memo),signature(defs,d['v'],memo)
        assert d['span']==len(u)+len(v)
        result=u+v
    memo[k]=result
    return result


def activates(symbols,hist,i):
    absent=object()
    return all(hist.get(i-len(symbols)+1+j,absent)==sym for j,sym in enumerate(symbols))


def native_expression_fires(defs,k,hist,i,memo):
    key=(k,i)
    if key in memo:return memo[key]
    d=defs[k]
    if d['sym'] is not None:r=hist.get(i,object())==d['sym']
    else:r=native_expression_fires(defs,d['v'],hist,i,memo) and native_expression_fires(defs,d['u'],hist,i-defs[d['v']]['span'],memo)
    memo[key]=r
    return r


class FutureEvidence:
    def __init__(self,lf,issued):
        import grownet as GN
        b=self.b=lf.brain
        assert all(type(n) is GN.Net for n in b.nets), 'Only exact Net supported; clock-named streams are not a different class'
        self.limit=GN.HIST
        self.issued=issued
        self.defs=[{} for n in b.nets]
        self.initial_histories=[dict(n.hist) for n in b.nets]
        self.shadow=[dict(n.hist) for n in b.nets]
        self.version=[0]*len(b.nets)
        self.write_call=[0]*len(b.nets)
        self.events=[]
        self.predictions=[]
        self.speaking={}
        self.current_learn=None
        self.taste=None
        self.taste_id=0
        self.counters=Counter()
        for j,n in enumerate(b.nets):
            for k,x in n.units.items():self._save(j,k,x,-1,None)
            self._wrap(n,j)
        original_taste,original_predict=b.taste,b.predict
        def taste(value,at):
            assert self.taste is None
            self.taste=dict(id=self.taste_id,t=float(b.t+at));self.taste_id+=1
            try:return original_taste(value,at)
            finally:self.taste=None
        def predict():
            assert self.current_learn is None, 'Prediction interleaved with unfinalized structural definitions'
            result=original_predict()
            seq=self.emit('predict',t=float(b.t))
            self.predictions.append(seq)
            for j,r in enumerate(self.issued.last[1:]):
                if r.awake:
                    assert r.speaker in self.defs[j]
                    key=(j,r.speaker)
                    if key not in self.speaking:self.speaking[key]=dict(first_seq=seq,count=0)
                    self.speaking[key]['count']+=1
            self.counters['predict_calls']+=1
            return result
        b.taste,b.predict=taste,predict

    def emit(self,kind,**row):
        seq=len(self.events);self.events.append(dict(seq=seq,kind=kind,**row));return seq

    def _save(self,j,k,x,birth_seq,taste):
        d=definition(x)
        if k in self.defs[j]:assert self.defs[j][k]['definition']==d,'Structural definition changed'
        else:
            if d['sym'] is None:
                assert d['u'] in self.defs[j] and d['v'] in self.defs[j]
            self.defs[j][k]=dict(definition=d,birth_seq=birth_seq,birth_taste=taste,birth_time=float(x['born']))

    def _wrap(self,n,j):
        original_write,original_learn,original_add,original_remove=n.write,n.learn,n._add,n._remove
        ob=self
        def write(i,sym,keep=False):
            result=original_write(i,sym,keep)
            changed=write_history(ob.shadow[j],i,sym,keep,ob.limit)
            assert ob.shadow[j]==n.hist,'Native history differs from observer replay'
            ob.version[j]+=int(changed);ob.write_call[j]+=1
            ob.emit('write',stream=j,i=i,sym=sym,keep=bool(keep),changed=changed,version=ob.version[j])
            ob.counters['write_calls']+=1
            return result
        def add(*a,**kw):
            result=original_add(*a,**kw)
            assert ob.current_learn is not None and ob.current_learn['stream']==j
            ob.current_learn['new_ids'].append(result)
            ob.counters['adds']+=1
            return result
        def remove(k):
            if k in n.units:
                assert k in ob.defs[j], 'Removal before immutable definition finalization'
                assert ob.defs[j][k]['definition']==definition(n.units[k])
                ob.emit('remove',stream=j,k=k,t=float(ob.b.t),
                    taste=None if ob.taste is None else ob.taste['id'],counts=list(n.units[k]['n']),
                    version=ob.version[j],write_call=ob.write_call[j],i=ob.b.place(n)-1)
                ob.counters['removals']+=1
            return original_remove(k)
        def learn(i,letter,t,speaker,firing):
            assert ob.current_learn is None and ob.taste is not None
            for k,x in n.units.items():assert ob.defs[j][k]['definition']==definition(x),'Mutable activation semantics'
            seq=ob.emit('learn',stream=j,i=i,t=float(t),letter=int(letter),taste=ob.taste['id'],
                living=list(n.units),firing=list(firing),version=ob.version[j],write_call=ob.write_call[j])
            ctx=dict(stream=j,new_ids=[]);ob.current_learn=ctx
            try:result=original_learn(i,letter,t,speaker,firing)
            finally:ob.current_learn=None
            for k in ctx['new_ids']:
                assert k in n.units,'New unit vanished before finalized immutable snapshot'
                born=ob.emit('birth',stream=j,k=k,t=float(t),taste=ob.taste['id'])
                ob._save(j,k,n.units[k],born,ob.taste['id'])
            ob.counters['learn_calls']+=1
            return result
        n.write,n.learn,n._add,n._remove=write,learn,add,remove

    def raw(self):
        return dict(classes=[type(n).__name__ for n in self.b.nets],names=[n.kind for n in self.b.nets],
            definitions=self.defs,initial_histories=self.initial_histories,events=self.events,
            prediction_positions=self.predictions,speaking=self.speaking,hist_limit=self.limit,counters=dict(self.counters))


def provenance():
    paths=('lab/future_evidence.py','lab/future_evidence_checks.py','lab/issued_credit.py','lab/issued_credit_compare.py',
           'lab/alloc_rules.py','lab/alloc_compare.py','lab/grownet.py','lab/teach.py')
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        baseline_sha256=hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        command='timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/future_evidence.py run')


def run():
    import alloc_compare as C
    from issued_credit import install
    from active_mixture_audit import fingerprint
    from stage2_lang import arms as S
    started=time.monotonic();out=dict(provenance=provenance());trace=None
    baseline=json.loads(BASELINE.read_text());assert 'failure' not in baseline and all(baseline['identity'].values())
    old=S.live
    def live(lf,seconds):
        nonlocal trace
        issued=install(lf,True);trace=FutureEvidence(lf,issued)
        result=old(lf,seconds)
        out['fingerprint']=fingerprint(lf)[0];out['issued_credit']=issued.summary()
        return result
    S.live=live;C.G=1000
    try:
        r=C.one(('seq','W',560,177000,'red'))
        out['result']=json.loads(json.dumps(r['result']));out['allocation']=r['alloc']
        out['identity']=dict(fingerprint=out['fingerprint']==baseline['fingerprint'],result=out['result']==baseline['result'],
            allocation=r['alloc']==baseline['alloc'],additions=trace.counters['adds']==baseline['counters']['add_calls'],
            removals=trace.counters['removals']==baseline['counters']['removed_units'],
            learns=trace.counters['learn_calls']==baseline['counters']['verified_room_rng_states'])
        assert all(out['identity'].values()),'D83 neutral identity failed'
        print('IDENTITY PASS',out['identity'],flush=True)
    except Exception as e:
        out['failure']=dict(type=type(e).__name__,message=str(e));raise
    finally:
        S.live=old;out['wall_s']=time.monotonic()-started
        out['raw_pickle']=str(BASE.with_suffix('.pkl'))
        if trace is not None:out['counters']=dict(trace.counters)
        BASE.with_suffix('.pkl').write_bytes(pickle.dumps(dict(summary=out,raw={} if trace is None else trace.raw())))
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':
    assert sys.argv[1:]==['run'];run()
