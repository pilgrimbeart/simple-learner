"""Read-only explanation of D126 v1 pilot failures; no new circuit evaluation."""
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent/'v/dynamic_parts'
rows=[json.loads(l) for l in (BASE/'pilot_v1.jsonl').read_text().splitlines()]
out=[]
for r in rows:
    if r['control'] and not r['control_passed']:
        out.append(dict(name=r['name'],seed=r['seed'],control_voltage_residual_V=r['control_residual_V']))
    if r['control'] or r['dt']!=.000125 or r['name'] not in ('memory','resonator'): continue
    c=r['costs'][0]; nodes=np.array(c['nodes']); el=np.array(c['elements'])
    if r['name']=='memory':
        out.append(dict(name='memory',seed=r['seed'],rail_hits=c['rail_hits'],holds=r['metrics']['values']))
    else:
        a=nodes[1]/nodes[2]
        # Edges target x then y. Small-signal approximation ignores equilibrium shifts/saturation.
        b=abs(el[0]*el[2])/nodes[2]
        w=np.sqrt(max(0,b.prod()-(a*a).sum()/2))
        out.append(dict(name='resonator',seed=r['seed'],linear_peak_Hz=w/(2*np.pi),
            measured=r['metrics']['values'],limit='Small-signal estimate, not fitted or exact nonlinear peak'))
(BASE/'pilot_v1_diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
