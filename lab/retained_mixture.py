"""D87 neutral combined-forecast capture and fixed-history retained comparison."""
import hashlib
import json
import pickle
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
from future_evidence import FutureEvidence,write_history,signature,activates
import retained_prediction as R
from retained_uniform_control import summarize as uniform_summary
BASE=ROOT/'lab/v/retained_mixture'
RAW=ROOT/'lab/v/future_evidence.pkl'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        source_sha256={p:digest(ROOT/p) for p in ('lab/retained_mixture.py','lab/future_evidence.py',
            'lab/retained_prediction.py','lab/retained_uniform_control.py','lab/issued_credit.py','lab/alloc_compare.py')},
        baseline_sha256=digest(RAW),command='timeout --signal=TERM --kill-after=5s 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/retained_mixture.py '+sys.argv[1])


class Capture(FutureEvidence):
    def __init__(self,lf,issued):
        self.combined=[]
        super().__init__(lf,issued)

    def emit(self,kind,**row):
        seq=super().emit(kind,**row)
        if kind=='predict':
            records=self.issued.last
            weights=[getattr(self.b,'w_def',1.)]+[getattr(n,'w',1.) for n in self.b.nets]
            awake=[j for j,r in enumerate(records) if r.awake]
            p=sum(weights[j]*records[j].p1 for j in awake)/sum(weights[j] for j in awake)
            assert abs(p-self.b.p1)<=1e-12
            self.combined.append(dict(seq=seq,t=row['t'],p1=float(self.b.p1),reconstruction_error=abs(p-self.b.p1)))
        return seq


def capture():
    import alloc_compare as C
    from issued_credit import install
    from active_mixture_audit import fingerprint
    from stage2_lang import arms as S
    baseline=pickle.loads(RAW.read_bytes());bs=baseline['summary']
    for p,h in bs['provenance']['source_sha256'].items():assert digest(ROOT/p)==h,p
    old=S.live;trace=None;out=dict(provenance=provenance());started=time.monotonic()
    def live(lf,seconds):
        nonlocal trace
        issued=install(lf,True);trace=Capture(lf,issued)
        result=old(lf,seconds)
        out['fingerprint']=fingerprint(lf)[0];out['issued_credit']=issued.summary()
        return result
    S.live=live;C.G=1000
    try:
        r=C.one(('seq','W',560,177000,'red'))
        out['result']=json.loads(json.dumps(r['result']));out['allocation']=r['alloc']
        out['identity']=dict(fingerprint=out['fingerprint']==bs['fingerprint'],result=out['result']==bs['result'],
            allocation=out['allocation']==bs['allocation'],issued_credit=out['issued_credit']==bs['issued_credit'],
            entire_trace=trace.raw()==baseline['raw'])
        assert all(out['identity'].values()),'D84 identity failed'
        out['predictions']=trace.combined
        out['max_reconstruction_error']=max(r['reconstruction_error'] for r in trace.combined)
        print('IDENTITY PASS',out['identity'],'predictions',len(trace.combined),flush=True)
    except Exception as e:
        out['failure']=repr(e);raise
    finally:
        S.live=old;out['wall_s']=time.monotonic()-started
        BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


def analyse():
    started=time.monotonic();out=dict(provenance=provenance(),failures=[])
    target=BASE.with_name(BASE.name+'_analysis')
    try:
        capture=json.loads(BASE.with_suffix('.json').read_text())
        assert 'failure' not in capture and all(capture['identity'].values())
        for p,h in capture['provenance']['source_sha256'].items():assert digest(ROOT/p)==h,p
        assert capture['provenance']['baseline_sha256']==digest(RAW)
        raw=pickle.loads(RAW.read_bytes())['raw']
        old=pickle.loads((ROOT/'lab/v/retained_prediction.pkl').read_bytes())
        oldrows={(r['stream'],r['k']):r for r in old['rows']}
        forecasts={p['seq']:p for p in capture['predictions']}
        assert list(forecasts)==raw['prediction_positions']
        definitions=[{k:r['definition'] for k,r in ds.items()} for ds in raw['definitions']]
        words=[{} for ds in definitions]
        for j,ds in enumerate(definitions):
            for k in ds:signature(ds,k,words[j])
        hist=[dict(h) for h in raw['initial_histories']];indices=[-1]*len(hist)
        candidates=[];seen=set();last=None;unique=[]
        for e in raw['events']:
            if e['kind']=='write':
                j=e['stream'];assert e['i']==indices[j]+1
                indices[j]=e['i'];write_history(hist[j],e['i'],e['sym'],e['keep'],raw['hist_limit'])
            elif e['kind']=='predict':
                last=dict(seq=e['seq'],hist=[dict(h) for h in hist],indices=list(indices),p1=forecasts[e['seq']]['p1'])
                assert forecasts[e['seq']]['t']==e['t']
            elif e['kind']=='remove' and sum(e['counts'])==1:
                previous=oldrows[e['stream'],e['k']]
                c={k:previous[k] for k in ('stream','k','family','name','word','death_seq','death_t','death_taste','same_taste_birth','eligible_100s')}
                c.update(counts=list(e['counts']),weight=.5,later_lessons=0,full=R.new_score(),horizon=R.new_score())
                candidates.append(c)
            elif e['kind']=='learn' and e['taste'] not in seen:
                seen.add(e['taste']);assert last is not None
                unique.append(dict(t=e['t'],label=e['letter'],p1=last['p1'],seq=last['seq']))
                for c in candidates:
                    if c['death_taste']==e['taste']:continue
                    assert c['death_seq']<last['seq']<e['seq']
                    j=c['stream'];c['later_lessons']+=1
                    if activates(c['word'],last['hist'][j],last['indices'][j]):
                        R.score_and_update(c,last['p1'],e['letter'],c['eligible_100s'] and e['t']-c['death_t']<=100.)
        assert len(candidates)==len(oldrows)
        for c in candidates:
            prev=oldrows[c['stream'],c['k']]
            assert c['counts']==prev['counts'] and c['later_lessons']==prev['later_lessons']
            for key in ('full','horizon'):
                s=c[key];assert s['n']==prev[key]['n'] and s['retained_bits']==prev[key]['retained_bits']
                s['retained_saving_bits']=s['baseline_bits']-s['retained_bits']
                s['mixture_saving_bits']=s['baseline_bits']-s['mixture_bits']
                assert s['mixture_bits']<=min(s['baseline_bits'],s['retained_bits'])+1+1e-9
        out.update(validation=dict(entire_capture_trace_exact=True,candidates_match_D85=len(candidates),accepted_labels=len(seen)),
            full=R.summarize(candidates),horizon_100s=R.summarize([r for r in candidates if r['eligible_100s']],'horizon'),
            by_family={f:R.summarize([r for r in candidates if r['family']==f]) for f in ('event','clock','integrator','rhythm')},
            by_churn={str(c):R.summarize([r for r in candidates if r['same_taste_birth']==c]) for c in (False,True)},
            uniform_control=uniform_summary(candidates),uniform_horizon_100s=uniform_summary([r for r in candidates if r['eligible_100s']],'horizon'),
            capture_sha256=digest(BASE.with_suffix('.json')),D85_sha256=digest(ROOT/'lab/v/retained_prediction.pkl'),
            limits=['One reused fixed history; no action, learning or allocation intervention.',
                'All per-candidate sums overlap and do not count distinct brain-level information.',
                'Half prior per separate candidate is not a combined selection prior; winner counts are retrospective.',
                'No ancestor/displacement/material or physical activity costs are paid by this reference.'])
        target.with_suffix('.pkl').write_bytes(pickle.dumps(dict(rows=candidates,unique_tastes=unique,summary=out)))
        print('VALIDATION',out['validation']);print('SUMMARY',json.dumps(out['full']));print('UNIFORM',json.dumps(out['uniform_control']))
    except Exception as e:
        out['failures'].append(repr(e));raise
    finally:
        out['wall_s']=time.monotonic()-started;target.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        print('wall_s',out['wall_s'],flush=True)


if __name__=='__main__':
    assert sys.argv[1:] in (['capture'],['analyse'])
    capture() if sys.argv[1]=='capture' else analyse()
