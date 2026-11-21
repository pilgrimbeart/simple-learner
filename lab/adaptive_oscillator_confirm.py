"""D162 frozen fresh-draw confirmation, paired original and writer-removal arms."""
import argparse,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adaptive_oscillator import run,graph,DT,OUT as PILOT,protocol as pilotprotocol
from dynamic_parts_bench import ROOT,digest,provenance,interval,wilson
OUT=ROOT/'lab/v/adaptive_oscillator_confirm';SEEDS=list(range(2026120200,2026120240))
def protocol():return dict(graph=graph(),seeds=SEEDS,arms=['original','adaptive','writer_removed'],steps_s=[DT,DT/2,DT/4],duration_s=100.,criteria=pilotprotocol()['criteria'],refinement=pilotprotocol()['refinement'],reliability='Wilson95 lower>=.90, all3steps count once per draw',control='Writer-removed memory holds exactly; original and adaptive paired worlds and Brownian streams',budget_s=1200,scope='Fresh component draws in the same bench family, no robot learning or unseen-family claim')
def summarise(rows):
    assert len(rows)==360 and len({(r['seed'],r['arm'],r['dt']) for r in rows})==360
    result={}
    goodsets={}
    for arm in protocol()['arms']:
        rr=[r for r in rows if r['arm']==arm];good=[s for s in SEEDS if all(r['metrics']['passed'] for r in rr if r['seed']==s)];goodsets[arm]=set(good);ref={}
        for coarse,fine in [(DT,DT/2),(DT/2,DT/4)]:
          for key in rr[0]['metrics']['normalized']:
            ca={r['seed']:r['metrics']['normalized'][key] for r in rr if r['dt']==coarse};fi={r['seed']:r['metrics']['normalized'][key] for r in rr if r['dt']==fine}
            ref[f'{coarse}:{key}']=interval([fi[s]-ca[s] for s in SEEDS])
        result[arm]=dict(passed=len(good),draws=40,wilson95=wilson(len(good),40),reliability_pass=wilson(len(good),40)[0]>=.90,failed_seeds=sorted(set(SEEDS)-set(good)),refinement_pass=all(v[1]>-.05 and v[2]<.05 for v in ref.values()),refinement=ref,power_W=interval([r['cost']['power_W'] for r in rr if r['dt']==DT/4]))
    result['paired']={}
    for other in ['original','writer_removed']:
        pa={r['seed']:r['cost']['power_W'] for r in rows if r['arm']=='adaptive' and r['dt']==DT/4};pb={r['seed']:r['cost']['power_W'] for r in rows if r['arm']==other and r['dt']==DT/4}
        result['paired'][other]=dict(rescued=sorted(goodsets['adaptive']-goodsets[other]),harmed=sorted(goodsets[other]-goodsets['adaptive']),pass_difference=interval([float(s in goodsets['adaptive'])-float(s in goodsets[other]) for s in SEEDS]),power_difference_W=interval([pa[s]-pb[s] for s in SEEDS]))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run']);a=p.parse_args();OUT.mkdir(exist_ok=True)
    pilot=json.loads((PILOT/'summary.json').read_text());assert pilot['adaptive']['passed']==10 and pilot['adaptive']['refinement_pass']
    if a.stage=='prepare':
        with (OUT/'protocol.json').open('x') as f:json.dump(protocol(),f,indent=2)
        return
    assert json.loads((OUT/'protocol.json').read_text())==protocol()
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),ROOT/'lab/adaptive_oscillator.py',ROOT/'lab/motif_bench.py',PILOT/'protocol.json',PILOT/'summary.json']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    rows=[];start=time.monotonic()
    with (OUT/'rows.jsonl').open('x') as f:
      for seed in SEEDS:
       for arm in protocol()['arms']:
        for dt in protocol()['steps_s']:
            r,tr=run(seed,arm,dt)
            if arm=='writer_removed':assert r['memory']['held_exactly']
            rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
            if dt==DT/4 and (seed==SEEDS[0] or not r['metrics']['passed']):np.savez_compressed(OUT/f'{seed}_{arm}.npz',trace=tr)
            if time.monotonic()-start>1200:raise RuntimeError('Budget exceeded')
       print('completed',seed,'adaptive',all(r['metrics']['passed'] for r in rows if r['seed']==seed and r['arm']=='adaptive'),round(time.monotonic()-start,1),flush=True)
    result=summarise(rows);(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({a:{k:v for k,v in r.items() if k!='refinement'} for a,r in result.items()},indent=2))
if __name__=='__main__':main()
