"""D112 offline review: preserve all E-G outputs; no new lives."""
import hashlib,json,pickle,subprocess,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'lab'),str(ROOT)]
BASE=ROOT/'lab/v/gate_test_review'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(n):return json.loads((ROOT/'lab/v'/f'{n}.json').read_text())
def main():
 t0=time.monotonic();out={'success':False}
 try:
  out['hashes']={}
  for n in ('initial_prior_replay','market_transfer_cases'):
   out['hashes'][n]={p:sha(ROOT/p)==h for p,h in js(n)['provenance']['sha256'].items()};assert all(out['hashes'][n].values())
  capture=js('market_ledger_capture_capture');raw=Path(capture['raw']);assert sha(raw)==capture['raw_sha256']
  out['capture_source_hashes']={p:sha(ROOT/p)==h for p,h in capture['provenance']['sha256'].items()}
  assert sha(ROOT/'lab/market_ledger_capture.py')==js('market_ledger_capture')['analysis_sha256']
  lives=pickle.loads(raw.read_bytes());by={}
  for l in lives:
   key=(l['rule'],l['seed'],l['first'],l['observe']);assert key not in by;by[key]=l
  assert len(by)==8
  out['ledger']={}
  for rule in ('M','none'):
   for colour in ('red','blue'):
    a,b=by[rule,142000,colour,False],by[rule,142000,colour,True]
    assert a['fingerprint']==b['fingerprint'] and a['result']==b['result']
    req=b['requests'];g=[r for r in req if not r['under'] and (rule!='M' or r['due'])]
    passed=[r for r in g if r['saved']>r['price']]
    blocked=[r for r in passed if r['candidates'] and not r['ok']]
    assert all(r['pred_leaves']==0 and r['pred_spare']>0 for r in blocked)
    plus=sum(r['saved']<=r['price']<r['issued_balance'] for r in g)
    minus=sum(r['issued_balance']<=r['price']<r['saved'] for r in g)
    saved=js('market_ledger_capture')['lives'][f'{rule} {colour}']
    assert len(blocked)==saved['leafless_refusals'] and plus==saved['issued_would_pass'] and minus==saved['issued_would_fail']
    out['ledger'][f'{rule} {colour}']=dict(requests=len(req),gate_reached=len(g),historical_price_passes=len(passed),spare_leafless_refusals=len(blocked),distinct_refusal_streams=len({r['j'] for r in blocked}),distinct_refusal_times=len({r['t'] for r in blocked}),credit_flips_to_pass=plus,credit_flips_to_fail=minus,fail_flips_fraction_of_historical_passes=minus/len(passed),already_successful_spare_and_leaf=sum(r.get('pred_spare',0)>0 and r.get('pred_leaves',0)>0 and r['ok'] for r in passed))
  import market_transfer_cases as F
  cases=F.run_cases();assert json.loads(json.dumps(cases,default=str))==js('market_transfer_cases')['cases'];out['fixture_cases_reproduced']=len(cases)
  import initial_prior_replay as E
  prior=js('initial_prior_replay');out['prior_replay']={}
  for filename,arm in [('contest_prediction.pkl','R'),('ruler_ingredients.pkl','R+1')]:
   raw0=pickle.loads((ROOT/'lab/v'/filename).read_bytes());ls=raw0['lives'] if isinstance(raw0,dict) else raw0
   dd={}
   for l in ls:
    if l.get('name')!=arm:continue
    k=(l['seed'],l['first']);assert k not in dd
    rows=l['rows'];p0=np.array(E.issued_replay(rows,'baseline'));p1=np.array(E.issued_replay(rows,'alternative'));y=np.array([r['letter'] for r in rows]);mask=np.array([r['taste_t']<100 for r in rows]);assert np.max(abs(p0-np.array([r['p1'] for r in rows])))<1e-9
    errs=lambda p:np.where(p==.5,.5,(p>.5)!=y)
    dd[k]=float((errs(p1)-errs(p0))[mask].mean())
   assert len(dd)==20
   val=E.boot(dd,sorted({s for s,c in dd}));assert np.allclose(val['ci95'],prior['summary'][f'{arm} | first_third | alternative - baseline delta_errors']['ci95']);out['prior_replay'][arm]=val
  out['success']=True
 finally:
  out['provenance']=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),script_sha256=sha(__file__),input_sha256={str(p):sha(p) for p in [ROOT/'lab/v'/n for n in ('market_ledger_capture.pkl','market_transfer_cases.json','initial_prior_replay.json','contest_prediction.pkl','ruler_ingredients.pkl')]},command='timeout 240s env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python lab/gate_test_review.py')
  out['wall_s']=time.monotonic()-t0;BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
