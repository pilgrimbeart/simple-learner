"""D157 continuous-baseline reference on isolated histories, not a built learner."""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from order_local_calibration import trajectory
from population_trace_margin import convolution,SRC
from order_balance_information import bounds
from dynamic_parts_bench import ROOT,digest,provenance
from units import V_TYP,MISMATCH,TAU_MAX
OUT=ROOT/'lab/v/order_continuous_baseline'
TAUS=[.15,1.,TAU_MAX]
def lowpass(x,tau,dt,initial):
    a=math.exp(-dt/tau);out=np.empty(len(x));out[0]=initial
    out[1:]=convolution((1-a)*(x[:-1]+x[1:])/2,a,initial)
    return out

def observe(row,dt):
    t,v=trajectory(row,.15,dt);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=trajectory(p,.15,dt);u=v[7];der=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1)
    integ=lambda a:float(np.sum((a[:-1]+a[1:])*.5)*dt)
    quiet=(t>.7)&(t<.95);start=np.random.default_rng([row['seed'],157]).uniform(-.075,.075)
    result={}
    for tau in TAUS:
        for kind,iu,iv in [('random',start,0.),('informed',float(u[quiet].mean()),float(der[quiet].mean()))]:
            a=u-lowpass(u,tau,dt,iu);b=der-lowpass(der,tau,dt,iv)
            result[f'{tau}:{kind}']=[integ(w*a),integ(w*b)]
    return result,[integ(w*u),integ(w*der)],integ(w)

def main():
    OUT.mkdir(exist_ok=True);protocol=dict(taus_s=TAUS,initialisations=['random','informed'],readout_errors_V=[-MISMATCH*V_TYP,0.,MISMATCH*V_TYP],positive_near_priors=[.5,.8],source=str(SRC),budget_s=180,scope='Isolated-history linear reference with explicit startup/error probes; no noisy-circuit or learning claim')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    raw=[json.loads(l) for l in SRC.read_text().splitlines()];dt=min(r['dt'] for r in raw);raw=[r for r in raw if r['dt']==dt and not r['control']];assert len(raw)==1360
    source=ROOT/'lab/v/order_local_calibration/observations.json';old=json.loads(source.read_text());lookup={(r['seed'],r['case']['id']):r for r in old}
    records=[];err=refine=0.;start=time.monotonic()
    for row in raw:
        stats,base,w=observe(row,.00005);r=lookup[row['seed'],row['case']['id']]
        err=max(err,max(abs(a-b) for a,b in zip(base,r['observations_Vs']['raw'])))
        if row['seed']==raw[0]['seed']:
            fine,_,_=observe(row,.000025);refine=max(refine,max(abs(stats[k][j]-fine[k][j]) for k in stats for j in [0,1]))
        records.append(dict(seed=row['seed'],case=row['case'],u_V=r['u_V'],v_V=r['v_V'],coincidence_adequate=r['coincidence_adequate'],observations_Vs=stats,weight_s=w))
        if time.monotonic()-start>180:raise RuntimeError('Budget exceeded')
    assert err<1e-12
    draws=[];summaries={}
    for tau in TAUS:
      for kind in ['random','informed']:
       for offset in protocol['readout_errors_V']:
        for prior in [.5,.8]:
          tag=f'{tau}:{kind}:{offset}:{prior}';group=[]
          for seed in sorted({r['seed'] for r in records}):
            rr=[r for r in records if r['seed']==seed];numer=denom=0.
            for r in rr:
                c=r['case'];near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
                weight=(2*prior if c['delay']>0 else 2*(1-prior)) if near else 1.
                a,b=r['observations_Vs'][f'{tau}:{kind}'];numer+=weight*(a-offset*r['weight_s']);denom+=weight*b
            assert abs(denom)>1e-12
            raw_d=-numer/denom;d=float(np.clip(raw_d,-1,1));passes=[];rescued=harmed=0
            for r in rr:
                lo,hi=bounds(r['case']);ok=lo<r['u_V']+d*r['v_V']<hi and r['coincidence_adequate'];base=lo<r['u_V']<hi and r['coincidence_adequate'];passes.append(ok);rescued+=ok and not base;harmed+=base and not ok
            item=dict(mode=tag,seed=seed,d=d,raw_d=raw_d,positive_denominator=denom>0,passed=sum(passes),all_pass=all(passes),rescued=rescued,harmed=harmed);group.append(item);draws.append(item)
          summaries[tag]=dict(adequate_draws=sum(r['all_pass'] for r in group),adequate_cases=sum(r['passed'] for r in group),rescued=sum(r['rescued'] for r in group),harmed=sum(r['harmed'] for r in group),clamped=sum(abs(r['raw_d'])>1 for r in group))
    result=dict(raw_integral_reconstruction_max_Vs=err,first_draw_refinement_max_Vs=refine,comparisons=summaries)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,source,ROOT/'lab/order_local_calibration.py',ROOT/'lab/order_balance_information.py',ROOT/'lab/population_trace_margin.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('observations',records),('draws',draws)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
