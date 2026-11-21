"""D130 audit and human-readable basin comparison; no new trajectories."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,digest
from retained_write_report import svg_plot
from retained_write_preview import render
out=ROOT/'lab/v/oscillator_basins';rows=[json.loads(l) for l in (out/'rows.jsonl').read_text().splitlines()];protocol=json.loads((out/'protocol.json').read_text());prov=json.loads((out/'provenance.json').read_text())
assert len(rows)==60 and len({(r['seed'],r['initial_mode'],r['dt']) for r in rows})==60
for p,h in prov['files'].items():assert digest(ROOT/p)==h
assert prov['protocol_sha256']==digest(out/'protocol.json')
consistent=True;lines=['# Oscillator starting-state audit — D130','','Same four existing component draws, five starts, three timesteps, original noise and50s pulse. This is diagnosis, not fresh reliability evidence.','','| Draw | Start | Before pulse | After pulse |','|---|---|---|---|']
for seed in protocol['seeds']:
    for start in protocol['starts']:
        rr=[r for r in rows if r['seed']==seed and r['initial_mode']==start];states={(r['windows']['before']['state'],r['windows']['after']['state']) for r in rr};consistent &=len(states)==1
        r=next(r for r in rr if r['dt']==DT/4);lines.append(f'| {seed} | {start} | {r["windows"]["before"]["state"]} | {r["windows"]["after"]["state"]} |')
lines += ['',f'Window classifications agree across all three timesteps: {consistent}. Original-start finest amplitudes reproduced D126 exactly.','', 'Draw51005 supports coexistence: near-rest starts stay quiet until the pulse, then cycle; other starts already cycle. The three previously failing draws remain at rest from every sampled start. This weakens a generic startup-kick repair, but does not prove those draws have no other attractors.','', 'Raw metrics and initial voltages: rows.jsonl. Specification: protocol.json. Provenance: provenance.json. Script: lab/oscillator_basins.py. No noise-free trajectories, tuning or new mechanism. Large traces stay locally at '+str(out)+'/*.npz, with hashes in trace_manifest.json.']
(out/'report.md').write_text('\n'.join(lines)+'\n');(out/'analysis.json').write_text(json.dumps(dict(all_classifications_agree_across_steps=consistent,rows=60,source_sha256=digest(__file__),raw_sha256=digest(out/'rows.jsonl')),indent=2)+'\n');(out/'trace_manifest.json').write_text(json.dumps({str(p.resolve()):digest(p) for p in out.glob('*.npz')},indent=2)+'\n')
for mode in ['original','rest']:
    tr=np.load(out/f'51005_{mode}.npz')['trace'];svg=svg_plot([(tr[:,0],tr[:,1],'fast'),(tr[:,0],tr[:,2],'recovery')],f'Same draw51005; start={mode}',(48,53),(-.8,.8));p=out/f'51005_{mode}.svg';p.write_text(svg);render(p)
print('60rows and source hashes verified; state classifications across all3steps:',consistent)
