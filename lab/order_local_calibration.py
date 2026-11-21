"""D156 instrumented D139 quadrature; no circuit simulation or free baseline claim."""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from population_trace_margin import convolution,SRC
from dynamic_parts_bench import ROOT,digest,provenance
from units import V_TYP
from order_balance_information import bounds
OUT=ROOT/'lab/v/order_local_calibration'
def trajectory(row, threshold, dt):
    n=np.array(row['nodes']);e=np.array(row['elements']); t=np.arange(round(2.5/dt)+1)*dt
    starts=np.random.default_rng([row['seed'],128,4]).uniform(-.075,.075,8)
    v=np.empty((8,len(t)))
    for i in [0,1]:
        tau=n[2,i]/n[1,i];v[i]=starts[i]*np.exp(-t/tau)
        for at,duration,node,current in row['pulses']:
            if node==i:
                on=np.maximum(t-at,0);off=np.maximum(t-at-duration,0)
                v[i]+=current/n[1,i]*(np.exp(-off/tau)-np.exp(-on/tau))
    e[1,:2]+=threshold-.15
    for dest in range(2,8):
        current=np.zeros(len(t))
        for j in range(e.shape[1]):
            to,source,gate=np.array(row['links'])[:,j]
            if to!=dest:continue
            x=e[2,j]*(v[source]-e[1,j]);f=1/(1+np.exp(-x)) if e[4,j]>.5 else np.tanh(x)
            if gate>=0:f=f*np.clip(v[gate]/V_TYP,0,1)
            current+=e[0,j]*f
        a=math.exp(-dt*n[1,dest]/n[2,dest]);forcing=(1-a)/n[1,dest]*(current[1:]+current[:-1])/2
        v[dest,0]=starts[dest];v[dest,1:]=convolution(forcing,a,starts[dest])
    return t,v

def observations(row,dt):
    t,v=trajectory(row,.15,dt);positive=copy.deepcopy(row);positive['elements'][0][6]=0.
    _,pv=trajectory(positive,.15,dt)
    u=v[7];sensitivity=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1)
    baseline=(t>.7)&(t<.95)
    # Trapezoidal quadrature; discrete times denote numerical integration only.
    integral=lambda a:float(np.sum((a[:-1]+a[1:])*.5)*dt)
    stats={}
    for name,a,b in [('raw',u,sensitivity),('baseline_reference',u-u[baseline].mean(),sensitivity-sensitivity[baseline].mean())]:
        stats[name]=[integral(w*a),integral(w*b)]
    sample=np.arange(0,len(t),round(.001/dt));tt=t[sample]
    first=1+np.random.default_rng([row['seed'],128,5]).uniform(.001,.009);last=first+abs(row['case']['delay'])
    mask=(tt>last+.02)&(tt<last+.10);base=(tt>.7)&(tt<.95)
    metrics=[float(a[sample][mask].mean()-a[sample][base].mean()) for a in [u,sensitivity]]
    return stats,metrics

def main():
    OUT.mkdir(exist_ok=True);protocol=dict(source=str(SRC),gate='clip(raw coincidence/V_TYP,0,1)',integration_duration_s=2.5,steps_s=[.00005,.000025],references=['raw','baseline_reference'],positive_near_priors=[.5,.8],budget_s=180,scope='Stationary weighted-mean equilibrium reference, no constructed learner')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    raw=[json.loads(l) for l in SRC.read_text().splitlines()];dt=min(r['dt'] for r in raw);raw=[r for r in raw if r['dt']==dt and not r['control']];assert len(raw)==1360
    prior=ROOT/'lab/v/order_balance_information/branches.json';branches=json.loads(prior.read_text());lookup={(r['seed'],r['case']['id']):r for r in branches}
    records=[];error=refine=0.;start=time.monotonic()
    for row in raw:
        stats,metrics=observations(row,.00005);old=lookup[row['seed'],row['case']['id']]
        error=max(error,abs(metrics[0]-old['u_V']),abs(metrics[1]-old['v_V']))
        if row['seed']==raw[0]['seed']:
            fine,_=observations(row,.000025);refine=max(refine,max(abs(stats[k][j]-fine[k][j]) for k in stats for j in [0,1]))
        records.append(dict(**old,observations_Vs=stats))
        if time.monotonic()-start>180:raise RuntimeError('Budget exhausted; incomplete analysis')
    assert error<1e-12
    scored=[];draws=[];summary={}
    for mode in protocol['references']:
        for prior_positive in [.5,.8]:
            tag=f'{mode}_{prior_positive}';group=[]
            for seed in sorted({r['seed'] for r in records}):
                rr=[r for r in records if r['seed']==seed];numer=denom=0.
                for r in rr:
                    c=r['case'];near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
                    weight=(2*prior_positive if c['delay']>0 else 2*(1-prior_positive)) if near else 1.
                    a,b=r['observations_Vs'][mode];numer+=weight*a;denom+=weight*b
                assert abs(denom)>1e-12
                raw_d=-numer/denom;d=float(np.clip(raw_d,-1,1));good=[];rescued=harmed=0;failures={}
                for r in rr:
                    c=r['case'];lo,hi=bounds(c);y=r['u_V']+d*r['v_V'];ok=bool(lo<y<hi and r['coincidence_adequate']);base=bool(lo<r['u_V']<hi and r['coincidence_adequate']);good.append(ok);rescued+=ok and not base;harmed+=base and not ok
                    kind='single' if not(c['a'] and c['b']) else 'simultaneous' if not c['delay'] else 'far' if abs(c['delay'])>.15 else 'near'
                    if not ok:failures[kind]=failures.get(kind,0)+1
                    scored.append(dict(mode=tag,seed=seed,case=c,output_V=y,passed=ok))
                item=dict(mode=tag,seed=seed,d=d,raw_d=raw_d,denominator_Vs=denom,passed=sum(good),all_pass=all(good),rescued=rescued,harmed=harmed,failures=failures);group.append(item);draws.append(item)
            summary[tag]=dict(adequate_draws=sum(r['all_pass'] for r in group),adequate_cases=sum(r['passed'] for r in group),rescued=sum(r['rescued'] for r in group),harmed=sum(r['harmed'] for r in group),clamped=sum(abs(r['raw_d'])>1 for r in group),nonpositive_denominators=sum(r['denominator_Vs']<=0 for r in group),knob_range=[min(r['d'] for r in group),max(r['d'] for r in group)])
    result=dict(metric_reconstruction_error_V=error,first_draw_integral_refinement_max_Vs=refine,comparisons=summary)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,prior,ROOT/'lab/population_trace_margin.py',ROOT/'lab/order_balance_information.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('observations',records),('draws',draws),('rows',scored)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
