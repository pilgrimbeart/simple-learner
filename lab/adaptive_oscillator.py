"""D162 explicit retained bias adaptation; unchanged noisy circuit integrator."""
import argparse,copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,definitions,build as oldbuild,stimuli,integrate,metrics,interval,wilson,digest,provenance
from motif_bench import edge
from mixed_feedback import Circuit
from units import RAIL,V_TYP,I_MIN,SLEW,C_MAX,R_MAX,Q_SI
import chip
OUT=ROOT/'lab/v/adaptive_oscillator';SEEDS=list(range(51000,51008))+[51011,51036]
def graph():
    g=copy.deepcopy(definitions()['oscillator']);g['nodes'].append(dict(name='bias memory',C=CAP,R=None,bias=0.,memory=True))
    g['edges'] += [edge(0,2,-abs(g['edges'][1]['gain']),V_TYP),edge(2,0,CAP*V_TYP/5.,V_TYP)]
    return g

def protocol():return dict(graph=graph(),seeds=SEEDS,arms=['original','adaptive','writer_removed'],steps_s=[DT,DT/2,DT/4],duration_s=100.,
    criteria='Original D126 metrics unchanged: before10..45s and after55..95s, amp>.15V, >=10cycles, CV<.1; frequency and amplitude post/pre in(.9,1.1); no rail hits. All adaptive cases required.',
    refinement='Both successive paired-seed bootstrap95 intervals inside ±.05 on original normalized metrics',control='Removed writer holds memory exactly; original metrics reproduce D126 within1e-12; full original/removal behavioural denominators reported',
    purpose='Diagnostic local bias adaptation, not task learning or global oscillation proof',writer_shot_sigma_1s_V=math.sqrt(Q_SI*CAP*V_TYP/5)/CAP,budget_s=600)

def build(seed,arm):
    if arm=='original':return oldbuild('oscillator',definitions()['oscillator'],seed)
    c=Circuit(seed=seed,streams=True,substrate='silicon');g=graph();rng=np.random.default_rng([seed,126,1])
    for i,n in enumerate(g['nodes']):
        initial=rng.uniform(-V_TYP/4,V_TYP/4) if i<2 else np.random.default_rng([seed,162,1]).uniform(-V_TYP/4,V_TYP/4)
        c.node(**n,lo=-RAIL,hi=RAIL,start=initial)
    for e in g['edges']:c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=e['tau'],gate=e['gate'])
    c._ready()
    if arm=='writer_removed':
        c.el_arr=c.el_arr[:,:-1].copy();c.link=c.link[:,:-1].copy();c.Vx=c.Vx[:-1].copy();c.cfg[1]=chip.still(c.node_arr,c.el_arr,c.link,2*RAIL)
    return c

def run(seed,arm,dt):
    c=build(seed,arm);initial=c.V.copy();pulses,sine,shift=stimuli('oscillator',seed);steps=round(100/dt);ratio=round(dt/(DT/4));z=np.empty((steps,len(c.V)))
    for i in range(len(c.V)):
        z[:,i]=np.random.default_rng([seed,126,3,i]).standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,sine)
    cost=dict(power_W=float(power),energy_J=float(power*100),gross_charge_C=charge.tolist(),crossings=c.spikes.tolist(),rail_hits=int(hits),shift=shift)
    m=metrics('oscillator',[tr],[cost]);memory={}
    if arm!='original':
        late=tr[:,0]>200/3;memory=dict(range_V=[float(tr[:,-1].min()),float(tr[:,-1].max())],change_V=float(tr[-1,-1]-initial[-1]),last_third_slope_V_per_s=float(np.polyfit(tr[late,0],tr[late,-1],1)[0]),held_exactly=bool(np.all(tr[:,-1]==initial[-1])))
    return dict(seed=seed,arm=arm,dt=dt,metrics=m,cost=cost,memory=memory,nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist()),tr

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pilot']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        for n in graph()['nodes']:assert n['C']<=C_MAX and(n['R'] is None or n['R']<=R_MAX)
        for e in graph()['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    old=[json.loads(l) for l in (ROOT/'lab/v/dynamic_parts/confirm_v2.jsonl').read_text().splitlines()];lookup={(r['seed'],r['dt']):r for r in old if r['name']=='oscillator'}
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),ROOT/'lab/motif_bench.py',ROOT/'lab/v/dynamic_parts/confirm_v2.jsonl']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];start=time.monotonic()
    with (OUT/'rows.jsonl').open('x') as f:
      for seed in SEEDS:
       for arm in protocol()['arms']:
        for dt in protocol()['steps_s']:
            r,tr=run(seed,arm,dt)
            if arm=='original':assert all(abs(r['metrics']['values'][k]-v)<1e-12 for k,v in lookup[seed,dt]['metrics']['values'].items())
            if arm=='writer_removed':assert r['memory']['held_exactly']
            rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
            if dt==DT/4:np.savez_compressed(OUT/f'{seed}_{arm}.npz',trace=tr)
            if time.monotonic()-start>600:raise RuntimeError('Pilot budget exceeded')
        print(seed,arm,r['metrics']['passed'],round(time.monotonic()-start,1),flush=True)
    result={}
    for arm in protocol()['arms']:
        rr=[r for r in rows if r['arm']==arm];good=[s for s in SEEDS if all(r['metrics']['passed'] for r in rr if r['seed']==s)];ref={}
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
          for key in rr[0]['metrics']['normalized']:
            ca={r['seed']:r['metrics']['normalized'][key] for r in rr if r['dt']==coarse};fi={r['seed']:r['metrics']['normalized'][key] for r in rr if r['dt']==fine}
            ref[f'{coarse}:{key}']=interval([fi[s]-ca[s] for s in SEEDS])
        result[arm]=dict(passed=len(good),draws=len(SEEDS),failed_seeds=sorted(set(SEEDS)-set(good)),refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),refinement=ref,power_W=interval([r['cost']['power_W'] for r in rr if r['dt']==DT/4]))
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({a:{k:v for k,v in r.items() if k!='refinement'} for a,r in result.items()},indent=2))
if __name__=='__main__':main()
