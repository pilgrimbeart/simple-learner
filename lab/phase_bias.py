"""D137 periodic Fourier analysis of stored circuits; no noise-disabled simulation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,CAP,digest,provenance
from retained_write_report import svg_plot
from retained_write_preview import render
OUT=ROOT/'lab/v/phase_bias';SRC=ROOT/'lab/v/phase_v1'
MODES=['original','zero_output_offsets','equal_output_gains','equal_upstream','equal_output_transfers','both_matched']

def predict(row,mode,size):
    n=np.array(row['nodes']);e=np.array(row['elements']);omega=2*np.pi*row['frequency_Hz'];theta=np.arange(size)*2*np.pi/size;k=np.fft.fftfreq(size)*size
    if mode in ['equal_upstream','both_matched']:
        for a,b in [(0,1),(2,3)]:n[:3,a]=n[:3,b]=n[:3,[a,b]].mean(axis=1)
        e[:,0]=e[:,1]=e[:,:2].mean(axis=1)
    if mode=='zero_output_offsets':e[1,2:]=0
    if mode=='equal_output_gains':e[0,2:]=np.mean(abs(e[0,2:]))*np.array([1.,-1.])
    if mode in ['equal_output_transfers','both_matched']:
        e[1:,2]=e[1:,3]=e[1:,2:].mean(axis=1);e[0,2:]=np.mean(abs(e[0,2:]))*np.array([1.,-1.])
    def coefficients(current,dest):return np.fft.fft(current)/size/(n[1,dest]+1j*k*omega*n[2,dest])
    v=[]
    for i in [0,1]:v.append(CAP/.005*.15/n[1,i]+np.real(CAP/.005*.1/(n[1,i]+1j*omega*n[2,i])*np.exp(1j*theta)))
    for i in [0,1]:v.append(np.fft.ifft(coefficients(e[0,i]*np.tanh(e[2,i]*(v[i]-e[1,i])),i+2)*size).real)
    current=e[0,2]*np.tanh(e[2,2]*(v[1]-e[1,2]))*np.clip(v[2]/.3,0,1)+e[0,3]*np.tanh(e[2,3]*(v[0]-e[1,3]))*np.clip(v[3]/.3,0,1)
    coeff=coefficients(current,4);wave=np.fft.ifft(coeff*size).real
    # Exact finite-window integral of the periodic Fourier representation, not whole-cycle averaging.
    mean=np.sum(coeff*np.exp(1j*k*(row['initial_phase_rad']+omega*9))*np.sinc(k*omega*3/np.pi)).real
    return dict(mean_V=float(mean),cycle_mean_V=float(coeff[0].real),maximum_absolute_output_V=float(np.max(abs(wave))),minimum_lag_V=float(min(v[2].min(),v[3].min())))

def main():
    OUT.mkdir(exist_ok=True);raw=[json.loads(l) for l in (SRC/'confirm.jsonl').read_text().splitlines()];rows=[r for r in raw if r['dt']==DT/4 and r['case']['phase']==0];assert len(rows)==80
    spec=dict(rows=80,source=str(SRC/'confirm.jsonl'),modes=MODES,resolutions=[4096,8192],analysis='Periodic Fourier solution of linear RC filters with nonlinear tanh and clipped gates evaluated on the phase grid. Mean over6..12s includes drawn initial phase. Omit rail fading, noise and startup transient; validate against original noisy means before interpreting interventions.',counterfactuals='Equal upstream averages paired input/lag leak/cap and lag element parameters. Equal output transfers averages gain magnitude, threshold and slope. All equalisation is an informed algebraic intervention, not an implementable calibration.',budget_minutes=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(spec,f,indent=2)
    prov=provenance();prov['files'].update({'lab/phase_bias.py':digest(__file__),'lab/v/phase_v1/confirm.jsonl':digest(SRC/'confirm.jsonl')});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    predictions=[];resolution=0.
    for r in rows:
        for mode in MODES:
            p=predict(r,mode,8192);coarse=predict(r,mode,4096);resolution=max(resolution,abs(p['mean_V']-coarse['mean_V']));predictions.append(dict(seed=r['seed'],frequency_Hz=r['frequency_Hz'],band_Hz=r['case']['frequency'],mode=mode,observed_mean_V=r['mean_V'],**p))
    original=[r for r in predictions if r['mode']=='original'];pred=np.array([r['mean_V'] for r in original]);obs=np.array([r['observed_mean_V'] for r in original]);err=pred-obs
    summary=dict(validation_rmse_V=float(np.sqrt(np.mean(err**2))),validation_max_error_V=float(max(abs(err))),validation_correlation=float(np.corrcoef(pred,obs)[0,1]),maximum_resolution_change_V=resolution,observed_rms_bias_V=float(np.sqrt(np.mean(obs**2))),modes={m:dict(predicted_rms_bias_V=float(np.sqrt(np.mean([r['mean_V']**2 for r in predictions if r['mode']==m]))),range_V=[min(r['mean_V'] for r in predictions if r['mode']==m),max(r['mean_V'] for r in predictions if r['mode']==m)]) for m in MODES})
    (OUT/'predictions.json').write_text(json.dumps(predictions,indent=2)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    indices=np.argsort(obs);x=np.arange(len(obs));svg=svg_plot([(x,obs[indices],'observed'),(x,pred[indices],'predicted')],'Zero-phase bias: all 80 draw/band pairs',(0,79),(-.27,.26),'pairs sorted by observed bias');(OUT/'prediction.svg').write_text(svg);render(OUT/'prediction.svg')
    lines=['# Phase-bias decomposition — D137','',f'Original transfer-equation prediction: RMSE **{summary["validation_rmse_V"]*1000:.3f} mV**, maximum error {summary["validation_max_error_V"]*1000:.3f} mV; observed RMS bias {summary["observed_rms_bias_V"]*1000:.2f} mV. Fourier resolution change {resolution:.3g} V.','','| Informed algebraic intervention | Predicted RMS zero-phase bias (mV) |','|---|---:|']
    for m,v in summary['modes'].items():lines.append(f'| {m.replace("_"," ")} | {v["predicted_rms_bias_V"]*1000:.3f} |')
    lines+=['','These are counterfactual transfer-equation calculations, not new circuit results. Effects interact and are not additive. Averaging away manufacturing differences requires information unavailable to the brain. The analysis retains nonlinear source/gate functions and finite-window periodic ripple, but omits rail fading, stochastic variation and startup transients. Validation error is reported against the original noisy runs. No calibrated control, phase locking or learned reference has been demonstrated.','', 'Reproduce with lab/phase_bias.py in a fresh output folder. Protocol, all predictions, source hashes and raw source provenance are retained.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
