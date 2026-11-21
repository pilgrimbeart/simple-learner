"""D148: local-zero-informed additive-current reference, not a calibration circuit."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from signed_control_bench import assess
from mixed_feedback import _fade
from units import RAIL,V_TYP,MISMATCH
import chip
OUT=ROOT/'lab/v/signed_control_zero';SRC=ROOT/'lab/v/signed_control/confirm.jsonl'
MODES={'original':(False,False,0.),'source_zero':(True,False,0.),'gate_centres':(False,True,0.),'both':(True,True,0.),'detector_positive_error':(True,True,MISMATCH*V_TYP),'detector_negative_error':(True,True,-MISMATCH*V_TYP)}
def solve(r,mode):
    n=np.array(r['nodes']);e=np.array(r['elements']);links=np.array(r['links']);source_cal,gate_cal,target=MODES[mode]
    corrections=np.zeros(4)
    def fade(current,voltage):return _fade(RAIL-voltage,chip.KNEE_P) if current>=0 else _fade(voltage+RAIL,chip.KNEE_N)
    def element(j,src,dest):
        full=abs(e[0,j]);f=np.sign(e[0,j])*np.tanh(e[2,j]*(src-e[1,j]))
        return full*(1+f)/2*_fade(RAIL-dest,chip.KNEE_P)-full*(1-f)/2*_fade(dest+RAIL,chip.KNEE_N)
    if gate_cal:
        for j in [0,1]:
            dest=j+2;reference=.15;needed=n[1,dest]*reference-n[0,dest]*fade(n[0,dest],reference)-element(j,0.,reference)
            corrections[j]=needed/fade(needed,reference)
    if source_cal:
        for j in [2,3]:
            needed=n[1,4]*target-element(j,0.,target);corrections[j]=needed/fade(needed,target)
    v=np.zeros(5);ext=np.array([CAP*r['case']['x']/.005,CAP*r['case']['y']/.005,0,0,0])
    for i in range(5):
        def balance(x):
            total=ext[i]+n[0,i]*fade(n[0,i],x)-n[1,i]*x
            for j in range(4):
                if links[0,j]!=i:continue
                opening=np.clip(v[links[2,j]]/V_TYP,0,1) if links[2,j]>=0 else 1.
                total+=opening*(element(j,v[links[1,j]],x)+corrections[j]*fade(corrections[j],x))
            return total
        lo,hi=-RAIL,RAIL;assert balance(lo)>=0 and balance(hi)<=0
        for _ in range(52):
            mid=(lo+hi)/2
            if balance(mid)>0:lo=mid
            else:hi=mid
        v[i]=(lo+hi)/2
    return float(v[4]),corrections.tolist()

def main():
    OUT.mkdir(exist_ok=True);rows=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in rows if r['dt']==DT/4];assert len(rows)==1000
    protocol=dict(modes=MODES,source=str(SRC),budget_s=120,meaning='Additive current reference fitted ONLY to an internal blanked-source/control equilibrium; detector target perturbations explicit. No parameter offsets changed. Original D145 signal criteria retained, dynamic recovery not re-evaluated.')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/signed_control_diagnosis.py',ROOT/'lab/v/signed_control_diagnosis/original_predictions.json']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    old=json.loads((ROOT/'lab/v/signed_control_diagnosis/original_predictions.json').read_text());lookup={(r['seed'],r['case']['id']):r['output_V'] for r in old};result=[];error=0.
    for mode in MODES:
        for r in rows:
            v,c=solve(r,mode)
            if mode=='original':error=max(error,abs(v-lookup[r['seed'],r['case']['id']]))
            result.append(dict(mode=mode,seed=r['seed'],case=r['case'],mean_V=v,corrections_A=c))
        print(mode,'done',flush=True)
    assert error<1e-12
    summary={}
    for mode in MODES:
        rr=[r for r in result if r['mode']==mode];seeds=sorted({r['seed'] for r in rr});good=[]
        for seed in seeds:
            # Only static sign/contrast criteria: no fabricated recovery or rail measurements.
            group=[r for r in rr if r['seed']==seed];lookup2={(r['case']['x'],r['case']['y']):r['mean_V'] for r in group}
            good.append(all(np.sign(x*y)*v>.02 for (x,y),v in lookup2.items() if x*y!=0) and all(np.sign(x)*(lookup2[x,y]-lookup2[x,-y])>m for x in [-.3,-.15,.15,.3] for y,m in [(.15,.04),(.3,.08)]))
        null=[r['mean_V'] for r in rr if r['case']['x']*r['case']['y']==0];source_null=[r['mean_V'] for r in rr if r['case']['x']==0]
        summary[mode]=dict(static_adequate_draws=sum(good),draws=40,null_range_V=[min(null),max(null)],source_zero_range_V=[min(source_null),max(source_null)],
            correction_ranges_A=[[min(r['corrections_A'][i] for r in rr),max(r['corrections_A'][i] for r in rr)] for i in range(4)])
    data=dict(validation_max_error_V=error,comparisons=summary);(OUT/'rows.json').write_text(json.dumps(result)+'\n');(OUT/'summary.json').write_text(json.dumps(data,indent=2,default=int)+'\n');print(json.dumps(data,indent=2,default=int))
if __name__=='__main__':main()
