"""D164 conditional detector-precision requirement; no sampled circuitry."""
import json,math,sys
from pathlib import Path
from statistics import NormalDist
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,digest,provenance
from units import MISMATCH,V_TYP
from order_continuous_baseline import TAUS
OUT=ROOT/'lab/v/order_calibration_precision'
SRC=ROOT/'lab/v/order_continuous_baseline/observations.json';CAPACITY=ROOT/'lab/v/order_balance_information/draws.json'
def main():
    OUT.mkdir(exist_ok=True);protocol=dict(source=str(SRC),capacity=str(CAPACITY),taus_s=TAUS,positive_near_priors=[.5,.8],initialisation='random',nominal_sigma_V=MISMATCH*V_TYP,independent_path_counts=[1,4,16],budget_s=30,scope='Conditional Gaussian detector-error reference on reused component draws; independence/material/readout not implemented')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    rows=json.loads(SRC.read_text());capacity={r['seed']:r for r in json.loads(CAPACITY.read_text())};result=[];normal=NormalDist()
    for tau in TAUS:
      for prior in [.5,.8]:
       for seed,c in capacity.items():
        rr=[r for r in rows if r['seed']==seed];a=b=w=0.
        for r in rr:
            cc=r['case'];near=cc['a'] and cc['b'] and 0<abs(cc['delay'])<=.15;weight=(2*prior if cc['delay']>0 else 2*(1-prior)) if near else 1.
            aa,bb=r['observations_Vs'][f'{tau}:random'];a+=weight*aa;b+=weight*bb;w+=weight*r['weight_s']
        assert b>0 and w>0
        lo,hi=c['feasible_interval'];feasible=c['feasible_order'] and c['coincidence_all']
        # None of these feasible sets reaches a clipping boundary; do not silently ignore its mass.
        if feasible:assert -1<lo<hi<1
        lower,upper=(a+b*lo)/w,(a+b*hi)/w
        probs={str(n):normal.cdf(upper/(MISMATCH*V_TYP/math.sqrt(n)))-normal.cdf(lower/(MISMATCH*V_TYP/math.sqrt(n))) if feasible else 0. for n in [1,4,16]}
        result.append(dict(seed=seed,tau_s=tau,prior=prior,feasible=feasible,error_interval_V=[lower,upper],symmetric_error_margin_V=max(0.,min(-lower,upper)) if feasible else 0.,conditional_success=probs))
    summary={}
    for tau in TAUS:
      for prior in [.5,.8]:
        rr=[r for r in result if r['tau_s']==tau and r['prior']==prior];positive=sorted(r['symmetric_error_margin_V'] for r in rr if r['symmetric_error_margin_V']>0)
        summary[f'{tau}:{prior}']=dict(draws=40,zero_error_adequate=sum(r['symmetric_error_margin_V']>0 for r in rr),positive_symmetric_margin_range_V=[min(positive),max(positive)] if positive else None,conditional_expected_adequate_draws={str(n):sum(r['conditional_success'][str(n)] for r in rr) for n in [1,4,16]})
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,CAPACITY,ROOT/'lab/order_continuous_baseline.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    for name,obj in [('provenance',prov),('summary',summary),('rows',result)]: (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
