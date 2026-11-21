"""D127 retained state and controlled writes: frozen component bench, unchanged _step."""
import argparse, json, math, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import (ROOT,CAP,DT,integrate,interval,wilson,digest,provenance)
from mixed_feedback import Circuit
from units import RAIL,V_TYP,K_B,T,E,SLEW,I_MIN,R_MAX,TAU_LEAK,C_MAX
from minimal.spice import count
OUT=ROOT/'lab/v/retained_write'; DURATION=100.
PILOT=list(range(52000,52008)); CONFIRM=list(range(52100,52140))

def definition():
    ns=[]
    for name,tau in [('evidence',.02),('eligibility',.05),('stored',None),('probe',.02),('response',.05)]:
        ns.append(dict(name=name,C=CAP,R=None if tau is None else tau/CAP,bias=0.,memory=tau is None))
    # Readout first, so removing the writer preserves readout mismatch draws.
    es=[dict(to=4,source=3,gate=2,gain=CAP*.4/.05,offset=0.,slope=1/.15,tau=0.),
        dict(to=2,source=0,gate=1,gain=8e-12,offset=0.,slope=1/.15,tau=0.)]
    return dict(nodes=ns,edges=es,duration=DURATION)

def protocol():
    return dict(version=1,graph=definition(),pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],
        signs=[-1,1],substrate='silicon',record_s=.001,
        initial='Stored voltage uniform .14 to .16 V; all dynamic nodes independent uniform +/- .075 V. Measure baseline after startup settles.',
        stimulus='Evidence +/- .5 V nominal for .30 s from 1+jitter; eligibility +.6 V nominal for .25 s at same time. Opposite evidence alone at 50+jitter. Identical probe pulses at .4,3,98+jitter. Jitter continuous, .001 to .009 s. Currents delivered only to explicit dynamic input nodes.',
        criteria={'write':'Signed change from baseline to post-write stored voltage in [.03,.14] V for EACH sign.',
                  'hold':'Stored max-min < .0001 V from 2 to 97 s, including closed-gate opposite evidence; <=.0001 V change of mean across disturbance.',
                  'readout':'Signed post-minus-pre response > .025 V; late-minus-post abs < .005 V.',
                  'rails':'No node reaches .999 rail.',
                  'robustness':'Both signs at all steps per seed; Wilson 95% lower >=.90 in 40 fresh seeds.',
                  'refinement':'Both paired mean successive-halving bootstrap 95% intervals inside +/- .05 for every normalized metric.'},
        controls='Pilot only, all steps and signs: no eligibility stimulus and removed writer must give stored delta abs < .0001 V and readout delta abs < .005 V; ungated readout must give readout delta abs < .005 V while signed write passes. All controls zero rail hits.',
        noise_estimate=dict(thermal_sigma_V=math.sqrt(K_B*T/CAP),write_shot_sigma_V=math.sqrt(E*8e-12*.3)/CAP,
            minimum_write_V=.03,hold_margin_V=.0001,comment='No rest noise in retained node is the established substrate contract, not a new switch. Dead zone should stop thermal gate chatter. No multiple explorers or learning/credit claim.'),
        budget='One sequential process, maths threads1. Pilot <=600s, confirmation <=1200s. At most two graph variants; diagnose before changing. No robot/search.',
        limitations='Unipolar gate clips negative state; write sign comes from bipolar evidence through tanh. Stored value stays positive to modulate readout; no signed learned-weight construction claimed. No internal filtered connection. High-voltage pump cost absent in existing model.')

def build(seed,control):
    s=definition(); c=Circuit(seed=seed,streams=True,substrate='silicon'); rng=np.random.default_rng([seed,127,1])
    for n in s['nodes']:
        c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(.14,.16) if n['memory'] else rng.uniform(-.075,.075))
    for i,e in enumerate(s['edges']):
        if i==1 and control=='no_writer': continue
        c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=e['tau'],gate=-1 if i==0 and control=='ungated_readout' else e['gate'])
    c._ready();return c

def run(seed,dt,sign,control='none'):
    c=build(seed,control); jitter=np.random.default_rng([seed,127,2]).uniform(.001,.009)
    pulses=[(1+jitter,.3,0,sign*CAP*.5/.02),(50+jitter,.3,0,-sign*CAP*.5/.02)]
    if control!='no_eligibility': pulses.append((1+jitter,.25,1,CAP*.6/.05))
    for at in [.4,3,98]: pulses.append((at+jitter,.3,3,CAP*.5/.02))
    pulses=np.array(pulses); assert np.max(np.abs(pulses[:,3]))/CAP<=SLEW
    steps=round(DURATION/dt); ratio=round(dt/(DT/4)); z=np.empty((steps,5))
    for i in range(5):
        rng=np.random.default_rng([seed,127,3,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5))
    t=tr[:,0]; m=tr[:,3]; response=tr[:,5]
    def mean(v,a,b): return float(v[(t>a)&(t<b)].mean())
    before=mean(m,.8,.95); after=mean(m,2,2.9);delta=after-before
    hold=float(np.ptp(m[(t>2)&(t<97)])); disturbance=mean(m,51,52)-mean(m,49,49.9)
    reads=[mean(response,a+jitter+.15,a+jitter+.28) for a in [.4,3,98]]
    change=reads[1]-reads[0]; late=reads[2]-reads[1]
    norm=dict(write=delta/V_TYP,hold=hold/V_TYP,disturbance=disturbance/V_TYP,readout=change/V_TYP,late_readout=late/V_TYP)
    if control in ('no_writer','no_eligibility'):
        ok=abs(delta)<.0001 and abs(change)<.005 and hold<.0001
    elif control=='ungated_readout': ok=.03<sign*delta<.14 and abs(change)<.005 and hold<.0001
    else: ok=.03<sign*delta<.14 and hold<.0001 and abs(disturbance)<.0001 and sign*change>.025 and abs(late)<.005
    row=dict(seed=seed,dt=dt,sign=sign,control=control,passed=bool(ok and hits==0),metrics=dict(write_delta_V=delta,hold_span_V=hold,
        closed_gate_delta_V=disturbance,readout_change_V=change,late_readout_delta_V=late,readout_levels_V=reads,stored_baseline_V=before,stored_after_V=after),normalized=norm,
        cost=dict(power_W=float(power),energy_J=float(power*DURATION),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits)),
        nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),pulses=pulses.tolist())
    return row,tr

def summarise(rows,seeds):
    primary=[r for r in rows if r['control']=='none']; assert len(primary)==len(seeds)*6
    assert len({(r['seed'],r['dt'],r['sign']) for r in primary})==len(primary)
    passed=[s for s in seeds if all(r['passed'] for r in primary if r['seed']==s)]
    refinement={}
    for sign in [-1,1]:
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in primary[0]['normalized']:
                a={r['seed']:r['normalized'][metric] for r in primary if r['dt']==coarse and r['sign']==sign}
                b={r['seed']:r['normalized'][metric] for r in primary if r['dt']==fine and r['sign']==sign}
                ci=interval([b[s]-a[s] for s in seeds]); refinement[f'{sign}:{coarse}:{metric}']=ci
    powers=[np.mean([r['cost']['power_W'] for r in primary if r['seed']==s and r['dt']==DT/4]) for s in seeds]
    return dict(seeds=len(seeds),passed=len(passed),failed_seeds=sorted(set(seeds)-set(passed)),wilson95=wilson(len(passed),len(seeds)),
        reliability_pass=wilson(len(passed),len(seeds))[0]>=.9,refinement=refinement,
        refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in refinement.values()),
        control_pass=all(r['passed'] for r in rows if r['control']!='none'),control_rows=sum(r['control']!='none' for r in rows),
        mean_power_W=interval(powers),limitations=protocol()['limitations'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','pilot','confirm']);a=parser.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        target=OUT/'protocol_v1.json';assert not target.exists()
        for n in definition()['nodes']:
            assert n['C']<=C_MAX and (n['memory'] or (n['R']<=R_MAX and n['C']*n['R']>=TAU_LEAK))
        for e in definition()['edges']: assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        target.write_text(json.dumps(protocol(),indent=2)+'\n'); print(target);return
    assert json.loads((OUT/'protocol_v1.json').read_text())==protocol()
    if a.stage=='confirm':
        pilot=json.loads((OUT/'pilot_v1.json').read_text());assert pilot['passed']==8 and pilot['control_pass'] and pilot['refinement_pass']
    path=OUT/f'{a.stage}_v1.jsonl';assert not path.exists()
    prov=provenance();prov['files']['lab/retained_write_bench.py']=digest(__file__);prov['protocol_sha256']=digest(OUT/'protocol_v1.json')
    (OUT/f'{a.stage}_provenance_v1.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];seeds=PILOT if a.stage=='pilot' else CONFIRM;start=time.monotonic()
    with path.open('x') as out:
        for seed in seeds:
            for control in (['none','no_eligibility','no_writer','ungated_readout'] if a.stage=='pilot' else ['none']):
                for sign in [-1,1]:
                    for dt in [DT,DT/2,DT/4]:
                        row,tr=run(seed,dt,sign,control);rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
                        if seed==seeds[0] and dt==DT/4: np.savez_compressed(OUT/f'{a.stage}_{control}_{sign}_v1.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=[(r['control'],r['sign'],r['dt']) for r in rows if r['seed']==seed and not r['passed']],elapsed_s=time.monotonic()-start)),flush=True)
    result=summarise(rows,seeds);result['elapsed_s']=time.monotonic()-start
    (OUT/f'{a.stage}_v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
