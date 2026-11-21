"""D127 offline equilibrium analysis. No trajectories, grid search or engine changes."""
import copy, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import OUT, build, definitions, DT, provenance, digest
from dynamic_parts_failure import drift,jacobian

def root(c):
    v=np.zeros(2)
    for _ in range(100):
        f=drift(v,c)
        if np.linalg.norm(f)<1e-8: break
        delta=np.linalg.solve(jacobian(v,c),f)
        # Backtracking Newton: equilibrium calculation, never a circuit simulation.
        scale=1.
        while scale>1/1024 and np.linalg.norm(drift(v-scale*delta,c))>=np.linalg.norm(f): scale/=2
        v-=scale*delta
    j=jacobian(v,c); ev=np.linalg.eigvals(j)
    return dict(root_V=v.tolist(),residual=float(np.linalg.norm(drift(v,c))),jacobian=j.tolist(),
        max_real_per_s=float(max(ev.real)),trace_per_s=float(np.trace(j)),det_per_s2=float(np.linalg.det(j)),
        local_unstable=bool(max(ev.real)>0))

def main():
    spec=definitions()['oscillator']; rows=[json.loads(l) for l in (OUT/'confirm_v2.jsonl').read_text().splitlines()]
    rows=[r for r in rows if r['name']=='oscillator' and r['dt']==DT/4]
    results=[]
    for row in rows:
        c=build('oscillator',spec,row['seed']); cases={}
        for mode in ['actual','zero_offsets','nominal_gains','nominal_slopes','nominal_leaks','nominal_caps','recovery_gain_7_over_5']:
            d=copy.deepcopy(c)
            if mode=='recovery_gain_7_over_5': d.el_arr[0,1]*=7/5
            if mode=='zero_offsets': d.el_arr[1,:]=0
            if mode=='nominal_gains': d.el_arr[0,:]=[e['gain'] for e in spec['edges']]
            if mode=='nominal_slopes': d.el_arr[2,:]=[e['slope'] for e in spec['edges']]
            if mode=='nominal_leaks': d.node_arr[1,:]=[1/n['R'] for n in spec['nodes']]
            if mode=='nominal_caps': d.node_arr[2,:]=[n['C'] for n in spec['nodes']]
            cases[mode]=root(d)
        results.append(dict(seed=row['seed'],cycle_pass=row['metrics']['passed'],cases=cases))
    result=dict(provenance=provenance(),script_sha256=digest(__file__),analysis=results,
        limits='Single Newton root per draw; no global uniqueness or cycle certificate. Category replacements are algebraic counterfactuals, not noisy replay or fresh evaluation.')
    (OUT/'margin_v2.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in results:
        print(r['seed'],r['cycle_pass'],{k:round(v['max_real_per_s'],3) for k,v in r['cases'].items()},'root',r['cases']['actual']['root_V'])
    assert max(v['residual'] for r in results for v in r['cases'].values())<1e-6
if __name__=='__main__': main()
