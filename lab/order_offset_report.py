"""Audit D134 rescue/harm counts; keep every original failure class visible."""
import collections,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest
out=ROOT/'lab/v/order_offsets';rows=[json.loads(x) for x in (out/'rows.jsonl').read_text().splitlines()]
prov=json.loads((out/'provenance.json').read_text());assert digest(out/'protocol.json')==prov['protocol_sha256']
for path,h in prov['files'].items():assert digest(ROOT/path)==h,path
spec=json.loads((out/'protocol.json').read_text());assert digest(spec['source'])==spec['source_sha256']
def kind(r):
    c=r['case'];return 'single' if not c['a'] or not c['b'] else 'simultaneous' if c['delay']==0 else 'long gap' if abs(c['delay'])==.6 else 'ordered pair'
summary={};classes={}
for mode in spec['modes']:
    rr=[r for r in rows if r['intervention']==mode];assert len(rr)==204 and len({(r['seed'],r['case']['id']) for r in rr})==204
    summary[mode]=dict(cases=len(rr),passed=sum(r['passed'] for r in rr),rescued=sum(r['passed'] and not r['original_passed'] for r in rr),new_failures=sum(not r['passed'] and r['original_passed'] for r in rr))
    classes[mode]={k:dict(original_failures=sum(not r['original_passed'] for r in rr if kind(r)==k),rescued=sum(r['passed'] and not r['original_passed'] for r in rr if kind(r)==k),new_failures=sum(not r['passed'] and r['original_passed'] for r in rr if kind(r)==k)) for k in ['single','simultaneous','long gap','ordered pair']}
    if mode=='original':assert all(all(abs(r['metrics'][k]-v)<1e-12 for k,v in r['original_metrics'].items()) for r in rr)
assert summary==json.loads((out/'summary.json').read_text())
(out/'failure_classes.json').write_text(json.dumps(classes,indent=2)+'\n')
lines=['# Temporal-order parameter diagnosis — D134','','All 204 conditions on the six previously failed draws were replayed at the existing finest step. Original metrics reproduce within 1e-12 V. Noise, starting states and stimuli remain paired. This is selected-case diagnosis, not fresh reliability evidence.','','| Parameter group restored to nominal | Cases passing / 204 | Original failures rescued / 20 | Previously passing cases harmed / 184 |','|---|---:|---:|---:|']
for mode,s in summary.items():lines.append(f'| {mode.replace("_"," ")} | {s["passed"]} | {s["rescued"]} | {s["new_failures"]} |')
lines+=['','Trace thresholds account for the largest isolated rescue without observed harm in this selected set. They do not explain all failures. Other groups rescue and harm different cases, so nominalising the entire circuit or adding these rescue counts would be unjustified. These interventions use knowledge unavailable to the circuit; they are not a manufacturable cure.','','Detailed rescue/harm counts by event class: failure_classes.json. Protocol and source hashes: protocol.json and provenance.json. All 1,020 raw rows: rows.jsonl. Reproduction: lab/order_offset_diagnose.py (new output folder required); audit: lab/order_offset_report.py. No engine or body change, no additional topology, no fresh-seed claim.']
(out/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(classes,indent=2))
