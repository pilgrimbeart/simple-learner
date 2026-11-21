"""D151 explicit correction-kernel lower-bound count and nominal offset propagation."""
import json,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,digest,provenance
from motif_bench import node,edge
from units import V_TYP,MISMATCH,RAIL,C_MAX,R_MAX,I_MIN,SLEW
from minimal.spice import count
OUT=ROOT/'lab/v/correction_cell_budget'
def main():
    OUT.mkdir(exist_ok=True);g=dict(nodes=[node('source',.005),node('output',.01),dict(name='retained correction',bias=0.,R=None,C=CAP,memory=True),node('calibration permission',.005)],
        edges=[edge(1,0,CAP*V_TYP/.01),edge(1,2,-CAP*V_TYP/.01),edge(2,1,CAP*V_TYP/.1,gate=3),edge(2,2,-CAP*V_TYP/.1,gate=3)])
    protocol=dict(graph=g,a_per_s=10.,r_per_s=10.,K_V_per_V=1.,output_tau_s=.01,
        original_offset_sigma_V=MISMATCH*V_TYP,assumption='Independent equal nominal device offsets; linearised local loop. Source blanking/path isolation/local schedule absent and required.',budget_s=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    for n in g['nodes']:assert n['C']<=C_MAX and (n['R'] is None or n['R']<=R_MAX)
    for e in g['edges']:assert I_MIN<=abs(e['gain'])<=CAP*SLEW
    parts={}
    for mode in ['full','partial']:
        edges=g['edges'][:3] if mode=='full' else g['edges']
        spec=dict(nodes=[[n['name'],n['bias'],n['R'],n['C'],None,None,None,n['memory']] for n in g['nodes']],elements=[[e['to'],e['source'],e['gate'],e['gain'],e['offset'],e['slope'],e['tau'],False] for e in edges],sensors=[],taste=-1)
        parts[mode]=count(spec)
    s2=(MISMATCH*V_TYP)**2;bvar=2*s2;evar=s2;pvar=s2;alpha=(bvar+pvar)/(bvar+pvar+evar)
    def risk(a):return (1-a)**2*bvar+a*a*evar+(1-a)**2*pvar
    mse=dict(original_path=s2,correction_hardware_held_at_nominal=bvar,full_correction=evar,half_correction=risk(.5),quadratic_model_minimum=risk(alpha))
    # Full correction has no prior writer; alpha=1 removes its contribution exactly.
    assert abs(risk(1)-mse['full_correction'])<1e-15
    eig={str(r):np.linalg.eigvals(np.array([[-100.,-100.],[10.,-r]])).real.tolist() for r in [0.,10.]}
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),ROOT/'lab/motif_bench.py',ROOT/'minimal/spice.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    result=dict(nominal_RMS_V={k:math.sqrt(v) for k,v in mse.items()},model_optimal_alpha=alpha,linear_loop_eigenvalues_per_s=eig,
        nominal_correction_current_authority_A=CAP*V_TYP/.01*np.tanh(RAIL/V_TYP),parts=parts,
        scope='Kernel lower bound only: external current sources, internal source blanking, path-isolation switches, local schedule and downstream readout not counted; pump implementation/power omitted under existing memory model. No noise trajectories or physical pass claim.')
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
