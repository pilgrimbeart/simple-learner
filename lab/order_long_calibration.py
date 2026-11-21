"""D163 1000s calibration-opportunity reference, not online learning."""
import copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from order_baseline_stream import stream_trajectory
from order_continuous_baseline import lowpass,TAUS
from population_trace_margin import SRC
from order_bench import cases
from order_balance_information import bounds
from dynamic_parts_bench import ROOT,CAP,digest,provenance
from units import V_TYP
OUT=ROOT/'lab/v/order_long_calibration'
def make_long_stream(row,spacing,index):
    rng=np.random.default_rng([row['seed'],158,index]);cc=cases();weights=[]
    for c in cc:
        near=c['a'] and c['b'] and 0<abs(c['delay'])<=.15
        weights.append((1.6 if c['delay']>0 else .4) if near else 1.)
    prob=np.array(weights)/sum(weights);events=[];pulses=[];at=rng.uniform(0,spacing)
    while at<999.36:
        c=cc[rng.choice(len(cc),p=prob)];events.append(dict(first_s=float(at),case=c))
        for node,amp,t0 in [(0,c['a'],at+max(-c['delay'],0)),(1,c['b'],at+max(c['delay'],0))]:
            if amp:pulses.append([float(t0),.04,node,CAP*amp/.01])
        at+=rng.uniform(.8,1.2)*spacing
    r=copy.deepcopy(row);r['pulses']=pulses
    return r,events

def observe(row,dt):
    t,v=stream_trajectory(row,.15,dt,1000.);p=copy.deepcopy(row);p['elements'][0][6]=0.
    _,pv=stream_trajectory(p,.15,dt,1000.);u=v[7];der=2*pv[7]-u;w=np.clip(v[6]/V_TYP,0,1);mask=t>=2000/3
    integ=lambda a:float(np.sum((a[mask][:-1]+a[mask][1:])*.5)*dt)
    stats={'raw':[integ(w*u),integ(w*der)]};initial=np.random.default_rng([row['seed'],157]).uniform(-.075,.075)
    for tau in TAUS:stats[str(tau)]=[integ(w*(u-lowpass(u,tau,dt,initial))),integ(w*(der-lowpass(der,tau,dt,0.)))]
    return stats,float(np.max(np.abs(v)))

def main():
    OUT.mkdir(exist_ok=True);protocol=dict(duration_s=1000.,spacing_s=10.,taus_s=TAUS,steps_s=[.0005,.00025],knob_refinement_tolerance=.001,source=str(SRC),budget_s=600,scope='Same-generator extended histories; ideal stationary calibration reference, no online learner')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    raw=[json.loads(l) for l in SRC.read_text().splitlines()];dt=min(r['dt'] for r in raw);seedrows={r['seed']:r for r in raw if r['dt']==dt and not r['control']}
    previous=ROOT/'lab/v/order_baseline_stream/streams.json';old={r['seed']:r for r in json.loads(previous.read_text()) if r['spacing_s']==10.}
    metricpath=ROOT/'lab/v/order_balance_information/branches.json';metrics=json.loads(metricpath.read_text());draws=[];streams=[];refine=0.;start=time.monotonic()
    def score(seed,d):
        return [bool((lambda b:b[0]<m['u_V']+d*m['v_V']<b[1])(bounds(m['case'])) and m['coincidence_adequate']) for m in metrics if m['seed']==seed]
    for seed,row in sorted(seedrows.items()):
        r,events=make_long_stream(row,10.,2);assert [e for e in events if e['first_s']<99.36]==old[seed]['events']
        stats,maxv=observe(r,.0005)
        if seed==min(seedrows):
            fine,_=observe(r,.00025)
            for mode in stats:
                a,b=stats[mode];aa,bb=fine[mode];d=float(np.clip(-a/b,-1,1));dd=float(np.clip(-aa/bb,-1,1));refine=max(refine,abs(d-dd));assert score(seed,d)==score(seed,dd)
            assert refine<.001
        ns=sum(bool(e['first_s']>=2000/3 and e['case']['a'] and e['case']['b'] and e['case']['delay']==0) for e in events)
        streams.append(dict(seed=seed,events=events,simultaneous_last_third=ns,maximum_state_abs_V=maxv,observations_Vs=stats))
        for mode,(a,b) in stats.items():
            assert abs(b)>1e-12
            raw_d=-a/b;d=float(np.clip(raw_d,-1,1));ok=score(seed,d);base=score(seed,0.)
            draws.append(dict(seed=seed,mode=mode,d=d,raw_d=raw_d,denominator_Vs=b,simultaneous_last_third=ns,passed=sum(ok),all_pass=all(ok),rescued=sum(x and not y for x,y in zip(ok,base)),harmed=sum(y and not x for x,y in zip(ok,base))))
        print('completed',seed,round(time.monotonic()-start,1),flush=True)
        if time.monotonic()-start>600:raise RuntimeError('Budget exceeded')
    summary=dict(first_draw_knob_refinement_max=refine,zero_anchor_histories=sum(r['simultaneous_last_third']==0 for r in streams),anchor_count_range=[min(r['simultaneous_last_third'] for r in streams),max(r['simultaneous_last_third'] for r in streams)],comparisons={})
    for mode in ['raw']+list(map(str,TAUS)):
        rr=[r for r in draws if r['mode']==mode];summary['comparisons'][mode]=dict(adequate_draws=sum(r['all_pass'] for r in rr),adequate_cases=sum(r['passed'] for r in rr),rescued=sum(r['rescued'] for r in rr),harmed=sum(r['harmed'] for r in rr),clamped=sum(abs(r['raw_d'])>1 for r in rr),nonpositive_denominators=sum(r['denominator_Vs']<=0 for r in rr))
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,previous,metricpath,ROOT/'lab/order_baseline_stream.py',ROOT/'lab/order_continuous_baseline.py',ROOT/'lab/order_balance_information.py',ROOT/'lab/population_trace_margin.py',ROOT/'lab/order_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',summary),('streams',streams),('draws',draws)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
