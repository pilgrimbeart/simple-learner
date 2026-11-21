"""D168 Task E: the noise wall for a later noisy calibration pilot (arithmetic on saved schedules and records).

Feasible ranges, not bits (no learner prior or likelihood is specified). Quantities:
 1. evidence rate: simultaneous anchors per second, nominal (4/34 of events at 10 s mean spacing) and counted in the
    40 D163 schedules; time for 95% chance of at least N anchors (binomial in the event count T/10 s).
 2. per-anchor B and W (and integral of w^2) from D167's category totals (full 1000 s window), spread over draws;
    per-anchor settings from D165's final-third per-event contributions, and whether one anchor alone lands in the
    draw's feasible interval (evidence variability, distinct from circuit noise).
 3. signal to noise: equivalent readout error per anchor from the noise of nodes that would carry the observation,
    under mixed_feedback.py's noise model (silicon required; biology shown as a reference only):
      order node (exists): Ornstein-Uhlenbeck with time constant C/leak; var(int w*n dt) ~ 2*s^2*tau*int w^2 dt
      (valid when tau is short beside the anchor's weight; stated approximation);
      baseline node (would exist, 25 pF, 0.15 s): nearly constant over an anchor, equivalent error = its SD;
      knob memory (would exist, 25 pF): shot noise of the charge written, sqrt(q*|dV|/C), for a full V_TYP write.
    compared with Task A's requirement; anchors needed for the noise SD to reach the requirement and a third of it.
 4. explorers per credit window: one knob (1), two gains (2).
"""
import json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from units import K_B,T,E,V_TYP,C_MAX,Q_BIO,J_REST,V_CAL,MISMATCH
V=ROOT/'lab/v';OUT=V/'calibration_precision_20261120/e';P_ANCHOR=4/34;SPACING=10.
def q(a,p):return float(np.quantile(a,p))
def tN(N,prob=.95):
    """smallest event count n (time n*SPACING) with P(at least N anchors) >= prob."""
    n=N
    while True:
        cdf=sum(math.comb(n,k)*P_ANCHOR**k*(1-P_ANCHOR)**(n-k) for k in range(N))
        if 1-cdf>=prob:return n*SPACING
        n+=1
def main():
    OUT.mkdir(parents=True,exist_ok=False)
    A=json.loads((V/'calibration_precision_20261120/a/summary.json').read_text())
    req={(t['set'],t['weight'],t['window'],t['mode']):t for t in A['table']}
    streams=json.loads((V/'order_long_calibration/streams.json').read_text())
    counts=[sum(1 for e in s['events'] if e['case']['a']>0 and e['case']['b']>0 and e['case']['delay']==0) for s in streams]
    nev=[len(s['events']) for s in streams]
    rate=dict(nominal_anchor_interval_s=SPACING/P_ANCHOR,counted_anchors_per_1000s=dict(min=min(counts),median=float(np.median(counts)),max=max(counts),mean=float(np.mean(counts))),
        events_per_1000s_mean=float(np.mean(nev)),time_s_for_95pct_at_least_N_anchors={str(N):tN(N) for N in [1,2,4,8]})
    recs=[json.loads(l) for l in (V/'calibration_next_20261120/t1b/records.jsonl').read_text().splitlines()]
    per={}
    for r in recs:
        if r['window']!='full_1000s':continue
        c=r['categories']['simultaneous'];n=c['n']
        per.setdefault((r['weight'],r['mode']),[]).append(dict(seed=r['seed'],n=n,B=c['B_Vs']/n,W=c['W_s']/n,W2=c['W2_s']/n))
    anchor_stats={f'{w}|{m}':dict(anchors=sum(x['n'] for x in v),B_per_anchor_Vs=[q([x['B'] for x in v],p) for p in (.1,.5,.9)],W_per_anchor_s=[q([x['W'] for x in v],p) for p in (.1,.5,.9)],
        W2_per_anchor_s=[q([x['W2'] for x in v],p) for p in (.1,.5,.9)],note='10%, 50%, 90% over 40 draws of each draw\'s mean per anchor') for (w,m),v in sorted(per.items())}
    # per-anchor settings (evidence variability), D165 final-third contributions
    feas={r['seed']:r for r in json.loads((V/'overnight_20261119/failures_results/feasible_intervals.json').read_text())}
    ev=[json.loads(l) for l in (V/'overnight_20261119/attribution_results/event_contributions.jsonl').read_text().splitlines()]
    single={}
    for m in ['raw','0.15','1.0','3.8585074308112732']:
        inside=tot=0;ds=[]
        for x in ev:
            if x['kind']!='simultaneous' or x['seed']==2026112215:continue
            d=-x['A_Vs'][m]/x['B_Vs'][m];lo,hi=feas[x['seed']]['interval'];tot+=1;inside+=lo<d<hi;ds.append(d)
        single[m]=dict(anchors=tot,single_anchor_setting_inside_feasible_interval=inside,share=inside/tot,setting_quantiles_10_50_90=[q(ds,p) for p in (.1,.5,.9)])
    # noise of nodes that would carry the observation
    raw=[json.loads(l) for l in (V/'motifs/order_v2/confirm.jsonl').read_text().splitlines()]
    dtmin=min(r['dt'] for r in raw);rows={r['seed']:r for r in raw if r['dt']==dtmin and not r['control']}
    w_anchor=per['w','0.15'];W2a=np.median([x['W2'] for x in w_anchor]);Wa=np.median([x['W'] for x in w_anchor])
    def substrate(name):
        out=[]
        for s,r in sorted(rows.items()):
            n=np.array(r['nodes']);e=np.array(r['elements']);C=n[2,7];G=n[1,7];tau=C/G
            gross=abs(e[0,5])+abs(e[0,6])+G*V_TYP   # upper bound on currents at the order node
            if name=='silicon':rate_I=E*gross+2*K_B*T*G
            else:rate_I=Q_BIO*V_TYP/V_CAL*gross+Q_BIO*J_REST*C*(V_TYP/V_CAL)**2
            s2=rate_I*tau/(2*C*C);var_int=2*s2*tau*W2a;out.append(math.sqrt(var_int)/Wa)
        Cb=C_MAX/2;Gb=Cb/.15
        sb=math.sqrt(K_B*T/Cb) if name=='silicon' else math.sqrt((Q_BIO*J_REST*Cb*(V_TYP/V_CAL)**2)*.15/(2*Cb*Cb))
        qe=E if name=='silicon' else Q_BIO*V_TYP/V_CAL
        sm=math.sqrt(qe*V_TYP/Cb)                    # memory volts for a full V_TYP write
        sm_e=sm/V_TYP*float(np.median([x['B'] for x in w_anchor]))/Wa   # in d units (span +-V_TYP <-> +-1), then e-equivalent
        order=float(np.median(out));tot=math.sqrt(order**2+sb**2+sm_e**2)
        reqs={'D165 histories, 95%':req[('D165_histories','w','full_1000s','0.15')]['required_sigma_mV_95'],'D163 draws, 95%':req[('D163_schedules','w','full_1000s','0.15')]['required_sigma_mV_95']}
        return dict(order_node_equivalent_error_per_anchor_mV=dict(median=1000*order,max=1000*max(out)),baseline_node_mV=1000*sb,memory_write_equivalent_mV=1000*sm_e,
            combined_per_anchor_mV=1000*tot,
            requirement_mV=reqs,snr_per_anchor={k:v/(1000*tot) for k,v in reqs.items()},
            anchors_for_noise_sd_equal_requirement={k:max(1,math.ceil((1000*tot/v)**2)) for k,v in reqs.items()},
            anchors_for_noise_sd_third_of_requirement={k:max(1,math.ceil((3*1000*tot/v)**2)) for k,v in reqs.items()},
            evidence_rate_snr2_per_second={k:(v/(1000*tot))**2/(SPACING/P_ANCHOR) for k,v in reqs.items()})
    noise=dict(silicon=substrate('silicon'),biology_reference_only=substrate('biology'),
        assumptions='order node currents bounded by |g5|+|g6|+leak*V_TYP; integral of OU noise approximated as white over the anchor; Wa, W2a medians per anchor (w, 0.15 s); memory 25 pF, full V_TYP write, knob span +-V_TYP for d in +-1; noise model of mixed_feedback.py, silicon events of one electron')
    explorers=dict(one_knob=1,two_gains=2,note='one scalar observation per credit window (an anchor); two gains need anchors whose positive/negative branch responses differ in ratio to separate them')
    fixed=dict(one_offset_mV=1000*MISMATCH*V_TYP,note='a fixed offset is not reduced by more anchors (D164, D167); noise is')
    out=dict(evidence_rate=rate,per_anchor=anchor_stats,single_anchor_settings=single,noise=noise,explorers_per_credit_window=explorers,fixed_offset_for_comparison=fixed)
    (OUT/'noise_wall.json').write_text(json.dumps(out,indent=1)+'\n');print(json.dumps(out,indent=1))
if __name__=='__main__':main()
