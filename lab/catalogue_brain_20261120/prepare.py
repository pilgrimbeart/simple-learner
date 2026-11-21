"""Static preparation checks only. No circuit dynamics, robot lives or tuning."""
import hashlib, itertools, json, math, subprocess
from pathlib import Path
from design import graph, validate
from units import K_B,T,C_TYP,PULSE,I_TYP
from brains.circuit import PULSES
from minimal.spice import count
ROOT=Path(__file__).resolve().parents[2]
g=graph(); checks=[validate(graph(s)) for s in itertools.product((0,1),repeat=2)]
ix={n['name']:i for i,n in enumerate(g['nodes'])}
spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],n['lo'],n['hi'],None,n['memory']] for n in g['nodes']],
          elements=[[ix[e['to']],ix[e['source']],-1 if e['gate'] is None else ix[e['gate']],e['gain'],e['offset'],e['slope'],e['tau'],e['sigmoid']] for e in g['edges']],
          sensors=[ix[n] for n in g['sensors']],taste=ix[g['taste']])
paths=['lab/catalogue_brain_20261120/design.py','lab/catalogue_brain_20261120/DESIGN.md',
       'lab/catalogue_brain_20261120/prepare.py','lab/WORK_ORDER_2026-11-20_catalogue_brain.md',
       'mixed_feedback.py','units.py','chip.py','creature.py','world.py']
cap=2*C_TYP; resistance=.010/cap
result=dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            checks=checks,nominal_parts=count(spec),
            estimates=dict(sensor_peak_V=PULSES*I_TYP*resistance*(1-math.exp(-PULSE/.010)),
                           passive_input_sigma_V=math.sqrt(K_B*T/cap)),
            limitations=['No simulation or reward observed','Nominal static checks only',
                         'Existing cost model; memory write supply energy unmeasured',
                         'Runner, adapter and benches are executor deliverables'])
path=ROOT/'lab/v/catalogue_brain_20261120/preparation.json'
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
