"""Independent arithmetic checks and observer overhead accounting for completed L capture."""
from pathlib import Path
import pickle,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'lab/v'
rows=pickle.loads((V/'gate_contribution_capture.pkl').read_bytes());reported=json.loads((V/'gate_contribution_capture.json').read_text())
out={'success':False,'per_life':[]};maxerr=0.
for r in rows:
 c=r['capture'];units=c['units'];expected=next(x for x in reported['lives'] if (x['cond'],x['arm'],x['first'])==(r['cond'],r['arm'],r['first']))
 vals=[]
 for x in c['rows']:
  aw=np.isfinite(x['q']);weights=np.r_[x['wd'],x['w'][aw]];probs=np.r_[x['pd'],x['q'][aw]]
  p=float(np.dot(weights,probs)/weights.sum());maxerr=max(maxerr,abs(p-x['p']))
  qq=x['q'].copy()
  for j,k in enumerate(x['ids']):
   u=units.get((j,k))
   if aw[j] and u:
    assert u['born']<=x['t']+1e-9
    assert u['removed'] is None or u['removed']>=x['t']-1e-9
    if u['same_call']:qq[j]=x['pd']
  pp=float(np.dot(weights,np.r_[x['pd'],qq[aw]])/weights.sum())
  vals.append(float(np.log2((p if x['y'] else 1-p)/(pp if x['y'] else 1-pp))))
 assert abs(sum(vals)-expected['windows']['same_call full']['bits_total'])<1e-9
 if r['arm']=='issued':assert all(v==0 for v in vals)
 act=c['activity'];native=act.get('native_donor_list_traversals',0);adapter=act.get('adapter_donor_list_traversals',0)
 transfers=sum(e['kind']=='transfer' for e in c['events'])
 # Exact counts derived from the observer loops in frozen capture source; not fed back.
 out['per_life'].append(dict(condition=r['cond'],arm=r['arm'],first=r['first'],native_donor_list_traversals=native,adapter_donor_list_traversals=adapter,adapter_invariant_traversals=act.get('adapter_invariant_allowance_traversals',0),observer_pre_request_snapshot_traversals=native,observer_post_transfer_donor_traversals=transfers,observer_issued_weight_snapshots=len(r['trace_pred']),actual_final_units=r['final_units'],peak_units=r['alloc']['peak'],conditional_forecast_gain_total=sum(vals)))
assert maxerr<1e-9
out.update(success=True,max_mixture_error=maxerr,note='Conditional forecast substitution gain only; no causal control claim. Loop counts are software traversals, not physical communication.',raw_sha256=hashlib.sha256((V/'gate_contribution_capture.pkl').read_bytes()).hexdigest())
(V/'gate_contribution_review.json').write_text(json.dumps(out,indent=2)+'\n');print('Independent mixture arithmetic, born/removed timing and baseline controls passed; max error',maxerr)
