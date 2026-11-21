"""D144: offset attribution in the frozen fully linear signed reference."""
import copy,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from phase_signed_drift import response
from dynamic_parts_bench import ROOT,DT,digest,provenance
OUT=ROOT/'lab/v/phase_drift_feedthrough';SRC=ROOT/'lab/v/phase_v1/confirm.jsonl'
def main():
    OUT.mkdir(exist_ok=True);rows=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in rows if r['dt']==DT/4 and r['case']['phase']==0];assert len(rows)==80
    modes={'original':[],'zero_lag_offsets':[0,1],'zero_output_offsets':[2,3],'zero_all_offsets':[0,1,2,3]}
    protocol=dict(modes=modes,grid=[32,64],source=str(SRC),budget_s=60,meaning='Same linear signed reference, only the listed offsets set to zero by an informed analyst.')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    old=json.loads((ROOT/'lab/v/phase_signed_drift/rows.json').read_text());lookup={(r['seed'],r['band_Hz']):r for r in old if r['mode']=='linear_signed' and r['phase_rad']==0}
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),ROOT/'lab/phase_signed_drift.py',SRC,ROOT/'lab/v/phase_signed_drift/rows.json']});(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    result=[];error=0.;higher=0.
    for mode,indices in modes.items():
        for orig in rows:
            r=copy.deepcopy(orig)
            for j in indices:r['elements'][1][j]=0
            p=[response(r,[.05,.1],.05,s,'linear_signed',32,64)[0] for s in [False,True]];c=(p[0]-p[1])/2
            if mode=='original':
                error=max(error,float(np.max(abs(c-np.array(lookup[r['seed'],r['case']['frequency']]['corrected_V'])[::4]))))
                f=np.fft.rfft(c)/len(c);higher=max(higher,float(np.sum(abs(f[2:]))))
            result.append(dict(mode=mode,seed=r['seed'],band_Hz=r['case']['frequency'],curve_V=c.tolist(),maximum_abs_V=float(max(abs(c)))))
    assert error<1e-10 and higher<1e-10
    summary=dict(validation_max_error_V=error,maximum_higher_harmonic_sum_V=higher,modes={m:dict(maximum_absolute_bias_V=max(r['maximum_abs_V'] for r in result if r['mode']==m),rms_bias_V=float(np.sqrt(np.mean([v*v for r in result if r['mode']==m for v in r['curve_V']])))) for m in modes})
    assert summary['modes']['zero_all_offsets']['maximum_absolute_bias_V']<1e-10
    (OUT/'rows.json').write_text(json.dumps(result)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
