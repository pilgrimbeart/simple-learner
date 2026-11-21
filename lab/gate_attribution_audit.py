"""K: bounded offline attribution audit; no lives."""
from pathlib import Path
import json,pickle,hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'lab/v/gate_attribution_audit'
def checks():
 q=np.array([.9,.1]);w=np.array([.99,.001]);p=.5+w*(q-.5)
 assert np.log2(q/.5).sum()<0<np.log2(p/.5).sum()
 assert .5+0*(.9-.5)==.5
 # Product likelihoods cancel standalone, but different weights break cancellation.
 q=np.array([.8,.3125]);assert abs(np.log2(q/.5).sum())<1e-12
 assert abs(np.log2((.5+np.array([.9,.01])*(q-.5))/.5).sum())>.1
 return ['signed standalone savings do not bound weighted gain','zero weight has zero effect','cancelling standalone gains need not cancel in mixture']
def main():
 out=dict(checks=checks());path=ROOT/'lab/v/spare_allowance_survival.pkl';raw=pickle.loads(path.read_bytes())
 keys={(r['cond'],r['seed'],r['first']) for r in raw};assert keys=={(c,s,f) for c in ('seq','time') for s in range(142000,142010) for f in ('red','blue')}
 rows=[]
 for r in raw:
  us=[u for u in r['units'] if u['cause']=='allowance-only transfer'];c=r['gate']['counters'];T=300 if r['cond']=='seq' else 3000
  rows.append(dict(condition=r['cond'],seed=r['seed'],first=r['first'],latest_transfer_births=len(us),pending_births=c.get('births_after_allowance_only_transfer',0),transfers=c['allowance-only transfers'],positive=sum(max(0,u['bits']) for u in us),negative=sum(min(0,u['bits']) for u in us),censored=sum(u['alive_at_end'] for u in us),family={f:sum(u['family']==f for u in us) for f in ('event','clock','integrator','rhythm')},birth_third=[sum(min(2,int(u['born']/(T/3)))==i for u in us) for i in range(3)],first_speaking_third=[sum(u['first_spoke'] is not None and min(2,int(u['first_spoke']/(T/3)))==i for u in us) for i in range(3)],duration_lower_median=float(np.median([u['seen']-u['born'] for u in us])),duration_upper_or_censor_median=float(np.median([(u['gone'] if u['gone'] is not None else T)-u['born'] for u in us]))))
 out.update(success=True,lives=40,per_life=rows,mismatches=[r for r in rows if r['latest_transfer_births']!=r['pending_births']],missing=['issued per-stream weights and forecasts at each scored taste','exact transfer/birth/removal chronology','last speaking time','exact death time; seen/gone are observation bounds'],decision='L required for weighted conditional contribution; aggregate totals cannot reconstruct it',raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 assert len(out['mismatches'])==10
 BASE.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print('K passed: 40 lives, 10 attribution mismatches; weighted event data absent.')
if __name__=='__main__':
 if '--check' in sys.argv:print(checks())
 else:main()
