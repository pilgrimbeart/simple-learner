"""D128 fixed motif benches. No optimisation; all stochastic dynamics call original _step."""
import argparse, json, math, sys,time,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,integrate,interval,wilson,digest,provenance
from mixed_feedback import Circuit
from units import RAIL,V_TYP,C_MAX,R_MAX,TAU_LEAK,I_MIN,SLEW,K_B,T
OUT=ROOT/'lab/v/motifs'

def node(name,tau):return dict(name=name,C=CAP,R=tau/CAP,bias=0.,memory=False)
def edge(to,source,gain,scale=.3,gate=-1):return dict(to=to,source=source,gain=gain,offset=0.,slope=1/scale,tau=0.,gate=gate)

def graph(name):
    if name=='change_v2':
        return dict(nodes=[node('input',.01),dict(name='integral',C=CAP,R=None,bias=0.,memory=True),node('response',.02)],
            edges=[edge(2,0,CAP*.6/.02),edge(2,1,-CAP*.6/.02),edge(1,2,CAP*.15/.08,.15)])
    assert name=='change_v1'
    return dict(nodes=[node('input',.01),node('fast',.02),node('slow',.2),node('response',.01)],
        edges=[edge(1,0,CAP*.3/.02),edge(2,0,CAP*.3/.2),edge(3,1,CAP*.4/.01,.15),edge(3,2,-CAP*.4/.01,.15)])

def cases(name):return [dict(id=f'{sgn}_{a}_{d}',sign=sgn,amplitude=a,duration=d) for sgn,a,d in itertools.product([-1,1],[.08,.16],[1.,2.])]
def seeds(name,stage):return list(range(2026111900,2026111908)) if stage=='pilot' else list(range(2026112000,2026112040))

def protocol(name):
    p=dict(name=name,graph=graph(name),cases=cases(name),steps=[DT,DT/2,DT/4],pilot=seeds(name,'pilot'),confirm=seeds(name,'confirm'),
        criteria='Every case: signed onset and opposite offset peaks >.025 V; sustained change from baseline <.35 times EACH peak; after return abs residual <.01 V. Zero rail hits. All cases/all steps per seed. Wilson95 lower>=.90 in40 seeds.',
        control='Remove slow-to-output connection: sustained/onset>.70, onset>.025 V; zero rails. Pilot seeds only, all cases/steps.',
        windows='Input at1+jitter(.001,.009)s; baseline .7-.95s; onset start+.01 to+.4; sustained end-.2 to-.02; offset end+.01 to+.4; recovery end+.8 to+1. Simulation ends input duration+2.2s. Max/min peaks taken on recorded .001s samples.',
        prediction='Linear matched branches: K[(1+s*.02)^-1-(1+s*.2)^-1], with .01s input/output lags; nominal DC rejection. Mismatched DC gains leave a persistent residual. Saturation/offset alternatives may reduce transients. No robust perfect-adaptation theorem claimed.',
        initial='Independent uniform +/- .075 V, then settling; silicon mismatch and existing thermal/shot noise. Jitter not locked to integration step.',
        noise_sigma_passive_V=math.sqrt(K_B*T/CAP),minimum_signal_V=.025,
        refinement='Both successive step-halving paired-seed bootstrap95 intervals entirely inside +/-.05 on every normalized case metric.',
        budget='One sequential process; pilot <=600s, confirm <=1200s; <=2 construction variants with diagnosis before second. These are short component benches, not robot lives.',
        source='Ma et al. 2009, https://pmc.ncbi.nlm.nih.gov/articles/PMC3068210/ ; summary, adaptation definition and enzymatic-model assumptions read. Functional precedent, not transfer of biochemical guarantees.')
    if name=='change_v2':
        p['control']='Remove integral writer (last edge); unchanged low-pass criterion sustained/onset>.70 and zero rail hits.'
        p['prediction']='Integral negative feedback: local output/integral Jacobian approximately [[-50,-100],[12.5,0]] per second, stable poles -25 +/-25i. Write dead zone permits approx1.5mV residual relative to writer offset, independent of input within unsaturated authority. Offsets shift the baseline; they do not require exact feedforward cancellation. Same functional criteria as v1.'
        p['source']+=' Feedback-buffer equations2-4 and integral-control discussion read before v2.'
    return p

def build(name,seed,control=False):
    spec=graph(name);c=Circuit(seed=seed,streams=True,substrate='silicon');rng=np.random.default_rng([seed,128,1])
    for n in spec['nodes']:c.node(**n,lo=-RAIL,hi=RAIL,start=rng.uniform(-.075,.075))
    for i,e in enumerate(spec['edges']):
        if control and i==len(spec['edges'])-1:continue
        c.element(e['to'],e['source'],e['gain'],e['offset'],slope=e['slope'],tau=e['tau'],gate=e['gate'])
    c._ready();return c

def run(name,seed,dt,case,control=False):
    c=build(name,seed,control);start=1+np.random.default_rng([seed,128,2]).uniform(.001,.009);end=start+case['duration'];duration=case['duration']+2.2
    pulses=np.array([[start,case['duration'],0,case['sign']*CAP*case['amplitude']/.01]])
    steps=round(duration/dt);ratio=round(dt/(DT/4));z=np.empty((steps,len(c.V)))
    for i in range(len(c.V)):
        rng=np.random.default_rng([seed,128,3,i]);z[:,i]=rng.standard_normal(steps*ratio).reshape(steps,ratio).sum(axis=1)/math.sqrt(ratio)
    tr,power,charge,hits=integrate(c.V,c.Vx,c.armed,c.spikes,c.vmax,c.node_arr,c.el_arr,c.link,c.q,c.rest,c.cfg,z,dt,round(.001/dt),pulses,np.zeros(5))
    m=measure(tr,start,end,case['sign']);peak=m['onset_V'];fall=m['offset_V'];res=m['sustained_V'];late=m['recovery_V']
    passed=peak>.025 and (res/peak>.70 if control else (fall>.025 and abs(res)<.35*min(peak,fall) and abs(late)<.01)) and hits==0
    return dict(name=name,seed=seed,dt=dt,case=case,control=control,passed=bool(passed),metrics=m,normalized={k:v/V_TYP for k,v in m.items()},
        cost=dict(power_W=float(power),energy_J=float(power*duration),gross_charge_C=charge.tolist(),threshold_crossings=c.spikes.tolist(),rail_hits=int(hits)),
        nodes=c.node_arr.tolist(),elements=c.el_arr.tolist(),pulses=pulses.tolist()),tr

def measure(tr,start,end,sign):
    t=tr[:,0];y=tr[:,-1];base=float(y[(t>.7)&(t<.95)].mean());y=sign*(y-base)
    return dict(onset_V=float(np.max(y[(t>start+.01)&(t<start+.4)])),offset_V=float(-np.min(y[(t>end+.01)&(t<end+.4)])),
        sustained_V=float(y[(t>end-.2)&(t<end-.02)].mean()),recovery_V=float(y[(t>end+.8)&(t<end+1.)].mean()))

def summary(name,rows,ss):
    primary=[r for r in rows if not r['control']];expected={(s,dt,c['id']) for s in ss for dt in [DT,DT/2,DT/4] for c in cases(name)}
    assert len(primary)==len(expected) and {(r['seed'],r['dt'],r['case']['id']) for r in primary}==expected
    good=[s for s in ss if all(r['passed'] for r in primary if r['seed']==s)];ref={}
    for case in cases(name):
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
            for metric in primary[0]['normalized']:
                a={r['seed']:r['normalized'][metric] for r in primary if r['dt']==coarse and r['case']['id']==case['id']}
                b={r['seed']:r['normalized'][metric] for r in primary if r['dt']==fine and r['case']['id']==case['id']}
                ref[f'{case["id"]}:{coarse}:{metric}']=interval([b[s]-a[s] for s in ss])
    return dict(passed=len(good),seeds=len(ss),failed_seeds=sorted(set(ss)-set(good)),wilson95=wilson(len(good),len(ss)),
        reliability_pass=wilson(len(good),len(ss))[0]>=.9,refinement=ref,refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),
        control_rows=sum(r['control'] for r in rows),control_pass=all(r['passed'] for r in rows if r['control']),
        power_W=interval([np.mean([r['cost']['power_W'] for r in primary if r['seed']==s and r['dt']==DT/4]) for s in ss]))

def main():
    p=argparse.ArgumentParser();p.add_argument('name',choices=['change_v1','change_v2']);p.add_argument('stage',choices=['prepare','pilot','confirm']);a=p.parse_args();out=OUT/a.name;out.mkdir(parents=True,exist_ok=True)
    if a.stage=='prepare':
        for n in graph(a.name)['nodes']:assert n['C']<=C_MAX and (n['memory'] or (n['R']<=R_MAX and n['R']*n['C']>=TAU_LEAK))
        for e in graph(a.name)['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
        with (out/'protocol.json').open('x') as f:json.dump(protocol(a.name),f,indent=2)
        return
    assert json.loads((out/'protocol.json').read_text())==protocol(a.name)
    if a.stage=='confirm':
        pilot=json.loads((out/'pilot.json').read_text());assert pilot['passed']==8 and pilot['refinement_pass'] and pilot['control_pass']
    path=out/f'{a.stage}.jsonl';assert not path.exists();prov=provenance();prov['files']['lab/motif_bench.py']=digest(__file__);prov['protocol_sha256']=digest(out/'protocol.json');(out/f'{a.stage}_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];ss=seeds(a.name,a.stage);started=time.monotonic()
    with path.open('x') as f:
        for seed in ss:
            for control in ([False,True] if a.stage=='pilot' else [False]):
                for case in cases(a.name):
                    for dt in [DT,DT/2,DT/4]:
                        row,tr=run(a.name,seed,dt,case,control);rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
                        if seed==ss[0] and dt==DT/4:np.savez_compressed(out/f'{a.stage}_{case["id"]}_{control}.npz',trace=tr)
            print(json.dumps(dict(seed=seed,failures=sum(not r['passed'] for r in rows if r['seed']==seed),elapsed_s=time.monotonic()-started)),flush=True)
    result=summary(a.name,rows,ss);result['elapsed_s']=time.monotonic()-started;(out/f'{a.stage}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='refinement'}),flush=True)
if __name__=='__main__':main()
