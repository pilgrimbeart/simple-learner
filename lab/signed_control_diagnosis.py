"""D146 scalar steady-state balances with original rail fading; no trajectories."""
import copy,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from signed_control_bench import graph
from mixed_feedback import _fade
import chip
from units import RAIL,V_TYP
OUT=ROOT/'lab/v/signed_control_diagnosis';SRC=ROOT/'lab/v/signed_control/confirm.jsonl'
def steady(row,mode):
    n=np.array(row['nodes']);e=np.array(row['elements']);g=graph();links=np.array(row['links'])
    if mode=='source_offsets':e[1,2:]=0
    if mode=='control_offsets':e[1,:2]=0
    if mode=='input_leaks':n[1,:2]=CAP/.005
    if mode=='gains':e[0]=[v['gain'] for v in g['edges']]
    if mode=='nominal':
        for i,node in enumerate(g['nodes']):n[:3,i]=[node['bias'],1/node['R'],node['C']]
        for j,edge in enumerate(g['edges']):e[:3,j]=[edge['gain'],edge['offset'],edge['slope']]
    v=np.zeros(5);external=np.array([CAP*row['case']['x']/.005,CAP*row['case']['y']/.005,0,0,0]);currents=np.zeros(4)
    def element(j,voltage):
        f=np.tanh(e[2,j]*(v[links[1,j]]-e[1,j]));gate=links[2,j];opening=np.clip(v[gate]/V_TYP,0,1) if gate>=0 else 1.
        full=abs(e[0,j])*opening;w=np.sign(e[0,j])*f
        return full*(1+w)/2*_fade(RAIL-voltage,chip.KNEE_P)-full*(1-w)/2*_fade(voltage+RAIL,chip.KNEE_N)
    for i in range(5):
        def balance(x):
            bias=n[0,i]*(_fade(RAIL-x,chip.KNEE_P) if n[0,i]>=0 else _fade(x+RAIL,chip.KNEE_N))
            return bias-n[1,i]*x+external[i]+sum(element(j,x) for j in range(4) if links[0,j]==i)
        lo,hi=-RAIL,RAIL;assert balance(lo)>=0 and balance(hi)<=0
        for _ in range(60):
            mid=(lo+hi)/2
            if balance(mid)>0:lo=mid
            else:hi=mid
        v[i]=(lo+hi)/2
    for j in range(4):currents[j]=element(j,v[links[0,j]])
    return dict(nodes_V=v.tolist(),gate_openings=np.clip(v[2:4]/V_TYP,0,1).tolist(),element_currents_A=currents.tolist(),output_V=float(v[4]))
def main():
    OUT.mkdir(exist_ok=True);rows=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in rows if r['dt']==DT/4];assert len(rows)==1000
    modes=['original','source_offsets','control_offsets','input_leaks','gains','nominal'];protocol=dict(modes=modes,source=str(SRC),validation_tolerance_V=.0001,budget_s=60)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/signed_control_bench.py',ROOT/'chip.py',ROOT/'mixed_feedback.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    original=[dict(seed=r['seed'],case=r['case'],observed_V=r['mean_V'],**steady(r,'original')) for r in rows];errors=np.array([r['output_V']-r['observed_V'] for r in original]);assert max(abs(errors))<.0001
    fail=next(r for r in rows if r['seed']==2026113011 and r['case']['x']==-.15 and r['case']['y']==.15)
    result=dict(validation_rmse_V=float(np.sqrt(np.mean(errors**2))),validation_max_error_V=float(max(abs(errors))),failure={m:steady(fail,m) for m in modes})
    (OUT/'original_predictions.json').write_text(json.dumps(original)+'\n');(OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
