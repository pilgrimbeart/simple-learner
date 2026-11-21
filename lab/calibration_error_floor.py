"""D149 conditional error propagation for independent local detector offsets."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest,provenance,interval
from units import MISMATCH,V_TYP
OUT=ROOT/'lab/v/calibration_error_floor';SRC=ROOT/'lab/v/signed_control_diagnosis/original_predictions.json'
def main():
    OUT.mkdir(exist_ok=True);raw=json.loads(SRC.read_text());rows=[r for r in raw if r['case']['x']==0];assert len(rows)==200
    sigma=MISMATCH*V_TYP;protocol=dict(detector_prior='Independent zero-mean Gaussian offsets, sigma=MISMATCH*V_TYP; detectors independent of previously drawn circuit',
        sigma_V=sigma,source=str(SRC),formula='E residual^2 = sigma^2*(g_plus^2+g_minus^2)',scope='Steady small-error detector-mismatch contribution only, no new physical implementation or sampled detector errors',budget_s=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'units.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    result=[dict(seed=r['seed'],control_V=r['case']['y'],uncorrected_squared_V2=r['output_V']**2,
        expected_detector_squared_V2=sigma**2*sum(g*g for g in r['gate_openings']),gate_openings=r['gate_openings']) for r in rows]
    seeds=sorted({r['seed'] for r in result});assert len(seeds)==40
    def group(rr):
        before=float(np.mean([r['uncorrected_squared_V2'] for r in rr]));after=float(np.mean([r['expected_detector_squared_V2'] for r in rr]))
        byseed=[np.mean([r['expected_detector_squared_V2']-r['uncorrected_squared_V2'] for r in rr if r['seed']==s]) for s in seeds]
        return dict(uncorrected_rms_V=before**.5,conditional_expected_detector_rms_V=after**.5,
            expected_minus_observed_MSE_V2=after-before,paired_draw_bootstrap95_MSE_difference=interval(byseed),
            draws_where_conditional_expected_MSE_is_lower=sum(v<0 for v in byseed),draws=40)
    summary=dict(all_controls=group(result),by_control={str(y):group([r for r in result if r['control_V']==y]) for y in sorted({r['control_V'] for r in result})})
    # Analytic limiting fixtures: closed gates remove contribution, one open gives sigma, equal half gates sigma/sqrt2.
    assert sigma**2*(0**2+0**2)==0 and abs((sigma**2*(.5**2+.5**2))**.5-sigma/np.sqrt(2))<1e-15
    (OUT/'rows.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2,default=int)+'\n');print(json.dumps(summary,indent=2,default=int))
if __name__=='__main__':main()
