"""D136 unchanged circuit, paired gap diagnostic; no new construction."""
import json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oneshot_bench as b
from dynamic_parts_bench import provenance,digest
OUT=b.ROOT/'lab/v/pulse_recovery';GAPS=[.02,.05,.1,.2,.5,1.]

def run(seed,case,gap):
    dt=b.DT/4;c=b.build(seed,False);first=1+np.random.default_rng([seed,132,2]).uniform(.001,.009)
    starts=[first,first+case['duration']+gap];triggers=starts if case['sign']>0 else [at+case['duration'] for at in starts]
    duration=3+2*case['duration']+.02 # Preserve the complete old noise stream for every gap.
    pulses=np.array([[at,case['duration'],0,case['sign']*b.CAP*case['amplitude']/.01] for at in starts]);steps=round(duration/dt);z=np.empty((steps,4))
    for i in range(4):z[:,i]=np.random.default_rng([seed,132,3,i]).standard_normal(steps)
    tr,power,charge,hits=b.integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5))
    m=b.measure(tr,triggers);events=m['events'];matched=[]
    for at in triggers:matched.append([i for i,e in enumerate(events) if 0<=e['start_s']-at<.15])
    used={i for group in matched for i in group};idx=np.searchsorted(tr[:,0],triggers[1])-1
    merged=sum(any(e['start_s']<at<e['start_s']+e['width_s'] for e in events) for at in triggers[1:])
    return dict(seed=seed,case=case,gap_s=gap,positive_change_spacing_s=triggers[1]-triggers[0],triggers=triggers,metrics=m,missed=sum(not x for x in matched),extra=len(events)-len(used),merged=merged,state_before_second_positive_change_V=tr[idx,1:].tolist(),rail_hits=int(hits),power_W=float(power)),tr

def main():
    OUT.mkdir(exist_ok=True);spec=dict(gaps_s=GAPS,seeds=b.PILOT,cases=b.cases(),dt_s=b.DT/4,source='lab/oneshot_bench.py',criterion='Unchanged absolute pulse metrics; missed=no event start within150ms; extra=event outside both windows; merged=earlier event remains active at second positive change. Gap is input-off time, not positive-event spacing.',budget_s=600,limitations='Development draws and one previously tested timestep; diagnostic, not new robustness evidence.')
    with (OUT/'protocol.json').open('x') as f:json.dump(spec,f,indent=2)
    prov=provenance();prov['files'].update({p:digest(b.ROOT/p) for p in ['lab/pulse_recovery.py','lab/oneshot_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    old=[json.loads(x) for x in (b.OUT/'pilot.jsonl').read_text().splitlines()];ref={(r['seed'],r['case']['id']):r for r in old if not r['control'] and r['dt']==b.DT/4};rows=[];start=time.monotonic()
    with (OUT/'rows.jsonl').open('x') as f:
        for gap in reversed(GAPS): # Original replay must pass before interpreting smaller gaps.
            for seed in b.PILOT:
                for case in b.cases():
                    r,tr=run(seed,case,gap)
                    if gap==1:assert r['metrics']==ref[seed,case['id']]['metrics']
                    rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                    if seed==b.PILOT[0] and case['amplitude']==.4 and case['duration']==.5:np.savez_compressed(OUT/f'{gap}_{case["sign"]}.npz',trace=tr)
            rr=[r for r in rows if r['gap_s']==gap];print(json.dumps(dict(gap_s=gap,passes=sum(r['metrics']['passed'] and not r['rail_hits'] for r in rr),cases=len(rr),missed=sum(r['missed'] for r in rr),extra=sum(r['extra'] for r in rr),merged=sum(r['merged'] for r in rr),elapsed_s=time.monotonic()-start)),flush=True)
    (OUT/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in OUT.glob('*.npz')},indent=2)+'\n')
if __name__=='__main__':main()
