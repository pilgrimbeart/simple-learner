"""D140: Fourier transfer analysis of full-port reversal, no circuit simulations."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,CAP,DT,digest,provenance
from units import V_TYP,RAIL
OUT=ROOT/'lab/v/phase_reversal'; SRC=ROOT/'lab/v/phase_v1/confirm.jsonl'
SCENARIOS={'equal':([.15,.15],[.1,.1]),'weak_A':([.15,.15],[.05,.1]),
           'weak_B':([.15,.15],[.1,.05]),'unequal_DC':([.1,.2],[.1,.1])}

def transfer(row,dc,amp,swap,size):
    n=np.array(row['nodes']);e=np.array(row['elements']);omega=2*np.pi*row['frequency_Hz']
    theta=np.arange(size)*2*np.pi/size;k=np.fft.fftfreq(size)*size
    phase=[0,row['case']['phase']];route=[1,0] if swap else [0,1]
    def coeff(current,dest):return np.fft.fft(current)/size/(n[1,dest]+1j*k*omega*n[2,dest])
    v=[]
    for i,j in enumerate(route):
        v.append(CAP/.005*dc[j]/n[1,i]+np.real(CAP/.005*amp[j]/(n[1,i]+1j*omega*n[2,i])*np.exp(1j*(theta+phase[j]))))
    for i in [0,1]:v.append(np.fft.ifft(coeff(e[0,i]*np.tanh(e[2,i]*(v[i]-e[1,i])),i+2)*size).real)
    current=e[0,2]*np.tanh(e[2,2]*(v[1]-e[1,2]))*np.clip(v[2]/V_TYP,0,1)+e[0,3]*np.tanh(e[2,3]*(v[0]-e[1,3]))*np.clip(v[3]/V_TYP,0,1)
    c=coeff(current,4)
    mean=float(np.sum(c*np.exp(1j*k*(row['initial_phase_rad']+omega*9))*np.sinc(k*omega*3/np.pi)).real)
    # Maximum departure from cycle mean for an arbitrary starting phase of a 6 s window.
    ripple=float(np.sum(np.abs(c[1:]*np.sinc(k[1:]*omega*3/np.pi))))
    return dict(cycle_mean_V=float(c[0].real),finite_mean_V=mean,window_error_bound_V=ripple)

def settling(row):
    n=np.array(row['nodes']);e=np.array(row['elements']);a=np.diag(-n[1]/n[2])
    # Global Lipschitz bounds for tanh and clipped gates; independent of amplitude and phase.
    for i in [0,1]:a[i+2,i]=abs(e[0,i]*e[2,i])/n[2,i+2]
    a[4,1]=abs(e[0,2]*e[2,2])/n[2,4];a[4,0]=abs(e[0,3]*e[2,3])/n[2,4]
    a[4,2]=abs(e[0,2])/V_TYP/n[2,4];a[4,3]=abs(e[0,3])/V_TYP/n[2,4]
    vals,vec=np.linalg.eig(a);weights=vec[4]*np.linalg.solve(vec,np.full(5,2*RAIL))
    ts=np.linspace(0,20,2001);bound=(np.exp(ts[:,None]*vals)*weights).sum(axis=1).real
    assert bound.min()>-1e-10
    # Last exceedance gives a conservative grid-rounded time for the computed curve, not sampled trajectory.
    times={}
    for tol in [.001,.0001]:
        bad=np.flatnonzero(bound>tol);times[str(tol)]=float(ts[bad[-1]+1]) if len(bad) and bad[-1]+1<len(ts) else None
    return dict(wait_to_bound_s=times,bound_at_6s_V=float((np.exp(6*vals)*weights).sum().real),
        mean_bound_6_to_12s_V=float((weights*(np.exp(12*vals)-np.exp(6*vals))/(6*vals)).sum().real),
        maximum_RC_s=float(max(n[2]/n[1])))

def main():
    OUT.mkdir(exist_ok=True);raw=[json.loads(l) for l in SRC.read_text().splitlines()]
    rows=[r for r in raw if r['dt']==DT/4 and not r['control']]
    assert len(rows)==480 and len({(r['seed'],r['case']['id']) for r in rows})==480
    protocol=dict(scenarios=SCENARIOS,resolutions=[4096,8192],identity_refinement_size=32768,source=str(SRC),
        criterion='Original D133 near>.004V, far>.008V, adjacent local drop>.001V; bias separately.',
        interpretation='Full-port swap retains component arrays; cycle mean and same-window mean are distinct. '
        'Sequential physical readout additionally incurs settling, arbitrary window phase and drift.',budget_s=180)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'lab/phase_bias.py']});prov['protocol_sha256']=digest(OUT/'protocol.json')
    (OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    results=[];errors=[];resolution=0.;identity=0.;identity_coarse=0.;refined=0
    for name,(dc,amp) in SCENARIOS.items():
        for r in rows:
            p=[transfer(r,dc,amp,s,8192) for s in [False,True]]
            for swap in [False,True]:
                coarse=transfer(r,dc,amp,swap,4096)
                resolution=max(resolution,abs(p[swap]['finite_mean_V']-coarse['finite_mean_V']))
            corrected=(p[0]['cycle_mean_V']-p[1]['cycle_mean_V'])/2
            if name=='equal':
                errors.append(p[0]['finite_mean_V']-r['mean_V'])
                if r['case']['phase']==0:assert abs(corrected)<1e-14
            # Reverse complete labelled waveform pair, including absolute phase shift.
            reverse=dict(r,case=dict(r['case'],phase=-r['case']['phase']))
            q=transfer(reverse,list(reversed(dc)),list(reversed(amp)),False,8192)
            err=abs(q['cycle_mean_V']-p[1]['cycle_mean_V']);identity_coarse=max(identity_coarse,err)
            if err>1e-10:
                fine_q=transfer(reverse,list(reversed(dc)),list(reversed(amp)),False,32768)
                fine_s=transfer(r,dc,amp,True,32768)
                err=abs(fine_q['cycle_mean_V']-fine_s['cycle_mean_V']);refined+=1
            identity=max(identity,err)
            results.append(dict(scenario=name,seed=r['seed'],band_Hz=r['case']['frequency'],
                phase_rad=r['case']['phase'],normal=p[0],swapped=p[1],corrected_cycle_V=corrected,
                sequential_window_error_bound_V=(p[0]['window_error_bound_V']+p[1]['window_error_bound_V'])/2))
        print('completed',name,flush=True)
    summary=dict(validation_rmse_V=float(np.sqrt(np.mean(np.array(errors)**2))),validation_max_error_V=max(abs(x) for x in errors),
        maximum_resolution_change_V=resolution,swap_cycle_identity_error_V=identity,coarse_identity_error_V=identity_coarse,refined_identity_cases=refined,scenarios={})
    (OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    assert summary['validation_max_error_V']<.001 and resolution<1e-6 and identity<1e-10
    for name in SCENARIOS:
        rr=[r for r in results if r['scenario']==name];groups=[]
        for seed in sorted({r['seed'] for r in rr}):
            for band in [2.,5.]:
                cc=sorted([r for r in rr if r['seed']==seed and r['band_Hz']==band],key=lambda r:r['phase_rad'])[:5]
                m=[r['corrected_cycle_V'] for r in cc];drops=[m[i]-m[i+1] for i in range(4)]
                groups.append(dict(seed=seed,band_Hz=band,near_V=m[1]-m[3],far_V=m[0]-m[4],minimum_drop_V=min(drops),
                    sensitivity_adequate=m[1]-m[3]>.004 and m[0]-m[4]>.008 and min(drops)>.001))
        zeros=[r['corrected_cycle_V'] for r in rr if r['phase_rad']==0]
        local=[r for r in rr if 0<abs(r['phase_rad'])<=np.pi/2]
        summary['scenarios'][name]=dict(zero_bias_range_V=[min(zeros),max(zeros)],zero_bias_rms_V=float(np.sqrt(np.mean(np.array(zeros)**2))),
            adequate_draws=sum(all(g['sensitivity_adequate'] for g in groups if g['seed']==s) for s in sorted({r['seed'] for r in rr})),draws=40,
            wrong_local_sign=sum(r['corrected_cycle_V']*r['phase_rad']>=0 for r in local),local_cases=len(local),
            max_sequential_window_error_bound_V=max(r['sequential_window_error_bound_V'] for r in rr),groups=groups)
    ss=[dict(seed=r['seed'],**settling(r)) for r in rows if r['case']['id']=='2.0_2'];assert len(ss)==40
    summary['settling']=dict(max_wait_1mV_s=max(s['wait_to_bound_s']['0.001'] for s in ss),max_wait_0_1mV_s=max(s['wait_to_bound_s']['0.0001'] for s in ss),
        max_mean_error_6_to_12s_V=max(s['mean_bound_6_to_12s_V'] for s in ss),max_RC_s=max(s['maximum_RC_s'] for s in ss))
    (OUT/'rows.json').write_text(json.dumps(results)+'\n');(OUT/'settling.json').write_text(json.dumps(ss,indent=2)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({**summary,'scenarios':{k:{kk:vv for kk,vv in v.items() if kk!='groups'} for k,v in summary['scenarios'].items()}},indent=2))
if __name__=='__main__':main()
