"""D150: frozen half correction from nominal Gaussian prior, conditional reference only."""
import json,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest,provenance,interval
from units import MISMATCH,V_TYP
OUT=ROOT/'lab/v/partial_calibration';SRC=ROOT/'lab/v/calibration_error_floor/rows.json'
def main():
    OUT.mkdir(exist_ok=True);rows=json.loads(SRC.read_text());assert len(rows)==200
    sigma=MISMATCH*V_TYP;alpha=sigma**2/(sigma**2+sigma**2);assert alpha==.5
    protocol=dict(prior_sigma_V=sigma,detector_sigma_V=sigma,alpha=alpha,comparators=[0.,alpha,1.],source=str(SRC),budget_s=30,
        limitation='Normal approximation, supplied zero-centred prior and ideal internal-zero measurement; no brain learning or physical calibration claim.')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'units.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    seeds=sorted({r['seed'] for r in rows});results=[];summary={}
    for a in protocol['comparators']:
        rr=[dict(seed=r['seed'],control_V=r['control_V'],alpha=a,expected_MSE_V2=(1-a)**2*r['uncorrected_squared_V2']+a*a*r['expected_detector_squared_V2'],uncorrected_MSE_V2=r['uncorrected_squared_V2']) for r in rows];results.extend(rr)
        differences=[float(np.mean([r['expected_MSE_V2']-r['uncorrected_MSE_V2'] for r in rr if r['seed']==s])) for s in seeds]
        summary[str(a)]=dict(conditional_expected_RMS_V=float(np.sqrt(np.mean([r['expected_MSE_V2'] for r in rr]))),
            paired_draw_bootstrap95_MSE_difference=interval(differences),draws_lower_expected_MSE=sum(x<0 for x in differences),draws=40)
    data=dict(gaussian_reference_information_bits=.5*math.log2(2.),gaussian_reference_posterior_sigma_V=sigma/math.sqrt(2),comparisons=summary)
    assert abs(summary['0.5']['conditional_expected_RMS_V']**2-(summary['0.0']['conditional_expected_RMS_V']**2+summary['1.0']['conditional_expected_RMS_V']**2)/4)<1e-15
    (OUT/'rows.json').write_text(json.dumps(results)+'\n');(OUT/'summary.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main()
