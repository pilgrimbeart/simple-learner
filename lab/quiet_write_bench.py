"""D131 split thresholded writers with explicit noisy inversion; frozen bench."""
import argparse,copy,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from retained_write_bench import definition as old_definition
from dynamic_parts_bench import ROOT,CAP,DT,integrate,interval,wilson,digest,provenance
from mixed_feedback import Circuit
from units import RAIL,V_TYP,C_MAX,R_MAX,TAU_LEAK,I_MIN,SLEW
OUT=ROOT/'lab/v/quiet_write';PILOT=list(range(2026112300,2026112308));CONFIRM=list(range(2026112400,2026112440));CASES=[-.5,-.05,0.,.05,.5]

def graph():
    g=copy.deepcopy(old_definition());g['duration']=12.;g['nodes'].append(dict(name='inverted evidence',C=CAP,R=.02/CAP,bias=0.,memory=False))
    g['edges'][0]['sigmoid']=False;g['edges'][1].update(offset=V_TYP,slope=60.,sigmoid=True)
    g['edges'] += [dict(to=5,source=0,gain=-CAP*(2.5*V_TYP)/.02,offset=0.,slope=1/(2*V_TYP),tau=0.,gate=-1,sigmoid=False),dict(to=2,source=5,gain=-8e-12,offset=V_TYP,slope=60.,tau=0.,gate=1,sigmoid=True)]
    return g

def protocol():
    return dict(graph=graph(),cases=CASES,pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],
        initial='D127 first5state initialization retained; added inverter uniform+/-.075V; stored uniform.14-.16V.',
        stimulus='Evidence amplitude case for.3s at1+jitter; eligibility+.6Vnominal .25s (1s for zero evidence stress). Opposite evidence alone at6+jitter. Probe+.5Vfor.3s at.4,3,10+jitter.12s component bench, continuous jitter. Cases +/- .05 intentionally below deadband.',
        criteria='Every case/all3steps per seed. For +/- .5: signed write in(.03,.14)V and signed response change>.025V. For0,+/-.05: abs write<.001V and abs response change<.005V. Hold span2.5-9.9s<.0001V, late response change<.005V, startup write abs<.001V, no rails.',
        controls='Pilot allcases/steps: no eligibility pulse; removed positive/negative writers. Stored delta<1mV; response change<5mV; same hold/startup/rail checks. Readout and inverter retain original per-edge mismatches.',
        prediction='Threshold V_TYP=.3V and60/V logistic: each branch falls below existing1%writer dead zone when source is about77mV below threshold. Inverter nominal -.75*tanh(evidence/.6)V makes negative .5V evidence about+.51V; weak .05V yields about.062V. Cost/lag/offset of inversion explicit. This intentionally rejects weak evidence; thresholds are innate, not learned.',
        reliability='Wilson95 lower>=.90 in40draws; paired-seed4000bootstrap bothstep-halving intervals within+/- .05 for each normalized metric/case.',
        budget='One sequential process; pilot600s,confirm1200s; at most2variants then diagnosis. No engine noise/driver parameter changes.',
        limitations='Positive stored control range; no signed learned-weight/readout claim, no useful eligibility generation, no robot learning. Pump implementation/energy absent as in existing model.')

def build(seed,control):
    c=Circuit(seed=seed,streams=True,substrate='silicon');rng=np.random.default_rng([seed,127,1]);g=graph()
    for n in g['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(.14,.16) if n['memory'] else rng.uniform(-.075,.075))
    for e in g['edges']:c.element(e['to'],e['source'],e['gain'],e['offset'],tau=0.,slope=e['slope'],gate=e['gate'],sigmoid=e['sigmoid'])
    c._ready()
    if control=='no_writers':
        keep=[0,2];c.el_arr=c.el_arr[:,keep].copy();c.link=c.link[:,keep].copy();c.Vx=c.Vx[keep].copy();import chip;c.cfg[1]=chip.still(c.node_arr,c.el_arr,c.link,2*RAIL)
    return c

def run(seed,dt,amplitude,control):
    c=build(seed,control);initial=float(c.V[2]);j=np.random.default_rng([seed,131,1]).uniform(.001,.009);pulses=[]
    if amplitude:pulses +=[(1+j,.3,0,CAP*amplitude/.02),(6+j,.3,0,-CAP*amplitude/.02)]
    if control!='no_gate':pulses.append((1+j,1. if amplitude==0 else .25,1,CAP*.6/.05))
    for at in [.4,3,10]:pulses.append((at+j,.3,3,CAP*.5/.02))
    pulses=np.array(pulses);steps=round(12/dt);ratio=round(dt/(DT/4));z=np.empty((steps,6))
    for i in range(6):
        rng=np.random.default_rng([seed,131,2,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5));t=tr[:,0];m=tr[:,3];response=tr[:,5]
    def avg(v,a,b):return float(v[(t>a)&(t<b)].mean())
    before=avg(m,.8,.95);after=avg(m,2.5,2.9);delta=after-before;hold=float(np.ptp(m[(t>2.5)&(t<9.9)]));reads=[avg(response,a+j+.15,a+j+.28) for a in [.4,3,10]];change=reads[1]-reads[0];late=reads[2]-reads[1];startup=before-initial
    useful=abs(amplitude)==.5 and control=='none';sgn=np.sign(amplitude)
    ok=(.03<sgn*delta<.14 and sgn*change>.025) if useful else (abs(delta)<.001 and abs(change)<.005)
    ok=bool(ok and hold<.0001 and abs(late)<.005 and abs(startup)<.001 and hits==0)
    metrics=dict(write_V=delta,hold_V=hold,readout_V=change,late_readout_V=late,startup_V=startup)
    return dict(seed=seed,dt=dt,amplitude=amplitude,control=control,passed=ok,metrics=metrics,cost=dict(power_W=float(power),energy_J=float(power*12),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits)),nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist(),pulses=pulses.tolist()),tr

def summary(rows,ss):
    rr=[r for r in rows if r['control']=='none'];expected={(s,dt,a) for s in ss for dt in [DT,DT/2,DT/4] for a in CASES};assert len(rr)==len(expected) and {(r['seed'],r['dt'],r['amplitude']) for r in rr}==expected
    good=[s for s in ss if all(r['passed'] for r in rr if r['seed']==s)];ref={}
    for amp in CASES:
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in rr[0]['metrics']:
                a={r['seed']:r['metrics'][metric]/V_TYP for r in rr if r['dt']==coarse and r['amplitude']==amp};b={r['seed']:r['metrics'][metric]/V_TYP for r in rr if r['dt']==fine and r['amplitude']==amp};ref[f'{amp}:{coarse}:{metric}']=interval([b[s]-a[s] for s in ss])
    return dict(passed=len(good),seeds=len(ss),failed_seeds=sorted(set(ss)-set(good)),wilson95=wilson(len(good),len(ss)),reliability_pass=wilson(len(good),len(ss))[0]>=.9,refinement=ref,refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),
        control_rows=sum(r['control']!='none' for r in rows),control_pass=all(r['passed'] for r in rows if r['control']!='none'),power_W=interval([np.mean([r['cost']['power_W'] for r in rr if r['seed']==s and r['dt']==DT/4]) for s in ss]))

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pilot','confirm']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        for n in graph()['nodes']:assert n['C']<=C_MAX and (n['memory'] or n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK)
        for e in graph()['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    if a.stage=='confirm':
        p=json.loads((OUT/'pilot.json').read_text());assert p['passed']==8 and p['control_pass'] and p['refinement_pass']
    target=OUT/f'{a.stage}.jsonl';assert not target.exists();prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/quiet_write_bench.py','lab/retained_write_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n');ss=PILOT if a.stage=='pilot' else CONFIRM;rows=[];start=time.monotonic()
    with target.open('x') as f:
        for seed in ss:
            for control in (['none','no_gate','no_writers'] if a.stage=='pilot' else ['none']):
                for amp in CASES:
                    for dt in [DT,DT/2,DT/4]:
                        r,tr=run(seed,dt,amp,control);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(OUT/f'{a.stage}_{amp}_{control}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=sum(not r['passed'] for r in rows if r['seed']==seed),elapsed_s=time.monotonic()-start)),flush=True)
    result=summary(rows,ss);result['elapsed_s']=time.monotonic()-start;(OUT/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='refinement'}),flush=True)
if __name__=='__main__':main()
