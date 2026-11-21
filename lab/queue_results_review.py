"""D108: read-only targeted audit of D104-D107; no simulations or old output writes."""
from pathlib import Path
import hashlib,json,pickle,sys,time,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
import selection_share_audit as S
import selection_share_extension as X
BASE=ROOT/'lab/v/queue_results_review'
def read(n):return pickle.loads((ROOT/'lab/v'/n).read_bytes())
def js(n):return json.loads((ROOT/'lab/v'/n).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def boot(vals,seeds):
 a=np.array([vals[s,c] for s in seeds for c in ('red','blue')]);i=np.random.default_rng(0).integers(0,len(seeds),(2000,len(seeds)));ix=np.concatenate((2*i,2*i+1),axis=1)
 return dict(mean=float(a.mean()),ci95=np.quantile(a[ix].mean(1),[.025,.975]).tolist())
def main():
 start=time.monotonic();out=dict(success=False)
 try:
  hashes={}
  for name in ('forecast_window_audit','market_currency_audit','selection_share_audit','selection_share_extension'):
   p=js(name+'.json')['provenance'];h=p.get('sha256',p.get('inputs',{}));hashes[name]={f:sha(ROOT/f)==v for f,v in h.items()}
   if 'script_sha256' in p:hashes[name]['script']=sha(ROOT/'lab'/f'{name}.py')==p['script_sha256']
  out['hashes']=hashes
  # Record post-analysis script edits as provenance limitations rather than hiding them.
  forecast=js('forecast_window_audit.json')['results'];out['forecast_checks']={};out['first_weights']={};out['exact_subset_collisions']={};out['corrected_small_brain_share']={}
  for name,path in S.SETS.items():
   raw=read(Path(path).name);lives=raw['lives'] if isinstance(raw,dict) else raw
   T=3000. if 'timing' in name else 300.;a,b=('design2240','design560') if T==3000 else ('high','low')
   M={};initial={};seen={};collisions=[]
   for l in lives:
    rows=l['rows'];p=np.array([r['p1'] for r in rows]);y=np.array([r['letter'] for r in rows]);m=np.array([r['taste_t']>=2*T/3 for r in rows])
    initial.setdefault(l['name'],[]).append(bool(rows[0]['wd']==1 and np.all(rows[0]['w']==1)))
    M[l['name'],l['seed'],l['first']]=(float(np.mean(-np.log2(np.clip(np.where(y,p,1-p)[m],1e-12,1-1e-12)))),float(np.mean(np.where(p[m]==.5,.5,(p[m]>.5)!=y[m]))))
    if all(t['exact'] for t in S.replay_check(rows)):
     k=(l['seed'],l['first'])
     if k in seen:collisions.append(dict(seed=k[0],first=k[1],overwritten=seen[k],replacement=l['name']))
     seen[k]=l['name']
   seeds=sorted({s for _,s,_ in M});r={}
   saved=next(v for k,v in forecast.items() if k.startswith(name))
   for j,metric in enumerate(('bits','errors')):
    v=boot({(s,c):M[a,s,c][j]-M[b,s,c][j] for s in seeds for c in ('red','blue')},seeds)
    target=saved['paired'][f'last_third | native | {metric} per taste'];assert np.allclose(v['ci95'],target['ci95'],atol=1e-12)
    r[metric]=v
   per={};maxerr=0.
   for l in lives:
    if l['name']!=b:continue
    rows=l['rows'];p1=np.array(S.replay_probs(rows,.01));p0=np.array(S.replay_probs(rows,0.));y=np.array([r['letter'] for r in rows]);ts=np.array([r['taste_t'] for r in rows])
    maxerr=max(maxerr,float(np.max(abs(p1-np.array([r['p1'] for r in rows])))))
    d=-np.log2(np.clip(np.where(y,p0,1-p0),1e-12,1-1e-12))+np.log2(np.clip(np.where(y,p1,1-p1),1e-12,1-1e-12))
    per[l['seed'],l['first']]={w:float(d[(ts>=lo)&(ts<hi)].mean()) for w,lo,hi in [('full',0,T+1),('first_third',0,T/3),('last_third',2*T/3,T+1)]}
   assert maxerr<1e-9 and len(per)==20
   out['corrected_small_brain_share'][name]=dict(arm=b,lives=len(per),max_native_error=maxerr,windows={w:boot({k:v[w] for k,v in per.items()},seeds) for w in ('full','first_third','last_third')},maximum_absolute_life_window_effect=max(abs(x) for v in per.values() for x in v.values()))
   out['forecast_checks'][name]=r;out['first_weights'][name]={k:dict(lives=len(v),all_one=sum(v)) for k,v in initial.items()};out['exact_subset_collisions'][name]=collisions
   del raw,lives
  out['d100']=X.d100_lives();assert out['d100']==js('selection_share_extension.json')['d100']
  out['d79']=X.d79_replay();assert out['d79']==js('selection_share_extension.json')['d79_large_brain']
  m=js('market_diagnosis.json')['requests']['event'];full=sum(v for k,v in m.items() if k.startswith('full'))
  out['market_event']=dict(full_requests=full,savings_fail=m['full, savings test fails']/full,leafless_fraction=1-m['transfers']/m['full, transfer attempted'])
  out['success']=True
 finally:
  out['provenance']=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),inputs={p:sha(ROOT/p) for p in [*S.SETS.values(),'lab/v/active_mixture_audit.pkl','lab/v/contest_prediction.pkl','lab/v/ruler_ingredients.pkl','lab/v/followup_silent.pkl','lab/v/market_diagnosis.json']},command='timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/queue_results_review.py')
  out['wall_s']=time.monotonic()-start;BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
