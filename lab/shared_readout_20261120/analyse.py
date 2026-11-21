"""D170 task 5: frozen analysis of the causal replay (replay/records.jsonl, refinement.json, controls.jsonl).
Reports every arm and parameter point; no winner chosen. Refuses to run unless the replay's gates passed.
Writes lab/v/shared_readout_20261120/analysis/{analysis.json,per_draw.jsonl}."""
import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'lab/v/shared_readout_20261120/replay';OUT=ROOT/'lab/v/shared_readout_20261120/analysis'

def stats(x):
    x=np.array([v for v in x if v is not None and np.isfinite(v)],float)
    if not len(x):return None
    return dict(n=int(len(x)),mean=float(x.mean()),sd=float(x.std(ddof=1)) if len(x)>1 else 0.,rms=float(np.sqrt(np.mean(x*x))),max_abs=float(np.max(abs(x))),
        median=float(np.median(x)),p10=float(np.percentile(x,10)),p90=float(np.percentile(x,90)))

def boot_diff(a,b,rng,n=4000):
    a=np.array(a,float);b=np.array(b,float);k=len(a);idx=rng.integers(0,k,(n,k));d=(a[idx]-b[idx]).sum(1)
    return dict(diff=float(a.sum()-b.sum()),ci95=[float(np.percentile(d,2.5)),float(np.percentile(d,97.5))],note='bootstrap over draws, exploratory, reused draws')

def main():
    st=json.loads((R/'status.json').read_text())
    if not st['gate_passed']:raise SystemExit('replay gates did not pass; not interpreted: '+json.dumps(st)[:500])
    OUT.mkdir(exist_ok=False);rng=np.random.default_rng(170)
    recs=[json.loads(l) for l in (R/'records.jsonl').read_text().splitlines()]
    by={}
    for r in recs:by[(r['point'],r['arm'])]=by.get((r['point'],r['arm']),{})|{r['seed']:r}
    seeds=sorted({r['seed'] for r in recs});assert len(seeds)==40
    arms=[('P1_native','shared'),('P1_native','separate'),('P2_preamp','shared'),('P2_preamp','separate'),('none','fixed'),('none','offline_full_1000s'),('none','offline_final_third_1000s')]
    summary={}
    for k in arms:
        rs=[by[k][s] for s in seeds];name='|'.join(k)
        S=dict(draws_all_pass=sum(r['all_pass'] for r in rs),draws=40,cases_passed=sum(r['passed'] for r in rs),cases=40*34,
            feasible_draws=sum(r['feasible'] is not None for r in rs))
        if k[1] in ('shared','separate','fixed'):
            S.update(eps_vs_offline_full_mV=stats([r['eps_vs_offline_full_1000s_mV'] for r in rs]),eps_vs_offline_final_third_mV=stats([r['eps_vs_offline_final_third_1000s_mV'] for r in rs]),
                eps_within_10mV=dict(full=sum(abs(r['eps_vs_offline_full_1000s_mV'])<=10 for r in rs),final_third=sum(abs(r['eps_vs_offline_final_third_1000s_mV'])<=10 for r in rs)),
                eps_within_15mV=dict(full=sum(abs(r['eps_vs_offline_full_1000s_mV'])<=15 for r in rs),final_third=sum(abs(r['eps_vs_offline_final_third_1000s_mV'])<=15 for r in rs)),
                time_in_feasible_full=stats([r['time_in_feasible_full'] for r in rs]),time_in_feasible_last_third=stats([r['time_in_feasible_last_third'] for r in rs]),
                calibration_delay_s=stats([r['calibration_delay_s'] for r in rs]),never_settled_in_feasible=sum(r['calibration_delay_s'] is None for r in rs),
                event_isolated_pass_share=dict(full=stats([r['event_isolated_pass_share']['full'] for r in rs]),last_third=stats([r['event_isolated_pass_share']['last_third'] for r in rs])),
                pos_near_mean_V=stats([r['pos_near_mean_V'] for r in rs]),neg_near_mean_V=stats([r['neg_near_mean_V'] for r in rs]),
                d_final=stats([r['d_final'] for r in rs]),knob_clipped=sum(abs(r['d_final'])>=1 for r in rs))
        if k[1] in ('shared','separate'):
            S.update(tracking_full_mV=dict(rms=stats([r['tracking_full_mV']['rms'] for r in rs]),mean=stats([r['tracking_full_mV']['mean'] for r in rs]),max=max(r['tracking_full_mV']['max'] for r in rs)),
                tracking_last_third_mV=dict(rms=stats([r['tracking_last_third_mV']['rms'] for r in rs]),mean=stats([r['tracking_last_third_mV']['mean'] for r in rs]),max=max(r['tracking_last_third_mV']['max'] for r in rs)),
                write_charge_C=stats([r['acc']['write_charge_C'] for r in rs]),write_time_s=stats([r['acc']['write_time_s'] for r in rs]),quiet_write_charge_C=stats([r['acc']['quiet_write_charge_C'] for r in rs]),
                max_abs_Vd_V=max(r['acc']['max_abs_Vd'] for r in rs),max_abs_m_V=max(r['max_abs_m'] for r in rs),
                affine_deviation_V=dict(max=max(r['affine_deviation_V']['max'] for r in rs),max_where_w=max(r['affine_deviation_V']['max_where_w_gt_0p01'] for r in rs)))
        summary[name]=S
    # paired draw and case rescues/harms (A against B: rescued = pass in A, fail in B)
    pairs=[(('P1_native','shared'),('none','fixed')),(('P2_preamp','shared'),('none','fixed')),(('P1_native','shared'),('P1_native','separate')),(('P2_preamp','shared'),('P2_preamp','separate')),
           (('P1_native','shared'),('none','offline_final_third_1000s')),(('P1_native','shared'),('none','offline_full_1000s')),(('P2_preamp','shared'),('none','offline_final_third_1000s')),
           (('P2_preamp','shared'),('none','offline_full_1000s')),(('P2_preamp','shared'),('P1_native','shared')),(('P1_native','separate'),('none','fixed')),(('P2_preamp','separate'),('none','fixed'))]
    paired={}
    for A,Bk in pairs:
        a=[by[A][s] for s in seeds];b=[by[Bk][s] for s in seeds]
        dr=sum(x['all_pass'] and not y['all_pass'] for x,y in zip(a,b));dh=sum(y['all_pass'] and not x['all_pass'] for x,y in zip(a,b))
        cr=sum(sum(p and not q for p,q in zip(x['case_pass'],y['case_pass'])) for x,y in zip(a,b));ch=sum(sum(q and not p for p,q in zip(x['case_pass'],y['case_pass'])) for x,y in zip(a,b))
        paired[f"{'|'.join(A)} vs {'|'.join(Bk)}"]=dict(draws_rescued=dr,draws_harmed=dh,cases_rescued=cr,cases_harmed=ch,
            rescued_seeds=[s for s,x,y in zip(seeds,a,b) if x['all_pass'] and not y['all_pass']],harmed_seeds=[s for s,x,y in zip(seeds,a,b) if y['all_pass'] and not x['all_pass']],
            all_pass_difference=boot_diff([x['all_pass'] for x in a],[y['all_pass'] for y in b],rng))
    per=[]
    for s in seeds:
        row=dict(seed=s,feasible=by[('none','fixed')][s]['feasible'])
        for k in arms:
            r=by[k][s];row['|'.join(k)]=dict(d=r['d_final'],all_pass=r['all_pass'],passed=r['passed'],eps_full_mV=r.get('eps_vs_offline_full_1000s_mV'),eps_lt_mV=r.get('eps_vs_offline_final_third_1000s_mV'),
                delay_s=r.get('calibration_delay_s'))
        per.append(row)
    failures={}
    for k in arms[:4]:
        failures['|'.join(k)]=[dict(seed=s,feasible=by[k][s]['feasible'],d_final=by[k][s]['d_final'],passed=by[k][s]['passed'],eps_full_mV=by[k][s]['eps_vs_offline_full_1000s_mV'],
            eps_lt_mV=by[k][s]['eps_vs_offline_final_third_1000s_mV'],offline_lt_d=by[('none','offline_final_third_1000s')][s]['d_final'],
            offline_lt_all_pass=by[('none','offline_final_third_1000s')][s]['all_pass'],tracking_rms_mV=by[k][s]['tracking_full_mV']['rms'],errors=by[k][s]['errors'],
            d_at_events_last5=by[k][s]['d_at_events'][-5:]) for s in seeds if not by[k][s]['all_pass']]
    ref=json.loads((R/'refinement.json').read_text())
    ctl=[json.loads(l) for l in (R/'controls.jsonl').read_text().splitlines()]
    controls=[dict(seed=x['seed'],control=x['control'],events_kept=x['events_kept'],point=x['point'],arm=x['arm'],d_final=x['d_final'],max_abs_d=None,all_pass=x['all_pass'],
        eps_full_mV=x.get('eps_vs_offline_full_1000s_mV'),write_charge_C=x.get('acc',{}).get('write_charge_C'),quiet_write_charge_C=x.get('acc',{}).get('quiet_write_charge_C'),
        tracking_rms_mV=x.get('tracking_full_mV',{}).get('rms')) for x in ctl if x['arm'] in ('shared','separate','fixed')]
    res=dict(status=st,summary=summary,paired=paired,failures=failures,refinement=ref,controls=controls)
    (OUT/'analysis.json').write_text(json.dumps(res,indent=1)+'\n');(OUT/'per_draw.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in per))
    for k,S in summary.items():
        e=S.get('eps_vs_offline_final_third_mV') or {};print(k,'all-pass',S['draws_all_pass'],'cases',S['cases_passed'],'eps_lt mean %.2f rms %.2f max %.2f'%(e.get('mean',0),e.get('rms',0),e.get('max_abs',0)) if e else '')
    for k,v in paired.items():print(k,{x:v[x] for x in ('draws_rescued','draws_harmed','cases_rescued','cases_harmed')},v['all_pass_difference']['ci95'])
if __name__=='__main__':main()
