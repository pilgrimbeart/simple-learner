"""Passive D128 temporal failure classification and resting-trace estimate."""
import json,sys,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,V_TYP,digest
from mixed_feedback import _fade
from units import RAIL
import chip
out=ROOT/'lab/v/motifs/order_v2';rows=[json.loads(l) for l in (out/'confirm.jsonl').read_text().splitlines()];fine=[r for r in rows if r['dt']==DT/4]
fail=[];seeds=sorted({r['seed'] for r in fine});summary=[]
for seed in seeds:
    rr=[r for r in fine if r['seed']==seed];r=rr[0];n=np.array(r['nodes']);e=np.array(r['elements'])
    # Input nodes have zero bias/no incoming links; resting source=0. For the two sigmoid trace builders,
    # rail fade is negligible in the measured low baseline range; record approximation, not a simulation.
    trace=e[0,:2]/n[1,2:4]/(1+np.exp(e[2,:2]*e[1,:2]))
    singles=[x for x in rr if x['case']['id'].startswith('single')]
    summary.append(dict(seed=seed,approx_rest_trace_V=trace.tolist(),approx_rest_gate=np.clip(trace/V_TYP,0,1).tolist(),max_single_order_V=max(abs(x['metrics']['order_V']) for x in singles),
        coincidence_pass=all(x['criteria'].get('coincidence',True) for x in rr),order_pass=all(x['criteria'].get('order',True) for x in rr)))
    for x in rr:
        if not x['passed']:
            case=x['case'];kind='single' if case['a']==0 or case['b']==0 else 'simultaneous' if case['delay']==0 else 'long_separation' if abs(case['delay'])==.6 else 'weak_order'
            fail.append(dict(seed=seed,case=case,kind=kind,metrics=x['metrics']))
# Audit absolute decoder on saved first seed only; do not pretend all traces were recorded.
raw=[]
for p in sorted(out.glob('confirm_pair_*_False.npz')):
    caseid=p.name[len('confirm_'):-len('_False.npz')];r=next(r for r in fine if r['seed']==seeds[0] and r['case']['id']==caseid);d=r['case']['delay']
    if abs(d) not in (.06,.15):continue
    tr=np.load(p)['trace'];t=tr[:,0];last=max(q[0] for q in r['pulses']);value=float(tr[(t>last+.02)&(t<last+.10),8].mean())
    raw.append(dict(case=caseid,mean_raw_order_V=value,baseline_relative_order_V=r['metrics']['order_V'],raw_sign_correct=bool(np.sign(d)*value>0)))
# Algebraic resting baseline of the acyclic graph; no circuit simulation or fitted readout.
absolute=[]
for seed in seeds:
    rr=[r for r in fine if r['seed']==seed];r=rr[0];n=np.array(r['nodes']);e=np.array(r['elements']);link=np.array(r['links']);v=np.zeros(8)
    for dest in range(8):
        def current(y):
            total=-n[1,dest]*y
            for ix in range(e.shape[1]):
                if link[0,ix]!=dest:continue
                source,gate=link[1:,ix];assert source<dest and (gate<0 or gate<dest)
                gain,offset,slope,tau,sig=e[:,ix];assert tau==0
                f=1/(1+np.exp(-slope*(v[source]-offset))) if sig else np.tanh(slope*(v[source]-offset))
                g=np.clip(v[gate]/V_TYP,0,1) if gate>=0 else 1
                if sig:total+=gain*f*g*(_fade(RAIL-y,chip.KNEE_P) if gain>0 else _fade(y+RAIL,chip.KNEE_N))
                else:
                    full=abs(gain)*g;w=np.sign(gain)*f
                    total+=full*((1+w)*_fade(RAIL-y,chip.KNEE_P)-(1-w)*_fade(y+RAIL,chip.KNEE_N))/2
            return total
        lo,hi=-RAIL,RAIL
        for _ in range(70):
            mid=(lo+hi)/2
            if current(mid)>0:lo=mid
            else:hi=mid
        v[dest]=(lo+hi)/2
    scored=[r for r in rr if abs(r['case']['delay']) in (.06,.15)]
    absolute.append(dict(seed=seed,rest_order_V=float(v[7]),cases=len(scored),estimated_raw_sign_correct=int(sum(np.sign(r['case']['delay'])*(r['metrics']['order_V']+v[7])>0 for r in scored))))
result=dict(source_sha256=digest(__file__),input_sha256=digest(out/'confirm.jsonl'),cases=len(fine),failure_classes=dict(collections.Counter(x['kind'] for x in fail)),failures=fail,by_seed=summary,
    coincidence_seeds_passing=sum(x['coincidence_pass'] for x in summary),order_seeds_passing=sum(x['order_pass'] for x in summary),raw_readout_audit_first_seed=raw,approximate_absolute_readout_by_seed=absolute,
    limits='Resting trace estimate omits exponentially tiny rail fade; not a fitted causal decomposition. Failure classification is exact against frozen metrics. Absolute decoder audit covers saved first seed only.')
(out/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('by_seed','failures','raw_readout_audit_first_seed','approximate_absolute_readout_by_seed')},indent=2));print('raw zero-threshold signs',sum(x['raw_sign_correct'] for x in raw),'/',len(raw));print('largest resting gate',max(max(x['approx_rest_gate']) for x in summary))

print('Algebraic-baseline estimated raw signs',sum(x['estimated_raw_sign_correct'] for x in absolute),'/',sum(x['cases'] for x in absolute))
