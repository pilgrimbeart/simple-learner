"""D142 stationary transfer interventions on signed representation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from units import V_TYP
OUT=ROOT/'lab/v/phase_gate_diagnosis';SRC=ROOT/'lab/v/phase_v1/confirm.jsonl'
MODES=['original','zero_lag_offsets','signed_gate','linear_signed']

def predict(row,amp,swap,mode,size):
    n=np.array(row['nodes']);e=np.array(row['elements']);w=2*np.pi*row['frequency_Hz'];theta=np.arange(size)*2*np.pi/size;k=np.fft.fftfreq(size)*size
    if mode=='zero_lag_offsets':e[1,:2]=0
    def activation(x):return x if mode=='linear_signed' else np.tanh(x)
    def lowpass(current,i):return np.fft.ifft(np.fft.fft(current)/(n[1,i]+1j*k*w*n[2,i])).real
    v=[]
    for i,j in enumerate([1,0] if swap else [0,1]):
        ph=row['case']['phase'] if j else 0.;hp=1j*w/(1+1j*w)
        v.append(np.real(CAP/.005*amp[j]*hp/(n[1,i]+1j*w*n[2,i])*np.exp(1j*(theta+ph))))
    for i in [0,1]:v.append(lowpass(e[0,i]*activation(e[2,i]*(v[i]-e[1,i])),i+2))
    gates=[x/V_TYP if mode in ['signed_gate','linear_signed'] else np.clip(x/V_TYP,0,1) for x in v[2:]]
    current=e[0,2]*activation(e[2,2]*(v[1]-e[1,2]))*gates[0]+e[0,3]*activation(e[2,3]*(v[0]-e[1,3]))*gates[1]
    return dict(mean_V=float(current.mean()/n[1,4]),lag_min_V=[float(x.min()) for x in v[2:]],lag_max_V=[float(x.max()) for x in v[2:]],
        positive_fraction=[float(np.mean(x>0)) for x in v[2:]])

def main():
    OUT.mkdir(exist_ok=True);raw=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in raw if r['dt']==DT/4 and not r['control']];assert len(rows)==480
    protocol=dict(modes=MODES,scenarios={'equal':[.1,.1],'unequal_amplitude':[.05,.1]},grids=[4096,8192],tolerance_V=.00005,budget_s=120,
        meaning='Algebraic interventions only: a signed gate and ideal linear transfer are not silently added to circuit engine.')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    old=json.loads((ROOT/'lab/v/phase_baseline/rows.json').read_text());old={(r['scenario'],r['seed'],r['band_Hz'],r['phase_rad']):r for r in old if r['mode']=='matched' and r['scenario']!='drifting'}
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/v/phase_baseline/rows.json']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    result=[];validation=0.;resolution=0.
    for mode in MODES:
        for scenario,amp in protocol['scenarios'].items():
            for r in rows:
                p=[predict(r,amp,s,mode,8192) for s in [False,True]];c=(p[0]['mean_V']-p[1]['mean_V'])/2
                coarse=[predict(r,amp,s,mode,4096) for s in [False,True]];resolution=max(resolution,abs(c-(coarse[0]['mean_V']-coarse[1]['mean_V'])/2))
                if mode=='original':validation=max(validation,abs(c-old[scenario,r['seed'],r['case']['frequency'],r['case']['phase']]['corrected_V'][0]))
                result.append(dict(mode=mode,scenario=scenario,seed=r['seed'],band_Hz=r['case']['frequency'],phase_rad=r['case']['phase'],corrected_V=c,normal=p[0],swapped=p[1]))
        print(mode,'done',flush=True)
    checks=dict(validation_max_V=validation,resolution_max_V=resolution);assert validation<.00005 and resolution<.00005
    summary={}
    for mode in MODES:
        for scenario in protocol['scenarios']:
            rr=[r for r in result if r['mode']==mode and r['scenario']==scenario];good=[]
            for seed in sorted({r['seed'] for r in rr}):
                ok=True
                for band in [2.,5.]:
                    cc=sorted([r for r in rr if r['seed']==seed and r['band_Hz']==band],key=lambda r:r['phase_rad'])[:5];m=[r['corrected_V'] for r in cc]
                    ok &= m[1]-m[3]>.004 and m[0]-m[4]>.008 and min(m[i]-m[i+1] for i in range(4))>.001
                good.append(ok)
            local=[r for r in rr if 0<abs(r['phase_rad'])<=np.pi/2];zeros=[r['corrected_V'] for r in rr if r['phase_rad']==0]
            summary[mode+':'+scenario]=dict(adequate_draws=sum(good),draws=40,strictly_wrong_sign=sum(r['corrected_V']*np.sign(r['phase_rad'])>1e-10 for r in local),
                no_signal=sum(abs(r['corrected_V'])<=1e-10 for r in local),local_cases=320,zero_bias_range_V=[min(zeros),max(zeros)],
                both_lags_closed_cases=sum(max(r['normal']['lag_max_V'])<=0 and max(r['swapped']['lag_max_V'])<=0 for r in local))
    (OUT/'rows.json').write_text(json.dumps(result)+'\n');(OUT/'summary.json').write_text(json.dumps(dict(checks=checks,comparisons=summary),indent=2,default=int)+'\n');print(json.dumps(dict(checks=checks,comparisons=summary),indent=2,default=int))
if __name__=='__main__':main()
