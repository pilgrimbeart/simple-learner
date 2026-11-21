"""D152: parity decomposition of reused static transfers; no circuit claim."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT, digest, provenance
OUT=ROOT/'lab/v/shared_path_reversal'
SRC=ROOT/'lab/v/signed_control_diagnosis/original_predictions.json'
def main():
    OUT.mkdir(exist_ok=True)
    protocol=dict(source=str(SRC),modes=['original','source_odd','both_odd'],
        criteria='D145 static sign >.02V, control contrast >.04/.08V; reused draws, no reliability or dynamic claim',
        assumption='Same stationary transfer, exact external reversal and subtraction; switching/storage/settling absent',budget_s=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    rows=json.loads(SRC.read_text()); assert len(rows)==1000
    data={(r['seed'],r['case']['x'],r['case']['y']):r['output_V'] for r in rows}
    assert len(data)==1000
    seeds=sorted({k[0] for k in data}); levels=sorted({k[1] for k in data})
    components={}; outputs=[]; maxerr=0.; energies=np.zeros(4); cross=np.zeros((4,4))
    for (s,x,y),v in data.items():
        vals=np.array([data[s,x,y],data[s,-x,y],data[s,x,-y],data[s,-x,-y]])
        ee,oe,eo,oo=np.array([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]])@vals/4
        parts=np.array([ee,oe,eo,oo]); energies+=parts**2;cross+=np.outer(parts,parts)
        maxerr=max(maxerr,abs(parts.sum()-v))
        components[s,x,y]={'original':v,'source_odd':oe+oo,'both_odd':oo}
        outputs.append(dict(seed=s,x_V=x,y_V=y,even_even_V=ee,odd_even_V=oe,even_odd_V=eo,odd_odd_V=oo))
    assert maxerr<1e-14
    assert np.max(np.abs(cross-np.diag(np.diag(cross))))<1e-12
    summary={}
    for mode in protocol['modes']:
        passed=[]; margins=[]; source0=[];control0=[]
        for s in seeds:
            f=lambda x,y:components[s,x,y][mode]
            margins.extend(np.sign(x*y)*f(x,y) for x in levels for y in levels if x*y)
            passed.append(all(np.sign(x*y)*f(x,y)>.02 for x in levels for y in levels if x*y) and all(np.sign(x)*(f(x,y)-f(x,-y))>m for x in levels if x for y,m in [(.15,.04),(.3,.08)]))
            source0.extend(f(0.,y) for y in levels);control0.extend(f(x,0.) for x in levels)
        summary[mode]=dict(static_adequate_draws=sum(passed),draws=len(seeds),minimum_signed_response_V=min(margins),source_zero_max_abs_V=max(abs(np.array(source0))),control_zero_max_abs_V=max(abs(np.array(control0))))
    result=dict(comparisons=summary,reconstruction_max_error_V=maxerr,component_RMS_V=dict(zip(['even_even','odd_even','even_odd','odd_odd'],np.sqrt(energies/len(data)).tolist())),scope=protocol['assumption'])
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC]});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',result),('rows',outputs)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2,default=lambda x:x.item())+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
