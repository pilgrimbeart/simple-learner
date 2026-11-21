"""D129 bounded exploratory audit of the unchanged D127 memory circuit."""
import argparse,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from retained_write_bench import build,definition
from dynamic_parts_bench import ROOT,CAP,DT,integrate,digest,provenance
from units import RAIL
OUT=ROOT/'lab/v/memory_limits';SEEDS=list(range(2026112300,2026112308))

def cases():
    return ([dict(id=f'overlap_{s}_{d}',kind='overlap',sign=s,delay=d) for s in [-1,1] for d in [-.5,-.1,0.,.1,.3,.6]]+
        [dict(id='gate_only',kind='gate_only',sign=1,delay=0.),dict(id='evidence_only',kind='evidence_only',sign=1,delay=0.)]+
        [dict(id=f'repeated_{s}',kind='repeated',sign=s,delay=0.) for s in [-1,1]])

def protocol():
    return dict(graph=definition(),seeds=SEEDS,cases=cases(),steps=[DT,DT/2,DT/4],
        question='Where does D127 retained-write operation stop behaving like ideal gated signed evidence?',
        prediction='Write integrates gated saturating evidence minus existing1%driver dead zone. Uncorrelated thermal noise is small, but offset in evidence transfer can create gate-only writes. Memory clamps at declared rails on repeated writes; opposite writes should release it. Hold and saturation reflect engine contract, not empirical hardware retention.',
        stimulus='Use D127 currents: evidence +/-.5V nominal for.3s, eligibility+.6V for.25s. Overlap delays -.5,-.1,0,.1,.3,.6s relative gate at1.6+jitter; gate-only and evidence-only controls. Repeated:18 matching gate/evidence events at1..18s, reverse at21,22s;26s duration. Other cases5s.',
        metrics='Compare retained mean before first event with2s after last in overlap cases. Gate-only/evidence-only practical unwanted-write margin1mV; zero-delay useful write>30mV. Repeated: reach abs>.89V before reverse and move inward>30mV after first reverse. Record startup shift and dynamic-node rail samples separately. Memory saturation intentionally allowed here.',
        analysis='Exploratory8draw diagnostic, not40seed reliability claim. All rows kept, steps paired; never alter D127 pass labels. Report per-case ranges and step differences; analytic overlap uses actual mismatched parts, not a new simulator.',
        budget='One fixed-circuit batch <=600s, no variants/tuning in this audit. No robot lives; no engine/body/noise changes.')

def run(seed,dt,case):
    c=build(seed,'none');j=np.random.default_rng([seed,129,1]).uniform(.001,.009);sgn=case['sign'];pulses=[]
    def pair(at,sign,delay=0.,gate=True,evidence=True):
        if gate:pulses.append((at,.25,1,CAP*.6/.05))
        if evidence:pulses.append((at+delay,.3,0,sign*CAP*.5/.02))
    if case['kind']=='repeated':
        for at in range(1,19):pair(at+j,sgn)
        pair(21+j,-sgn);pair(22+j,-sgn);duration=26.
    else:
        pair(1.6+j,sgn,case['delay'],gate=case['kind']!='evidence_only',evidence=case['kind']!='gate_only');duration=5.
    pulses=np.array(pulses);steps=round(duration/dt);ratio=round(dt/(DT/4));z=np.empty((steps,5))
    for i in range(5):
        rng=np.random.default_rng([seed,129,2,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    initial=float(c.V[2]);tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5));t=tr[:,0];m=tr[:,3]
    def avg(a,b):return float(m[(t>a)&(t<b)].mean())
    before=avg(.8,.95);metrics=dict(startup_shift_V=before-initial,write_delta_V=avg(duration-.5,duration-.1)-before,
        stored_min_V=float(m.min()),stored_max_V=float(m.max()),dynamic_max_abs_V=float(np.max(np.abs(tr[:,[1,2,4,5]]))))
    if case['kind']=='repeated':metrics.update(plateau_V=avg(19,20),reverse_change_V=avg(21.7,21.9)-avg(20,20.9))
    row=dict(seed=seed,dt=dt,case=case,metrics=metrics,nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),pulses=pulses.tolist(),
        cost=dict(power_W=float(power),energy_J=float(power*duration),gross_charge_C=charge.tolist(),rail_hits_including_intentional_memory_saturation=int(hits)))
    return row,tr

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol();target=OUT/'rows.jsonl';assert not target.exists()
    prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/memory_limits.py','lab/retained_write_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n');start=time.monotonic()
    with target.open('x') as f:
        for seed in SEEDS:
            for case in cases():
                for dt in [DT,DT/2,DT/4]:
                    row,tr=run(seed,dt,case);f.write(json.dumps(row)+'\n');f.flush()
                    if seed==SEEDS[0] and dt==DT/4:np.savez_compressed(OUT/f'{case["id"]}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,elapsed_s=time.monotonic()-start)),flush=True)
    (OUT/'complete.json').write_text(json.dumps(dict(rows=len(SEEDS)*len(cases())*3,elapsed_s=time.monotonic()-start))+'\n')
if __name__=='__main__':main()
