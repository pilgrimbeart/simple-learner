"""D130: fixed small starting-state audit of existing oscillator draws; no repair/tuning."""
import argparse,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,OUT as ORIGINAL,DT,definitions,build,stimuli,integrate,oscillation,digest,provenance
OUT=ROOT/'lab/v/oscillator_basins';SEEDS=[51005,51006,51011,51036]
STARTS=['original','rest','near_rest','far_positive','far_negative']

def protocol():
    return dict(seeds=SEEDS,starts=STARTS,steps=[DT,DT/2,DT/4],duration_s=100.,graph=definitions()['oscillator'],
        initials='Original D126 seeded start; D127 solved equilibrium; equilibrium +(.005,0)V; (+.4,-.1)V;(-.4,+.1)V. Set only before simulation.',
        perturbation='Unchanged D126 current pulse at50+jitter s. Same original Brownian streams and mismatch, not new independent draws.',
        criteria='Classify windows10-45s,55-95s separately: cycle if amplitude>.15V, >=10cycles, periodCV<.1; rest if amplitude<.01V; otherwise unresolved. Do not demand phase alignment. Original-start finest metrics must reproduce old values.',
        prediction='Stable equilibrium predicts small perturbations decay locally. Different persistent behaviour from another start would support coexistence on these draws. The50s pulse can cross a basin boundary. No global uniqueness, exhaustive basin map, new reliability claim or repair.',
        noise='Original silicon thermal/shot noise, .005V local perturbation above microvolt fluctuations; no noiseless replay.',
        budget='One sequential batch <=120s wall time,60trajectories fixed; no added states/seeds or retries. No code/noise/body modification.')

def run(seed,mode,dt,roots):
    spec=definitions()['oscillator'];c=build('oscillator',spec,seed)
    if mode=='rest':c.V[:]=roots[seed]
    if mode=='near_rest':c.V[:]=np.array(roots[seed])+[.005,0]
    if mode=='far_positive':c.V[:]=[.4,-.1]
    if mode=='far_negative':c.V[:]=[-.4,.1]
    initial=c.V.copy();pulses,sine,_=stimuli('oscillator',seed);steps=round(100/dt);ratio=round(dt/(DT/4));z=np.empty((steps,2))
    for i in range(2):
        rng=np.random.default_rng([seed,126,3,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,sine);windows={}
    for label,a,b in [('before',10,45),('after',55,95)]:
        f,cv,amp,n=oscillation(tr[:,0],tr[:,1],a,b);state='cycle' if amp>.15 and n>=10 and cv<.1 else 'rest' if amp<.01 else 'unresolved'
        windows[label]=dict(state=state,frequency_Hz=f if state=='cycle' else None,period_cv=cv,amplitude_V=amp,cycles=n)
    return dict(seed=seed,initial_mode=mode,initial_V=initial.tolist(),dt=dt,windows=windows,power_W=float(power),rail_hits=int(hits)),tr

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol();target=OUT/'rows.jsonl';assert not target.exists()
    analysis=json.loads((ORIGINAL/'margin_v2.json').read_text())['analysis'];roots={r['seed']:r['cases']['actual']['root_V'] for r in analysis};prior=[json.loads(l) for l in (ORIGINAL/'confirm_v2.jsonl').read_text().splitlines()]
    prov=provenance();prov['files']['lab/oscillator_basins.py']=digest(__file__);prov['roots_sha256']=digest(ORIGINAL/'margin_v2.json');prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n');start=time.monotonic();rows=[]
    with target.open('x') as f:
        for seed in SEEDS:
            for mode in STARTS:
                for dt in [DT,DT/2,DT/4]:
                    r,tr=run(seed,mode,dt,roots)
                    if mode=='original' and dt==DT/4:
                        old=next(x for x in prior if x['name']=='oscillator' and x['seed']==seed and x['dt']==dt)['metrics']['values'];assert abs(old['amplitude_V']-r['windows']['before']['amplitude_V'])<1e-12 and abs(old['post_amplitude_V']-r['windows']['after']['amplitude_V'])<1e-12
                    rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                    if dt==DT/4:np.savez_compressed(OUT/f'{seed}_{mode}.npz',trace=tr)
                print(json.dumps(dict(seed=seed,start=mode,before=r['windows']['before']['state'],after=r['windows']['after']['state'],elapsed_s=time.monotonic()-start)),flush=True)
    assert len(rows)==60;(OUT/'complete.json').write_text(json.dumps(dict(rows=len(rows),elapsed_s=time.monotonic()-start))+'\n')
if __name__=='__main__':main()
