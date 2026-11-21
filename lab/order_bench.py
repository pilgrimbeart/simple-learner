"""D128: explicit coincidence and mirrored temporal comparison, no Python event decisions in circuit."""
import argparse,itertools,json,math,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from motif_bench import node,edge
from dynamic_parts_bench import ROOT,CAP,DT,integrate,interval,wilson,digest,provenance
from mixed_feedback import Circuit
from units import RAIL,V_TYP,K_B,T,SLEW,C_MAX,R_MAX,TAU_LEAK,I_MIN
OUT=ROOT/'lab/v/motifs/order_v2'
PILOT=list(range(2026112100,2026112108));CONFIRM=list(range(2026112200,2026112240))

def graph():
    nodes=[node('A',.01),node('B',.01),node('trace A',.15),node('trace B',.15),node('A then B',.01),node('B then A',.01),node('coincidence',.01),node('order difference',.02)]
    edges=[edge(2,0,CAP*.6/.1),edge(3,1,CAP*.6/.1),edge(4,1,CAP*.45/.01,gate=2),edge(5,0,CAP*.45/.01,gate=3),edge(6,0,CAP*.45/.01,gate=1),edge(7,4,CAP*.3/.02),edge(7,5,-CAP*.3/.02)]
    for i,e in enumerate(edges):
        e['sigmoid']=i<5
        if i<5:e['offset']=.15;e['slope']=40.
    return dict(nodes=nodes,edges=edges)

def cases():
    cc=[dict(id=f'pair_{a}_{b}_{delay}',a=a,b=b,delay=delay) for a,b,delay in itertools.product([.35,.5],[.35,.5],[-.6,-.15,-.06,0.,.06,.15,.6])]
    return cc+[dict(id=f'single_{side}_{amp}',a=amp if side=='A' else 0.,b=amp if side=='B' else 0.,delay=0.) for side,amp in itertools.product(['A','B'],[.35,.5,.6])]

def protocol():
    return dict(graph=graph(),cases=cases(),pilot=PILOT,confirm=CONFIRM,steps=[DT,DT/2,DT/4],duration_s=2.5,
        stimuli='A and B independent input nodes; positive .04s pulses at1+jitter and1+jitter+delay, shifted together if delay negative so first at1+jitter. Jitter .001-.009s. Large singles up to .6V nominal.',
        initial='All8 nodes uniform +/-.075V; silicon noise/mismatch; baseline .7-.95s. No internal filter or Python event recognition.',
        criteria='Each seed/all steps: coincidence peak simultaneous>.15V; every single and +/- .15/.6s separated coincidence<.03V. Order difference signed mean following second event>.03V at +/- .06/.15s. Simultaneous abs order mean<.06V; far-separated abs order mean<.03V. No criterion for near-separated coincidence; finite bandwidth. All rails untouched.',
        windows='Coincidence: baseline-subtracted max from first event to last+.2s. Order: baseline-subtracted mean last+.02 to+.10s. Far test excludes first-event transient by design.',
        controls='Pilot: remove trace-building edges; order mean abs<.015V for all cases, coincidence tests unchanged. Single-input conditions are coincidence controls. No-trace is a distinct graph, not parameters changed during run.',
        prediction='Mirrored low-pass-then-gate paths approximate delay-and-correlate. V2 changes only trace leaks: time constant .15s at unchanged capacitance/current. A trace decays with .15s time constant: later second input uses remaining first trace. Reversing order reverses explicit difference node. Fast A/B overlap drives separate coincidence output. Sigmoid thresholds reduce absent-input offset leakage; no exact multiplier or motion-inference claim.',
        noise_sigma_V=math.sqrt(K_B*T/CAP),minimum_margin_V=.015,
        reliability='Wilson95 lower>=.90 for40seeds. One seed counts once across34conditions/3steps.',
        refinement='Both successive paired-seed bootstrap95 intervals inside +/-.05 for coincidence/V_TYP and order/V_TYP in every case.',
        budget='Pilot<=600s; confirm<=1200s; at most2 variants after diagnosis; one job/one maths thread.',
        source='Haag,Denk,Borst2004 https://www.pnas.org/doi/10.1073/pnas.0407368101 introduction and Fig1 construction read; mirrored asymmetric filters, products, subtraction. This bench implements approximate gated products, not a fly model.')

def build(seed,control=False):
    c=Circuit(seed=seed,streams=True,substrate='silicon');rng=np.random.default_rng([seed,128,4]);g=graph()
    for n in g['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-.075,.075))
    for i,e in enumerate(g['edges']):
        # Keep remaining per-edge draws aligned in the control by constructing all then removing in stored declaration before _ready.
        c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=0.,gate=e['gate'],sigmoid=e['sigmoid'])
    c._ready()
    if control:
        # Fixed control graph, rebuilt using the original per-edge draws; no mutation during a run.
        c.el_arr=c.el_arr[:,2:].copy();c.link=c.link[:,2:].copy();c.Vx=c.Vx[2:].copy()
        import chip
        c.cfg[1]=chip.still(c.node_arr,c.el_arr,c.link,2*RAIL)
    return c

def run(seed,dt,case,control=False):
    c=build(seed,control);jitter=np.random.default_rng([seed,128,5]).uniform(.001,.009);first=1+jitter
    ta=first+max(-case['delay'],0);tb=first+max(case['delay'],0);last=max(ta,tb);pulses=[]
    for i,(at,amp) in enumerate([(ta,case['a']),(tb,case['b'])]):
        if amp:pulses.append((at,.04,i,CAP*amp/.01))
    pulses=np.array(pulses);assert np.max(np.abs(pulses[:,3]))/CAP<=SLEW
    steps=round(2.5/dt);ratio=round(dt/(DT/4));z=np.empty((steps,8))
    for i in range(8):
        rng=np.random.default_rng([seed,128,6,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5))
    t=tr[:,0];base=tr[(t>.7)&(t<.95),1:].mean(axis=0);delta=tr[:,1:]-base
    coinc=float(np.max(delta[(t>first)&(t<last+.2),6]));order=float(delta[(t>last+.02)&(t<last+.10),7].mean())
    pair=case['a']>0 and case['b']>0;delay=case['delay'];criteria={}
    if pair and delay==0:criteria['coincidence']=coinc>.15
    elif not pair or abs(delay)>=.15:criteria['coincidence']=coinc<.03
    if control:criteria['order']=abs(order)<.015
    elif pair and 0<abs(delay)<=.15:criteria['order']=np.sign(delay)*order>.03
    elif pair:criteria['order']=abs(order)<(.06 if delay==0 else .03)
    else:criteria['order']=abs(order)<.03
    criteria['rails']=hits==0
    return dict(seed=seed,dt=dt,case=case,control=control,passed=bool(all(criteria.values())),criteria={k:bool(v) for k,v in criteria.items()},
        metrics=dict(coincidence_V=coinc,order_V=order),cost=dict(power_W=float(power),energy_J=float(power*2.5),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits)),
        nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),links=c.link.tolist(),pulses=pulses.tolist()),tr

def summary(rows,ss):
    primary=[r for r in rows if not r['control']];expected={(s,dt,c['id']) for s in ss for dt in [DT,DT/2,DT/4] for c in cases()};assert len(primary)==len(expected) and {(r['seed'],r['dt'],r['case']['id']) for r in primary}==expected
    good=[s for s in ss if all(r['passed'] for r in primary if r['seed']==s)];ref={}
    for case in cases():
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in ['coincidence_V','order_V']:
                a={r['seed']:r['metrics'][metric]/V_TYP for r in primary if r['dt']==coarse and r['case']['id']==case['id']};b={r['seed']:r['metrics'][metric]/V_TYP for r in primary if r['dt']==fine and r['case']['id']==case['id']}
                ref[f'{case["id"]}:{coarse}:{metric}']=interval([b[s]-a[s] for s in ss])
    return dict(passed=len(good),seeds=len(ss),failed_seeds=sorted(set(ss)-set(good)),wilson95=wilson(len(good),len(ss)),reliability_pass=wilson(len(good),len(ss))[0]>=.9,refinement=ref,
        refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),control_rows=sum(r['control'] for r in rows),control_pass=all(r['passed'] for r in rows if r['control']),
        power_W=interval([np.mean([r['cost']['power_W'] for r in primary if r['seed']==s and r['dt']==DT/4]) for s in ss]))

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pilot','confirm']);a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.stage=='prepare':
        for n in graph()['nodes']:assert n['C']<=C_MAX and n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK
        for e in graph()['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    if a.stage=='confirm':
        p=json.loads((OUT/'pilot.json').read_text());assert p['passed']==8 and p['control_pass'] and p['refinement_pass']
    target=OUT/f'{a.stage}.jsonl';assert not target.exists();prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/order_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];ss=PILOT if a.stage=='pilot' else CONFIRM;start=time.monotonic()
    with target.open('x') as f:
        for seed in ss:
            for control in ([False,True] if a.stage=='pilot' else [False]):
                for case in cases():
                    for dt in [DT,DT/2,DT/4]:
                        row,tr=run(seed,dt,case,control);rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(OUT/f'{a.stage}_{case["id"]}_{control}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=sum(not r['passed'] for r in rows if r['seed']==seed),elapsed_s=time.monotonic()-start)),flush=True)
    result=summary(rows,ss);result['elapsed_s']=time.monotonic()-start;(OUT/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='refinement'}),flush=True)
if __name__=='__main__':main()
