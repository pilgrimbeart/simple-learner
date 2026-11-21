"""Replay failed oscillator draws, then analyse their deterministic drift (not a noiseless simulation).
The replay uses unchanged silicon noise; the Jacobian is observational mathematics only.
"""
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import OUT, DT, definitions, run_one, build, provenance
from mixed_feedback import _fade
from units import RAIL


def drift(v,c):
    """Algebraic mean current / capacitance, for the unfiltered ungated tanh subgrammar only."""
    node=c.node_arr; kp,kn=c.cfg[3:5]
    bias=np.array([b*_fade(RAIL-v[i],kp) if b>0 else b*_fade(v[i]+RAIL,kn) for i,b in enumerate(node[0])])
    current=bias-node[1]*v
    for j in range(c.link.shape[1]):
        dest,source,gate=c.link[:,j]
        gain,offset,slope,tau,sig=c.el_arr[:,j]
        assert gate==-1 and tau==0 and sig==0
        w=np.sign(gain)*np.tanh(slope*(v[source]-offset))
        current[dest]+=abs(gain)*((1+w)*_fade(RAIL-v[dest],kp)-(1-w)*_fade(v[dest]+RAIL,kn))/2
    return current/node[2]


def jacobian(v,c):
    eps=1e-6; eye=np.eye(len(v))*eps
    return np.column_stack([(drift(v+d,c)-drift(v-d,c))/(2*eps) for d in eye])


def main():
    rows=[json.loads(l) for l in (OUT/'confirm_v2.jsonl').read_text().splitlines()]
    failed=sorted({r['seed'] for r in rows if r['name']=='oscillator' and not r['metrics']['passed']})
    result=dict(provenance=provenance(),failed_seeds=failed,analysis=[])
    for seed in failed:
        spec=definitions()['oscillator']; tr,cost=run_one('oscillator',spec,seed,DT/4)
        np.savez_compressed(OUT/f'oscillator_failure_{seed}_v2.npz',trace=tr)
        c=build('oscillator',spec,seed); observed=tr[tr[:,0]>95,1:].mean(axis=0)
        root=observed.copy()
        for _ in range(20):
            residual=drift(root,c)
            if np.linalg.norm(residual)<1e-9: break
            root-=np.linalg.solve(jacobian(root,c),residual)
        eigen=np.linalg.eigvals(jacobian(root,c))
        item=dict(seed=seed,observed_mean_V=observed.tolist(),fixed_point_V=root.tolist(),
            drift_residual_V_per_s=float(np.linalg.norm(drift(root,c))),
            jacobian_per_s=jacobian(root,c).tolist(),eigenvalues_per_s=[[float(z.real),float(z.imag)] for z in eigen],
            local_equilibrium_stable=bool(np.all(eigen.real<0)),distance_from_observed_V=float(np.linalg.norm(root-observed)),
            recorded_metrics=next(r['metrics'] for r in rows if r['name']=='oscillator' and r['seed']==seed and r['dt']==DT/4))
        result['analysis'].append(item)
        print(json.dumps(item),flush=True)
    (OUT/'oscillator_failure_diagnosis_v2.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__': main()
