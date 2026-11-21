"""D128 compare settled circuit drift with residuals; no new trajectories."""
import json,sys,copy
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from motif_bench import OUT,build,graph,DT,CAP,digest
from dynamic_parts_failure import drift,jacobian

def equilibrium(c,drive):
    v=np.zeros(len(c.V))
    for _ in range(50):
        f=drift(v,c)+drive/c.node_arr[2]
        if np.linalg.norm(f)<1e-9:break
        v-=np.linalg.solve(jacobian(v,c),f)
    assert np.linalg.norm(drift(v,c)+drive/c.node_arr[2])<1e-6
    return v

out=OUT/'change_v1';rows=[json.loads(l) for l in (out/'pilot.jsonl').read_text().splitlines()];rows=[r for r in rows if not r['control'] and r['dt']==DT/4]
result=[]
for r in rows:
    spec=graph('change_v1');c=build('change_v1',r['seed']);drive=np.zeros(4);drive[0]=r['pulses'][0][3];modes={}
    for mode in ['actual','nominal_gains','nominal_leaks','nominal_slopes','zero_offsets','all_nominal']:
        d=copy.deepcopy(c)
        if mode in ('nominal_gains','all_nominal'):d.el_arr[0]=[e['gain'] for e in spec['edges']]
        if mode in ('nominal_leaks','all_nominal'):d.node_arr[1]=[1/n['R'] for n in spec['nodes']]
        if mode in ('nominal_slopes','all_nominal'):d.el_arr[2]=[e['slope'] for e in spec['edges']]
        if mode in ('zero_offsets','all_nominal'):d.el_arr[1]=0
        modes[mode]=float(r['case']['sign']*(equilibrium(d,drive)[-1]-equilibrium(d,np.zeros(4))[-1]))
    result.append(dict(seed=r['seed'],case=r['case'],passed=r['passed'],observed=r['metrics'],predicted_DC_V=modes))
a=np.array([r['observed']['sustained_V'] for r in result]);b=np.array([r['predicted_DC_V']['actual'] for r in result])
summary=dict(source_sha256=digest(__file__),input_sha256=digest(out/'pilot.jsonl'),rows=result,
    residual_correlation=float(np.corrcoef(a,b)[0,1]),residual_RMSE_V=float(np.sqrt(np.mean((a-b)**2))),
    rms_DC_by_restoration={mode:float(np.sqrt(np.mean([r['predicted_DC_V'][mode]**2 for r in result]))) for mode in result[0]['predicted_DC_V']},
    failures=dict(onset=sum(r['observed']['onset_V']<=.025 for r in result),offset=sum(r['observed']['offset_V']<=.025 for r in result),residual=sum(abs(r['observed']['sustained_V'])>=.35*min(r['observed']['onset_V'],r['observed']['offset_V']) for r in result),recovery=sum(abs(r['observed']['recovery_V'])>=.01 for r in result)))
(out/'diagnosis.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
