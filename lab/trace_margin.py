"""D135 transfer-equation bound and pulse quadrature; not a circuit simulation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT,DT,CAP,digest,provenance
from retained_write_report import svg_plot
from retained_write_preview import render
OUT=ROOT/'lab/v/trace_margin';SRC=ROOT/'lab/v/motifs/order_v2'

def trace(row,side,nominal,dt):
    n=np.array(row['nodes']);e=np.array(row['elements']);dest=2+side;t=np.arange(round(.25/dt)+1)*dt
    tau=n[2,side]/n[1,side];vmax=CAP*.35/.01/n[1,side];x=np.where(t<=.04,vmax*(-np.expm1(-t/tau)),vmax*(-np.expm1(-.04/tau))*np.exp(-(t-.04)/tau))
    threshold=e[1,side]+nominal-.15;gain=e[0,side];slope=e[2,side];leak=n[1,dest];cap=n[2,dest];tau_y=cap/leak
    current=gain/(1+np.exp(-slope*(x-threshold)));base=gain/leak/(1+np.exp(slope*threshold));weighted=np.exp(t/tau_y)*current/cap
    integral=np.concatenate(([0.],np.cumsum((weighted[:-1]+weighted[1:])*.5*dt)))
    y=np.exp(-t/tau_y)*(base+integral)
    return t,y,base

def main():
    OUT.mkdir(exist_ok=True);raw=[json.loads(x) for x in (SRC/'confirm.jsonl').read_text().splitlines()];seeds=sorted({r['seed'] for r in raw if not r['passed']});rows=[next(r for r in raw if r['seed']==s and r['dt']==DT/4) for s in seeds]
    spec=dict(seeds=seeds,gate_target_fraction=.01,gate_scale_V=.3,weakest_input_nominal_V=.35,pulse_duration_s=.04,sample_times_after_onset_s=[.06,.15],sample_times_after_offset_s=[.06,.15],quadrature_steps_s=[.00005,.000025],interpretation='Common nominal threshold shift preserves observed offset errors; approximate leaky sigmoid response omits rail fade and stochastic variation. No pass criterion changed.')
    with (OUT/'protocol.json').open('x') as f:json.dump(spec,f,indent=2)
    prov=provenance();prov['files'].update({'lab/trace_margin.py':digest(__file__),'lab/v/motifs/order_v2/confirm.jsonl':digest(SRC/'confirm.jsonl')});prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    requirements=[]
    for r in rows:
        n=np.array(r['nodes']);e=np.array(r['elements'])
        for i in [0,1]:
            A=e[0,i]/n[1,2+i];h=np.log(A/.003-1)/e[2,i];delta=e[1,i]-.15
            requirements.append(dict(seed=r['seed'],side=i,actual_threshold_required_V=float(h),offset_error_V=float(delta),nominal_required_V=float(h-delta)))
    common=max(r['nominal_required_V'] for r in requirements);nominals=sorted(set([.15,common]+np.linspace(.15,max(.3,common),16).tolist()));result=[];resolution=0.
    for nominal in nominals:
        for r in rows:
            for side in [0,1]:
                t,y,base=trace(r,side,nominal,.000025);tc,yc,_=trace(r,side,nominal,.00005);resolution=max(resolution,float(np.max(abs(yc-y[::2]))))
                result.append(dict(seed=r['seed'],side=side,nominal_V=nominal,rest_V=float(base),peak_V=float(y.max()),onset_60ms_V=float(np.interp(.06,t,y)),onset_150ms_V=float(np.interp(.15,t,y)),offset_60ms_V=float(np.interp(.10,t,y)),offset_150ms_V=float(np.interp(.19,t,y))))
    validation=[]
    for side,label in enumerate(['A','B']):
        case=f'single_{label}_0.35';r=next(r for r in raw if r['seed']==2026112200 and r['case']['id']==case and r['dt']==DT/4);tr=np.load(SRC/f'confirm_{case}_False.npz')['trace'];start=r['pulses'][0][0];mask=(tr[:,0]>=start)&(tr[:,0]<=start+.25);t,y,_=trace(r,side,.15,.000025);error=np.interp(tr[mask,0]-start,t,y)-tr[mask,side+3]
        validation.append(dict(seed=r['seed'],side=side,rmse_V=float(np.sqrt(np.mean(error**2))),max_error_V=float(np.max(abs(error)))))
    chosen=[r for r in result if r['nominal_V']==common];base=[r for r in result if r['nominal_V']==.15]
    summary=dict(common_nominal_threshold_V=common,maximum_rest_at_bound_V=max(r['rest_V'] for r in chosen),original_maximum_rest_V=max(r['rest_V'] for r in base),range_at_bound={key:[min(r[key] for r in chosen),max(r[key] for r in chosen)] for key in ['peak_V','onset_60ms_V','onset_150ms_V','offset_60ms_V','offset_150ms_V']},maximum_quadrature_change_V=resolution,saved_trace_validation=validation)
    for name,data in [('requirements',requirements),('curve',result),('summary',summary)]:(OUT/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    xx=np.array(nominals);series=[]
    for key,label in [('rest_V','max resting trace'),('onset_60ms_V','min at 60 ms'),('onset_150ms_V','min at 150 ms')]:series.append((xx,np.array([(max if key=='rest_V' else min)(r[key] for r in result if r['nominal_V']==x) for x in xx]),label))
    svg=svg_plot(series,'Quietness versus retained signal',(xx.min(),xx.max()),(0,max(y.max() for _,y,_ in series)*1.1),'nominal threshold (V)');(OUT/'tradeoff.svg').write_text(svg);render(OUT/'tradeoff.svg')
    (OUT/'report.md').write_text('# Quiet-trace bound — D135\n\n'+f'Common nominal threshold required for a 1% resting gate: **{common:.4f} V**, versus 0.15 V originally. This is an informed diagnostic bound over six selected draws, not a repair or a universal threshold.\n\n'+json.dumps(summary,indent=2)+'\n\nAt the bound, equality leaves no stochastic safety margin. Weak-event voltage is reported, not declared sufficient to pass the complete order task. Both downstream threshold/gain balance and the original frozen criteria still matter. Rail fading and noise are omitted only in these transfer-equation calculations; saved noisy traces provide an independent approximation check. Full curve, settings, raw-source hashes and validation are retained beside this report.\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
