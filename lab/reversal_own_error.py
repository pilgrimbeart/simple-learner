"""D153: error parity of the available signed control as a reverser."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,digest,provenance
from signed_control_diagnosis import steady
OUT=ROOT/'lab/v/reversal_own_error';SRC=ROOT/'lab/v/signed_control/confirm.jsonl'
def main():
    OUT.mkdir(exist_ok=True)
    protocol=dict(source=str(SRC),control_magnitude_V=.3,secant_source_magnitude_V=.15,modes=['original','source_offsets'],budget_s=30,meaning='Reused static reference; no switching, dynamics or reliability claim')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    raw=[json.loads(l) for l in SRC.read_text().splitlines()];raw=[r for r in raw if r['dt']==DT/4 and abs(r['case']['y'])==.3 and abs(r['case']['x']) in [0.,.15]]
    assert len(raw)==240
    results=[]
    for mode in protocol['modes']:
        lookup={(r['seed'],r['case']['x'],r['case']['y']):steady(r,mode)['output_V'] for r in raw}
        for s in sorted({k[0] for k in lookup}):
            a=(lookup[s,0.,.3]+lookup[s,0.,-.3])/2
            b=lambda x:(lookup[s,x,.3]-lookup[s,x,-.3])/2
            gain=(b(.15)-b(-.15))/.3;assert gain>0
            results.append(dict(mode=mode,seed=s,rejected_even_error_V=a,retained_odd_error_V=b(0.),secant_gain=gain,input_referred_error_V=b(0.)/gain,error_to_signal_ratio=abs(b(0.))/min(abs(b(.15)-b(0.)),abs(b(-.15)-b(0.)))))
    summary={}
    for mode in protocol['modes']:
        rr=[r for r in results if r['mode']==mode];summary[mode]={}
        for key in ['rejected_even_error_V','retained_odd_error_V','secant_gain','input_referred_error_V','error_to_signal_ratio']:
            v=np.array([r[key] for r in rr]);summary[mode][key]=dict(min=float(min(v)),max=float(max(v)),rms=float(np.sqrt(np.mean(v*v))))
    # Independent polynomial fixture for the stated counterexample, not a circuit simulation.
    x,y,k,bx,by,c,ae,ao,be,bo=.12,-.19,.7,.2,-.3,.08,.04,-.03,.02,.05
    z=sum(q*r*(k*(q*x+ae+q*ao)*(r*y+be+r*bo)+bx*(q*x+ae+q*ao)+by*(r*y+be+r*bo)+c) for q in [-1,1] for r in [-1,1])/4
    assert abs(z-k*(x+ao)*(y+bo))<1e-15
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/signed_control_diagnosis.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',summary),('rows',results)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
