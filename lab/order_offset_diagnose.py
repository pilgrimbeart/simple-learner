"""D134 paired interventions on failed D128 draws; diagnostic, not circuit repair."""
import json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import order_bench as b
from dynamic_parts_bench import provenance,digest,ROOT
OUT=ROOT/'lab/v/order_offsets'; MODES=['original','trace_offsets','detector_offsets','difference_offsets','connection_gains']
original_build=b.build

def main():
    OUT.mkdir(exist_ok=True)
    source=b.OUT/'confirm.jsonl'; raw=[json.loads(l) for l in source.read_text().splitlines()]
    seeds=sorted({r['seed'] for r in raw if not r['passed']})
    selected=[r for r in raw if r['seed'] in seeds and r['dt']==b.DT/4]
    spec=dict(source=str(source),source_sha256=digest(source),seeds=seeds,cases='All34 cases for each of six previously failed seeds',step_s=b.DT/4,modes=MODES,interpretation='Diagnostic nominalisation of one parameter group at a time, not a realizable repair or fresh evaluation. All dynamic noise remains enabled. No combined intervention.',baseline_tolerance_V=1e-12,budget_s=600)
    with (OUT/'protocol.json').open('x') as f:json.dump(spec,f,indent=2)
    prov=provenance();prov['files'].update({p:digest(ROOT/p) for p in ['lab/order_offset_diagnose.py','lab/order_bench.py','lab/motif_bench.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    start=time.monotonic();records=[]
    with (OUT/'rows.jsonl').open('x') as f:
        for mode in MODES:
            def build(seed,control=False):
                c=original_build(seed,control);edges=b.graph()['edges']
                indices={'trace_offsets':[0,1],'detector_offsets':[2,3],'difference_offsets':[5,6]}.get(mode,[])
                for i in indices:c.el_arr[1,i]=edges[i]['offset']
                if mode=='connection_gains':
                    for i,e in enumerate(edges):c.el_arr[0,i]=e['gain']
                return c
            b.build=build
            for old in selected:
                row,tr=b.run(old['seed'],b.DT/4,old['case']);row['intervention']=mode;row['original_passed']=old['passed'];row['original_metrics']=old['metrics']
                if mode=='original':
                    assert row['passed']==old['passed']
                    assert all(abs(row['metrics'][k]-v)<1e-12 for k,v in old['metrics'].items())
                records.append(row);f.write(json.dumps(row)+'\n');f.flush()
            rr=[r for r in records if r['intervention']==mode];print(json.dumps(dict(mode=mode,passed=sum(r['passed'] for r in rr),cases=len(rr),rescued=sum(r['passed'] and not r['original_passed'] for r in rr),new_failures=sum(not r['passed'] and r['original_passed'] for r in rr),elapsed_s=time.monotonic()-start)),flush=True)
    b.build=original_build
    result={mode:dict(cases=len(rr),passed=sum(r['passed'] for r in rr),rescued=sum(r['passed'] and not r['original_passed'] for r in rr),new_failures=sum(not r['passed'] and r['original_passed'] for r in rr)) for mode in MODES for rr in [[r for r in records if r['intervention']==mode]]}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
