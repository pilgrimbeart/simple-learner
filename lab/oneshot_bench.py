"""D132 adaptive pulse generator with absolute voltage readout; fixed tests."""
import argparse,itertools,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,integrate,interval,wilson,digest,provenance
from motif_bench import node,edge
from mixed_feedback import Circuit
from units import RAIL,C_MAX,R_MAX,TAU_LEAK,I_MIN,SLEW,V_TYP
OUT=ROOT/'lab/v/oneshot_v1';PILOT=list(range(2026112500,2026112508));CONFIRM=list(range(2026112600,2026112640))

def graph():
    return dict(nodes=[node('input',.01),dict(name='integral',C=CAP,R=None,bias=0.,memory=True),node('adaptive response',.02),node('pulse output',.005)],
        edges=[edge(2,0,CAP*.9/.02),edge(2,1,-CAP*1.35/.02),edge(1,2,CAP*.15/.08,.15),dict(to=3,source=2,gain=CAP*.6/.005,offset=.2,slope=40.,tau=0.,gate=-1,sigmoid=True)])

def cases():return [dict(id=f'{s}_{a}_{d}',sign=s,amplitude=a,duration=d) for s,a,d in itertools.product([-1,1],[.4,.55],[.5,2.])]
def protocol():
    return dict(graph=graph(),cases=cases(),pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],
        stimuli='Two equal input pulses: first1+jitter, second first+duration+1s; each lasts case duration. Positive trigger is rising onset for positive pulses and return to zero for negative pulses. Run ends1s after second offset.',
        criteria='Absolute output, no baseline subtraction: exactly2excursions above .25V after .8s, each starts within .15s after its positive input change, peak>.35V, width between .01 and .25s, later returns below .1V. Outside .3s following positive changes output<.05V. No rail hits. This is bounded pulse width, not amplitude-independent fixed width or demonstrated regenerative excitability.',
        measurement='Output crossings linearly interpolated at .001s recording; arm above .25V, re-arm below .1V. Width from upward .25V crossing to downward .1V. Each event represented by actual absolute node voltage; observer only measures.',
        control='Pilot positive pulses only: remove integral writer. At least one pulse remains above .25V for >.3s or no normal two-pulse response; the bounded one-shot criteria must fail. No changed parameters during run.',
        prediction='Input/output integral feedback provides adaptation. Stronger inhibitory authority bounds integral demands for larger input amplitudes. Approx local adaptive poles -25 +/-46.8i/s. Thresholded readout should emit one finite pulse per positive step and remain quiet during held input. Component offset, short pulse/lag or input saturation can defeat it.',
        initial='Each node uniform +/-.075V; all original silicon mismatch/noise; continuous stimulus jitter .001-.009s.',
        noise='Microvolt thermal state variation vs .05V quiet and .35V peak margins; gate transfer offsets dominate likely failures.',
        reliability='All8conditions/all3steps per seed; Wilson95 lower>=.90 in40newdraws. Both paired-seed bootstrap95 step-halving intervals inside+/-.05 on declared normalized metrics.',
        budget='One sequential pilot<=600s, confirmation<=1200s, at most2variants with diagnosis before second. No robot lives.',
        literature='TI SN74LVC1G123 product description checked: one-shot pulse generation and RC duration are established. This graph is an adaptive pulse generator, not that chip or a proof of all-or-none excitability.')

def build(seed,control):
    c=Circuit(seed=seed,streams=True,substrate='silicon');g=graph();rng=np.random.default_rng([seed,132,1])
    for n in g['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-.075,.075))
    for e in g['edges']:c.element(e['to'],e['source'],e['gain'],e['offset'],tau=0.,slope=e['slope'],gate=e['gate'],sigmoid=e.get('sigmoid',False))
    c._ready()
    if control:
        keep=[0,1,3];c.el_arr=c.el_arr[:,keep].copy();c.link=c.link[:,keep].copy();c.Vx=c.Vx[keep].copy();import chip;c.cfg[1]=chip.still(c.node_arr,c.el_arr,c.link,2*RAIL)
    return c

def measure(tr,triggers):
    t=tr[:,0];y=tr[:,-1];events=[];active=False;peak=0.;start=0.
    for i in np.flatnonzero(t>.8):
        if not active and y[i-1]<=.25<y[i]:
            active=True;start=float(t[i-1]+(.25-y[i-1])/(y[i]-y[i-1])*(t[i]-t[i-1]));peak=float(y[i])
        elif active:
            peak=max(peak,float(y[i]))
            if y[i]<.1<=y[i-1]:
                end=float(t[i-1]+(.1-y[i-1])/(y[i]-y[i-1])*(t[i]-t[i-1]));events.append(dict(start_s=start,width_s=end-start,peak_V=peak));active=False
    if active:events.append(dict(start_s=start,width_s=float(t[-1]-start),peak_V=peak,unfinished=True))
    quiet=t>.8
    for at in triggers:quiet &= ~((t>=at)&(t<=at+.3))
    maximum=float(np.max(y[quiet]));ok=len(events)==2 and maximum<.05
    if len(events)==2:
        ok=ok and all(0<=e['start_s']-at<.15 and .01<e['width_s']<.25 and e['peak_V']>.35 and not e.get('unfinished',False) for e,at in zip(events,triggers))
    # Continuous summary metrics remain defined even for missing/extra events.
    norm=dict(maximum=y[t>.8].max()/V_TYP,quiet=maximum/V_TYP,mean_level=float(y[t>.8].mean())/V_TYP)
    for j,at in enumerate(triggers):
        win=(t>=at)&(t<at+.3);norm[f'peak_{j}']=float(np.max(y[win]))/V_TYP;norm[f'area_{j}']=float(np.trapezoid(y[win],t[win]))/(.3*V_TYP)
    return dict(passed=bool(ok),events=events,quiet_max_V=maximum,normalized={k:float(v) for k,v in norm.items()})

def run(seed,dt,case,control):
    c=build(seed,control);first=1+np.random.default_rng([seed,132,2]).uniform(.001,.009);starts=[first,first+case['duration']+1];triggers=starts if case['sign']>0 else [at+case['duration'] for at in starts];duration=3+2*case['duration']+.02
    pulses=np.array([[at,case['duration'],0,case['sign']*CAP*case['amplitude']/.01] for at in starts]);steps=round(duration/dt);ratio=round(dt/(DT/4));z=np.empty((steps,4))
    for i in range(4):
        rng=np.random.default_rng([seed,132,3,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5));m=measure(tr,triggers)
    ok=(not m['passed']) if control else m['passed'];ok=bool(ok and (hits==0 if not control else True))
    return dict(seed=seed,dt=dt,case=case,control=control,passed=ok,metrics=m,triggers=triggers,pulses=pulses.tolist(),nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist(),cost=dict(power_W=float(power),energy_J=float(power*duration),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits))),tr

def summary(rows,ss):
    rr=[r for r in rows if not r['control']];expected={(s,dt,c['id']) for s in ss for dt in [DT,DT/2,DT/4] for c in cases()};assert len(rr)==len(expected) and {(r['seed'],r['dt'],r['case']['id']) for r in rr}==expected
    good=[s for s in ss if all(r['passed'] for r in rr if r['seed']==s)];ref={}
    for case in cases():
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in rr[0]['metrics']['normalized']:
                a={r['seed']:r['metrics']['normalized'][metric] for r in rr if r['dt']==coarse and r['case']['id']==case['id']};b={r['seed']:r['metrics']['normalized'][metric] for r in rr if r['dt']==fine and r['case']['id']==case['id']};ref[f'{case["id"]}:{coarse}:{metric}']=interval([b[s]-a[s] for s in ss])
    return dict(passed=len(good),seeds=len(ss),failed_seeds=sorted(set(ss)-set(good)),wilson95=wilson(len(good),len(ss)),reliability_pass=wilson(len(good),len(ss))[0]>=.9,refinement=ref,refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),control_rows=sum(r['control'] for r in rows),control_pass=all(r['passed'] for r in rows if r['control']),power_W=interval([np.mean([r['cost']['power_W'] for r in rr if r['seed']==s and r['dt']==DT/4]) for s in ss]))

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
    target=OUT/f'{a.stage}.jsonl';assert not target.exists();prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/oneshot_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n');ss=PILOT if a.stage=='pilot' else CONFIRM;rows=[];start=time.monotonic()
    with target.open('x') as f:
        for seed in ss:
            for control in ([False,True] if a.stage=='pilot' else [False]):
                for case in cases():
                    if control and case['sign']<0:continue
                    for dt in [DT,DT/2,DT/4]:
                        r,tr=run(seed,dt,case,control);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(OUT/f'{a.stage}_{case["id"]}_{control}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=sum(not r['passed'] for r in rows if r['seed']==seed),elapsed_s=time.monotonic()-start)),flush=True)
    result=summary(rows,ss);result['elapsed_s']=time.monotonic()-start;(OUT/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='refinement'}),flush=True)
if __name__=='__main__':main()
