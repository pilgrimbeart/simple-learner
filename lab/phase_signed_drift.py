"""D143: signed-reference drift response and analytical high-pass separation."""
import json,sys,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from units import V_TYP,RAIL,TAU_MAX
OUT=ROOT/'lab/v/phase_signed_drift';SRC=ROOT/'lab/v/phase_v1/confirm.jsonl'
def response(row,amp,drift,swap,representation,nf,nd):
    n=np.array(row['nodes']);e=np.array(row['elements']);w=2*np.pi*row['frequency_Hz'];wd=2*np.pi*.05
    theta=np.arange(nf)[:,None]*2*np.pi/nf;psi=np.arange(nd)[None,:]*2*np.pi/nd
    frequencies=w*(np.fft.fftfreq(nf)*nf)[:,None]+wd*(np.fft.fftfreq(nd)*nd)[None,:]
    tau=np.ones(2)
    def hp(freq,i):return 1j*freq*tau[i]/(1+1j*freq*tau[i])
    def filt(current,dest):return np.fft.ifft2(np.fft.fft2(current)/(n[1,dest]+1j*frequencies*n[2,dest])).real
    def activation(x):return x if representation=='linear_signed' else np.tanh(x)
    v=[]
    for i,j in enumerate([1,0] if swap else [0,1]):
        ph=row['case']['phase'] if j else 0.
        fast=CAP/.005*amp[j]*hp(w,i)/(n[1,i]+1j*w*n[2,i])
        slow=CAP/.005*drift*(1 if j==0 else -1)*hp(wd,i)/(n[1,i]+1j*wd*n[2,i])
        mean=0.
        v.append(mean+np.real(fast*np.exp(1j*(theta+ph)))+np.real(slow*np.exp(1j*psi)))
    for i in [0,1]:v.append(filt(e[0,i]*activation(e[2,i]*(v[i]-e[1,i])),i+2))
    current=e[0,2]*activation(e[2,2]*(v[1]-e[1,2]))*(v[2]/V_TYP)+e[0,3]*activation(e[2,3]*(v[0]-e[1,3]))*(v[3]/V_TYP)
    y=filt(current,4)
    return y.mean(axis=0),float(max(np.max(abs(x)) for x in v+[y])),tau.tolist()

def main():
    OUT.mkdir(exist_ok=True);rows=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in rows if r['dt']==DT/4 and not r['control']];assert len(rows)==480
    modes=['signed_gate','linear_signed'];protocol=dict(modes=modes,amp_V=[.05,.1],drift_V=.05,drift_Hz=.05,highpass_tau_s=1.,
        grids=[[256,128],[512,256]],tolerance_V=.00005,wanted_transmission=.9,drift_transmission=.1,budget_s=180)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/phase_baseline.py',ROOT/'lab/v/phase_gate_diagnosis/rows.json']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    old=json.loads((ROOT/'lab/v/phase_gate_diagnosis/rows.json').read_text());lookup={(r['mode'],r['seed'],r['band_Hz'],r['phase_rad']):r['corrected_V'] for r in old if r['scenario']=='unequal_amplitude'}
    result=[];validation=0.;resolution=0.;peak=0.
    for mode in modes:
        for r in rows:
            stationary=[response(r,[.05,.1],0.,s,mode,512,1)[0][0] for s in [False,True]]
            validation=max(validation,abs((stationary[0]-stationary[1])/2-lookup[mode,r['seed'],r['case']['frequency'],r['case']['phase']]))
            pair=[];coarse=[]
            for swap in [False,True]:
                y,p,_=response(r,[.05,.1],.05,swap,mode,512,256);pair.append(y);peak=max(peak,p)
                z,_,_=response(r,[.05,.1],.05,swap,mode,256,128);coarse.append(z)
            corrected=(pair[0]-pair[1])/2;low=(coarse[0]-coarse[1])/2;resolution=max(resolution,float(np.max(abs(corrected[::2]-low))))
            result.append(dict(mode=mode,seed=r['seed'],band_Hz=r['case']['frequency'],phase_rad=r['case']['phase'],corrected_V=corrected.tolist()))
        print(mode,'done',flush=True)
    checks=dict(validation_max_V=validation,resolution_max_V=resolution,maximum_state_V=peak);assert validation<.00005 and resolution<.00005 and peak<RAIL
    summary={}
    for mode in modes:
        rr=[r for r in result if r['mode']==mode];good=[];bias=[];wrong=0;zero=0
        for seed in sorted({r['seed'] for r in rr}):
            ok=True
            for band in [2.,5.]:
                cc=sorted([r for r in rr if r['seed']==seed and r['band_Hz']==band],key=lambda r:r['phase_rad'])[:5];m=np.array([r['corrected_V'] for r in cc]);bias.extend(m[2])
                ok &= bool(np.all(m[1]-m[3]>.004) and np.all(m[0]-m[4]>.008) and np.all(m[:-1]-m[1:]>.001))
                wrong+=sum(np.any(np.array(r['corrected_V'])*np.sign(r['phase_rad'])>1e-10) for r in cc if r['phase_rad']!=0)
                zero+=sum(np.any(abs(np.array(r['corrected_V']))<=1e-10) for r in cc if r['phase_rad']!=0)
            good.append(ok)
        summary[mode]=dict(adequate_draws=sum(good),draws=40,any_drift_phase_wrong_sign_cases=int(wrong),any_drift_phase_zero_cases=int(zero),local_cases=320,zero_bias_range_V=[float(min(bias)),float(max(bias))])
    a=.9;b=.1;fs=min(r['frequency_Hz'] for r in rows);fb=.05
    lower=a/(2*np.pi*fs*np.sqrt(1-a*a));upper=b/(2*np.pi*fb*np.sqrt(1-b*b))
    bound=dict(wanted_min_Hz=fs,drift_Hz=fb,minimum_frequency_ratio=float(a*np.sqrt(1-b*b)/(b*np.sqrt(1-a*a))),
        feasible_tau_interval_s=[float(lower),float(upper)],physical_leak_tau_max_s=TAU_MAX,
        frozen_1s_fast_transmission=float(2*np.pi*fs/np.sqrt(1+(2*np.pi*fs)**2)),frozen_1s_drift_transmission=float(2*np.pi*fb/np.sqrt(1+(2*np.pi*fb)**2)),
        condition='Bounds apply to a first-order ideal filter and specified sinusoidal components; not a universal brain prior or demonstrated circuit optimum.')
    data=dict(checks=checks,comparisons=summary,separation=bound);(OUT/'rows.json').write_text(json.dumps(result)+'\n');(OUT/'summary.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
if __name__=='__main__':main()
