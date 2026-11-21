"""D139 feedforward transfer quadrature; no circuit simulator or fresh samples."""
import json, math, sys
from pathlib import Path
from statistics import NormalDist
import numpy as np
from numba import njit
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dynamic_parts_bench import ROOT, CAP, digest, provenance
from units import MISMATCH, V_TYP, K_B, T, Q_SI, RAIL
OUT=ROOT/'lab/v/population_trace_margin'
SRC=ROOT/'lab/v/motifs/order_v2/confirm.jsonl'

@njit(cache=True)
def convolution(forcing, a, initial):
    out=np.empty(len(forcing))
    value=initial
    for i in range(len(forcing)):
        value=a*value+forcing[i]
        out[i]=value
    return out

def envelope():
    z=NormalDist().inv_cdf(1-.01/(2*14)); lo=1-MISMATCH*z; hi=1+MISMATCH*z
    amplitude=.9*hi/lo; slope=40*lo
    input_sigma=math.sqrt(K_B*T/(CAP*lo))
    # Gross current bounded by leak*rail + full writer current in the approximate leaky path.
    gain=CAP*.6/.1*hi; leak=CAP/.15*lo
    out_sigma=math.sqrt(K_B*T/(CAP*lo)+Q_SI*(leak*RAIL+gain)/(2*leak*CAP*lo))
    allowed=.003-6*out_sigma
    assert allowed>0
    threshold=MISMATCH*V_TYP*z+6*input_sigma+math.log(amplitude/allowed-1)/slope
    return dict(z=z,simultaneous_component_probability_lower=.99,variables=14,
        input_thermal_sigma_upper_V=input_sigma,trace_noise_sigma_upper_V=out_sigma,
        nominal_threshold_V=threshold,allowed_deterministic_rest_V=allowed,
        maximum_gain_over_leak_V=amplitude,minimum_slope_per_V=slope)

def predict(row, threshold, dt):
    n=np.array(row['nodes']);e=np.array(row['elements']); t=np.arange(round(2.5/dt)+1)*dt
    starts=np.random.default_rng([row['seed'],128,4]).uniform(-.075,.075,8)
    v=np.empty((8,len(t)))
    for i in [0,1]:
        tau=n[2,i]/n[1,i];v[i]=starts[i]*np.exp(-t/tau)
        for at,duration,node,current in row['pulses']:
            if node==i:
                on=np.maximum(t-at,0);off=np.maximum(t-at-duration,0)
                v[i]+=current/n[1,i]*(np.exp(-off/tau)-np.exp(-on/tau))
    e[1,:2]+=threshold-.15
    for dest in range(2,8):
        current=np.zeros(len(t))
        for j in range(e.shape[1]):
            to,source,gate=np.array(row['links'])[:,j]
            if to!=dest:continue
            x=e[2,j]*(v[source]-e[1,j]);f=1/(1+np.exp(-x)) if e[4,j]>.5 else np.tanh(x)
            if gate>=0:f=f*np.clip(v[gate]/V_TYP,0,1)
            current+=e[0,j]*f
        a=math.exp(-dt*n[1,dest]/n[2,dest]);forcing=(1-a)/n[1,dest]*(current[1:]+current[:-1])/2
        v[dest,0]=starts[dest];v[dest,1:]=convolution(forcing,a,starts[dest])
    # Match the stored nominal 1ms sampling (bench stride rounds to 32 finest steps).
    sample=np.arange(0,len(t),round(.001/dt)); tt=t[sample];vv=v[:,sample]
    base=vv[:,(tt>.7)&(tt<.95)].mean(axis=1);delta=vv-base[:,None]
    first=1+np.random.default_rng([row['seed'],128,5]).uniform(.001,.009)
    last=first+abs(row['case']['delay'])
    coinc=float(delta[6,(tt>first)&(tt<last+.2)].max())
    order=float(delta[7,(tt>last+.02)&(tt<last+.10)].mean())
    case=row['case'];pair=case['a']>0 and case['b']>0;delay=case['delay']
    good_c=coinc>.15 if pair and delay==0 else coinc<.03 if not pair or abs(delay)>=.15 else True
    good_o=np.sign(delay)*order>.03 if pair and 0<abs(delay)<=.15 else abs(order)<(.06 if pair and delay==0 else .03)
    return dict(coincidence_V=coinc,order_V=order,metric_adequate=bool(good_c and good_o),
        order_adequate=bool(good_o),coincidence_adequate=bool(good_c))

def main():
    OUT.mkdir(exist_ok=True);raw=[json.loads(s) for s in SRC.read_text().splitlines()]
    dt=min(r['dt'] for r in raw);rows=[r for r in raw if r['dt']==dt and not r['control']]
    assert len(rows)==40*34 and len({(r['seed'],r['case']['id']) for r in rows})==len(rows)
    env=envelope();old=json.loads((ROOT/'lab/v/trace_margin/summary.json').read_text())['common_nominal_threshold_V']
    thresholds={'original':.15,'selected_draw_bound':old,'population_envelope':env['nominal_threshold_V']}
    protocol=dict(thresholds_V=thresholds,envelope=env,quadrature_steps_s=[.00005,.000025],
        source=str(SRC),interpretation='RC convolution with trapezoid forcing; omits rail fading/noise. '
        'Original 34-case criteria unchanged; no reliability or physical pass assigned to predictions.',
        budget_minutes=30)
    with (OUT/'protocol.json').open('x') as f:json.dump(protocol,f,indent=2)
    prov=provenance();prov['files'].update({str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__).resolve(),SRC,ROOT/'units.py',ROOT/'mixed_feedback.py']})
    prov['protocol_sha256']=digest(OUT/'protocol.json');(OUT/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    results=[];refine=0
    for mode,h in thresholds.items():
        for row in rows:
            p=predict(row,h,.00005)
            if row['seed']==rows[0]['seed']:
                finer=predict(row,h,.000025);refine=max(refine,max(abs(p[k]-finer[k]) for k in ['order_V','coincidence_V']))
            results.append(dict(mode=mode,seed=row['seed'],case=row['case'],observed_metrics=row['metrics'],**p))
        rr=[r for r in results if r['mode']==mode]
        print(mode, sum(r['metric_adequate'] for r in rr), '/',len(rr),flush=True)
    original=[r for r in results if r['mode']=='original'];summary=dict(envelope=env,maximum_refinement_change_V=refine,
        validation={k:dict(rmse_V=float(np.sqrt(np.mean([(r[k]-r['observed_metrics'][k])**2 for r in original]))),
                          maximum_error_V=max(abs(r[k]-r['observed_metrics'][k]) for r in original)) for k in ['order_V','coincidence_V']},
        modes={})
    for mode in thresholds:
        rr=[r for r in results if r['mode']==mode];ss=sorted({r['seed'] for r in rr})
        summary['modes'][mode]=dict(adequate_cases=sum(r['metric_adequate'] for r in rr),cases=len(rr),
            adequate_draws=sum(all(r['metric_adequate'] for r in rr if r['seed']==s) for s in ss),draws=len(ss),
            failed_order=sum(not r['order_adequate'] for r in rr),
            failed_near_order=sum(not r['order_adequate'] for r in rr if r['case']['a'] and r['case']['b'] and 0<abs(r['case']['delay'])<=.15),
            maximum_rest_trace_V=max(np.array(r['elements'])[0,i]/np.array(r['nodes'])[1,2+i]/(1+np.exp(np.array(r['elements'])[2,i]*(np.array(r['elements'])[1,i]+thresholds[mode]-.15))) for r in rows[::34] for i in [0,1]))
    (OUT/'rows.json').write_text(json.dumps(results)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
