"""D141: two-frequency transfer equations, no circuit trajectory simulation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from phase_reversal import transfer
from units import V_TYP,RAIL
OUT=ROOT/'lab/v/phase_baseline';SRC=ROOT/'lab/v/phase_v1/confirm.jsonl'
SCENARIOS={'equal':([.1,.1],0.),'unequal_amplitude':([.05,.1],0.),'drifting':([.05,.1],.05)}

def response(row,amp,drift,swap,mode,nf,nd):
    n=np.array(row['nodes']);e=np.array(row['elements']);w=2*np.pi*row['frequency_Hz'];wd=2*np.pi*.05
    theta=np.arange(nf)[:,None]*2*np.pi/nf;psi=np.arange(nd)[None,:]*2*np.pi/nd
    frequencies=w*(np.fft.fftfreq(nf)*nf)[:,None]+wd*(np.fft.fftfreq(nd)*nd)[None,:]
    tau=np.ones(2) if mode=='matched' else (n[2,:2]/n[1,:2])/.005
    def hp(freq,i):return 1j*freq*tau[i]/(1+1j*freq*tau[i]) if mode!='bypass' else 1.
    def filt(current,dest):return np.fft.ifft2(np.fft.fft2(current)/(n[1,dest]+1j*frequencies*n[2,dest])).real
    v=[]
    for i,j in enumerate([1,0] if swap else [0,1]):
        ph=row['case']['phase'] if j else 0.
        fast=CAP/.005*amp[j]*hp(w,i)/(n[1,i]+1j*w*n[2,i])
        slow=CAP/.005*drift*(1 if j==0 else -1)*hp(wd,i)/(n[1,i]+1j*wd*n[2,i])
        mean=CAP/.005*.15/n[1,i] if mode=='bypass' else 0.
        v.append(mean+np.real(fast*np.exp(1j*(theta+ph)))+np.real(slow*np.exp(1j*psi)))
    for i in [0,1]:v.append(filt(e[0,i]*np.tanh(e[2,i]*(v[i]-e[1,i])),i+2))
    current=e[0,2]*np.tanh(e[2,2]*(v[1]-e[1,2]))*np.clip(v[2]/V_TYP,0,1)+e[0,3]*np.tanh(e[2,3]*(v[0]-e[1,3]))*np.clip(v[3]/V_TYP,0,1)
    y=filt(current,4)
    return y.mean(axis=0),float(max(np.max(abs(x)) for x in v+[y])),tau.tolist()

def main():
    OUT.mkdir(exist_ok=True);rows=[json.loads(l) for l in SRC.read_text().splitlines()];rows=[r for r in rows if r['dt']==DT/4 and not r['control']];assert len(rows)==480
    protocol=dict(scenarios=SCENARIOS,constant_means_V=[.1,.2],highpass_tau_s=1.,drift_frequency_Hz=.05,modes=['matched','reused_RC'],
        grids=[[256,128],[512,256]],tolerance_V=.00005,budget_s=180,
        observation='Fast-phase Fourier projection at every drift phase, retaining slow nonlinear response. No observer projection supplied to a brain; no noise/rail-fading/new filter offsets in this analytical reference.')
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/phase_reversal.py']});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    # Independent reduction check over all original phase/frequency/draw cases.
    validation=max(abs(response(r,[.1,.1],0.,False,'bypass',512,1)[0][0]-transfer(r,[.15,.15],[.1,.1],False,8192)['cycle_mean_V']) for r in rows)
    results=[];resolution=0.;peak=0.
    for mode in protocol['modes']:
        for scenario,(amp,drift) in SCENARIOS.items():
            for r in rows:
                nd=256 if drift else 1;coarse_nd=128 if drift else 1
                pair=[];coarse=[]
                for swap in [False,True]:
                    y,p,tau=response(r,amp,drift,swap,mode,512,nd);pair.append(y);peak=max(peak,p)
                    z,_,_=response(r,amp,drift,swap,mode,256,coarse_nd);coarse.append(z)
                corrected=(pair[0]-pair[1])/2;low=(coarse[0]-coarse[1])/2
                resolution=max(resolution,float(np.max(abs(corrected[::2 if drift else 1]-low))))
                results.append(dict(mode=mode,scenario=scenario,seed=r['seed'],band_Hz=r['case']['frequency'],phase_rad=r['case']['phase'],
                    corrected_V=corrected.tolist(),highpass_tau_s=tau))
            print(mode,scenario,'done',flush=True)
    checks=dict(bypass_validation_max_error_V=validation,maximum_resolution_change_V=resolution,maximum_state_magnitude_V=peak,within_rails=peak<RAIL)
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(OUT/'rows.json').write_text(json.dumps(results)+'\n');print(json.dumps(checks),flush=True)
    assert validation<.00005 and resolution<.00005 and peak<RAIL
    summary={}
    for mode in protocol['modes']:
        for scenario in SCENARIOS:
            rr=[r for r in results if r['mode']==mode and r['scenario']==scenario];good=[];signbad=0;bias=[];mingap=1e9
            for seed in sorted({r['seed'] for r in rr}):
                ok=True
                for band in [2.,5.]:
                    cc=sorted([r for r in rr if r['seed']==seed and r['band_Hz']==band],key=lambda r:r['phase_rad'])[:5]
                    m=np.array([r['corrected_V'] for r in cc]);drops=m[:-1]-m[1:];mingap=min(mingap,float(drops.min()))
                    ok &= bool(np.all(m[1]-m[3]>.004) and np.all(m[0]-m[4]>.008) and np.all(drops>.001))
                    bias.extend(m[2]);signbad+=sum(np.any(np.array(r['corrected_V'])*r['phase_rad']>=0) for r in cc if r['phase_rad']!=0)
                good.append(ok)
            summary[mode+':'+scenario]=dict(adequate_draws=sum(good),draws=40,any_drift_phase_wrong_sign_cases=int(signbad),local_cases=320,
                zero_phase_range_V=[float(min(bias)),float(max(bias))],minimum_adjacent_drop_V=mingap)
    (OUT/'summary.json').write_text(json.dumps(dict(checks=checks,comparisons=summary),indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
