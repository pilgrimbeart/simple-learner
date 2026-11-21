"""D161 bias authority at selected intrinsic references; no tuned circuit."""
import copy,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,build,definitions,digest,provenance
from oscillator_root_census import slow
from dynamic_parts_failure import drift,jacobian
from mixed_feedback import _fade
from units import RAIL,V_TYP,MISMATCH,SLEW
OUT=ROOT/'lab/v/oscillator_bias_authority'
def main():
    OUT.mkdir(exist_ok=True);src=ROOT/'lab/v/oscillator_root_census/rows.json';old=json.loads(src.read_text());seeds=sorted({r['seed'] for r in old})
    targets={'negative_reference':-MISMATCH*V_TYP,'zero_reference':0.,'positive_reference':MISMATCH*V_TYP,'informed_self_centre':None}
    protocol=dict(seeds=seeds,targets_V=targets,source=str(src),budget_s=30,scope='Static bias reference; no autonomous calibration or oscillation claim')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    rows=[]
    for seed in seeds:
      c=build('oscillator',definitions()['oscillator'],seed)
      for mode,target in targets.items():
        d=copy.deepcopy(c);x=float(d.el_arr[1,0]) if target is None else target;y=float(slow(x,d));v=np.array([x,y]);needed=-drift(v,d)[0]*d.node_arr[2,0]
        fade=_fade(RAIL-x,d.cfg[3]) if needed>=0 else _fade(x+RAIL,d.cfg[4]);bias=needed/fade;d.node_arr[0,0]=bias
        residual=float(np.linalg.norm(drift(v,d)));assert residual<1e-8
        eig=np.linalg.eigvals(jacobian(v,d));assert abs(bias)<=d.node_arr[2,0]*SLEW
        rows.append(dict(seed=seed,mode=mode,target_V=x,slow_V=y,bias_A=bias,residual_V_per_s=residual,max_real_per_s=float(max(eig.real)),det_per_s2=float(np.linalg.det(jacobian(v,d))),local_unstable=bool(max(eig.real)>0)))
    summary={}
    for mode in targets:
        rr=[r for r in rows if r['mode']==mode];summary[mode]=dict(unstable_draws=sum(r['local_unstable'] for r in rr),draws=40,bias_range_A=[min(r['bias_A'] for r in rr),max(r['bias_A'] for r in rr)],max_real_range_per_s=[min(r['max_real_per_s'] for r in rr),max(r['max_real_per_s'] for r in rr)],minimum_det_per_s2=min(r['det_per_s2'] for r in rr))
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),src,ROOT/'lab/oscillator_root_census.py',ROOT/'lab/dynamic_parts_failure.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',summary),('rows',rows)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
