"""D145: explicit complementary control nodes, unchanged noisy circuit engine."""
import argparse,itertools,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,integrate,interval,wilson,digest,provenance
from motif_bench import node,edge
from mixed_feedback import Circuit
from units import RAIL,V_TYP,C_MAX,R_MAX,TAU_LEAK,I_MIN,SLEW,K_B,T,Q_SI
OUT=ROOT/'lab/v/signed_control';PILOT=list(range(2026112900,2026112908));CONFIRM=list(range(2026113000,2026113040))
LEVELS=[-.3,-.15,0.,.15,.3]
def graph():
    ns=[node('source',.005),node('control',.005),node('positive gate',.01),node('negative gate',.01),node('output',.01)]
    for i in [2,3]:ns[i]['bias']=CAP*.15/.01
    return dict(nodes=ns,edges=[edge(2,1,CAP*.3/.01),edge(3,1,-CAP*.3/.01),edge(4,0,CAP*.3/.01,gate=2),edge(4,0,-CAP*.3/.01,gate=3)])
def cases():return [dict(x=x,y=y,id=f'{i}_{j}') for i,x in enumerate(LEVELS) for j,y in enumerate(LEVELS)]
def protocol():return dict(graph=graph(),cases=cases(),pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],
    stimuli='Both .6s pulses start .2+jitter(.001,.009)s; raw mean onset+.2..+.5s; recovery1.1..1.2s; starts uniform+/-.075V.',
    criteria='All nonzero xy: sign(xy)*mean>.02V; control contrasts at +/-.15 >.04V and +/-.30>.08V after sign(x). Recovery to own zero-zero condition within .01V. No rails.',
    control='Remove only y-to-gate connections after building aligned arrays. Output spread over control levels at fixed source <.005V. Biases remain; no zero-output claim.',
    refinement='Both paired-seed bootstrap95 intervals inside +/-.05 for output and recovery divided by V_TYP, each of25 cases.',
    reliability='All conditions and3steps per seed, Wilson95 lower>=.90 on40fresh draws.',budget='pilot600s confirm1200s; two variants maximum after diagnosis',
    noise=dict(thermal_sigma_V=math.sqrt(K_B*T/CAP),output_full_current_sigma_V=math.sqrt(K_B*T/CAP+Q_SI*4*(CAP*.3/.01)/(2*(CAP/.01)*CAP))),
    limitation='Signed saturating control only; zero-input feedthrough reported, not removed. No exact multiplier, retained signed weight, calibration or reward learning.')
def build(seed,control=False):
    c=Circuit(seed=seed,streams=True,substrate='silicon');rng=np.random.default_rng([seed,145,1]);g=graph()
    for n in g['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-.075,.075))
    for e in g['edges']:c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=0.,gate=e['gate'])
    c._ready()
    if control:
        import chip
        c.el_arr=c.el_arr[:,2:].copy();c.link=c.link[:,2:].copy();c.Vx=c.Vx[2:].copy();c.cfg[1]=chip.still(c.node_arr,c.el_arr,c.link,2*RAIL)
    return c

def run(seed,dt,case,control):
    c=build(seed,control);start=.2+np.random.default_rng([seed,145,2]).uniform(.001,.009)
    pulses=np.array([[start,.6,0,CAP*case['x']/.005],[start,.6,1,CAP*case['y']/.005]])
    steps=round(1.2/dt);ratio=round(dt/(DT/4));z=np.empty((steps,5))
    for i in range(5):z[:,i]=np.random.default_rng([seed,145,3,i]).standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5))
    t=tr[:,0];out=tr[:,-1];mean=float(out[(t>start+.2)&(t<start+.5)].mean());recovery=float(out[t>1.1].mean())
    return dict(seed=seed,dt=dt,case=case,control=control,start_s=start,mean_V=mean,recovery_V=recovery,
        nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist(),
        cost=dict(power_W=float(power),energy_J=float(power*1.2),gross_charge_C=charge.tolist(),crossings=c.spikes.tolist(),rail_hits=hits)),tr

def assess(rr,control):
    assert len(rr)==25;lookup={(r['case']['x'],r['case']['y']):r for r in rr};fail=[]
    base=lookup[0.,0.]['recovery_V']
    for r in rr:
        x,y=r['case']['x'],r['case']['y']
        if not control and x*y!=0 and np.sign(x*y)*r['mean_V']<=.02:fail.append(['sign',x,y,r['mean_V']])
        if abs(r['recovery_V']-base)>=.01:fail.append(['recovery',x,y,r['recovery_V']-base])
        if r['cost']['rail_hits']:fail.append(['rails',x,y])
    for x in LEVELS:
        if control:
            spread=np.ptp([lookup[x,y]['mean_V'] for y in LEVELS])
            if spread>=.005:fail.append(['control_spread',x,float(spread)])
        elif x!=0:
            for y,margin in [(.15,.04),(.3,.08)]:
                contrast=np.sign(x)*(lookup[x,y]['mean_V']-lookup[x,-y]['mean_V'])
                if contrast<=margin:fail.append(['contrast',x,y,float(contrast)])
    return fail

def summary(rows,seeds):
    primary=[r for r in rows if not r['control']];expected={(s,dt,c['id']) for s in seeds for dt in [DT,DT/2,DT/4] for c in cases()}
    assert len(primary)==len(expected) and {(r['seed'],r['dt'],r['case']['id']) for r in primary}==expected
    groups=[dict(seed=s,dt=dt,control=ctrl,failures=assess([r for r in rows if r['seed']==s and r['dt']==dt and r['control']==ctrl],ctrl)) for s in seeds for dt in [DT,DT/2,DT/4] for ctrl in sorted({r['control'] for r in rows})]
    good=[s for s in seeds if all(not r['failures'] for r in groups if r['seed']==s and not r['control'])];ref={}
    for case in cases():
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in ['mean_V','recovery_V']:
                a={r['seed']:r[metric]/V_TYP for r in primary if r['dt']==coarse and r['case']['id']==case['id']};b={r['seed']:r[metric]/V_TYP for r in primary if r['dt']==fine and r['case']['id']==case['id']};ref[f'{case["id"]}:{coarse}:{metric}']=interval([b[s]-a[s] for s in seeds])
    zero=[r['mean_V'] for r in primary if r['dt']==DT/4 and r['case']['x']*r['case']['y']==0]
    return dict(passed=len(good),seeds=len(seeds),failed_seeds=sorted(set(seeds)-set(good)),wilson95=wilson(len(good),len(seeds)),reliability_pass=wilson(len(good),len(seeds))[0]>=.9,
        refinement=ref,refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),control_pass=all(not r['failures'] for r in groups if r['control']),groups=groups,
        null_input_output_range_V=[min(zero),max(zero)],power_W=interval([np.mean([r['cost']['power_W'] for r in primary if r['seed']==s and r['dt']==DT/4]) for s in seeds]))

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pilot','confirm']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    if a.stage=='prepare':
        for n in graph()['nodes']:assert n['C']<=C_MAX and n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK
        for e in graph()['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    if a.stage=='confirm':
        prior=json.loads((OUT/'pilot.json').read_text());assert prior['passed']==8 and prior['control_pass'] and prior['refinement_pass']
    target=OUT/f'{a.stage}.jsonl';assert not target.exists();prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/signed_control_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];ss=PILOT if a.stage=='pilot' else CONFIRM;start=time.monotonic()
    with target.open('x') as f:
        for seed in ss:
            for control in ([False,True] if a.stage=='pilot' else [False]):
                for case in cases():
                    for dt in [DT,DT/2,DT/4]:
                        r,tr=run(seed,dt,case,control);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(OUT/f'{a.stage}_{case["id"]}_{control}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=sum(len(assess([r for r in rows if r['seed']==seed and r['dt']==dt and r['control']==False],False)) for dt in [DT,DT/2,DT/4]),elapsed_s=time.monotonic()-start)),flush=True)
    result=summary(rows,ss);result['elapsed_s']=time.monotonic()-start;(OUT/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['groups','refinement']}),flush=True)
if __name__=='__main__':main()
