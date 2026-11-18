"""D103 read-only review of D88-D102 saved artifacts. No simulation or old output writes."""
import gc
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
BASE=ROOT/'lab/v/agent_work_review'


def read(name):return pickle.loads((ROOT/f'lab/v/{name}.pkl').read_bytes())
def js(name):return json.loads((ROOT/f'lab/v/{name}.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ci(a):return dict(median=float(np.median(a)),ci95=np.quantile(a,[.025,.975]).tolist())
def loss(p,y):return -np.log2(np.clip(np.where(y,p,1-p),1e-12,1-1e-12))


def gap_samples(lives,refs,names,seeds):
    by={(r['name'],r['seed'],r['first']):r for r in lives}
    ids=np.random.default_rng(0).integers(0,len(seeds),(2000,len(seeds)))
    idx=np.concatenate((2*ids,2*ids+1),axis=1)
    order=[(s,c) for s in seeds for c in ('red','blue')]
    def eff(rows):
        a=np.array([[r[2],r[3]] for r in rows]);return a[idx,0].sum(1)/a[idx,1].sum(1)
    b=eff([refs['circuit',s,c] for s,c in order]);t=eff([refs['vtold',s,c] for s,c in order])
    return {n:(eff([by[n,s,c]['result'] for s,c in order])-b)/(t-b) for n in names}


def forecast_audit(lives,start):
    out={};all_inc=[];maxerr=0
    for name in sorted({r['name'] for r in lives}):
        rows_for_name=[r for r in lives if r['name']==name];native=[];full_best=[];window_best=[];n=[];spans=[]
        for r in rows_for_name:
            rows=r['rows'];y=np.array([z['letter'] for z in rows]);p=np.array([z['p1'] for z in rows])
            mask=np.array([z['taste_t']>=start for z in rows]);pd=np.array([z['pd'] for z in rows]);q=np.stack([z['q'] for z in rows]);w=np.stack([z['w'] for z in rows]);wd=np.array([z['wd'] for z in rows])
            awake=np.isfinite(q);re=(wd*pd+np.sum(w*np.where(awake,q,0),axis=1))/(wd+np.sum(w*awake,axis=1))
            maxerr=max(maxerr,float(abs(re-p).max()));assert maxerr<1e-12
            assert all(z['t']<=z['taste_t']+1e-10 for z in rows)
            completed=np.where(awake,q,pd[:,None]);ls=loss(completed,y[:,None])
            j=ls.sum(0).argmin();k=ls[mask].sum(0).argmin()
            native.append(float(loss(p[mask],y[mask]).sum()));full_best.append(float(ls[mask,j].sum()));window_best.append(float(ls[mask,k].sum()));n.append(int(mask.sum()))
            ev=np.array(r['fam'])=='event';sp=np.stack([z['span'] for z in rows])
            spans.append((sp[:,ev][awake[:,ev]].sum(),awake[:,ev].sum(),sp[mask][:,ev][awake[mask][:,ev]].sum(),awake[mask][:,ev].sum()))
            inc=np.log2(np.where(y[:,None],q,1-q)/np.where(y,pd,1-pd)[:,None]);all_inc.extend(inc[awake].tolist())
        sp=np.sum(spans,axis=0)
        out[name]=dict(lives=len(rows_for_name),accepted_in_window=sum(n),native=sum(native)/sum(n),full_selected_single_in_window=sum(full_best)/sum(n),window_selected_single=sum(window_best)/sum(n),event_span_full=float(sp[0]/sp[1]) if sp[1] else None,event_span_window=float(sp[2]/sp[3]) if sp[3] else None)
    return dict(per_arm=out,max_mixture_error=maxerr,issued_saving_increment=dict(n=len(all_inc),over_one_bit=sum(x>1 for x in all_inc),maximum=max(all_inc)))


def main():
    start=time.monotonic();out=dict(success=False,checks={},findings={})
    try:
        hashes={}
        for name in ('growth_parent_census','growth_child_prediction','growth_missing_partner','followup_fresh','followup_silent','followup_timing'):
            x=js(name);p=x.get('provenance',x)
            h={**p.get('source_sha256',{}),**p.get('input_sha256',{})}
            hashes[name]={f:digest(ROOT/f)==v for f,v in h.items()}
            assert all(hashes[name].values()),name
        out['checks']['recorded_hashes_match']=hashes
        import growth_parent_census as G
        raw=G.load_raw();c=G.Census();r=G.Replay(raw,c).run()
        saved=read('growth_parent_census')['rows'];assert c.rows==saved
        out['checks']['parent_rows_exact']=len(c.rows);out['checks']['native_replay']=dict(r.checks)
        del raw,c,r,saved;gc.collect()
        fresh=read('followup_fresh');refs={(r['rule'],r['seed'],r['first']):r['result'] for r in js('alloc_curve')['lives'] if r['rule'] in ('circuit','vtold')}
        x=gap_samples(fresh,refs,('low','high','R+M+1'),range(176000,176010))
        out['findings']['fresh_gap']={k:ci(x[a]-x[b]) for k,a,b in [('high - low','high','low'),('R+M+1 - high','R+M+1','high')]}
        for k,v in out['findings']['fresh_gap'].items():assert np.allclose(v['ci95'],js('followup_fresh')['differences'][k]['ci95'],atol=1e-12)
        out['findings']['fresh_forecasts']=forecast_audit(fresh,200.)
        out['findings']['fresh_final_units']={a:float(np.mean([2042+sum(l['grown'].values()) for l in fresh if l['name']==a])) for a in ('low','high','R+M+1')}
        del fresh;gc.collect()
        original=read('room_prediction');out['findings']['original_forecasts']=forecast_audit(original['lives'],200.)
        del original;gc.collect()
        timing=read('followup_timing');out['findings']['timing_forecasts']=forecast_audit(timing,2000.)
        out['findings']['timing_reported_prediction_interval']=js('followup_timing')['differences']['bits native']
        del timing;gc.collect()
        silent=read('followup_silent');by={(r['name'],r['seed'],r['first']):r for r in silent};same=0
        for seed in range(142000,142010):
            for first in ('red','blue'):
                a,b=by['R silent',seed,first],by['R+1 silent',seed,first]
                # Diagnostic counters (index 6) differ: compare behaviour and loss only.
                assert a['result'][:6]==b['result'][:6]
                assert a['result'][7:]==b['result'][7:]
                assert len(a['rows'])==len(b['rows'])
                for aa,bb in zip(a['rows'],b['rows']):
                    for k in aa:assert np.array_equal(aa[k],bb[k],equal_nan=True),(seed,first,k)
                same+=1
        out['checks']['silent_behaviour_and_forecast_pairs_exact']=same
        out['findings']['saving_example_bits']=math.log2(.75/.1)
        out['findings']['scope_limits']=['Source/record and targeted numerical audit, not a new simulation replication.',
            'D93-D102 native historical credit differs from D82 corrected contract.',
            'Best single is a restricted hindsight comparator, not an oracle over all combiners.',
            'Loss savings relative to a default can exceed one bit per binary label.',
            'Followup scripts record result mismatches but do not assert empty lists before summarising; saved current lists are empty.',
            'D93 speaker spans in combiners are full-life despite the notebook table last-third label.']
        out['success']=True
    finally:
        out['provenance']=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=digest(__file__),input_sha256={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/f'lab/v/{n}.pkl' for n in ('room_prediction','followup_fresh','followup_silent','followup_timing','growth_parent_census','future_evidence')]},command='timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/agent_work_review.py')
        out['wall_s']=time.monotonic()-start;BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
