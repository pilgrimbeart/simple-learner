"""D126: fixed circuit witnesses; all dynamics/noise use mixed_feedback._step.
Prepare freezes protocol/specifications without simulation. Pilot and confirm never overwrite output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from numba import njit
from mixed_feedback import Circuit, _step
from units import (C_MAX, DT, I_MIN, K_B, R_MAX, RAIL, SLEW, T, TAU_LEAK,
                   TAU_LOOP, V_TYP)

OUT = ROOT / 'lab/v/dynamic_parts'
CAP = C_MAX / 2
VS = V_TYP / 2


def definitions():
    def node(name, tau):
        return dict(name=name, C=CAP, R=tau/CAP, bias=0., memory=False)
    def edge(to, source, gain, scale=V_TYP):
        return dict(to=to, source=source, gain=gain, offset=0., slope=1/scale, tau=0., gate=-1)
    return {
        'trace': dict(nodes=[node('trace', .05)], edges=[], duration=2.),
        'memory': dict(nodes=[node('bit', .05)],
                       edges=[edge(0, 0, CAP*.6/.05, VS)], duration=100.),
        'resonator': dict(nodes=[node('x', .1), node('y', .1)],
                         edges=[edge(0, 1, -CAP*60*V_TYP), edge(1, 0, CAP*60*V_TYP)],
                         duration=6.5, frequencies=[60/(2*math.pi)*v for v in [.25,.5,1,2,4]]),
        'oscillator': dict(nodes=[node('fast', .02), node('recovery', .2)],
                          edges=[edge(0, 0, 3*CAP*VS/.02, VS),
                                 edge(0, 1, -5*CAP*VS/.02, VS),
                                 edge(1, 0, CAP*V_TYP/.2)], duration=100.)}


def protocol():
    return dict(version=1, substrate='silicon', definitions=definitions(),
                pilot_seeds=list(range(8)), confirm_seeds=list(range(51000,51040)),
                steps=[DT, DT/2, DT/4], record_interval_s=.001,
                criteria={
                    'trace': 'peak > .15 V; measured tau/nominal in [.5,1.6]; late residual < .01 V',
                    'memory': 'after set/reset, >=99.9% of samples in each hold window beyond +/- .3 V; weak opposite pulses do not erase',
                    'resonator': 'central drive has largest response; central amplitude >1.5 times both extreme-frequency amplitudes; after drive ends late amplitude < .1 driven amplitude',
                    'oscillator': 'each before/after window >=10 cycles, mean peak-to-peak amplitude > .15 V; period CV < .1; post/pre frequency and amplitude ratios in [.9,1.1]',
                    'robustness': 'all four per-seed criteria at all three steps; Wilson 95% lower bound >= .90 per circuit on confirm seeds',
                    'refinement': 'for every named dimensionless metric, paired mean difference bootstrap 95% CI lies inside [-.05,.05] for both successive halvings',
                },
                controls='Trace absent input; memory self-feedback removed; resonator cross-coupling removed; oscillator positive self-feedback removed. Pilot seeds only; final dynamic energy/amplitude must fall below .01 V for removed-feedback controls.',
                analysis='Bootstrap over seeds, 4000 draws, seed 126; Wilson binomial interval. No optimisation. At most 2 construction variants per failed circuit; preserve v1 results.',
                budget='One sequential process, <=600 s pilot and <=1200 s confirmation per fixed variant. No robot lives or biological-noise claim.',
                pulse_note='Bench stimulus, not a body/interface change. Pulse overlap integrated at continuous jittered times; sinusoid phase independent of initial circuit state.',
                initialisation='Each node starts independently uniform +/-V_TYP/4; memory starts unknown, trace and resonator settle before input. Oscillator is never started at a supplied phase.',
                noise_feasibility=dict(passive_sigma_V=math.sqrt(K_B*T/CAP),
                    minimum_signal_V=.01, comment='Thermal sigma approx 13 uV versus 10 mV minimum; shot-noise estimate recorded per run. Mismatch 10% plus offset ~30 mV is the main anticipated challenge.'),
                limitations='No nonvolatile-memory/write-gate coverage yet. No internal filtered channels; every dynamic state is an explicit node. Counts use chip.py blocks; no SPICE or silicon validation.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance():
    paths=['lab/dynamic_parts_bench.py','mixed_feedback.py','chip.py','units.py', 'minimal/spice.py']
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                files={p:digest(ROOT/p) for p in paths},
                dirty=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines())


def validate(spec):
    for n in spec['nodes']:
        assert 0 < n['C'] <= C_MAX and 0 < n['R'] <= R_MAX
        assert n['R']*n['C'] >= TAU_LEAK
    for e in spec['edges']:
        assert abs(e['gain']) >= I_MIN and e['tau']==0
        assert abs(e['gain'])/spec['nodes'][e['to']]['C'] <= SLEW
        if e['to']==e['source']:
            assert abs(e['gain'])*e['slope']/spec['nodes'][e['to']]['C'] <= 1/TAU_LOOP


def build(name, spec, seed, control=False):
    c=Circuit(seed=seed, streams=True, substrate='silicon')
    rng=np.random.default_rng([seed,126,1])
    for n in spec['nodes']:
        c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-V_TYP/4,V_TYP/4))
    for e in spec['edges']:
        if control and (name in ('memory','resonator') or (name=='oscillator' and e['to']==e['source'])):
            continue
        c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=e['tau'],gate=e['gate'])
    # Empty edge arrays are supported by the shared engine. No dummy active part.
    c._ready()
    return c


def stimuli(name, seed, control=False, frequency=None):
    rng=np.random.default_rng([seed,126,2])
    shift=rng.uniform(.001,.009)
    pulses=[]
    if name=='trace' and not control:
        pulses=[(.2+shift,.01,0,CAP*.3/.01)]
    elif name=='memory':
        pulses=[(.2+shift,.02,0,CAP*1.2/.02),(5+shift,.01,0,-CAP*.06/.01),
                (50+shift,.02,0,-CAP*1.2/.02),(55+shift,.01,0,CAP*.06/.01)]
    elif name=='oscillator':
        pulses=[(50+shift,.01,0,CAP*.12/.01)]
    # No common phase or frequency with the autonomous oscillator.
    sine=(.2+shift,4.,12.5e-12,frequency or 0.,rng.uniform(0,2*math.pi))
    for _,_,_,current in pulses:
        assert abs(current)/CAP <= SLEW
    return np.array(pulses,dtype=float).reshape(-1,4),np.array(sine),shift


@njit(cache=True)
def integrate(V,Vx,armed,spikes,vmax,node,el,link,q,rest,cfg,z,dt,record_stride,pulses,sine):
    steps=z.shape[0]; n=len(V)
    trace=np.empty((steps//record_stride+1,n+1))
    trace[0,0]=0.; trace[0,1:]=V
    drive=np.zeros(n); dV=np.zeros(n); gross=np.zeros(n)
    power_sum=0.; charge=np.zeros(n); rail_hits=0; row=1
    for k in range(steps):
        t=k*dt
        drive[:]=0.
        for p in pulses:
            overlap=max(0.,min(t+dt,p[0]+p[1])-max(t,p[0]))
            drive[int(p[2])]+=p[3]*overlap/dt
        if sine[3]>0:
            a=max(t,sine[0]); b=min(t+dt,sine[0]+sine[1])
            if b>a:
                w=2*np.pi*sine[3]
                drive[0]+=sine[2]*(np.cos(w*a+sine[4])-np.cos(w*b+sine[4]))/(w*dt)
        power_sum+=_step(V,Vx,armed,spikes,vmax,drive,node,el,link,z[k],q,rest,dt,dV,gross,cfg)
        charge+=gross*dt
        for v in V:
            if abs(v)>=.999*RAIL: rail_hits+=1
        if (k+1)%record_stride==0:
            trace[row,0]=(k+1)*dt; trace[row,1:]=V; row+=1
    return trace[:row],power_sum/steps,charge,rail_hits


def run_one(name,spec,seed,dt,control=False,frequency=None):
    c=build(name,spec,seed,control)
    pulses,sine,shift=stimuli(name,seed,control,frequency)
    fine_dt=DT/4
    steps=int(round(spec['duration']/dt)); ratio=int(round(dt/fine_dt))
    # Same underlying Brownian increments at all refinements, per-node streams.
    z=np.empty((steps,len(c.V)))
    for i in range(len(c.V)):
        rng=np.random.default_rng([seed,126,3,i])
        z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    trace,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,
        c.q,c.rest,c.cfg,z,dt,int(round(.001/dt)),pulses,sine)
    return trace,dict(power_W=float(power),energy_J=float(power*spec['duration']),
        gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits),
        shot_sigma_unrestored_V=(np.sqrt(c.q*charge)/c.node_arr[2]).tolist(),
        nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),stimulus_pulses=pulses.tolist(),
        sine=sine.tolist(),shift=shift)


def amp(t,x,a,b):
    y=x[(t>=a)&(t<b)]
    return float(np.quantile(y,.95)-np.quantile(y,.05))


def oscillation(t,x,a,b):
    mask=(t>=a)&(t<b); tt=t[mask]; xx=x[mask]
    threshold=(float(np.quantile(xx,.95))+float(np.quantile(xx,.05)))/2
    ix=np.where((xx[:-1]<threshold)&(xx[1:]>=threshold))[0]
    crossings=tt[ix]+(threshold-xx[ix])/(xx[ix+1]-xx[ix])*(tt[ix+1]-tt[ix])
    periods=np.diff(crossings)
    if len(periods)<2: return 0., 10., amp(t,x,a,b),len(periods)
    return float(1/periods.mean()),float(periods.std()/periods.mean()),amp(t,x,a,b),len(periods)


def metrics(name,traces,costs):
    tr=traces[0]; t=tr[:,0]; x=tr[:,1]; shift=costs[0]['shift']
    if name=='trace':
        end=.21+shift
        baseline=float(np.mean(x[(t>.12)&(t<.19)]))
        peak=float(x[np.searchsorted(t,end)])-baseline
        m=(t>end+.01)&(t<end+.12)&(x-baseline>max(peak*.05,1e-5))
        tau=-1/np.polyfit(t[m],np.log(x[m]-baseline),1)[0] if m.sum()>5 else 0.
        late=float(np.max(np.abs(x[(t>end+.4)])))
        values=dict(peak_V=peak,tau_s=float(tau),late_V=late)
        normalized=dict(peak=peak/V_TYP,tau=tau/.05,late=late/V_TYP)
        ok=peak>.15 and .5<tau/.05<1.6 and late<.01
    elif name=='memory':
        a=x[(t>1)&(t<49)]; b=x[(t>51)&(t<99)]
        pos=float(np.mean(a>.3)); neg=float(np.mean(b<-.3))
        values=dict(positive_hold_fraction=pos,negative_hold_fraction=neg,positive_V=float(a.mean()),negative_V=float(b.mean()))
        normalized=dict(positive=pos,negative=neg,contrast=(a.mean()-b.mean())/(2*V_TYP))
        ok=pos>=.999 and neg>=.999
    elif name=='resonator':
        amplitudes=[]; tails=[]
        for tr,cost in zip(traces,costs):
            tt=tr[:,0]; yy=tr[:,2]; f=cost['sine'][3]; end=cost['sine'][0]+4
            m=(tt>end-2)&(tt<end)
            basis=np.column_stack([np.ones(m.sum()),np.sin(2*np.pi*f*tt[m]),np.cos(2*np.pi*f*tt[m])])
            coef=np.linalg.lstsq(basis,yy[m],rcond=None)[0]
            amplitudes.append(float(np.hypot(coef[1],coef[2])))
            tails.append(amp(tt,yy,end+.8,end+1.8)/2)
        values=dict(amplitudes_V=amplitudes,tail_V=tails,peak_frequency_index=int(np.argmax(amplitudes)))
        normalized={f'amplitude_{i}':v/V_TYP for i,v in enumerate(amplitudes)}
        normalized.update({f'tail_{i}':v/V_TYP for i,v in enumerate(tails)})
        ok=np.argmax(amplitudes)==2 and amplitudes[2]>1.5*max(amplitudes[0],amplitudes[4]) and tails[2]<.1*amplitudes[2]
    else:
        f,cv,a,n=oscillation(t,x,10,45); f2,cv2,a2,n2=oscillation(t,x,55,95)
        values=dict(frequency_Hz=f,post_frequency_Hz=f2,period_cv=cv,post_period_cv=cv2,
                    amplitude_V=a,post_amplitude_V=a2,cycles=n,post_cycles=n2)
        normalized=dict(frequency=f*.02,post_frequency=f2*.02,amplitude=a/V_TYP,post_amplitude=a2/V_TYP,
                        period_cv=cv,post_period_cv=cv2)
        ok=n>=10 and n2>=10 and a>.15 and a2>.15 and cv<.1 and cv2<.1 and .9<f2/max(f,1e-20)<1.1 and .9<a2/max(a,1e-20)<1.1
    ok=bool(ok and all(c['rail_hits']==0 for c in costs))
    return dict(passed=ok,values=values,normalized={k:float(v) for k,v in normalized.items()})


def interval(values):
    a=np.asarray(values,dtype=float)
    rng=np.random.default_rng(126)
    sample=a[rng.integers(0,len(a),(4000,len(a)))].mean(axis=1)
    return [float(a.mean()),*np.quantile(sample,[.025,.975]).tolist()]


def wilson(k,n):
    z=1.959963984540054; p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den; half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(mid-half),float(mid+half)]


def summary(rows,seeds):
    result={}
    for name in definitions():
        rr=[r for r in rows if r['name']==name and not r['control']]
        k=sum(all(r['metrics']['passed'] for r in rr if r['seed']==s) for s in seeds)
        refinement={}
        for d0,d1 in zip([DT,DT/2],[DT/2,DT/4]):
            pairs=[]
            for seed in seeds:
                a=next(r for r in rr if r['seed']==seed and r['dt']==d0)
                b=next(r for r in rr if r['seed']==seed and r['dt']==d1)
                pairs.append({key:b['metrics']['normalized'][key]-v for key,v in a['metrics']['normalized'].items()})
            refinement[str(d0)]={key:interval([p[key] for p in pairs]) for key in pairs[0]}
        converged=all(v[1]>-.05 and v[2]<.05 for half in refinement.values() for v in half.values())
        ctr=[r for r in rows if r['name']==name and r['control']]
        result[name]=dict(successes=k,n=len(seeds),wilson95=wilson(k,len(seeds)),refinement=refinement,
                          refinement_passed=converged,demonstrated=wilson(k,len(seeds))[0]>=.9 and converged,
                          power_W=interval([sum(c['power_W'] for c in r['costs'])/len(r['costs']) for r in rr if r['dt']==DT/4]),
                          failed_cases=[dict(seed=r['seed'],dt=r['dt'],values=r['metrics']['values']) for r in rr if not r['metrics']['passed']],
                          control_passed=all(r['control_passed'] for r in ctr) if ctr else None)
    return result


def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'protocol_v1.json'
    if target.exists(): raise RuntimeError('Protocol already frozen; refusing overwrite')
    for spec in definitions().values(): validate(spec)
    target.write_text(json.dumps(protocol(),indent=2)+'\n')
    print('Frozen',target,flush=True)


def run(stage):
    proto=json.loads((OUT/'protocol_v1.json').read_text())
    assert proto==protocol(), 'Protocol/code mismatch'
    path=OUT/f'{stage}_v1.json'
    raw=OUT/f'{stage}_v1.jsonl'
    if path.exists() or raw.exists(): raise RuntimeError('Refusing to overwrite results')
    seeds=proto[f'{stage}_seeds']; rows=[]; start=time.monotonic()
    metadata=dict(protocol_sha256=digest(OUT/'protocol_v1.json'),provenance=provenance(),stage=stage)
    (OUT/f'{stage}_provenance_v1.json').write_text(json.dumps(metadata,indent=2)+'\n')
    with raw.open('x') as log:
        for name,spec in definitions().items():
            for seed in seeds:
                for dt in proto['steps']:
                    traces=[]; costs=[]
                    for f in spec.get('frequencies',[None]):
                        tr,cost=run_one(name,spec,seed,dt,frequency=f)
                        traces.append(tr); costs.append(cost)
                    row=dict(name=name,seed=seed,dt=dt,control=False,costs=costs,metrics=metrics(name,traces,costs))
                    rows.append(row); log.write(json.dumps(row)+'\n'); log.flush()
                    if seed==seeds[0] and dt==DT/4:
                        for i,tr in enumerate(traces):
                            np.savez_compressed(OUT/f'{stage}_{name}_{i}_trace_v1.npz',trace=tr)
                if stage=='pilot':
                    # Remove the defining mechanism; no new circuit variant is tuned.
                    tr,cost=run_one(name,spec,seed,DT,control=True,frequency=spec.get('frequencies',[None])[0])
                    t=tr[:,0]; y=tr[:,-1]
                    a=1. if name=='trace' else (5.5 if name=='resonator' else 60.)
                    residue=float(np.max(np.abs(y[t>a])))
                    row=dict(name=name,seed=seed,dt=DT,control=True,costs=[cost],control_residual_V=residue,control_passed=residue<.01)
                    rows.append(row); log.write(json.dumps(row)+'\n'); log.flush()
            print(name, 'done',round(time.monotonic()-start,1),'s',flush=True)
    result=dict(**metadata,elapsed_s=time.monotonic()-start,summary=summary(rows,seeds))
    path.write_text(json.dumps(result,indent=2)+'\n')
    for name,r in result['summary'].items():
        print(name,r['successes'],'/',r['n'],'refinement',r['refinement_passed'],'controls',r['control_passed'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['prepare','pilot','confirm'])
    action=parser.parse_args().action
    prepare() if action=='prepare' else run(action)
