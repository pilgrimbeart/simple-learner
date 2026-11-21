"""D158 continuous event-stream feedforward reference; no circuit-learning claim."""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from population_trace_margin import convolution,SRC
from order_continuous_baseline import lowpass,TAUS
from order_balance_information import bounds
from order_bench import cases
from dynamic_parts_bench import ROOT,CAP,digest,provenance
from units import V_TYP
OUT=ROOT/'lab/v/order_baseline_stream'
def stream_trajectory(row, threshold, dt, duration):
    n=np.array(row['nodes']);e=np.array(row['elements']); t=np.arange(round(duration/dt)+1)*dt
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

def make_stream(row,spacing,index):
    rng=np.random.default_rng([row['seed'],158,index]);cc=cases();weights=[]
    for c in cc:
        near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
        weights.append((1.6 if c['delay']>0 else .4) if near else 1.)
    prob=np.array(weights)/sum(weights);events=[];pulses=[];at=rng.uniform(0,spacing)
    while at<99.36:
        c=cc[rng.choice(len(cc),p=prob)];events.append(dict(first_s=float(at),case=c))
        for node,amp,t0 in [(0,c['a'],at+max(-c['delay'],0)),(1,c['b'],at+max(c['delay'],0))]:
            if amp:pulses.append([float(t0),.04,node,CAP*amp/.01])
        at+=rng.uniform(.8,1.2)*spacing
    r=copy.deepcopy(row);r['pulses']=pulses
    return r,events

def observe(row,dt):
    t,v=stream_trajectory(row,.15,dt,100.);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=stream_trajectory(p,.15,dt,100.);u=v[7];der=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1);mask=t>=200/3
    integ=lambda a:float(np.sum((a[mask][:-1]+a[mask][1:])*.5)*dt)
    result={'raw':[integ(w*u),integ(w*der)]};initial=np.random.default_rng([row['seed'],157]).uniform(-.075,.075)
    for tau in TAUS:
        result[str(tau)]=[integ(w*(u-lowpass(u,tau,dt,initial))),integ(w*(der-lowpass(der,tau,dt,0.)))]
    return result,integ(w),float(np.max(np.abs(v)))

def main():
    OUT.mkdir(exist_ok=True);protocol=dict(duration_s=100.,spacings_s=[1.,2.5,10.],taus_s=TAUS,steps_s=[.00025,.000125],near_positive_prior=.8,source=str(SRC),budget_s=360,scope='New recorded development schedules of old cases; fixed component draws; analytic stationary-balance reference, no noise trajectories or online learner')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    raw=[json.loads(l) for l in SRC.read_text().splitlines()];dt=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dt and not r['control']}
    metricpath=ROOT/'lab/v/order_balance_information/branches.json';metrics=json.loads(metricpath.read_text());draws=[];streams=[];refine=0.;d_refine=0.;start=time.monotonic()
    for seed,row in sorted(seedrows.items()):
      for index,spacing in enumerate(protocol['spacings_s']):
        r,events=make_stream(row,spacing,index);stats,weight,maxv=observe(r,.00025)
        if seed==min(seedrows):
            fine,_,_=observe(r,.000125);refine=max(refine,max(abs(stats[k][j]-fine[k][j]) for k in stats for j in [0,1]))
            d_refine=max(d_refine,max(abs(np.clip(-stats[k][0]/stats[k][1],-1,1)-np.clip(-fine[k][0]/fine[k][1],-1,1)) for k in stats))
        streams.append(dict(seed=seed,spacing_s=spacing,events=events,weight_s=weight,maximum_state_abs_V=maxv,observations_Vs=stats))
        for mode,(a,b) in stats.items():
            identifiable=abs(b)>1e-12;raw_d=-a/b if identifiable else 0.;d=float(np.clip(raw_d,-1,1));passes=[];rescued=harmed=0
            for m in metrics:
                if m['seed']!=seed:continue
                lo,hi=bounds(m['case']);good=lo<m['u_V']+d*m['v_V']<hi and m['coincidence_adequate'];base=lo<m['u_V']<hi and m['coincidence_adequate'];passes.append(good);rescued+=good and not base;harmed+=base and not good
            draws.append(dict(seed=seed,spacing_s=spacing,mode=mode,identifiable=identifiable,denominator_Vs=b,raw_d=raw_d,d=d,passed=sum(passes),all_pass=all(passes),rescued=rescued,harmed=harmed))
        if time.monotonic()-start>360:raise RuntimeError('Budget exceeded')
      print('completed',seed,round(time.monotonic()-start,1),flush=True)
    comparisons={}
    for spacing in protocol['spacings_s']:
      for mode in ['raw']+list(map(str,TAUS)):
        rr=[r for r in draws if r['spacing_s']==spacing and r['mode']==mode]
        comparisons[f'{spacing}:{mode}']=dict(adequate_draws=sum(r['all_pass'] for r in rr),adequate_cases=sum(r['passed'] for r in rr),rescued=sum(r['rescued'] for r in rr),harmed=sum(r['harmed'] for r in rr),clamped=sum(abs(r['raw_d'])>1 for r in rr),nonpositive_denominator=sum(r['denominator_Vs']<=0 for r in rr),unidentifiable=sum(not r['identifiable'] for r in rr))
    result=dict(first_draw_integral_refinement_max_Vs=refine,first_draw_knob_refinement_max=d_refine,maximum_state_abs_V=max(r['maximum_state_abs_V'] for r in streams),comparisons=comparisons)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,metricpath,ROOT/'lab/order_continuous_baseline.py',ROOT/'lab/order_local_calibration.py',ROOT/'lab/order_bench.py',ROOT/'lab/population_trace_margin.py',ROOT/'lab/order_balance_information.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('streams',streams),('draws',draws)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
