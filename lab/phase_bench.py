"""D133 mirrored filtered/gated phase comparison. All dynamics use original _step."""
import argparse,itertools,json,math,sys,time
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,interval,wilson,digest,provenance
from motif_bench import node,edge
from mixed_feedback import Circuit,_step
from units import RAIL,V_TYP,C_MAX,R_MAX,TAU_LEAK,I_MIN,SLEW
OUT=ROOT/'lab/v/phase_v1';PILOT=list(range(2026112700,2026112708));CONFIRM=list(range(2026112800,2026112840));PHASES=[-math.pi/2,-math.pi/6,0.,math.pi/6,math.pi/2,math.pi]

def graph():return dict(nodes=[node('A',.005),node('B',.005),node('lag A',.1),node('lag B',.1),node('phase response',.5)],edges=[edge(2,0,CAP*.3/.1),edge(3,1,CAP*.3/.1),edge(4,1,CAP*1./.5,gate=2),edge(4,0,-CAP*1./.5,gate=3)])
def cases():return [dict(id=f'{f}_{i}',frequency=f,phase_index=i,phase=phi) for f, (i,phi) in itertools.product([2.,5.],enumerate(PHASES))]
def protocol():
    return dict(graph=graph(),cases=cases(),pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],duration_s=12.,
        input='Two sinusoidal input currents, nominal voltage .15+.10*cos(omega*t+phase). Actual frequency uniform .9..1.1 times 2/5Hz, common initial phase uniform0..2pi per draw/frequency; B relative phase from six declared values. Circuit starts independently uniform+/-.075V; no circuit oscillator/reference phase. Integrate currents analytically over each step.',
        metrics='Mean raw phase-output voltage over6..12s; ripple amplitude recorded separately. Output offset at phase0 reported, never subtracted from stored raw means.',
        criteria='Per draw, each frequency: mean(-pi/6)-mean(+pi/6)>.004V, mean(-pi/2)-mean(+pi/2)>.008V; means at -pi/2,-pi/6,0,+pi/6,+pi/2 strictly descending with each adjacent drop>.001V. These are response comparisons across tests, not a circuit calibration. Phase pi included to expose ambiguity but no unique global phase inference claimed. No rails.',
        control='Pilot: remove differential lag by gating positive output connection with A directly and negative with B directly; all parts remain, so cost not a pruning claim. Both odd contrasts abs<.002V. Offsets/even phase dependence may remain.',
        prediction='Matched small-signal lag-and-product difference contains -sin(phi)*omega*tau/(1+(omega*tau)^2). This gives local signed phase sensitivity, not a universal zero-centred error. Nonnegative gates, nonlinear source response, component mismatch and input lag invalidate exact multiplication; test the realized curve.',
        reliability='All frequencies/steps per seed; Wilson95 lower>=.90 for40draws. Both paired-seed step-halving95 intervals within+/-.05 of V_TYP for each raw mean and ripple.',
        initial_noise='Original silicon noise/mismatch. Nominal thermal sigma~13uV versus1mV minimum adjacent separation; average over at least10cycles. No noise switch or filter state without its own noisy node.',
        budget='Pilot<=600s,confirm<=1200s; at most2variants after diagnosis, one sequential job.',
        limitation='This establishes a phase-dependent analogue response only. Zero-phase bias and 2pi ambiguity prevent claiming an absolute unwrapped phase sensor, lock acquisition, frequency learning or robot skill. Independent constant phases/frequencies are bench stimuli, not brain inputs beyond their waveforms.',
        source='Haag,Denk,Borst2004 introduction/Fig1 checked in D128; this is the same established asymmetric-filter/product/subtraction family, now tested with harmonic input.')

def build(seed,control):
    c=Circuit(seed=seed,streams=True,substrate='silicon');rng=np.random.default_rng([seed,133,1]);g=graph()
    for n in g['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-.075,.075))
    for i,e in enumerate(g['edges']):
        gate=(0 if i==2 else 1) if control and i>=2 else e['gate']
        c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=0.,gate=gate)
    c._ready();return c

@njit(cache=True)
def integrate_phase(V,Vx,armed,spikes,vmax,node,el,link,q,rest,cfg,z,dt,stride,frequency,initial,relative):
    steps=len(z);trace=np.empty((steps//stride+1,6));trace[0,0]=0.;trace[0,1:]=V;drive=np.zeros(5);dV=np.zeros(5);gross=np.zeros(5);charge=np.zeros(5);power=0.;hits=0;row=1;omega=2*np.pi*frequency
    for k in range(steps):
        t=k*dt
        for i in range(2):
            phase=initial+(relative if i else 0.)
            mean_cos=(np.sin(omega*(t+dt)+phase)-np.sin(omega*t+phase))/(omega*dt)
            drive[i]=CAP/.005*(.15+.1*mean_cos)
        power+=_step(V,Vx,armed,spikes,vmax,drive,node,el,link,z[k],q,rest,dt,dV,gross,cfg);charge+=gross*dt
        for v in V:
            if abs(v)>=.999*RAIL:hits+=1
        if (k+1)%stride==0:
            trace[row,0]=(k+1)*dt;trace[row,1:]=V;row+=1
    return trace[:row],power/steps,charge,hits

def run(seed,dt,case,control):
    c=build(seed,control);rng=np.random.default_rng([seed,133,2,int(case['frequency'])]);frequency=case['frequency']*rng.uniform(.9,1.1);initial=rng.uniform(0,2*np.pi);steps=round(12/dt);ratio=round(dt/(DT/4));z=np.empty((steps,5))
    for i in range(5):
        rng=np.random.default_rng([seed,133,3,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate_phase(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),frequency,initial,case['phase']);y=tr[tr[:,0]>=6,-1];mean=float(y.mean());ripple=float(np.quantile(y,.95)-np.quantile(y,.05))
    return dict(seed=seed,dt=dt,case=case,control=control,frequency_Hz=frequency,initial_phase_rad=initial,mean_V=mean,ripple_V=ripple,nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist(),cost=dict(power_W=float(power),energy_J=float(power*12),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits))),tr

def assess(rr,control):
    metrics={};ok=True
    for f in [2.,5.]:
        r=sorted([r for r in rr if r['case']['frequency']==f],key=lambda r:r['case']['phase_index']);assert len(r)==6
        means=[x['mean_V'] for x in r];near=means[1]-means[3];far=means[0]-means[4];drops=[means[i]-means[i+1] for i in range(4)]
        passed=(abs(near)<.002 and abs(far)<.002) if control else (near>.004 and far>.008 and min(drops)>.001)
        passed=bool(passed and all(x['cost']['rail_hits']==0 for x in r));ok &=passed;metrics[str(f)]=dict(means_V=means,near_contrast_V=near,far_contrast_V=far,adjacent_drops_V=drops,zero_phase_bias_V=means[2],passed=passed)
    return bool(ok),metrics

def summary(rows,ss):
    primary=[r for r in rows if not r['control']];expected={(s,dt,c['id']) for s in ss for dt in [DT,DT/2,DT/4] for c in cases()};assert len(primary)==len(expected) and {(r['seed'],r['dt'],r['case']['id']) for r in primary}==expected
    groups=[]
    for seed in ss:
        for dt in [DT,DT/2,DT/4]:
            for control in sorted({r['control'] for r in rows}):
                passed,metrics=assess([r for r in rows if r['seed']==seed and r['dt']==dt and r['control']==control],control);groups.append(dict(seed=seed,dt=dt,control=control,passed=passed,metrics=metrics))
    good=[s for s in ss if all(r['passed'] for r in groups if r['seed']==s and not r['control'])];ref={}
    for case in cases():
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in ['mean_V','ripple_V']:
                a={r['seed']:r[metric]/V_TYP for r in primary if r['dt']==coarse and r['case']['id']==case['id']};b={r['seed']:r[metric]/V_TYP for r in primary if r['dt']==fine and r['case']['id']==case['id']};ref[f'{case["id"]}:{coarse}:{metric}']=interval([b[s]-a[s] for s in ss])
    return dict(passed=len(good),seeds=len(ss),failed_seeds=sorted(set(ss)-set(good)),wilson95=wilson(len(good),len(ss)),reliability_pass=wilson(len(good),len(ss))[0]>=.9,groups=groups,refinement=ref,refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),control_rows=sum(r['control'] for r in rows),control_pass=all(r['passed'] for r in groups if r['control']),power_W=interval([np.mean([r['cost']['power_W'] for r in primary if r['seed']==s and r['dt']==DT/4]) for s in ss]))

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pilot','confirm']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        for n in graph()['nodes']:assert n['C']<=C_MAX and n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK
        for e in graph()['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    if a.stage=='confirm':
        p=json.loads((OUT/'pilot.json').read_text());assert p['passed']==8 and p['control_pass'] and p['refinement_pass']
    target=OUT/f'{a.stage}.jsonl';assert not target.exists();prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/phase_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n');ss=PILOT if a.stage=='pilot' else CONFIRM;rows=[];start=time.monotonic()
    with target.open('x') as f:
        for seed in ss:
            for control in ([False,True] if a.stage=='pilot' else [False]):
                for case in cases():
                    for dt in [DT,DT/2,DT/4]:
                        r,tr=run(seed,dt,case,control);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(OUT/f'{a.stage}_{case["id"]}_{control}.npz',trace=tr)
            failures=sum(not assess([r for r in rows if r['seed']==seed and r['dt']==dt and r['control']==ctrl],ctrl)[0] for dt in [DT,DT/2,DT/4] for ctrl in ([False,True] if a.stage=='pilot' else [False]));print(json.dumps(dict(seed=seed,failed_groups=failures,elapsed_s=time.monotonic()-start)),flush=True)
    result=summary(rows,ss);result['elapsed_s']=time.monotonic()-start;(OUT/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('refinement','groups')}),flush=True)
if __name__=='__main__':main()
